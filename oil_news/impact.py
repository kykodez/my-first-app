"""The core idea: compare the price when news broke to the price N hours later."""

from datetime import datetime, timedelta

import pandas as pd

from . import config


def price_at_or_before(prices: pd.Series, when: datetime):
    """Last known price at or before `when` (the 'baseline' price)."""
    before = prices[prices.index <= when]
    return None if before.empty else before.iloc[-1]


def price_at_or_after(prices: pd.Series, when: datetime):
    """First known price at or after `when`.

    Markets close overnight and on weekends, so "+1h" might land in a gap;
    we use the next price that actually traded.
    """
    after = prices[prices.index >= when]
    return None if after.empty else after.iloc[0]


def measure_event(prices: pd.Series, news_time: datetime, windows=None) -> dict:
    """% change from the news time to each window. None if not enough data yet."""
    windows = windows or config.WINDOWS
    base = price_at_or_before(prices, news_time)
    result = {}
    for label, hours in windows.items():
        later = price_at_or_after(prices, news_time + timedelta(hours=hours))
        if base is None or later is None:
            result[label] = None
        else:
            result[label] = round((later - base) / base * 100, 2)
    return result


def build_impact_table(events: list[dict], prices: dict[str, pd.Series], windows=None) -> pd.DataFrame:
    """One row per (headline, ticker) with % moves for every window."""
    rows = []
    for event in events:
        for ticker, series in prices.items():
            moves = measure_event(series, event["published"], windows)
            rows.append({
                "published": event["published"],
                "title": event["title"],
                "score": event.get("score"),
                "ticker": ticker,
                "market": config.TICKERS.get(ticker, ticker),
                **moves,
            })
    return pd.DataFrame(rows)


def average_impact(table: pd.DataFrame, windows=None) -> pd.DataFrame:
    """Average SIZE of the % move per market (ignores missing data).

    We use absolute values: good news (+3%) and bad news (-3%) would
    otherwise cancel out and look like "no effect".
    """
    windows = windows or config.WINDOWS
    if table.empty:
        return pd.DataFrame()
    avg = table.groupby("market")[list(windows)].agg(lambda col: col.abs().mean()).round(2)
    order = [m for m in config.TICKERS.values() if m in avg.index]
    return avg.reindex(order + [m for m in avg.index if m not in order])
