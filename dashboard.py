import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from config import DATA_CLEANED

df = pd.read_csv(DATA_CLEANED / "price_history_cleaned.csv")
df["date"] = pd.to_datetime(df["date"])

fig = px.line(
    df,
    x="date",
    y="price_usd",
    color="coin",
    title="Crypto Prices — Last 7 Days",
    markers=True,
    hover_data={"price_usd": ":,.2f", "coin": True, "date": True}
)

fig.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    title_font_size=20
)

fig.update_traces(mode="lines+markers", marker=dict(size=8))

import webbrowser
from pathlib import Path
out = Path(__file__).parent / "dashboard.html"
fig.write_html(str(out))
webbrowser.open(str(out))
print("Done!")
