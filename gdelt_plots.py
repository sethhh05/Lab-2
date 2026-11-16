"""Figure functions for the GDELT tone report.

One function per figure (Figures 1 to 21 of the main notebook), all
sharing the style set by ``set_style``. Each function returns the
figure; the notebook saves it with ``save_fig`` and shows it. Captions
live in the notebook, so figures carry no titles.

Used by the main notebook in every step that draws a figure.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

FIG_DIR = "./figures"
DPI = 150
WIDTH = 10  # inches; every figure shares this width

# Palette: one colour per QuadClass, a diverging map for tone, and one
# accent for the Philippines.
QUAD_COLORS = {1: "#4C78A8", 2: "#72B7B2", 3: "#F58518", 4: "#E45756"}
QUAD_LABELS = {1: "Verbal cooperation", 2: "Material cooperation",
               3: "Verbal conflict", 4: "Material conflict"}
NEUTRAL = "#7F7F7F"
LIGHT = "#D9D9D9"
ACCENT = "#B5179E"
POSITIVE = "#2166AC"
NEGATIVE = "#B2182B"
TONE_CMAP = "RdBu"
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]


def set_style():
    """Apply one font, figure size and look to every figure.

    Returns
    -------
    None
    """
    plt.rcParams.update({
        "figure.figsize": (WIDTH, 5),
        "figure.dpi": 100,
        "savefig.dpi": DPI,
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#EBEBEB",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
    })


def save_fig(fig, name, fig_dir=FIG_DIR):
    """Save a matplotlib figure as PNG in the figures folder.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    name : str
        File name without extension, e.g. 'fig02_daily_volume'.
    fig_dir : str
        Relative output folder.

    Returns
    -------
    str
        Relative path of the saved file.
    """
    os.makedirs(fig_dir, exist_ok=True)
    path = os.path.join(fig_dir, name + ".png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    return path


def _box(ax, x, y, text, color, width=1.9, height=0.9):
    """Draw one rounded pipeline box centred at (x, y)."""
    patch = FancyBboxPatch((x - width / 2, y - height / 2), width, height,
                           boxstyle="round,pad=0.02,rounding_size=0.12",
                           facecolor=color, edgecolor="none", alpha=0.9)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5,
            color="white", wrap=True)


def _arrow(ax, start, end):
    """Draw an arrow between two points of the pipeline diagram."""
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "-|>", "color": NEUTRAL,
                            "lw": 1.2})


def plot_pipeline_diagram():
    """Figure 1: pipeline of the study (boxes and arrows).

    Returns
    -------
    matplotlib.figure.Figure
    """
    prep, agg, rq, other = "#4C78A8", "#54A24B", "#F58518", NEUTRAL
    fig, ax = plt.subplots(figsize=(WIDTH, 4.6))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 5)
    ax.axis("off")
    top = 3.9
    _box(ax, 1.1, top, "Raw input\n2,335 daily zips\n24 GB", other,
         width=1.8)
    _box(ax, 3.3, top, "1. Ingest\nSpark parse,\nParquet cache\n"
         "(Steps 4-7)", prep)
    _box(ax, 5.6, top, "2. Explore\nvolume, tone, nulls,\nlag, duplicates"
         "\n(Steps 8-15)", prep)
    _box(ax, 7.9, top, "3. Filter\ncounted at\nevery step\n"
         "(Steps 16-17)", prep)
    _box(ax, 10.6, top, "4. Aggregate\ncountry x month,\ncountry x CAMEO"
         "\n(Steps 18, 26)", agg, width=2.2)
    for x0, x1 in [(2.0, 2.35), (4.25, 4.65), (6.55, 6.95),
                   (8.85, 9.5)]:
        _arrow(ax, (x0, top), (x1, top))
    low = 1.5
    rq_boxes = [
        (1.6, "5. RQ1 Rank\nCIs, map, robustness\n(Steps 19-21)"),
        (4.3, "6. RQ2 Seasonality\ndetrend, index,\npermutation test\n"
              "(Steps 22-25)"),
        (7.0, "7. RQ3 Drivers\nmix vs within\n(Steps 26-27)"),
        (9.7, "8. RQ4 Philippines\nvs Southeast Asia\n(Steps 28-30)"),
    ]
    for x, label in rq_boxes:
        _box(ax, x, low, label, rq, width=2.3, height=1.1)
        _arrow(ax, (10.6, top - 0.47), (x, low + 0.57))
    _box(ax, 11.75, low, "Report\nSections\n11-12", other, width=1.1,
         height=1.1)
    _arrow(ax, (10.87, low), (11.18, low))
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in
               (prep, agg, rq)]
    ax.legend(handles, ["Prepare data", "Aggregate", "Answer RQs"],
              loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06))
    return fig


def plot_daily_volume(daily_pd, missing_days):
    """Figure 2: events per day with a 30-day mean and missing days.

    Parameters
    ----------
    daily_pd : pandas.DataFrame
        Columns date (datetime) and events, on the full date range
        (NaN on missing days).
    missing_days : list of pandas.Timestamp
        Days with no raw file.

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = daily_pd.sort_values("date")
    thousands = data["events"] / 1000
    fig, ax = plt.subplots(figsize=(WIDTH, 4))
    ax.plot(data["date"], thousands, color=LIGHT, lw=0.6,
            label="Daily")
    ax.plot(data["date"],
            thousands.rolling(30, center=True, min_periods=20).mean(),
            color=POSITIVE, lw=1.8, label="30-day centred mean")
    ax.plot(list(missing_days), [0] * len(missing_days), "|",
            color=NEGATIVE, ms=14, mew=2, label="No file")
    ax.set_ylabel("Events added per day (thousands)")
    ax.set_xlabel("Publication date (DATEADDED)")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left")
    return fig


def plot_tone_hist(hist_pd, mean_tone, median_tone, share_outside):
    """Figure 3: histogram of AvgTone with mean and median lines.

    Parameters
    ----------
    hist_pd : pandas.DataFrame
        Columns bin (left edge, width 0.5) and count, from Spark.
    mean_tone, median_tone : float
        Global mean and median tone.
    share_outside : float
        Percent of events outside -20..+20.

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = hist_pd[(hist_pd["bin"] >= -20) & (hist_pd["bin"] < 20)]
    share = 100 * data["count"] / hist_pd["count"].sum()
    colors = np.where(data["bin"] < 0, NEGATIVE, POSITIVE)
    fig, ax = plt.subplots(figsize=(WIDTH, 4))
    ax.bar(data["bin"], share, width=0.5, align="edge", color=colors,
           alpha=0.75)
    ax.axvline(mean_tone, color="black", ls="--", lw=1.2,
               label=f"Mean {mean_tone:.2f}")
    ax.axvline(median_tone, color="black", ls=":", lw=1.4,
               label=f"Median {median_tone:.2f}")
    ax.text(0.99, 0.95, f"{share_outside:.2f}% of events outside "
            "-20 to +20", transform=ax.transAxes, ha="right",
            va="top", color=NEUTRAL)
    ax.set_xlabel("AvgTone (bins of 0.5)")
    ax.set_ylabel("Share of events (%)")
    ax.legend(loc="upper left")
    return fig


def plot_tone_by_root(root_pd, global_mean):
    """Figure 4: mean tone per CAMEO root, coloured by QuadClass.

    Parameters
    ----------
    root_pd : pandas.DataFrame
        Columns event_root_code, root_name, quad_class, mean_tone.
    global_mean : float
        Global mean tone (vertical line).

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = root_pd.sort_values("mean_tone")
    labels = data["event_root_code"] + " " + data["root_name"]
    colors = [QUAD_COLORS[q] for q in data["quad_class"]]
    fig, ax = plt.subplots(figsize=(WIDTH, 6))
    ax.barh(labels, data["mean_tone"], color=colors)
    ax.axvline(global_mean, color="black", ls="--", lw=1)
    ax.axvline(0, color=NEUTRAL, lw=0.8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=QUAD_COLORS[q])
               for q in QUAD_COLORS]
    handles.append(plt.Line2D([], [], color="black", ls="--"))
    ax.legend(handles, list(QUAD_LABELS.values()) + ["Global mean"],
              loc="lower right")
    ax.set_xlabel("Mean AvgTone")
    ax.grid(axis="y", visible=False)
    return fig


def plot_unlocated(share_month_pd, tone_quad_pd):
    """Figure 5: (a) unlocated share per month, (b) tone by QuadClass.

    Parameters
    ----------
    share_month_pd : pandas.DataFrame
        Columns ym_added and pct_unlocated.
    tone_quad_pd : pandas.DataFrame
        Columns quad_class, located (mean tone), unlocated (mean tone).

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(WIDTH, 4), gridspec_kw={"width_ratios": [1.6, 1]})
    months = pd.to_datetime(share_month_pd["ym_added"])
    ax_a.plot(months, share_month_pd["pct_unlocated"], color=POSITIVE)
    ax_a.set_ylabel("Events with no location (%)")
    ax_a.set_xlabel("Publication month")
    ax_a.set_ylim(bottom=0)
    ax_a.set_title("(a)", loc="left")
    pos = np.arange(len(tone_quad_pd))
    ax_b.bar(pos - 0.2, tone_quad_pd["located"], 0.4, color=POSITIVE,
             label="Located")
    ax_b.bar(pos + 0.2, tone_quad_pd["unlocated"], 0.4, color=LIGHT,
             label="No location")
    ax_b.set_xticks(pos)
    ax_b.set_xticklabels([QUAD_LABELS[q].replace(" ", "\n")
                          for q in tone_quad_pd["quad_class"]],
                         fontsize=8)
    ax_b.axhline(0, color=NEUTRAL, lw=0.8)
    ax_b.set_ylabel("Mean AvgTone")
    ax_b.set_title("(b)", loc="left")
    ax_b.legend()
    fig.tight_layout()
    return fig


def plot_lag(lag_pd):
    """Figure 6: share of events per lag bucket, mean tone annotated.

    Parameters
    ----------
    lag_pd : pandas.DataFrame
        Columns bucket (ordered labels), pct and mean_tone.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(WIDTH, 4))
    ax.barh(lag_pd["bucket"], lag_pd["pct"], color=POSITIVE)
    for y, (pct, tone) in enumerate(zip(lag_pd["pct"],
                                        lag_pd["mean_tone"])):
        ax.text(pct, y, f"  {pct:.1f}%  (tone {tone:.2f})",
                va="center", fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Share of events (%)")
    ax.set_ylabel("Days between event and publication")
    ax.set_xlim(0, lag_pd["pct"].max() * 1.35)
    ax.grid(axis="y", visible=False)
    return fig


def plot_funnel(funnel_pd):
    """Figure 7: rows remaining after each filtering step.

    Parameters
    ----------
    funnel_pd : pandas.DataFrame
        Columns step (label), rows and pct_of_raw, in filter order.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(WIDTH, 4))
    millions = funnel_pd["rows"] / 1e6
    ax.barh(funnel_pd["step"], millions, color=POSITIVE)
    for y, (val, pct) in enumerate(zip(millions, funnel_pd["pct_of_raw"])):
        ax.text(val, y, f"  {val:,.1f} M ({pct:.1f}%)", va="center",
                fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Rows remaining (millions)")
    ax.set_xlim(0, millions.max() * 1.3)
    ax.grid(axis="y", visible=False)
    return fig


def plot_threshold(country_n_pd, thresholds, chosen):
    """Figure 8: 95% half-width against events per country (log-log).

    Parameters
    ----------
    country_n_pd : pandas.DataFrame
        Columns n_events and half_width (one row per country).
    thresholds : list of int
        Candidate thresholds (dashed lines).
    chosen : int
        Chosen threshold (solid line).

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(WIDTH, 4.5))
    ax.scatter(country_n_pd["n_events"], country_n_pd["half_width"],
               s=12, color=POSITIVE, alpha=0.7)
    for value in thresholds:
        ax.axvline(value, color=NEUTRAL, ls="--", lw=0.9)
        ax.text(value, 1.01, f"{value:,}", transform=ax.get_xaxis_transform(),
                ha="center", fontsize=8, color=NEUTRAL)
    ax.axvline(chosen, color=NEGATIVE, lw=1.6)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Located events per country (log)")
    ax.set_ylabel("95% half-width of mean tone (log)")
    return fig


def plot_ranking(ranked_pd, global_mean, top_n):
    """Figure 9: most positive and most negative countries with CIs.

    Parameters
    ----------
    ranked_pd : pandas.DataFrame
        Eligible countries with country_name, mean_tone, ci_low and
        ci_high.
    global_mean : float
        Global mean tone (dashed line).
    top_n : int
        Countries shown at each end.

    Returns
    -------
    matplotlib.figure.Figure
    """
    ordered = ranked_pd.sort_values("mean_tone", ascending=False)
    panels = [("Most positive", ordered.head(top_n)),
              ("Most negative", ordered.tail(top_n))]
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 0.32 * top_n + 1.5),
                             sharex=True)
    for ax, (label, data) in zip(axes, panels):
        data = data.iloc[::-1]  # best at the top of each panel
        color = np.where(data["mean_tone"] >= global_mean, POSITIVE,
                         NEGATIVE)
        y = np.arange(len(data))
        ax.errorbar(data["mean_tone"], y,
                    xerr=[data["mean_tone"] - data["ci_low"],
                          data["ci_high"] - data["mean_tone"]],
                    fmt="none", ecolor=NEUTRAL, elinewidth=1, capsize=2)
        ax.scatter(data["mean_tone"], y, c=color, s=28, zorder=3)
        ax.axvline(global_mean, color="black", ls="--", lw=1)
        ax.set_yticks(y)
        ax.set_yticklabels(data["country_name"], fontsize=8.5)
        ax.set_title(label, loc="left")
        ax.set_xlabel("Mean AvgTone (95% month-bootstrap CI)")
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def plot_world_map(map_pd, global_mean):
    """Figure 10: plotly choropleth of mean tone by country.

    Parameters
    ----------
    map_pd : pandas.DataFrame
        Columns iso3, country_name, n_events, mean_tone, ci_low,
        ci_high and eligible (bool).
    global_mean : float
        Midpoint of the diverging colour scale.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    import plotly.graph_objects as go

    data = map_pd.dropna(subset=["iso3"])
    shown = data[data["eligible"]]
    grey = data[~data["eligible"]]
    spread = np.nanpercentile(np.abs(shown["mean_tone"] - global_mean),
                              98)
    hover = ("<b>%{customdata[0]}</b><br>Mean tone %{z:.2f}"
             "<br>95% CI %{customdata[1]:.2f} to %{customdata[2]:.2f}"
             "<br>Events %{customdata[3]:,}<extra></extra>")
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=grey["iso3"], z=np.zeros(len(grey)),
        colorscale=[[0, LIGHT], [1, LIGHT]], showscale=False,
        hovertext=grey["country_name"], hoverinfo="text",
        marker_line_color="white", marker_line_width=0.4))
    fig.add_trace(go.Choropleth(
        locations=shown["iso3"], z=shown["mean_tone"],
        customdata=shown[["country_name", "ci_low", "ci_high",
                          "n_events"]].to_numpy(),
        hovertemplate=hover, colorscale=TONE_CMAP,
        zmid=global_mean, zmin=global_mean - spread,
        zmax=global_mean + spread,
        colorbar={"title": "Mean<br>AvgTone"},
        marker_line_color="white", marker_line_width=0.4))
    fig.update_geos(projection_type="natural earth", showframe=False,
                    showcoastlines=False)
    fig.update_layout(height=520, margin={"l": 0, "r": 0, "t": 10,
                                          "b": 0})
    return fig


def plot_robustness(summary_pd):
    """Figure 11: event-weighted versus article-weighted mean tone.

    Parameters
    ----------
    summary_pd : pandas.DataFrame
        Eligible countries with country_name, mean_tone and
        mean_tone_art.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(WIDTH * 0.7, WIDTH * 0.7))
    ax.scatter(summary_pd["mean_tone"], summary_pd["mean_tone_art"],
               s=14, color=POSITIVE, alpha=0.7)
    low = summary_pd[["mean_tone", "mean_tone_art"]].min().min()
    high = summary_pd[["mean_tone", "mean_tone_art"]].max().max()
    ax.plot([low, high], [low, high], color=NEUTRAL, ls="--", lw=1)
    ordered = summary_pd.sort_values("mean_tone")
    for _, row in pd.concat([ordered.head(5), ordered.tail(5)]).iterrows():
        ax.annotate(row["country_name"],
                    (row["mean_tone"], row["mean_tone_art"]),
                    fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("Mean tone, each event weighted equally (Eq. 1)")
    ax.set_ylabel("Mean tone, weighted by articles (Eq. 2)")
    return fig


def _shade_months(ax, months, which=(12, 1)):
    """Shade given calendar months on a monthly time axis."""
    for month in months:
        if month.month in which:
            ax.axvspan(month, month + pd.offsets.MonthEnd(1),
                       color="#F2F2F2", lw=0, zorder=0)


def plot_global_monthly(global_month_pd):
    """Figure 12: global monthly tone with trend, and volume per day.

    Parameters
    ----------
    global_month_pd : pandas.DataFrame
        Columns ym_added, mean_tone, trend and events_per_day.

    Returns
    -------
    matplotlib.figure.Figure
    """
    months = pd.to_datetime(global_month_pd["ym_added"])
    fig, (ax_t, ax_v) = plt.subplots(2, 1, figsize=(WIDTH, 6),
                                     sharex=True)
    for ax in (ax_t, ax_v):
        _shade_months(ax, months)
    ax_t.plot(months, global_month_pd["mean_tone"], color=POSITIVE,
              marker="o", ms=2.5, lw=1, label="Monthly mean")
    ax_t.plot(months, global_month_pd["trend"], color="black", lw=1.8,
              label="2x12 moving average")
    ax_t.set_ylabel("Global mean AvgTone")
    ax_t.legend(loc="lower left")
    ax_v.plot(months, global_month_pd["events_per_day"] / 1000,
              color=NEUTRAL)
    ax_v.set_ylabel("Events per available day\n(thousands)")
    ax_v.set_xlabel("Publication month")
    fig.tight_layout()
    return fig


def plot_decomposition_example(raw, world, rel, trend, anomaly, name):
    """Figure 13: raw, relative, trend and anomaly for one country.

    Parameters
    ----------
    raw, world, rel, trend, anomaly : pandas.Series
        Monthly series indexed by 'YYYY-MM'.
    name : str
        Country name for the legend.

    Returns
    -------
    matplotlib.figure.Figure
    """
    months = pd.to_datetime(raw.index)
    fig, axes = plt.subplots(3, 1, figsize=(WIDTH, 7.5), sharex=True)
    axes[0].plot(months, raw.values, color=ACCENT, label=name)
    axes[0].plot(months, world.values, color=NEUTRAL, label="World")
    axes[0].set_ylabel("Mean AvgTone")
    axes[0].legend(loc="lower left")
    axes[1].plot(months, rel.values, color=ACCENT, lw=1,
                 label="Relative tone (Eq. 3)")
    axes[1].plot(months, trend.values, color="black", lw=1.8,
                 label="2x12 trend (Eq. 4)")
    axes[1].axhline(0, color=NEUTRAL, lw=0.8)
    axes[1].set_ylabel("Tone minus world")
    axes[1].legend(loc="lower left")
    anomaly_months = pd.to_datetime(anomaly.index)
    axes[2].bar(anomaly_months, anomaly.values, width=20,
                color=np.where(anomaly.values >= 0, POSITIVE, NEGATIVE))
    axes[2].axhline(0, color=NEUTRAL, lw=0.8)
    axes[2].set_ylabel("Anomaly (Eq. 5)")
    axes[2].set_xlabel("Publication month")
    for ax, tag in zip(axes, "abc"):
        ax.set_title(f"({tag})", loc="left")
    fig.tight_layout()
    return fig


def plot_seasonal_heatmap(index_pd, significant):
    """Figure 14: seasonal index heatmap, countries x calendar months.

    Parameters
    ----------
    index_pd : pandas.DataFrame
        Rows = country names (already ordered), columns = 1..12.
    significant : set of str
        Countries with q < 0.05 (marked with an asterisk).

    Returns
    -------
    matplotlib.figure.Figure
    """
    limit = np.nanmax(np.abs(index_pd.to_numpy()))
    height = 0.24 * len(index_pd) + 1.5
    fig, ax = plt.subplots(figsize=(WIDTH * 0.75, height))
    image = ax.imshow(index_pd.to_numpy(), cmap=TONE_CMAP, vmin=-limit,
                      vmax=limit, aspect="auto")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES)
    ax.set_yticks(range(len(index_pd)))
    ax.set_yticklabels([f"{c} *" if c in significant else c
                        for c in index_pd.index], fontsize=8)
    ax.grid(False)
    fig.colorbar(image, ax=ax, shrink=0.6,
                 label="Seasonal index (tone points)")
    return fig


def plot_seasonal_curves(index_pd, band_low, band_high, q_values,
                         countries):
    """Figure 15: seasonal curves with permutation bands (3 x 3).

    Parameters
    ----------
    index_pd : pandas.DataFrame
        Seasonal index per country (rows), columns 1..12.
    band_low, band_high : pandas.DataFrame
        Permutation chance band, same shape as ``index_pd``.
    q_values : pandas.Series
        q-value per country.
    countries : list
        Index labels of the nine countries to show.

    Returns
    -------
    matplotlib.figure.Figure
    """
    shown = index_pd.loc[countries]
    limit = max(np.nanmax(np.abs(shown.to_numpy())),
                np.nanmax(np.abs(band_high.loc[countries].to_numpy())))
    fig, axes = plt.subplots(3, 3, figsize=(WIDTH, 7.5), sharex=True,
                             sharey=True)
    months = np.arange(1, 13)
    for ax, country in zip(axes.ravel(), countries):
        ax.fill_between(months, band_low.loc[country],
                        band_high.loc[country], color="#EBEBEB")
        ax.plot(months, index_pd.loc[country], color=ACCENT, marker="o",
                ms=3)
        ax.axhline(0, color=NEUTRAL, lw=0.8)
        ax.set_title(f"{country} (q = {q_values.loc[country]:.3f})",
                     fontsize=9)
        ax.set_ylim(-1.1 * limit, 1.1 * limit)
        ax.set_xticks(months)
        ax.set_xticklabels([m[0] for m in MONTH_NAMES], fontsize=8)
    fig.supylabel("Seasonal index (tone points)")
    fig.tight_layout()
    return fig


def plot_event_mix(mix_pd):
    """Figure 16: QuadClass shares for top and bottom countries.

    Parameters
    ----------
    mix_pd : pandas.DataFrame
        Rows = 'World' then countries (top to bottom), columns 1..4
        holding shares in percent.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(WIDTH, 0.3 * len(mix_pd) + 1.2))
    left = np.zeros(len(mix_pd))
    y = np.arange(len(mix_pd))
    for quad in (1, 2, 3, 4):
        ax.barh(y, mix_pd[quad], left=left, color=QUAD_COLORS[quad],
                label=QUAD_LABELS[quad])
        left += mix_pd[quad].to_numpy()
    ax.set_yticks(y)
    ax.set_yticklabels(mix_pd.index, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of the country's events (%)")
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.grid(axis="y", visible=False)
    return fig


def plot_decomposition(decomp_pd):
    """Figure 17: mix and within parts of each country's tone gap.

    Parameters
    ----------
    decomp_pd : pandas.DataFrame
        Rows = country names (ordered by gap), columns gap, mix and
        within.

    Returns
    -------
    matplotlib.figure.Figure
    """
    y = np.arange(len(decomp_pd))
    mix = decomp_pd["mix"].to_numpy()
    within = decomp_pd["within"].to_numpy()
    fig, ax = plt.subplots(figsize=(WIDTH, 0.28 * len(decomp_pd) + 1.4))
    ax.barh(y, mix, color="#9ECAE1", label="Event mix (what happens)")
    # stack within on the same side as mix, otherwise start at zero
    base = np.where(np.sign(within) == np.sign(mix), mix, 0)
    ax.barh(y, within, left=base, color="#FDAE6B",
            label="Within category (how it is reported)")
    ax.scatter(decomp_pd["gap"], y, color="black", s=16, zorder=3,
               label="Total gap")
    ax.axvline(0, color=NEUTRAL, lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(decomp_pd.index, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Difference from the reference mean tone (tone points)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3)
    ax.grid(axis="y", visible=False)
    return fig


def plot_sea_panel(sea_pd, global_mean, focus_name="Philippines"):
    """Figure 18: Southeast Asian countries with CIs, focus highlighted.

    The regional map of Figure 18(b) is drawn separately with
    ``plot_world_map`` on the same colour scale, zoomed with
    ``fig.update_geos(fitbounds='locations')``.

    Parameters
    ----------
    sea_pd : pandas.DataFrame
        Columns country_name, mean_tone, ci_low, ci_high.
    global_mean : float
        Global mean tone.
    focus_name : str
        Country drawn in the accent colour.

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = sea_pd.sort_values("mean_tone")
    y = np.arange(len(data))
    colors = [ACCENT if n == focus_name else POSITIVE
              for n in data["country_name"]]
    fig, ax = plt.subplots(figsize=(WIDTH * 0.75, 4.5))
    ax.errorbar(data["mean_tone"], y,
                xerr=[data["mean_tone"] - data["ci_low"],
                      data["ci_high"] - data["mean_tone"]],
                fmt="none", ecolor=NEUTRAL, capsize=2)
    ax.scatter(data["mean_tone"], y, c=colors, s=40, zorder=3)
    ax.axvline(global_mean, color="black", ls="--", lw=1,
               label="Global mean")
    ax.set_yticks(y)
    ax.set_yticklabels(data["country_name"])
    ax.set_xlabel("Mean AvgTone (95% month-bootstrap CI)")
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig


def plot_ph_timeline(rel_tone_pd, events):
    """Figure 19: Philippines vs other SEA relative tone over time.

    Parameters
    ----------
    rel_tone_pd : pandas.DataFrame
        Columns 'ph' and 'sea', indexed by 'YYYY-MM'.
    events : list of dict
        PH_EVENTS from gdelt_lookups (start, end, label).

    Returns
    -------
    matplotlib.figure.Figure
    """
    months = pd.to_datetime(rel_tone_pd.index)
    fig, ax = plt.subplots(figsize=(WIDTH, 4.5))
    for number, event in enumerate(events):
        start = pd.Timestamp(event["start"])
        end = pd.Timestamp(event["end"])
        if end > start:
            ax.axvspan(start, end, color="#F2F2F2", lw=0)
        else:
            ax.axvline(start, color=NEUTRAL, ls=":", lw=1)
        # alternate label heights so neighbouring labels never overlap
        ax.text(start, 1.02 + 0.06 * (number % 2), event["label"],
                fontsize=8, transform=ax.get_xaxis_transform(),
                color=NEUTRAL)
    for column, color, label in [("sea", NEUTRAL, "Other SEA"),
                                 ("ph", ACCENT, "Philippines")]:
        series = rel_tone_pd[column]
        ax.plot(months, series, color=color, lw=0.7, alpha=0.6)
        ax.plot(months, series.rolling(3, center=True).mean(),
                color=color, lw=2, label=f"{label} (3-month mean)")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("Tone minus global mean (Eq. 3)")
    ax.set_xlabel("Publication month")
    ax.legend(loc="lower left")
    return fig


def plot_ph_seasonal(ph_index, sea_index, ph_band_low, ph_band_high):
    """Figure 20: Philippine seasonal index against SEA average.

    Parameters
    ----------
    ph_index, sea_index : pandas.Series
        Twelve monthly index values (index 1..12).
    ph_band_low, ph_band_high : pandas.Series
        Permutation chance band for the Philippines.

    Returns
    -------
    matplotlib.figure.Figure
    """
    months = np.arange(1, 13)
    fig, ax = plt.subplots(figsize=(WIDTH * 0.75, 4))
    ax.axvspan(5.5, 11.5, color="#F7F7F7", lw=0)  # June to November
    ax.fill_between(months, ph_band_low, ph_band_high, color="#E6E6E6",
                    label="Chance range (Philippines)")
    ax.plot(months, sea_index, color=NEUTRAL, marker="o", ms=3,
            label="Other SEA (average)")
    ax.plot(months, ph_index, color=ACCENT, marker="o", ms=4, lw=2,
            label="Philippines")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_NAMES)
    ax.set_ylabel("Seasonal index (tone points)")
    ax.legend(loc="lower left", fontsize=8)
    return fig


def plot_ph_drivers(ph_decomp_pd):
    """Figure 21: CAMEO contributions to the PH-vs-SEA tone gap.

    Parameters
    ----------
    ph_decomp_pd : pandas.DataFrame
        Columns event_root_code, root_name, mix_k and within_k for the
        Philippines.

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = ph_decomp_pd.assign(
        total=ph_decomp_pd["mix_k"] + ph_decomp_pd["within_k"])
    data = data.sort_values("total")
    labels = data["event_root_code"] + " " + data["root_name"]
    y = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(WIDTH, 6))
    ax.barh(y - 0.2, data["mix_k"], 0.4, color="#9ECAE1",
            label="Event mix")
    ax.barh(y + 0.2, data["within_k"], 0.4, color="#FDAE6B",
            label="Within category")
    ax.axvline(0, color=NEUTRAL, lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlabel("Contribution to the gap vs other SEA (tone points)")
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig
