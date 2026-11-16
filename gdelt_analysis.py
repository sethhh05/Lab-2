"""Aggregation and statistics functions for the GDELT tone study.

The two Spark helpers summarise the large event table; the other
functions work on the small pandas tables of sums built in Steps 18 and
26. Equation numbers refer to Section 3.2 of the main notebook.

Used by the main notebook in Steps 9 to 30.
"""

import numpy as np
import pandas as pd

SEED = 2026
PERCENTILES = [0.01, 0.25, 0.5, 0.75, 0.99]
COUNTRY_KEYS = ["country_fips", "iso3", "country_name"]


def numeric_summary(df, cols):
    """Summarise numeric columns of a Spark DataFrame in one pass.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Event table.
    cols : list of str
        Numeric columns to summarise.

    Returns
    -------
    pandas.DataFrame
        One row per column: count, mean, std, min, p01, p25, p50, p75,
        p99, max (Table 13).
    """
    from pyspark.sql import functions as F

    exprs = []
    for col in cols:
        exprs += [
            F.count(col).alias(f"{col}__count"),
            F.mean(col).alias(f"{col}__mean"),
            F.stddev(col).alias(f"{col}__std"),
            F.min(col).alias(f"{col}__min"),
            F.max(col).alias(f"{col}__max"),
            F.percentile_approx(col, PERCENTILES, 10000)
            .alias(f"{col}__pct"),
        ]
    row = df.agg(*exprs).collect()[0]  # one job, one result row
    records = []
    for col in cols:
        p01, p25, p50, p75, p99 = row[f"{col}__pct"]
        records.append({
            "field": col,
            "count": row[f"{col}__count"],
            "mean": row[f"{col}__mean"],
            "std": row[f"{col}__std"],
            "min": row[f"{col}__min"],
            "p01": p01, "p25": p25, "p50": p50, "p75": p75, "p99": p99,
            "max": row[f"{col}__max"],
        })
    return pd.DataFrame(records).set_index("field")


def null_profile(df, column_names):
    """Count empty values in every raw column using the bit mask.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Parsed table with ``empty_mask`` and ``n_fields`` columns.
    column_names : list of str
        The 58 raw column names, in file order.

    Returns
    -------
    pandas.DataFrame
        Index, column name, number empty and percent empty (Table 17),
        computed over rows with 58 fields.
    """
    from pyspark.sql import functions as F

    valid_df = df.filter(F.col("n_fields") == len(column_names))
    exprs = [F.count(F.lit(1)).alias("rows")]
    for i in range(len(column_names)):
        # bit i of the mask is 1 when raw field i was empty
        exprs.append(
            F.sum(F.shiftright("empty_mask", i).bitwiseAND(1))
            .alias(f"c{i}"))
    row = valid_df.agg(*exprs).collect()[0]
    total = row["rows"]
    profile_pd = pd.DataFrame({
        "index": range(len(column_names)),
        "column": column_names,
        "empty": [int(row[f"c{i}"] or 0)
                  for i in range(len(column_names))],
    })
    profile_pd["pct_empty"] = 100 * profile_pd["empty"] / max(total, 1)
    return profile_pd


def pooled_means(country_month_pd):
    """Compute each country's pooled tone measures from monthly sums.

    Parameters
    ----------
    country_month_pd : pandas.DataFrame
        Country-by-month sums from Step 18 with columns country_fips,
        iso3, country_name, ym_added, n_events, sum_tone, sum_articles,
        sum_tone_art, n_root, sum_tone_root.

    Returns
    -------
    pandas.DataFrame
        Per country: n_events, mean_tone (Eq. 1), mean_tone_art
        (Eq. 2) and mean_tone_root (lead-paragraph events only).
    """
    sums = (country_month_pd
            .groupby(COUNTRY_KEYS, dropna=False)
            [["n_events", "sum_tone", "sum_articles", "sum_tone_art",
              "n_root", "sum_tone_root"]]
            .sum()
            .reset_index())
    sums["mean_tone"] = sums["sum_tone"] / sums["n_events"]
    sums["mean_tone_art"] = (sums["sum_tone_art"]
                             / sums["sum_articles"].replace(0, np.nan))
    sums["mean_tone_root"] = (sums["sum_tone_root"]
                              / sums["n_root"].replace(0, np.nan))
    return sums[COUNTRY_KEYS + ["n_events", "mean_tone", "mean_tone_art",
                                "mean_tone_root"]]


def _month_matrix(country_month_pd, value):
    """Pivot one sum column to a countries x months array (0 if absent).

    Parameters
    ----------
    country_month_pd : pandas.DataFrame
        Country-by-month sums.
    value : str
        Column to pivot.

    Returns
    -------
    pandas.DataFrame
        Rows = country_fips, columns = ym_added (sorted).
    """
    return (country_month_pd
            .pivot_table(index="country_fips", columns="ym_added",
                         values=value, aggfunc="sum", fill_value=0)
            .sort_index(axis=1))


def bootstrap_month_ci(country_month_pd, n_boot=2000, seed=SEED,
                       level=0.95):
    """Month-block bootstrap interval of each country's pooled mean.

    Parameters
    ----------
    country_month_pd : pandas.DataFrame
        Country-by-month sums from Step 18.
    n_boot : int
        Number of resamples.
    seed : int
        Random seed.
    level : float
        Confidence level.

    Returns
    -------
    pandas.DataFrame
        Indexed by country_fips, with ci_low and ci_high.
    """
    counts = _month_matrix(country_month_pd, "n_events")
    tones = _month_matrix(country_month_pd, "sum_tone").loc[counts.index]
    n_months = counts.shape[1]
    rng = np.random.default_rng(seed)
    # the same resampled months for every country in one draw
    draws = rng.integers(0, n_months, size=(n_boot, n_months))
    weights = np.zeros((n_boot, n_months))
    for b in range(n_boot):
        weights[b] = np.bincount(draws[b], minlength=n_months)
    boot_tone = weights @ tones.to_numpy(dtype=float).T
    boot_n = weights @ counts.to_numpy(dtype=float).T
    with np.errstate(invalid="ignore", divide="ignore"):
        boot_mean = boot_tone / boot_n  # pooled mean (Eq. 1) per draw
    tail = 100 * (1 - level) / 2
    return pd.DataFrame({
        "ci_low": np.nanpercentile(boot_mean, tail, axis=0),
        "ci_high": np.nanpercentile(boot_mean, 100 - tail, axis=0),
    }, index=counts.index)


def moving_average_2x12(values):
    """Centred 2x12 moving average along the last axis (Eq. 4).

    Parameters
    ----------
    values : array-like
        Monthly series, shape (n_months,) or (n_series, n_months).

    Returns
    -------
    numpy.ndarray
        Trend of the same shape; NaN for the first and last 6 months
        and wherever the 13-month window contains a NaN.
    """
    arr = np.asarray(values, dtype=float)
    weights = np.r_[1 / 24, np.full(11, 1 / 12), 1 / 24]
    windows = np.lib.stride_tricks.sliding_window_view(arr, 13, axis=-1)
    core = windows @ weights
    pad = np.full(arr.shape[:-1] + (6,), np.nan)
    return np.concatenate([pad, core, pad], axis=-1)


def _calendar_months(columns):
    """Calendar month (1-12) of each 'YYYY-MM' column label."""
    return np.array([int(str(c)[5:7]) for c in columns])


def _years(columns):
    """Year of each 'YYYY-MM' column label."""
    return np.array([int(str(c)[:4]) for c in columns])


def _index_from_labels(values, mask, labels):
    """Centred seasonal index for given month labels (vectorised).

    Parameters
    ----------
    values : numpy.ndarray
        Anomalies with NaN replaced by 0, shape (n_series, n_months).
    mask : numpy.ndarray
        1.0 where the anomaly exists, else 0.0.
    labels : numpy.ndarray
        Calendar month (1-12) of each column.

    Returns
    -------
    numpy.ndarray
        Seasonal index, shape (n_series, 12), each row summing to 0.
    """
    one_hot = (labels[:, None] == np.arange(1, 13)[None, :]).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        means = (values @ one_hot) / (mask @ one_hot)
    return means - np.nanmean(means, axis=1, keepdims=True)


def seasonal_index(anomaly_pd):
    """Seasonal index and amplitude per series (Eq. 6).

    Parameters
    ----------
    anomaly_pd : pandas.DataFrame
        Anomalies (Eq. 5), rows = countries, columns = 'YYYY-MM'.

    Returns
    -------
    tuple of pandas.DataFrame
        (index_pd with columns 1..12 summing to 0 per row,
        summary_pd with amplitude, peak_month and trough_month).
    """
    values = anomaly_pd.to_numpy(dtype=float)
    mask = (~np.isnan(values)).astype(float)
    index = _index_from_labels(np.nan_to_num(values), mask,
                               _calendar_months(anomaly_pd.columns))
    index_pd = pd.DataFrame(index, index=anomaly_pd.index,
                            columns=range(1, 13))
    summary_pd = pd.DataFrame({
        "amplitude": index_pd.max(axis=1) - index_pd.min(axis=1),
        "peak_month": index_pd.idxmax(axis=1),
        "trough_month": index_pd.idxmin(axis=1),
    })
    return index_pd, summary_pd


def permutation_amplitude_test(anomaly_pd, n_perm=2000, seed=SEED,
                               band=0.95):
    """Permutation test of each series' seasonal amplitude (Eq. 7).

    Calendar-month labels are shuffled within each year, the same
    shuffle for every country, and the amplitude is recomputed.

    Parameters
    ----------
    anomaly_pd : pandas.DataFrame
        Anomalies, rows = countries, columns = 'YYYY-MM'.
    n_perm : int
        Number of permutations.
    seed : int
        Random seed.
    band : float
        Coverage of the chance band returned for Figures 15 and 20.

    Returns
    -------
    tuple
        (p_values : pandas.Series,
        null_amp : numpy.ndarray of shape (n_countries, n_perm),
        band_low : pandas.DataFrame (countries x 12),
        band_high : pandas.DataFrame (countries x 12)).
    """
    values = anomaly_pd.to_numpy(dtype=float)
    mask = (~np.isnan(values)).astype(float)
    filled = np.nan_to_num(values)
    labels = _calendar_months(anomaly_pd.columns)
    years = _years(anomaly_pd.columns)
    observed = _index_from_labels(filled, mask, labels)
    observed_amp = (np.nanmax(observed, axis=1)
                    - np.nanmin(observed, axis=1))
    rng = np.random.default_rng(seed)
    n_series = values.shape[0]
    null_amp = np.empty((n_series, n_perm))
    null_index = np.empty((n_perm, n_series, 12))
    year_positions = [np.flatnonzero(years == y) for y in np.unique(years)]
    for b in range(n_perm):
        shuffled = labels.copy()
        for pos in year_positions:  # shuffle within each year only
            shuffled[pos] = rng.permutation(labels[pos])
        index = _index_from_labels(filled, mask, shuffled)
        null_index[b] = index
        null_amp[:, b] = (np.nanmax(index, axis=1)
                          - np.nanmin(index, axis=1))
    exceed = (null_amp >= observed_amp[:, None]).sum(axis=1)
    p_values = pd.Series((1 + exceed) / (1 + n_perm),
                         index=anomaly_pd.index, name="p_value")
    tail = 100 * (1 - band) / 2
    band_low = pd.DataFrame(np.nanpercentile(null_index, tail, axis=0),
                            index=anomaly_pd.index, columns=range(1, 13))
    band_high = pd.DataFrame(
        np.nanpercentile(null_index, 100 - tail, axis=0),
        index=anomaly_pd.index, columns=range(1, 13))
    return p_values, null_amp, band_low, band_high


def benjamini_hochberg(p_values):
    """Benjamini-Hochberg q-values for a set of p-values.

    Parameters
    ----------
    p_values : array-like
        Raw p-values.

    Returns
    -------
    numpy.ndarray
        q-values in the original order.
    """
    p = np.asarray(p_values, dtype=float)
    m = p.size
    order = np.argsort(p)
    scaled = p[order] * m / np.arange(1, m + 1)
    # cumulative minimum from the largest p down keeps q monotone
    q_sorted = np.minimum.accumulate(scaled[::-1])[::-1]
    q = np.empty(m)
    q[order] = np.minimum(q_sorted, 1.0)
    return q


def tone_decomposition(country_root_pd, reference_root_pd):
    """Split each country's tone gap into mix and within parts (Eq. 8).

    Parameters
    ----------
    country_root_pd : pandas.DataFrame
        Columns country_fips, event_root_code, n, sum_tone.
    reference_root_pd : pandas.DataFrame
        Columns event_root_code, n, sum_tone for the reference group
        (the world in Step 27, the other SEA countries in Step 30).

    Returns
    -------
    tuple of pandas.DataFrame
        (per_root_pd with country_fips, event_root_code, mix_k,
        within_k; per_country_pd indexed by country_fips with
        mean_tone, ref_mean, gap, mix, within).
    """
    ref = reference_root_pd.groupby("event_root_code")[
        ["n", "sum_tone"]].sum()
    ref_mean = ref["sum_tone"].sum() / ref["n"].sum()
    ref_share = ref["n"] / ref["n"].sum()
    ref_tone = ref["sum_tone"] / ref["n"]
    roots = sorted(set(ref.index)
                   | set(country_root_pd["event_root_code"]))
    s_g = ref_share.reindex(roots, fill_value=0.0)
    # a root absent from the reference gets the reference mean, which
    # keeps the two parts summing exactly to the gap
    t_g = ref_tone.reindex(roots).fillna(ref_mean)
    cty = (country_root_pd
           .pivot_table(index="country_fips", columns="event_root_code",
                        values=["n", "sum_tone"], aggfunc="sum",
                        fill_value=0)
           .reindex(columns=pd.MultiIndex.from_product(
               [["n", "sum_tone"], roots]), fill_value=0))
    n_ck = cty["n"].to_numpy(dtype=float)
    tone_ck = cty["sum_tone"].to_numpy(dtype=float)
    totals = n_ck.sum(axis=1, keepdims=True)
    s_c = n_ck / totals
    with np.errstate(invalid="ignore", divide="ignore"):
        t_c = np.where(n_ck > 0, tone_ck / n_ck, 0.0)
    mix = (s_c - s_g.to_numpy()) * (t_g.to_numpy() - ref_mean)
    within = s_c * (t_c - t_g.to_numpy())  # 0 where the country has none
    per_root_pd = pd.DataFrame({
        "country_fips": np.repeat(cty.index.to_numpy(), len(roots)),
        "event_root_code": np.tile(roots, len(cty.index)),
        "mix_k": mix.ravel(),
        "within_k": within.ravel(),
    })
    mean_tone = tone_ck.sum(axis=1) / totals[:, 0]
    per_country_pd = pd.DataFrame({
        "mean_tone": mean_tone,
        "ref_mean": ref_mean,
        "gap": mean_tone - ref_mean,
        "mix": mix.sum(axis=1),
        "within": within.sum(axis=1),
    }, index=cty.index)
    return per_root_pd, per_country_pd


def period_change(rel_tone_pd, split_month, n_boot=2000, seed=SEED,
                  level=0.95):
    """Before/after change of the Philippines versus SEA (Eq. 9).

    Parameters
    ----------
    rel_tone_pd : pandas.DataFrame
        Monthly relative tone (Eq. 3) with columns 'ph' and 'sea',
        indexed by 'YYYY-MM'.
    split_month : str
        First month of the 'after' period, e.g. '2016-07'.
    n_boot : int
        Bootstrap resamples (months resampled within each period,
        paired between the two groups).
    seed : int
        Random seed.
    level : float
        Confidence level.

    Returns
    -------
    pandas.DataFrame
        Rows ph, sea and delta; columns before, after, change, ci_low,
        ci_high (Table 32). The interval is given for delta only.
    """
    data = rel_tone_pd[["ph", "sea"]].dropna().sort_index()
    before = data[data.index < split_month].to_numpy()
    after = data[data.index >= split_month].to_numpy()

    def _delta(b_vals, a_vals):
        """Difference of changes, Eq. 9."""
        change = a_vals.mean(axis=0) - b_vals.mean(axis=0)
        return change[0] - change[1]

    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        b_idx = rng.integers(0, len(before), len(before))
        a_idx = rng.integers(0, len(after), len(after))
        boot[i] = _delta(before[b_idx], after[a_idx])
    tail = 100 * (1 - level) / 2
    mean_b = before.mean(axis=0)
    mean_a = after.mean(axis=0)
    table = pd.DataFrame({
        "before": [mean_b[0], mean_b[1], np.nan],
        "after": [mean_a[0], mean_a[1], np.nan],
        "change": [mean_a[0] - mean_b[0], mean_a[1] - mean_b[1],
                   _delta(before, after)],
        "ci_low": [np.nan, np.nan, np.percentile(boot, tail)],
        "ci_high": [np.nan, np.nan, np.percentile(boot, 100 - tail)],
    }, index=["ph", "sea", "delta"])
    return table
