"""All the knobs in one place. Edit these to change what the app tracks."""

# Markets to measure. Yahoo Finance ticker -> friendly name.
TICKERS = {
    "CL=F": "WTI Crude",
    "BZ=F": "Brent Crude",
    "XLE": "Energy Stocks (XLE)",
    "SPY": "S&P 500 (SPY)",
}

# How long after the news we check the price. Label -> hours.
WINDOWS = {
    "+1h": 1,
    "+4h": 4,
    "+1d": 24,
    "+3d": 72,
    "+5d": 120,
}

# Google News searches used to find oil news.
SEARCH_QUERIES = [
    "oil prices",
    "OPEC",
    "crude oil supply",
    "oil sanctions",
]

# Words that make a headline "prominent", with a weight for each.
# A headline's score is the sum of the weights of the words it contains.
KEYWORDS = {
    "opec": 3,
    "opec+": 3,
    "production cut": 3,
    "output cut": 3,
    "output hike": 3,
    "saudi": 2,
    "russia": 2,
    "iran": 2,
    "sanction": 2,
    "hormuz": 3,
    "pipeline": 1,
    "refinery": 1,
    "inventor": 2,  # inventory / inventories
    "eia": 2,
    "strategic petroleum reserve": 3,
    "spr": 2,
    "embargo": 3,
    "attack": 2,
    "hurricane": 2,
    "fed": 1,
    "tariff": 2,
    "surge": 1,
    "plunge": 1,
    "slump": 1,
    "soar": 1,
}

# Headlines need at least this score to count as "prominent".
MIN_SCORE = 3

# How much hourly price history to download.
PRICE_PERIOD = "3mo"
PRICE_INTERVAL = "1h"

DB_PATH = "oil_news.db"
