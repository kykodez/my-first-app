"""Oil News Impact Tracker - run with:  streamlit run app.py

Add "-- --demo" to use made-up data (no internet needed):
    streamlit run app.py -- --demo
"""

import sys
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from oil_news import config, storage
from oil_news.impact import average_impact, build_impact_table

# One fixed color per market so a market keeps its color on every chart.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MARKET_COLORS = {name: COLORS[i] for i, name in enumerate(config.TICKERS.values())}

st.set_page_config(page_title="Oil News Impact", page_icon="🛢️", layout="wide")
st.title("🛢️ Oil News Impact Tracker")
st.caption("Prominent oil-price headlines, and how markets moved in the hours and days after.")


@st.cache_data(ttl=60 * 30, show_spinner="Fetching news and prices…")
def load_live(min_score: int):
    from oil_news.news import fetch_headlines, pick_prominent
    from oil_news.prices import fetch_prices

    fresh = pick_prominent(fetch_headlines(), min_score=0)
    storage.save_events(fresh)  # keep history so older news isn't lost
    events = [e for e in storage.load_events() if (e["score"] or 0) >= min_score]
    return events, fetch_prices()


@st.cache_data
def load_demo(min_score: int):
    from oil_news.demo import demo_data

    events, prices = demo_data()
    return [e for e in events if e["score"] >= min_score], prices


# ---- Sidebar controls ----
with st.sidebar:
    demo = st.toggle("Use demo data", value="--demo" in sys.argv,
                     help="Made-up headlines and prices; works offline.")
    min_score = st.slider("Minimum headline importance", 1, 10, config.MIN_SCORE,
                          help="Headlines score points for keywords like OPEC, sanctions, Hormuz…")
    if st.button("Refresh now"):
        st.cache_data.clear()

try:
    events, prices = load_demo(min_score) if demo else load_live(min_score)
except Exception as err:  # network down, Yahoo blocked, etc.
    st.error(f"Couldn't load live data ({err}). Try the **Use demo data** switch in the sidebar.")
    st.stop()

if not events or not prices:
    st.warning("No prominent headlines or prices found. Try lowering the importance slider.")
    st.stop()

table = build_impact_table(events, prices)
windows = list(config.WINDOWS)

# ---- Average reaction ----
st.subheader("How much markets moved after prominent news")
avg = average_impact(table)
fig = go.Figure()
for market in avg.index:
    fig.add_bar(name=market, x=windows, y=avg.loc[market, windows],
                marker_color=MARKET_COLORS.get(market),
                hovertemplate="%{x}: ±%{y:.2f}%<extra>" + market + "</extra>")
fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08, height=360,
                  yaxis_title="average size of move", yaxis_ticksuffix="%",
                  legend_orientation="h", margin=dict(t=10, b=10))
st.plotly_chart(fig, width="stretch")
st.caption(f"Average absolute % move across {len(events)} headline(s), up or down. Note: moves aren't purely caused by the news — "
           "other things happen at the same time, so look for patterns across many events.")

# ---- One headline in detail ----
st.subheader("Look at one headline")
labels = [f"{e['published']:%Y-%m-%d %H:%M} UTC — {e['title']}" for e in events]
choice = st.selectbox("Headline", range(len(events)), format_func=lambda i: labels[i])
event = events[choice]
st.markdown(f"[Open article]({event['link']}) · source: {event.get('source') or 'n/a'} · "
            f"importance score: {event['score']}")

start = event["published"] - timedelta(hours=24)
end = event["published"] + timedelta(hours=max(config.WINDOWS.values()))
line = go.Figure()
for ticker, series in prices.items():
    window = series[(series.index >= start) & (series.index <= end)]
    base = series[series.index <= event["published"]]
    if window.empty or base.empty:
        continue
    pct = (window / base.iloc[-1] - 1) * 100  # % change vs. price when news broke
    name = config.TICKERS[ticker]
    line.add_scatter(x=pct.index, y=pct.values, mode="lines", name=name,
                     line=dict(width=2, color=MARKET_COLORS.get(name)),
                     hovertemplate="%{y:+.2f}%<extra>" + name + "</extra>")
line.add_vline(x=event["published"], line_dash="dash", line_color="#999")
line.add_annotation(x=event["published"], y=1, yref="paper", text="news", showarrow=False,
                    yanchor="bottom")
line.update_layout(height=380, hovermode="x unified", yaxis_title="% change since news",
                   yaxis_ticksuffix="%", legend_orientation="h", margin=dict(t=20, b=10))
st.plotly_chart(line, width="stretch")

detail = table[table["title"] == event["title"]].set_index("market")[windows]
st.dataframe(detail.style.format("{:+.2f}%", na_rep="not yet"), width="stretch")

# ---- Everything ----
with st.expander("All headlines × markets (table)"):
    show = table.copy()
    show["published"] = pd.to_datetime(show["published"]).dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(show.drop(columns=["ticker"]), width="stretch", hide_index=True)
    st.download_button("Download CSV", table.to_csv(index=False), "oil_news_impact.csv")
