# my-first-app — Oil News Impact Tracker

Learning to code with Claude. This app finds **prominent news about oil prices**
and measures **how markets moved 1 hour, 4 hours, 1 day, 3 days and 5 days later**.

## What it does

1. **Finds news.** Searches Google News (free, no API key) for oil-related headlines.
2. **Picks the prominent ones.** Each headline gets points for keywords like
   *OPEC*, *sanctions*, *Hormuz*, *production cut* (see `oil_news/config.py`).
   Low-scoring headlines are dropped, and duplicates are merged.
3. **Gets prices.** Downloads hourly prices from Yahoo Finance for WTI crude,
   Brent crude, energy stocks (XLE) and the S&P 500 (SPY).
4. **Measures the impact.** For each headline: price when the news broke vs.
   the price 1h / 4h / 1d / 3d / 5d later, as a % change.
5. **Shows it** in a dashboard: the average size of the move, a chart around
   any single headline, and a full table you can download as CSV.

Headlines are saved to `oil_news.db` (a small local database file), so history
builds up each time you run the app.

## Run it

You need Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py             # real news and prices
streamlit run app.py -- --demo   # made-up data, works offline
```

Your browser opens at http://localhost:8501. The sidebar has a demo-data switch
and a slider for how "important" a headline must be.

Run the tests with `pytest`.

## Project layout

| File | What it does |
|---|---|
| `app.py` | The dashboard (Streamlit) |
| `oil_news/config.py` | **Start here.** Tickers, time windows, keywords, search terms |
| `oil_news/news.py` | Fetches and scores headlines |
| `oil_news/prices.py` | Fetches hourly prices |
| `oil_news/impact.py` | The % move calculation |
| `oil_news/storage.py` | Saves headlines to SQLite |
| `oil_news/demo.py` | Fake data for offline use |

## Things to know

- **Correlation, not causation.** Markets move for many reasons at once. One
  headline proves little; patterns across many headlines say more.
- **Market hours.** If the news drops while a market is closed (nights,
  weekends), the "+1h" price is the first trade after it reopens.
- **Data limits.** Google News only returns recent headlines, and Yahoo only
  gives about 2 years of hourly data. Recent news shows "not yet" for windows
  that haven't happened yet.

## Ideas for next steps

- Separate bullish from bearish news (e.g. "cut" vs "hike") and compare.
- Compare oil's move to its normal hourly volatility, to see whether a move was unusual.
- Run it automatically every hour so the history builds up.
