"""Read the GDELT 1.0 daily event files with Apache Spark.

This module holds the column layout of the 58-column GDELT 1.0 daily
format (1 April 2013 onwards) and the functions that turn the zipped
raw files into a typed Spark DataFrame and a Parquet cache.

Used by the main notebook in Steps 4 to 7 (raw file inventory, parser
validation, full ingestion and acceptance checks).
"""

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
    # 1. glob.glob(os.path.join(raw_dir, pattern)) and sort the result.
    # 2. Return the list (expected length: 2,335).
    raise NotImplementedError("Step 4")


def parse_zip(path):
    """Yield one parsed row per line of one zipped daily file.

    Runs inside a Spark task (called through ``flatMap``), so it must
    only use the standard library.

    Parameters
    ----------
    path : str
        Path of one ``YYYYMMDD.export.CSV.zip`` file.

    Yields
    ------
    tuple
        The 19 kept fields as strings (None when the line is too short),
        then ``n_fields`` (int), ``empty_mask`` (int) and ``file_date``
        (int, YYYYMMDD from the file name).
    """
    # 1. file_date = int of the first 8 characters of the file name.
    # 2. Open the zip with zipfile.ZipFile; it holds exactly one member.
    # 3. Iterate over the member line by line (do not read it all into
    #    a list); decode UTF-8 with errors='replace'; strip only the
    #    trailing newline.
    # 4. fields = line.split('\t'); n_fields = len(fields).
    # 5. empty_mask = sum of (1 << i) for every i with fields[i] == '',
    #    only when n_fields == N_FIELDS; otherwise -1.
    # 6. Yield the KEEP_COLUMNS fields in index order (None if missing),
    #    then n_fields, empty_mask, file_date.
    raise NotImplementedError("Step 5")


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
        One row per event with typed and derived columns (see below).
        Nothing is read until an action runs.
    """
    # 1. rdd = spark.sparkContext.parallelize(paths, len(paths))
    #        .flatMap(parse_zip)          # one task per file
    # 2. Explicit StructType: the 19 kept fields as StringType, then
    #    n_fields (Integer), empty_mask (Long), file_date (Integer).
    # 3. df = spark.createDataFrame(rdd, schema).
    # 4. Cast in Spark: event_id long; sql_date, is_root, quad_class,
    #    num_mentions, num_sources, num_articles, geo_type, date_added
    #    int; goldstein, avg_tone, lat, lon double; event codes, adm1,
    #    geo_fullname stay strings (leading zeros); country_fips: ''
    #    -> null.
    # 5. Derived: date_added_dt, sql_date_dt (to_date 'yyyyMMdd'),
    #    year_added, month_added, ym_added ('yyyy-MM'),
    #    lag_days = datediff(date_added_dt, sql_date_dt).
    # 6. Return df.
    raise NotImplementedError("Steps 5 and 6")


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
    # 1. df.write.mode('overwrite').partitionBy(partition_col)
    #      .parquet(path)   # the single action that reads the raw files
    raise NotImplementedError("Steps 6 and 16")
