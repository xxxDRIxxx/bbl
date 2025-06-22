import streamlit as st
import pandas as pd

st.set_page_config(page_title="Basketball Scoring System", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("data/BBL_Statssheet.xlsx", sheet_name="SLvsBS JUN 21")
    df.columns = df.columns.str.strip()  # Clean up column names
    return df

df = load_data()

st.title("🏀 Basketball Player Scoring System")
st.markdown("Explore player statistics from the uploaded game data.")

# Show column names for debugging
st.write("🔍 Column names:", df.columns.tolist())

# Attempt to find the correct player name column
player_col = None
for col in df.columns:
    if "player" in col.lower():
        player_col = col
        break

if player_col:
    df[player_col] = df[player_col].fillna(method="ffill")
else:
    st.error("❌ Could not find a 'Player Name' column.")
    st.stop()

# Drop completely empty rows
df.dropna(how="all", inplace=True)

# Display raw data
with st.expander("🔍 Show Raw Data"):
    st.dataframe(df)

# Team selection
if "Team Name" in df.columns:
    teams = df["Team Name"].dropna().unique()
    selected_team = st.selectbox("Select Team", options=teams)

    team_df = df[df["Team Name"] == selected_team]

    st.subheader(f"📋 Player Stats for {selected_team}")
    st.dataframe(team_df)

    # Select only numeric columns that exist
    possible_numeric = ['FT made', '2PTM', '3PTM', 'Assist', 'TO', 'FOULS']
    numeric_cols = [col for col in possible_numeric if col in team_df.columns]
    if numeric_cols:
        agg_df = team_df[numeric_cols].sum(numeric_only=True).to_frame(name="Total")
        st.subheader("📊 Team Totals")
        st.table(agg_df)

    # Best & Defensive Player
    best = team_df.get('Best Player', pd.Series()).dropna().unique()
    defensive = team_df.get('Defensive Player', pd.Series()).dropna().unique()

    if len(best):
        st.success(f"🏆 **Best Player:** {', '.join(best)}")
    if len(defensive):
        st.info(f"🛡️ **Defensive Player:** {', '.join(defensive)}")
else:
    st.error("❌ 'Team Name' column not found in the data.")
