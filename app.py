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

st.title("🏀 BBL Scoring System (Dynamic Roster + Tally Buttons)")

# Team toggle
team_selection = st.radio("Select Team", ["Team A", "Team B"], horizontal=True)

# Admin input: number of players
num_players = st.number_input("🔢 How many players for each team?", min_value=1, max_value=20, value=5, step=1)

# Session key per team
team_key = f"player_stats_{team_selection}"
if team_key not in st.session_state:
    st.session_state[team_key] = []

# Adjust session state based on number of players
if len(st.session_state[team_key]) < num_players:
    for i in range(len(st.session_state[team_key]), num_players):
        st.session_state[team_key].append({
            "Player": f"Player {i+1}",
            "FT made": 0,
            "2PTM": 0,
            "3PTM": 0,
            "Assist": 0,
            "TO": 0,
            "FOULS": 0,
        })
elif len(st.session_state[team_key]) > num_players:
    st.session_state[team_key] = st.session_state[team_key][:num_players]

# Utility to handle increment/decrement
def score_button(col, label, key, delta=1):
    if col.button(label, key=key):
        return delta
    return 0

st.markdown(f"### ✍️ Player Stats for {team_selection} (Click + or - to Tally)")

updated_stats = []

for i, stats in enumerate(st.session_state[team_key]):
    st.markdown(f"#### 🧍 {stats['Player']}")
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2, 2, 2])

    for stat, col in zip(["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"],
                         [col1, col2, col3, col4, col5, col6]):
        col.markdown(f"**{stat}**")
        cols = col.columns(3)
        stats[stat] += score_button(cols[0], "➖", key=f"{team_selection}_{stat}_minus_{i}", delta=-1)
        cols[1].markdown(f"<h5 style='text-align: center;'>{stats[stat]}</h5>", unsafe_allow_html=True)
        stats[stat] += score_button(cols[2], "➕", key=f"{team_selection}_{stat}_plus_{i}", delta=1)

    # Player name editable
    stats["Player"] = col7.text_input("Name", value=stats["Player"], key=f"{team_selection}_name_{i}")
    updated_stats.append(stats)

# Show final table
result_df = pd.DataFrame(updated_stats)
st.markdown(f"## 📊 Live Player Scoring Table - {team_selection}")
st.dataframe(result_df, use_container_width=True)

# Team summary
st.markdown("## 📈 Team Totals")
team_totals = result_df[["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"]].sum().to_frame(name="Total")
st.table(team_totals)

# Award selection
st.markdown("## 🏅 Awards")
best = st.selectbox("🏆 Best Player", options=result_df["Player"], key=f"{team_selection}_best")
defensive = st.selectbox("🛡️ Defensive Player", options=result_df["Player"], key=f"{team_selection}_def")

st.success(f"🏆 Best Player: {best}")
st.info(f"🛡️ Defensive Player: {defensive}")

# Export to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=team_selection)
        team_totals.T.to_excel(writer, sheet_name="Totals")
    output.seek(0)
    return output

st.download_button(
    label="📥 Download Team Stats as Excel",
    data=convert_df_to_excel(result_df),
    file_name=f"{team_selection}_stats.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)  
