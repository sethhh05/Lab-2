"""Aggregation and statistics functions for the GDELT tone study.

Spark helpers summarise the large event table; the other functions
work on the small pandas tables of sums built in Steps 18 and 26.
Equation numbers refer to Section 3.2 of the main notebook.

Used by the main notebook in Steps 9 to 30.
"""

SEED = 2026


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
    # 1. Build ONE .agg() with, per column: count, mean, stddev, min,
    #    max and percentile_approx(col, [.01,.25,.5,.75,.99], 10000).
    # 2. Collect the single result row and reshape to one row per column.
    raise NotImplementedError("Step 9")


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
        Index, column name, number empty and percent empty (Table 17).
    """
    # 1. Keep rows with n_fields == 58.
    # 2. ONE .agg with sum(shiftright(empty_mask, i) & 1) for i in 0..57.
    # 3. Divide by the row count for the percentage.
    raise NotImplementedError("Step 11")


def pooled_means(country_month_pd):
    """Compute each country's pooled tone measures from monthly sums.

    Parameters
    ----------
    country_month_pd : pandas.DataFrame
        Country-by-month sums from Step 18.

    Returns
    -------
    pandas.DataFrame
        Per country: events, pooled mean (Eq. 1), article-weighted mean
        (Eq. 2) and lead-paragraph-only mean.
    """
    # 1. Group by country and sum every sum column over months.
    # 2. Eq. 1 = sum_tone / n_events; Eq. 2 = sum_tone_art /
    #    sum_articles; root-only = sum_tone_root / n_root.
    raise NotImplementedError("Step 19")


def bootstrap_month_ci(country_month_pd, n_boot=2000, seed=SEED):
    """Month-block bootstrap 95% interval of each country's pooled mean.

    Parameters
    ----------
    country_month_pd : pandas.DataFrame
        Country-by-month sums from Step 18.
    n_boot : int
        Number of resamples.
    seed : int
        Random seed.

    Returns
    -------
    pandas.DataFrame
        Per country: ci_low and ci_high (2.5th and 97.5th percentiles).
    """
    # 1. Pivot n_events and sum_tone to countries x months arrays
    #    (fill missing months with 0).
    # 2. rng = np.random.default_rng(seed); for each resample draw 77
    #    month indices with replacement (same draw for all countries).
    # 3. Pooled mean of the draw = sum(sum_tone) / sum(n_events).
    # 4. Percentiles over the resamples, per country. Vectorise; no
    #    loops over events.
    raise NotImplementedError("Step 19")


def moving_average_2x12(values):
    """Centred 2x12 moving average along the last axis (Eq. 4).

    Parameters
    ----------
    values : numpy.ndarray
        Monthly series, shape (n_months,) or (n_series, n_months).

    Returns
    -------
    numpy.ndarray
        Trend of the same shape; NaN for the first and last 6 months.
    """
    # 1. Weights: 1/24, then eleven times 1/12, then 1/24 (13 weights).
    # 2. Convolve along the month axis ('valid'), then pad 6 NaN each
    #    side.
    raise NotImplementedError("Step 23")


def seasonal_index(anomaly_pd):
    """Seasonal index and amplitude per series (Eq. 6).

    Parameters
    ----------
    anomaly_pd : pandas.DataFrame
        Anomalies (Eq. 5), rows = countries, columns = 'YYYY-MM'.

    Returns
    -------
    tuple of pandas.DataFrame
        (index with 12 columns summing to 0, summary with amplitude,
        peak month and trough month).
    """
    # 1. Mean of the anomalies per calendar month (ignore NaN).
    # 2. Subtract the mean of the 12 values.
    # 3. amplitude = max - min; peak = argmax; trough = argmin.
    raise NotImplementedError("Step 24")


def permutation_amplitude_test(anomaly_pd, n_perm=2000, seed=SEED):
    """Permutation p-value of each series' seasonal amplitude (Eq. 7).

    Parameters
    ----------
    anomaly_pd : pandas.DataFrame
        Anomalies, rows = countries, columns = 'YYYY-MM'.
    n_perm : int
        Number of permutations.
    seed : int
        Random seed.

    Returns
    -------
    tuple
        (p-values per country as pandas.Series, null amplitudes as
        numpy.ndarray of shape (n_countries, n_perm) for the bands of
        Figures 15 and 20).
    """
    # 1. For each permutation, shuffle the calendar-month labels WITHIN
    #    each year (same shuffle for all countries), recompute the
    #    amplitude with the logic of seasonal_index.
    # 2. p = (1 + count(null >= observed)) / (1 + n_perm).
    raise NotImplementedError("Step 24")


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
    # 1. Sort p ascending; q_i = p_i * m / rank_i.
    # 2. Enforce monotonicity from the largest rank down
    #    (cumulative minimum), cap at 1, restore the original order.
    raise NotImplementedError("Step 24")


def tone_decomposition(country_root_pd, global_root_pd):
    """Split each country's tone gap into mix and within parts (Eq. 8).

    Parameters
    ----------
    country_root_pd : pandas.DataFrame
        Events and tone sums per country and CAMEO root.
    global_root_pd : pandas.DataFrame
        Events and tone sums per CAMEO root over the reference group
        (the world in Step 27, the other SEA countries in Step 30).

    Returns
    -------
    pandas.DataFrame
        Per country and root: mix_k and within_k; per country: gap,
        mix, within (sums over roots).
    """
    # 1. Shares s_ck, s_gk and mean tones t_ck, t_gk; reference mean.
    # 2. mix_k = (s_ck - s_gk) * (t_gk - ref_mean);
    #    within_k = s_ck * (t_ck - t_gk); cells with s_ck = 0 add 0.
    # 3. The caller asserts gap == mix + within.
    raise NotImplementedError("Steps 27 and 30")


def period_change(rel_tone_pd, split_month, n_boot=2000, seed=SEED):
    """Before/after change of the Philippines versus SEA (Eq. 9).

    Parameters
    ----------
    rel_tone_pd : pandas.DataFrame
        Monthly relative tone (Eq. 3) with columns 'ph' and 'sea',
        indexed by 'YYYY-MM'.
    split_month : str
        First month of the 'after' period, e.g. '2016-07'.
    n_boot : int
        Bootstrap resamples (months resampled within each period).
    seed : int
        Random seed.

    Returns
    -------
    pandas.DataFrame
        Mean before and after for each group, delta and its 95% interval
        (Table 32).
    """
    # 1. Split the months at split_month.
    # 2. delta = (ph_after - ph_before) - (sea_after - sea_before).
    # 3. Bootstrap months within each period for the interval.
    raise NotImplementedError("Step 29")
