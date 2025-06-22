import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏀 Official BBL Scoring App", layout="wide")

@st.cache_data
def load_template():
    df = pd.read_excel("data/BBL_Statssheet.xlsx", sheet_name="score sheet OFFICIAL")
    df.columns = df.columns.str.strip()
    return df

df = load_template()

# Identify key columns
player_col = next((col for col in df.columns if "player" in col.lower()), None)
team_col = next((col for col in df.columns if "team" in col.lower()), None)

df[player_col] = df[player_col].fillna(method="ffill")
df.dropna(how="all", inplace=True)

st.title("🏀 BBL Scoring System (Official Form-Based)")
st.markdown("Use this interface to enter player stats using arrows and dropdowns.")

# Filter players
player_df = df[df[player_col].notna() & df[player_col].str.lower().str.startswith("p")]

# Utility to safely convert input to int
def safe_int(val):
    try:
        return int(pd.to_numeric(val, errors="coerce") or 0)
    except:
        return 0

edited_data = []

st.markdown("### ✍️ Player Statistics Entry")
for idx, row in player_df.iterrows():
    st.markdown(f"#### Player: {row[player_col]}")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    ft = col1.number_input("FT made", min_value=0, value=safe_int(row.get("FT made")), key=f"ft_{idx}")
    twopt = col2.number_input("2PTM", min_value=0, value=safe_int(row.get("2PTM")), key=f"2pt_{idx}")
    threept = col3.number_input("3PTM", min_value=0, value=safe_int(row.get("3PTM")), key=f"3pt_{idx}")
    assists = col4.number_input("Assist", min_value=0, value=safe_int(row.get("Assist")), key=f"ast_{idx}")
    to = col5.number_input("TO", min_value=0, value=safe_int(row.get("TO")), key=f"to_{idx}")
    fouls = col6.number_input("FOULS", min_value=0, value=safe_int(row.get("FOULS")), key=f"fouls_{idx}")

    edited_data.append({
        "#": row.get("#", ""),
        player_col: row[player_col],
        "FT made": ft,
        "2PTM": twopt,
        "3PTM": threept,
        "Assist": assists,
        "TO": to,
        "FOULS": fouls,
        "Team Name": row.get("Team Name", "")
    })

# Final stats DataFrame
result_df = pd.DataFrame(edited_data)

st.markdown("## 📊 Live Scoring Table")
st.dataframe(result_df, use_container_width=True)

if team_col and "FT made" in result_df.columns:
    st.markdown("## 🧮 Team Totals")
    team_scores = result_df.groupby("Team Name")[["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"]].sum()
    st.dataframe(team_scores)

# Best/Defensive Player
player_names = result_df[player_col].dropna().unique().tolist()

st.markdown("## 🏅 Awards")
col1, col2 = st.columns(2)
best = col1.selectbox("🏆 Best Player", options=player_names)
defensive = col2.selectbox("🛡️ Defensive Player", options=player_names)

st.success(f"**🏆 Best Player:** {best}")
st.info(f"**🛡️ Defensive Player:** {defensive}")
