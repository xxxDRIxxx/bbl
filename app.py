import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏀 BBL Official Scoring App", layout="wide")

st.title("🏀 BBL Scoring System (Dynamic Roster + Tally Buttons)")

# Admin input: number of players
num_players = st.number_input("🔢 How many players will you input?", min_value=1, max_value=20, value=5, step=1)

# Initialize session state
if "player_stats" not in st.session_state:
    st.session_state.player_stats = []

# Adjust session state based on number of players
if len(st.session_state.player_stats) < num_players:
    for i in range(len(st.session_state.player_stats), num_players):
        st.session_state.player_stats.append({
            "Player": f"Player {i+1}",
            "FT made": 0,
            "2PTM": 0,
            "3PTM": 0,
            "Assist": 0,
            "TO": 0,
            "FOULS": 0,
        })
elif len(st.session_state.player_stats) > num_players:
    st.session_state.player_stats = st.session_state.player_stats[:num_players]

# Utility to handle increment/decrement
def score_button(col, label, key, delta=1):
    if col.button(label, key=key):
        return delta
    return 0

st.markdown("### ✍️ Player Stats (Click + or - to Tally)")

updated_stats = []

for i, stats in enumerate(st.session_state.player_stats):
    st.markdown(f"#### 🧍 {stats['Player']}")
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2, 2, 2])

    for stat, col in zip(["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"],
                         [col1, col2, col3, col4, col5, col6]):
        col.markdown(f"**{stat}**")
        cols = col.columns(3)
        stats[stat] += score_button(cols[0], "➖", key=f"{stat}_minus_{i}", delta=-1)
        cols[1].markdown(f"<h5 style='text-align: center;'>{stats[stat]}</h5>", unsafe_allow_html=True)
        stats[stat] += score_button(cols[2], "➕", key=f"{stat}_plus_{i}", delta=1)

    # Player name editable
    stats["Player"] = col7.text_input("Name", value=stats["Player"], key=f"name_{i}")
    updated_stats.append(stats)

# Show final table
result_df = pd.DataFrame(updated_stats)
st.markdown("## 📊 Live Player Scoring Table")
st.dataframe(result_df, use_container_width=True)

# Team summary
st.markdown("## 📈 Team Totals")
team_totals = result_df[["FT made", "2PTM", "3PTM", "Assist", "TO", "FOULS"]].sum().to_frame(name="Total")
st.table(team_totals)

# Award selection
st.markdown("## 🏅 Awards")
best = st.selectbox("🏆 Best Player", options=result_df["Player"])
defensive = st.selectbox("🛡️ Defensive Player", options=result_df["Player"])

st.success(f"🏆 Best Player: {best}")
st.info(f"🛡️ Defensive Player: {defensive}")
