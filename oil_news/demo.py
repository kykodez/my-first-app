"""Made-up data so the app works without internet. Run with: --demo"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from . import config
from .news import score_headline

DEMO_HEADLINES = [
    (40, "OPEC+ agrees surprise production cut of 1 million barrels per day", +4.0),
    (32, "Oil prices plunge as EIA reports record crude inventory build", -3.0),
    (25, "US announces new sanctions on Iranian oil exports", +2.5),
    (18, "Tanker attack near Strait of Hormuz rattles oil markets", +3.5),
    (11, "Saudi Arabia signals output hike as demand outlook weakens", -2.5),
    (5, "Hurricane forces Gulf of Mexico refinery shutdowns", +1.5),
]


def demo_data(seed: int = 7):
    """Return (events, prices) shaped exactly like the real fetchers."""
    rng = np.random.default_rng(seed)
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    index = pd.date_range(end=now, periods=24 * 45, freq="h", tz="UTC")

    events = [
        {"title": title, "link": f"https://example.com/demo/{i}", "source": "Demo",
         "published": now - timedelta(days=days), "score": score_headline(title)}
        for i, (days, title, _) in enumerate(DEMO_HEADLINES)
    ]

    # Each market reacts to the news with a different strength.
    sensitivity = {"CL=F": 1.0, "BZ=F": 0.9, "XLE": 0.5, "SPY": -0.1}
    start_price = {"CL=F": 75, "BZ=F": 79, "XLE": 90, "SPY": 560}
    prices = {}
    for ticker in config.TICKERS:
        returns = rng.normal(0, 0.0015, len(index))
        for (days, _, shock), event in zip(DEMO_HEADLINES, events):
            pos = index.searchsorted(event["published"])
            # Spread the reaction over the next ~12 hours.
            returns[pos:pos + 12] += shock * sensitivity[ticker] / 100 / 12
        prices[ticker] = pd.Series(start_price[ticker] * np.exp(np.cumsum(returns)), index=index)
    return events, prices
