from datetime import datetime, timezone

import pandas as pd

from oil_news.impact import build_impact_table, measure_event
from oil_news.news import pick_prominent, score_headline


def _prices():
    index = pd.date_range("2026-01-05 00:00", periods=6, freq="h", tz="UTC")
    return pd.Series([100, 100, 110, 120, 120, 90], index=index)


def test_measure_event_uses_price_before_and_after():
    news = datetime(2026, 1, 5, 1, 30, tzinfo=timezone.utc)  # between bars
    moves = measure_event(_prices(), news, {"+1h": 1, "+2h": 2})
    # baseline = 01:00 bar (100); +1h -> 02:30 -> next bar 03:00 (120)
    assert moves == {"+1h": 20.0, "+2h": 20.0}


def test_measure_event_missing_future_is_none():
    news = datetime(2026, 1, 5, 4, tzinfo=timezone.utc)
    assert measure_event(_prices(), news, {"+5h": 5}) == {"+5h": None}


def test_build_table_one_row_per_ticker():
    events = [{"title": "OPEC cut", "published": datetime(2026, 1, 5, 1, tzinfo=timezone.utc)}]
    table = build_impact_table(events, {"CL=F": _prices(), "SPY": _prices()}, {"+1h": 1})
    assert len(table) == 2 and table["+1h"].tolist() == [10.0, 10.0]


def test_scoring_and_dedup():
    assert score_headline("OPEC+ agrees production cut") >= 3
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    items = [
        {"title": "OPEC cuts output - Reuters", "published": t},
        {"title": "OPEC cuts output - Bloomberg", "published": t},
        {"title": "Gas station opens downtown", "published": t},
    ]
    assert [i["title"] for i in pick_prominent(items, min_score=3)] == ["OPEC cuts output - Reuters"]


def test_average_uses_size_of_move():
    from oil_news.impact import average_impact
    table = pd.DataFrame({"market": ["WTI Crude", "WTI Crude"], "+1h": [3.0, -1.0]})
    assert average_impact(table, {"+1h": 1}).loc["WTI Crude", "+1h"] == 2.0
