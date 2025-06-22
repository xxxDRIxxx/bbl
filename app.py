import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="🏀 BBL Official Scoring App", layout="wide")

# --- Custom CSS for spacing and UI ---
st.markdown("""
    <style>
        .stButton>button {
            font-size: 15px;
            padding: 6px 14px;
        }
        .stTextInput>div>input {
            font-size: 15px;
        }
        h5 {
            margin-top: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Settings ---
st.sidebar.title("⚙️ Game Settings")
default_players = 17
num_players_team_a = st.sidebar.number_input("Number of Players - Team A", min_value=1, max_value=20, value=default_players)
num_players_team_b = st.sidebar.number_input("Number of Players - Team B", min_value=1, max_value=20, value=default_players)
team_a_name = st.sidebar.text_input("Team A Name", value="Team A")
team_b_name = st.sidebar.text_input("Team B Name", value="Team B")

# --- Team toggle ---
team_selection = st.radio("Select Team", [team_a_name, team_b_name], horizontal=True)
team_key = "team_a" if team_selection == team_a_name else "team_b"
num_players = num_players_team_a if team_selection == team_a_name else num_players_team_b

# --- Initialize session state ---
if team_key not in st.session_state:
    st.session_state[team_key] = []

# --- Default stat template ---
def default_stat(i):
    return {
        "Player": f"Player {i+1}",
        "FT made": 0, "FT Att.": 0,
        "2PTM": 0, "2PT Att.": 0,
        "3PTM": 0, "3PT Att.": 0,
        "Rebounds": 0, "Steals": 0, "Blocks": 0,
        "Assist": 0, "TO": 0, "FOULS": 0
    }

# --- Adjust player list ---
while len(st.session_state[team_key]) < num_players:
    st.session_state[team_key].append(default_stat(len(st.session_state[team_key])))
if len(st.session_state[team_key]) > num_players:
    st.session_state[team_key] = st.session_state[team_key][:num_players]

# --- Helper functions ---
def score_button(col, label, key, delta=1):
    if col.button(label, key=key):
        return delta
    return 0

def pct(made, att):
    return f"{(made/att*100):.1f}%" if att > 0 else "0%"

# --- Display Player Stats ---
st.title("🏀 BBL Scoring System (Full Stat Sheet + Export)")

updated_stats = []
for i, stats in enumerate(st.session_state[team_key]):
    st.markdown("---")
    st.markdown(f"#### 🧍 Player {i+1}")
    stats["Player"] = st.text_input("Player Name", value=stats["Player"], key=f"{team_key}_name_{i}")

    col_ft, col_2pt, col_3pt = st.columns(3)
    for label, col, made_key, att_key in [
        ("FT", col_ft, "FT made", "FT Att."),
        ("2PT", col_2pt, "2PTM", "2PT Att."),
        ("3PT", col_3pt, "3PTM", "3PT Att.")
    ]:
        col.markdown(f"**{label}**")
        subcols = col.columns(3)
        stats[made_key] += score_button(subcols[0], "➖", f"{team_key}_{made_key}_minus_{i}", -1)
        subcols[1].markdown(f"{stats[made_key]} / {stats[att_key]}", unsafe_allow_html=True)
        stats[made_key] += score_button(subcols[2], "➕", f"{team_key}_{made_key}_plus_{i}", 1)
        stats[att_key] = max(stats[att_key], stats[made_key])  # ensure attempts ≥ makes

    # Defensive + Other Stats
    col_r, col_s, col_b = st.columns(3)
    for stat, col in zip(["Rebounds", "Steals", "Blocks"], [col_r, col_s, col_b]):
        col.markdown(f"**{stat}**")
        c = col.columns(3)
        stats[stat] += score_button(c[0], "➖", f"{team_key}_{stat}_minus_{i}", -1)
        c[1].markdown(f"{stats[stat]}", unsafe_allow_html=True)
        stats[stat] += score_button(c[2], "➕", f"{team_key}_{stat}_plus_{i}", 1)

    col_a, col_to, col_foul = st.columns(3)
    for stat, col in zip(["Assist", "TO", "FOULS"], [col_a, col_to, col_foul]):
        col.markdown(f"**{stat}**")
        c = col.columns(3)
        stats[stat] += score_button(c[0], "➖", f"{team_key}_{stat}_minus_{i}", -1)
        c[1].markdown(f"{stats[stat]}", unsafe_allow_html=True)
        stats[stat] += score_button(c[2], "➕", f"{team_key}_{stat}_plus_{i}", 1)

    # Derived stats
    stats["FT %"] = pct(stats["FT made"], stats["FT Att."])
    stats["2PT %"] = pct(stats["2PTM"], stats["2PT Att."])
    stats["3PT %"] = pct(stats["3PTM"], stats["3PT Att."])
    stats["FGM"] = stats["2PTM"] + stats["3PTM"]
    stats["FG ATT."] = stats["2PT Att."] + stats["3PT Att."]
    stats["FG %"] = pct(stats["FGM"], stats["FG ATT."])
    stats["Player Total Score"] = stats["FT made"] + 2 * stats["2PTM"] + 3 * stats["3PTM"]
    updated_stats.append(stats)

# --- Create DataFrame with full columns ---
columns = [
    "Player", "FT made", "FT Att.", "FT %", "2PTM", "2PT Att.", "2PT %", "3PTM", "3PT Att.", "3PT %",
    "FGM", "FG ATT.", "FG %", "Player Total Score",
    "Rebounds", "Steals", "Blocks", "Assist", "TO", "FOULS"
]
result_df = pd.DataFrame(updated_stats)[columns]

# --- Display Table ---
st.markdown(f"## 📊 Scoring Table - {team_selection}")
st.dataframe(result_df, use_container_width=True)

# --- Team Totals ---
st.markdown("## 📈 Team Totals")
totals = result_df.drop(columns=["Player", "FT %", "2PT %", "3PT %", "FG %"]).sum().to_frame(name="Total")
st.table(totals)

# --- Awards ---
st.markdown("## 🏅 Awards")
best = st.selectbox("🏆 Best Player", options=result_df["Player"], key=f"{team_key}_best")
defensive = st.selectbox("🛡️ Defensive Player", options=result_df["Player"], key=f"{team_key}_def")
st.success(f"🏆 Best Player: {best}")
st.info(f"🛡️ Defensive Player: {defensive}")

# --- Excel Export ---
def convert_df_to_excel(df, team_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=team_name)
        totals.T.to_excel(writer, sheet_name="Totals")
    output.seek(0)
    return output

st.download_button(
    label="📥 Download Excel",
    data=convert_df_to_excel(result_df, team_selection),
    file_name=f"{team_selection}_stats.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
