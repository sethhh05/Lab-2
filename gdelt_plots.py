"""Figure functions for the GDELT tone report.

One function per figure (Figures 1 to 21 of the main notebook), all
sharing the style set by ``set_style``. Every function returns the
figure and is saved with ``save_fig``. Captions live in the notebook,
so figures carry no titles.

Used by the main notebook in every step that draws a figure.
"""

FIG_DIR = "./figures"
DPI = 150


def set_style():
    """Apply one font, palette and figure size to every figure.

    Returns
    -------
    None
    """
    # 1. plt.rcParams: one sans-serif font, font sizes, figure width,
    #    dpi=DPI, no top/right spines, light grid.
    # 2. Define the palette constants used below (QuadClass colours,
    #    diverging map scale, Philippines accent colour).
    raise NotImplementedError("Step 1")


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
    # 1. fig.savefig(os.path.join(fig_dir, name + '.png'), dpi=DPI,
    #    bbox_inches='tight'); return the path.
    raise NotImplementedError("All figures")


def plot_pipeline_diagram():
    """Figure 1: pipeline of the study (boxes and arrows, matplotlib).

    Returns
    -------
    matplotlib.figure.Figure
    """
    # Instructions: Step 0 code cell of the main notebook.
    raise NotImplementedError("Figure 1")


def plot_daily_volume(daily_pd, missing_days):
    """Figure 2: events per day with a 30-day mean and missing days.

    Parameters
    ----------
    daily_pd : pandas.DataFrame
        Daily counts on the full date range (NaN on missing days).
    missing_days : list of pandas.Timestamp
        Days with no raw file.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 2, Step 8")


def plot_tone_hist(hist_pd, mean_tone, median_tone, share_outside):
    """Figure 3: histogram of AvgTone with mean and median lines.

    Parameters
    ----------
    hist_pd : pandas.DataFrame
        Bin start and count, computed in Spark.
    mean_tone, median_tone : float
        Global mean and median tone.
    share_outside : float
        Percent of events outside -20..+20.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 3, Step 9")


def plot_tone_by_root(root_pd, global_mean):
    """Figure 4: mean tone per CAMEO root, coloured by QuadClass.

    Parameters
    ----------
    root_pd : pandas.DataFrame
        Root code, name, QuadClass, events and mean tone.
    global_mean : float
        Global mean tone (vertical line).

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 4, Step 10")


def plot_unlocated(share_month_pd, tone_quad_pd):
    """Figure 5: (a) unlocated share per month, (b) tone by QuadClass.

    Parameters
    ----------
    share_month_pd : pandas.DataFrame
        Percent of events with no location per publication month.
    tone_quad_pd : pandas.DataFrame
        Mean tone of located and unlocated events per QuadClass.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 5, Step 12")


def plot_lag(lag_pd):
    """Figure 6: share of events per lag bucket, mean tone annotated.

    Parameters
    ----------
    lag_pd : pandas.DataFrame
        Lag bucket, percent of events and mean tone.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 6, Step 13")


def plot_funnel(funnel_pd):
    """Figure 7: rows remaining after each filtering step.

    Parameters
    ----------
    funnel_pd : pandas.DataFrame
        Step, rows remaining and percent of all parsed rows.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 7, Step 16")


def plot_threshold(country_n_pd, thresholds, chosen):
    """Figure 8: 95% half-width against events per country (log-log).

    Parameters
    ----------
    country_n_pd : pandas.DataFrame
        Events and 95% half-width per country.
    thresholds : list of int
        Candidate thresholds (dashed lines).
    chosen : int
        Chosen threshold (solid line).

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 8, Step 17")


def plot_ranking(ranked_pd, global_mean, top_n):
    """Figure 9: most positive and most negative countries with CIs.

    Parameters
    ----------
    ranked_pd : pandas.DataFrame
        Eligible countries with mean tone and ci_low, ci_high.
    global_mean : float
        Global mean tone (dashed line).
    top_n : int
        Countries shown at each end.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 9, Step 19")


def plot_world_map(map_pd, global_mean):
    """Figure 10: plotly choropleth of mean tone by country.

    Parameters
    ----------
    map_pd : pandas.DataFrame
        ISO3, name, events, mean tone, CI, eligible flag.
    global_mean : float
        Midpoint of the diverging colour scale.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    raise NotImplementedError("Figure 10, Step 20")


def plot_robustness(summary_pd):
    """Figure 11: event-weighted versus article-weighted mean tone.

    Parameters
    ----------
    summary_pd : pandas.DataFrame
        Eligible countries with both means.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 11, Step 21")


def plot_global_monthly(global_month_pd):
    """Figure 12: global monthly tone with trend, and volume per day.

    Parameters
    ----------
    global_month_pd : pandas.DataFrame
        Monthly global tone, trend and events per available day.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 12, Step 22")


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
    raise NotImplementedError("Figure 13, Step 23")


def plot_seasonal_heatmap(index_pd, significant):
    """Figure 14: seasonal index heatmap, countries x calendar months.

    Parameters
    ----------
    index_pd : pandas.DataFrame
        Rows = countries (ordered), columns = Jan..Dec.
    significant : set of str
        Countries with q < 0.05 (marked with an asterisk).

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 14, Step 25")


def plot_seasonal_curves(index_pd, null_bands, q_values, countries):
    """Figure 15: seasonal curves with permutation bands (3 x 3).

    Parameters
    ----------
    index_pd : pandas.DataFrame
        Seasonal index per country.
    null_bands : dict
        Country -> (low, high) arrays of 12 values.
    q_values : pandas.Series
        q-value per country.
    countries : list of str
        The nine countries to show.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 15, Step 25")


def plot_event_mix(mix_pd):
    """Figure 16: QuadClass shares for top and bottom countries.

    Parameters
    ----------
    mix_pd : pandas.DataFrame
        Countries (plus 'World') x four QuadClass shares.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 16, Step 26")


def plot_decomposition(decomp_pd):
    """Figure 17: mix and within parts of each country's tone gap.

    Parameters
    ----------
    decomp_pd : pandas.DataFrame
        Country, gap, mix and within.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 17, Step 27")


def plot_sea_panel(sea_pd, global_mean):
    """Figure 18: SEA dot plot with CIs and regional map.

    Parameters
    ----------
    sea_pd : pandas.DataFrame
        The 11 SEA countries with mean tone, CI and ISO3.
    global_mean : float
        Global mean tone.

    Returns
    -------
    matplotlib.figure.Figure or plotly.graph_objects.Figure
    """
    raise NotImplementedError("Figure 18, Step 28")


def plot_ph_timeline(rel_tone_pd, events):
    """Figure 19: Philippines vs other SEA relative tone over time.

    Parameters
    ----------
    rel_tone_pd : pandas.DataFrame
        Monthly relative tone for 'ph' and 'sea'.
    events : list of dict
        PH_EVENTS from gdelt_lookups.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 19, Step 29")


def plot_ph_seasonal(ph_index, sea_index, ph_band):
    """Figure 20: Philippine seasonal index against SEA average.

    Parameters
    ----------
    ph_index, sea_index : pandas.Series
        Twelve monthly index values.
    ph_band : tuple of numpy.ndarray
        Permutation band (low, high) for the Philippines.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 20, Step 30")


def plot_ph_drivers(ph_decomp_pd):
    """Figure 21: CAMEO contributions to the PH-vs-SEA tone gap.

    Parameters
    ----------
    ph_decomp_pd : pandas.DataFrame
        Root, name, mix_k and within_k for the Philippines.

    Returns
    -------
    matplotlib.figure.Figure
    """
    raise NotImplementedError("Figure 21, Step 30")
