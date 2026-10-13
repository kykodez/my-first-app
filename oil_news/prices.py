"""Download hourly prices from Yahoo Finance."""

import pandas as pd
import yfinance as yf

from . import config


def fetch_prices(tickers=None, period=None, interval=None) -> dict[str, pd.Series]:
    """Return {ticker: Series of close prices indexed by UTC time}."""
    tickers = tickers or list(config.TICKERS)
    prices = {}
    for ticker in tickers:
        df = yf.Ticker(ticker).history(
            period=period or config.PRICE_PERIOD,
            interval=interval or config.PRICE_INTERVAL,
        )
        if df.empty:
            continue
        close = df["Close"].dropna()
        close.index = close.index.tz_convert("UTC")
        prices[ticker] = close
    return prices
