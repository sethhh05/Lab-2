"""Lookup tables for the GDELT 1.0 event codes used in the report.

Transcribed from the CAMEO codebook (Schrodt, 2012) and the GDELT data
format codebook V1.03 (GDELT Project, 2013). See Table 2 of the main
notebook for how each table was checked.

Used by the main notebook in Steps 10, 16 and 19 to 30.
"""

# CAMEO root categories (codes kept as two-character strings).
CAMEO_ROOT_NAMES = {
    "01": "Make public statement",
    "02": "Appeal",
    "03": "Express intent to cooperate",
    "04": "Consult",
    "05": "Engage in diplomatic cooperation",
    "06": "Engage in material cooperation",
    "07": "Provide aid",
    "08": "Yield",
    "09": "Investigate",
    "10": "Demand",
    "11": "Disapprove",
    "12": "Reject",
    "13": "Threaten",
    "14": "Protest",
    "15": "Exhibit force posture",
    "16": "Reduce relations",
    "17": "Coerce",
    "18": "Assault",
    "19": "Fight",
    "20": "Use unconventional mass violence",
}

QUAD_CLASS_NAMES = {
    1: "Verbal cooperation",
    2: "Material cooperation",
    3: "Verbal conflict",
    4: "Material conflict",
}

# Precision of the event location (ActionGeo_Type).
GEO_TYPE_NAMES = {
    0: "No location",
    1: "Country",
    2: "US state",
    3: "US city",
    4: "World city",
    5: "World state (first-level region)",
}

# FIPS 10-4 country code -> (ISO 3166-1 alpha-3, English name).
# GDELT uses FIPS, NOT ISO: AS = Australia, AU = Austria, RP = Philippines.
# The entries below are a verified starting set. COMPLETE THE TABLE from
# the FIPS 10-4 list referenced by the GDELT codebook so that it covers
# every code found in the data; Step 16 lists any code still unmapped
# (Table 22).
FIPS_TO_ISO3 = {
    "AS": ("AUS", "Australia"),
    "AU": ("AUT", "Austria"),
    "BM": ("MMR", "Myanmar"),
    "BX": ("BRN", "Brunei"),
    "CB": ("KHM", "Cambodia"),
    "CH": ("CHN", "China"),
    "GM": ("DEU", "Germany"),
    "ID": ("IDN", "Indonesia"),
    "IZ": ("IRQ", "Iraq"),
    "JA": ("JPN", "Japan"),
    "KS": ("KOR", "South Korea"),
    "LA": ("LAO", "Laos"),
    "MY": ("MYS", "Malaysia"),
    "NG": ("NER", "Niger"),
    "NI": ("NGA", "Nigeria"),
    "RP": ("PHL", "Philippines"),
    "RS": ("RUS", "Russia"),
    "SN": ("SGP", "Singapore"),
    "SP": ("ESP", "Spain"),
    "SW": ("SWE", "Sweden"),
    "SZ": ("CHE", "Switzerland"),
    "TH": ("THA", "Thailand"),
    "TT": ("TLS", "Timor-Leste"),
    "UK": ("GBR", "United Kingdom"),
    "US": ("USA", "United States"),
    "VM": ("VNM", "Vietnam"),
}

# The ten ASEAN member states plus Timor-Leste (FIPS codes).
SEA_FIPS = ["RP", "ID", "VM", "TH", "MY", "SN", "BM", "CB", "LA", "BX",
            "TT"]

# Dated national events marked in Figure 19, with their sources
# (full entries in the References section of the main notebook).
PH_EVENTS = [
    {"start": "2013-11-08", "end": "2013-11-08",
     "label": "Typhoon Haiyan (Yolanda) landfall",
     "source": "NDRRMC (2014)"},
    {"start": "2016-06-30", "end": "2016-06-30",
     "label": "Presidential inauguration",
     "source": "Dizon (2016)"},
    {"start": "2017-05-23", "end": "2017-10-23",
     "label": "Siege of Marawi",
     "source": "Placido (2017)"},
]
