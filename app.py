import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="🏀 BBL Official Scoring App", layout="wide")

st.markdown("""
    <style>
        .stButton>button {
            font-size: 16px;
            padding: 6px 12px;
        }
        .stTextInput>div>input {
            font-size: 16px;
        }
        h5 {
            margin-top: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 BBL Scoring System (Editable Roster + Tally Buttons + Export)")

# Sidebar Game Settings
st.sidebar.title("⚙️ Game Settings")
default_players = 17
num_players_team_a = st.sidebar.number_input("Number of Players - Team A", min_value=1, max_value=20, value=default_players)
num_players_team_b = st.sidebar.number_input("Number of Players - Team B", min_value=1, max_value=20, value=default_players)

# Editable Team Names
team_a_name = st.sidebar.text_input("Team A Name", value="Team A")
team_b_name = st.sidebar.text_input("Team B Name", value="Team B")

# Toggle between teams
team_selection = st.radio("Select Team", [team_a_name, team_b_name], horizontal=True)

# Determine selected team variables
is_team_a = (team_selection == team_a_name)
team_key = "player_stats_team_a" if is_team_a else "player_stats_team_b"
num_players = num_players_team_a if is_team_a else num_players_team_b

# Initialize session state if needed
if team_key not in st.session_state:
    st.session_state[team_key] = []

# Adjust player list in session state
while len(st.session_state[team_key]) < num_players:
    idx = len(st.session_state[team_key]) + 1
    st.session_state[team_key].append({
        "Player": f"Player {idx}",
        "FT made": 0,
        "2PTM": 0,
        "3PTM": 0,
        "Assist": 0,
        "TO": 0,
        "FOULS": 0,
    })
if len(st.session_state[team_key]) > num_players:
    st.session_state[team_key] = st.session_state[team_key][:num_players]

# Utility to handle increment/decrement
def score_button(col, label, key, delta=1):
    if col.button(label, key=key):
        return delta
    return 0

st.markdown(f"### ✍️ Player Stats for **{team_selection}**")

updated_stats = []

for i, stats in enumerate(st.session_state[team_key]):
    st.markdown(f"#### 🧍 Player {i+1}")
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2, 2, 2])

    for stat, col in zip(["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"],
                         [col1, col2, col3, col4, col5, col6]):
        col.markdown(f"**{stat}**")
        cols = col.columns([1, 1, 1])
        stats[stat] += score_button(cols[0], "➖", key=f"{team_key}_{stat}_minus_{i}", delta=-1)
        cols[1].markdown(f"<h5 style='text-align: center;'>{stats[stat]}</h5>", unsafe_allow_html=True)
        stats[stat] += score_button(cols[2], "➕", key=f"{team_key}_{stat}_plus_{i}", delta=1)

    # Editable player name
    stats["Player"] = col7.text_input("Name", value=stats["Player"], key=f"{team_key}_name_{i}")
    updated_stats.append(stats)

# DataFrame of player stats
result_df = pd.DataFrame(updated_stats)

st.markdown(f"## 📊 Live Player Scoring Table - {team_selection}")
st.dataframe(result_df, use_container_width=True)

# Team Totals
st.markdown("## 📈 Team Totals")
team_totals = result_df[["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"]].sum().to_frame(name="Total")
st.table(team_totals)

# Awards
st.markdown("## 🏅 Awards")
best = st.selectbox("🏆 Best Player", options=result_df["Player"], key=f"{team_key}_best")
defensive = st.selectbox("🛡️ Defensive Player", options=result_df["Player"], key=f"{team_key}_def")

st.success(f"🏆 Best Player: {best}")
st.info(f"🛡️ Defensive Player: {defensive}")

# Excel Export
def convert_df_to_excel(df, team_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=team_name)
        team_totals.T.to_excel(writer, sheet_name="Totals")
    output.seek(0)
    return output

st.download_button(
    label="📥 Download Team Stats as Excel",
    data=convert_df_to_excel(result_df, team_selection),
    file_name=f"{team_selection}_stats.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
