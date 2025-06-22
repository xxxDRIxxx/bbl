import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏀 Official Basketball Scoring Sheet", layout="wide")

# Load the official scoresheet template
@st.cache_data
def load_template():
    df = pd.read_excel("data/BBL_Statssheet.xlsx", sheet_name="score sheet OFFICIAL")
    df.columns = df.columns.str.strip()  # Clean column names
    return df

df = load_template()

st.title("🏀 Official Basketball Scoring System")
st.markdown("Use this form to fill in or edit live stats from the official score sheet.")

# Clean player names
player_col = next((col for col in df.columns if "player" in col.lower()), None)
if player_col:
    df[player_col] = df[player_col].fillna(method="ffill")
else:
    st.error("❌ Could not detect a 'Player Name' column.")
    st.stop()

# Drop fully blank rows
df.dropna(how="all", inplace=True)

# Let user edit the full sheet
st.markdown("### ✏️ Edit Player Stats")
editable_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="official_editor"
)

# Extract numeric columns to summarize
numeric_cols = ['FT made', '2PTM', '3PTM', 'Assist', 'TO']
numeric_cols = [col for col in numeric_cols if col in editable_df.columns]

if numeric_cols:
    st.markdown("### 📊 Team Totals")
    team_totals = editable_df[numeric_cols].sum(numeric_only=True).to_frame(name="Total")
    st.table(team_totals)

# Best Player selection
player_names = editable_df[player_col].dropna().unique().tolist()

st.markdown("### 🏅 Player Awards")
best_player = st.selectbox("🏆 Best Player", options=player_names)
def_player = st.selectbox("🛡️ Defensive Player", options=player_names)

# Show selections
st.success(f"🏆 Best Player: {best_player}")
st.info(f"🛡️ Defensive Player: {def_player}")
