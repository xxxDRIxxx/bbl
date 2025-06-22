
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Basketball Scoring System", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("data/BBL_Statssheet.xlsx", sheet_name="SLvsBS JUN 21")

df = load_data()

st.title("🏀 Basketball Player Scoring System")
st.markdown("Explore player statistics from the uploaded game data.")

# Clean data: Forward fill player names where they are split across rows
df["# Player Name"] = df["# Player Name"].fillna(method="ffill")

# Drop completely empty rows
df.dropna(how="all", inplace=True)

# Display raw data
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df)

# Team breakdown
teams = df["Team Name"].dropna().unique()
selected_team = st.selectbox("Select Team", options=teams)

team_df = df[df["Team Name"] == selected_team]

st.subheader(f"📋 Player Stats for {selected_team}")
st.dataframe(team_df)

# Aggregate team stats
numeric_cols = ['FT made', '2PTM', '3PTM', 'Assist', 'TO', 'FOULS']
agg_df = team_df[numeric_cols].sum(numeric_only=True).to_frame(name="Total")
st.subheader("📊 Team Totals")
st.table(agg_df)

# Best Player
best_player = team_df['Best Player'].dropna().unique()
def_player = team_df['Defensive Player'].dropna().unique()

if len(best_player):
    st.success(f"🏆 **Best Player:** {', '.join(best_player)}")

if len(def_player):
    st.info(f"🛡️ **Defensive Player:** {', '.join(def_player)}")
