"""Read the GDELT 1.0 daily event files with Apache Spark.

This module holds the column layout of the 58-column GDELT 1.0 daily
format (1 April 2013 onwards) and the functions that turn the zipped
raw files into a typed Spark DataFrame and a Parquet cache.

Used by the main notebook in Steps 4 to 7 (raw file inventory, parser
validation, full ingestion and acceptance checks).
"""

import datetime
import glob
import os
import zipfile

RAW_DIR = "/mnt/data/public/gdeltv1/events"
RAW_PATTERN = "*.export.CSV.zip"

# All 58 fields of the GDELT 1.0 daily format, in file order
# (GDELT data format codebook V1.03).
COLUMN_NAMES = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode",
    "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code",
    "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode",
    "Actor2KnownGroupCode", "Actor2EthnicCode", "Actor2Religion1Code",
    "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
    "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
    "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_Lat", "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_Lat", "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]
N_FIELDS = len(COLUMN_NAMES)  # 58

# Raw field index -> output column name, for the 19 fields of Table 1.
KEEP_COLUMNS = {
    0: "event_id",
    1: "sql_date",
    25: "is_root",
    26: "event_code",
    27: "event_base_code",
    28: "event_root_code",
    29: "quad_class",
    30: "goldstein",
    31: "num_mentions",
    32: "num_sources",
    33: "num_articles",
    34: "avg_tone",
    49: "geo_type",
    50: "geo_fullname",
    51: "country_fips",
    52: "adm1",
    53: "lat",
    54: "lon",
    56: "date_added",
}


# Python type of each kept field, used when parsing a line.
_INT_FIELDS = {"event_id", "sql_date", "is_root", "quad_class",
               "num_mentions", "num_sources", "num_articles", "geo_type",
               "date_added"}
_FLOAT_FIELDS = {"goldstein", "avg_tone", "lat", "lon"}
_KEEP_ITEMS = sorted(KEEP_COLUMNS.items())


def list_raw_files(raw_dir=RAW_DIR, pattern=RAW_PATTERN):
    """List the daily raw files of the study, sorted by date.

    Parameters
    ----------
    raw_dir : str
        Folder holding the GDELT 1.0 event files.
    pattern : str
        Glob pattern of the daily files.

    Returns
    -------
    list of str
        Full paths of the matching files, sorted by file name (= date).
    """
    return sorted(glob.glob(os.path.join(raw_dir, pattern)))


def _to_int(text):
    """Convert text to int, or None when empty or not a number."""
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def _to_float(text):
    """Convert text to float, or None when empty or not a number."""
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _to_date(value):
    """Convert a YYYYMMDD integer to a date, or None if invalid."""
    if value is None:
        return None
    try:
        return datetime.date(value // 10000, value // 100 % 100,
                             value % 100)
    except ValueError:  # e.g. day 00 in partial dates
        return None


def parse_line(line, file_date):
    """Parse one raw tab-separated line into a typed tuple.

    Parameters
    ----------
    line : str
        One line of a daily file, without the line break.
    file_date : int
        Date in the file name (YYYYMMDD).

    Returns
    -------
    tuple
        The 19 kept fields (typed; None when empty or invalid), then
        n_fields, empty_mask, file_date, date_added_dt and sql_date_dt.
        Rows that do not have 58 fields keep only their audit fields.
    """
    fields = line.split("\t")
    n_fields = len(fields)
    if n_fields != N_FIELDS:
        # malformed line: kept only to be counted and removed in Step 16
        return ((None,) * len(_KEEP_ITEMS)
                + (n_fields, -1, file_date, None, None))
    # bit i of empty_mask is 1 when raw field i is empty (Step 11)
    empty_mask = 0
    for i, value in enumerate(fields):
        if value == "":
            empty_mask |= 1 << i
    values = []
    for index, name in _KEEP_ITEMS:
        text = fields[index]
        if name in _INT_FIELDS:
            values.append(_to_int(text))
        elif name in _FLOAT_FIELDS:
            values.append(_to_float(text))
        else:
            # codes stay text to keep leading zeros ('04', '043')
            values.append(text if text != "" else None)
    named = dict(zip(KEEP_COLUMNS.values(), values))
    return (tuple(values)
            + (n_fields, empty_mask, file_date,
               _to_date(named["date_added"]),
               _to_date(named["sql_date"])))


def parse_zip(path):
    """Yield one parsed row per line of one zipped daily file.

    Runs inside a Spark task (called through ``flatMap``), so it only
    uses the standard library.

    Parameters
    ----------
    path : str
        Path of one ``YYYYMMDD.export.CSV.zip`` file.

    Yields
    ------
    tuple
        One row as returned by ``parse_line``.
    """
    file_date = int(os.path.basename(path)[:8])
    with zipfile.ZipFile(path) as archive:
        member = archive.namelist()[0]  # each zip holds one file
        with archive.open(member) as handle:
            for raw in handle:  # streamed, never read whole
                line = raw.decode("utf-8", errors="replace")
                yield parse_line(line.rstrip("\r\n"), file_date)


def events_schema():
    """Return the Spark schema of the rows produced by ``parse_zip``.

    Returns
    -------
    pyspark.sql.types.StructType
        Kept fields, audit fields and the two parsed dates.
    """
    from pyspark.sql import types as T

    fields = []
    for _, name in _KEEP_ITEMS:
        if name == "event_id":
            spark_type = T.LongType()
        elif name in _INT_FIELDS:
            spark_type = T.IntegerType()
        elif name in _FLOAT_FIELDS:
            spark_type = T.DoubleType()
        else:
            spark_type = T.StringType()
        fields.append(T.StructField(name, spark_type, True))
    fields += [
        T.StructField("n_fields", T.IntegerType(), False),
        T.StructField("empty_mask", T.LongType(), False),
        T.StructField("file_date", T.IntegerType(), False),
        T.StructField("date_added_dt", T.DateType(), True),
        T.StructField("sql_date_dt", T.DateType(), True),
    ]
    return T.StructType(fields)


def build_events_df(spark, paths):
    """Build the typed, lazy Spark DataFrame of events for given files.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Spark session.
    paths : list of str
        Raw files to read (one Spark task per file).

    Returns
    -------
    pyspark.sql.DataFrame
        One row per raw line: the kept fields, audit fields, the parsed
        dates and the derived columns year_added, month_added,
        ym_added ('yyyy-MM') and lag_days. Nothing is read until an
        action runs (lazy evaluation).
    """
    from pyspark.sql import functions as F

    # one partition per file -> one task per file (narrow flatMap)
    rows_rdd = (spark.sparkContext
                .parallelize(paths, max(len(paths), 1))
                .flatMap(parse_zip))
    events_df = spark.createDataFrame(rows_rdd, events_schema())
    return (events_df
            .withColumn("year_added", F.year("date_added_dt"))
            .withColumn("month_added", F.month("date_added_dt"))
            .withColumn("ym_added",
                        F.date_format("date_added_dt", "yyyy-MM"))
            .withColumn("lag_days",
                        F.datediff("date_added_dt", "sql_date_dt")))


def write_parquet(df, path, partition_col="year_added"):
    """Write a DataFrame to Parquet, partitioned by one column.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Table to write.
    path : str
        Relative output folder (inside ./scratch).
    partition_col : str
        Column used to partition the files on disk.

    Returns
    -------
    None
    """
    # the write is the action that triggers all upstream reading
    df.write.mode("overwrite").partitionBy(partition_col).parquet(path)
