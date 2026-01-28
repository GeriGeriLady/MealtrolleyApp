import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(layout="wide")
st.title("A350 Business Class – Meal Trolley")

# -----------------------------
# Seatmap A350
# -----------------------------
seatmap = [
    ["1A", "1C", None, "1D", "1G", None, "1H", "1K"],
    ["2A", "2C", None, "2D", "2G", None, "2H", "2K"],
    ["3A", "3C", None, "3D", "3G", None, "3H", "3K"],
    ["4A", "4C", None, "4D", "4G", None, "4H", "4K"],
    ["5A", "5C", None, "5D", "5G", None, "5H", "5K"],
]

# -----------------------------
# Meal Codes
# -----------------------------
starters = ["—", "VSV", "VSF"]
hotmeals = ["—", "HMV", "HMF", "HMR", "HMC"]

# -----------------------------
# Session State Initialisierung
# -----------------------------
if "selected_seat" not in st.session_state:
    st.session_state.selected_seat = None

if "seats" not in st.session_state:
    st.session_state.seats = {}

# Cateringzahlen
if "catering" not in st.session_state:
    st.session_state.catering = {m: 0 for m in ["VSV", "VSF", "HMR", "HMF", "HMC", "HMV"]}

if "backup" not in st.session_state:
    st.session_state.backup = {m: 0 for m in ["VSV", "VSF", "HMR", "HMF", "HMV"]}  # HMC kein Backup

# -----------------------------
# Catering Popups
# -----------------------------
with st.expander("Catering (Crew eintragen)"):
    st.markdown("### Hauptversorgung")
    for meal in st.session_state.catering:
        st.session_state.catering[meal] = st.number_input(
            f"{meal}",
            min_value=0,
            value=st.session_state.catering[meal],
            step=1,
            key=f"catering_{meal}"
        )

with st.expander("Crewmeals (Backup, außer HMC)"):
    st.markdown("### Backup")
    for meal in st.session_state.backup:
        st.session_state.backup[meal] = st.number_input(
            f"{meal}",
            min_value=0,
            value=st.session_state.backup[meal],
            step=1,
            key=f"backup_{meal}"
        )

st.markdown("---")

# -----------------------------
# Seatmap Anzeige
# -----------------------------
for row in seatmap:
    cols = st.columns(len(row))
    for i, seat in enumerate(row):
        if seat is None:
            cols[i].write("")
        else:
            seat_data = st.session_state.seats.get(seat, {})
            starter = seat_data.get("starter", "Keine")
            hotmeal = seat_data.get("hotmeal", "Keine")
            quickmeal = seat_data.get("quickmeal", False)

            # Sitzstatus bestimmen
            if quickmeal:
                label = f"🟣 {seat}"  # Quick Meal
            elif hotmeal not in (None, "—", "Keine"):
                label = f"🟢 {seat}"  # Hot Meal gewählt
            elif starter not in (None, "—", "Keine"):
                label = f"🟡 {seat}"  # Nur Vorspeise
            else:
                label = f"🔴 {seat}"  # nichts gewählt

            if cols[i].button(label, key=f"seat_{seat}"):
                st.session_state.selected_seat = seat

st.markdown("---")

# -----------------------------
# Catering Übersicht auf Hauptseite
# -----------------------------
st.subheader("Catering Übersicht")
catering_cols = st.columns(len(st.session_state.catering))
for i, meal in enumerate(st.session_state.catering):
    remaining = st.session_state.catering[meal]
    backup_num = st.session_state.backup.get(meal, 0)
    total_display = str(remaining)
    if remaining <= 0 and backup_num > 0:
        total_display = f"0 ({backup_num})"
    elif remaining <= 0 and backup_num <= 0:
        total_display = "0"

    # Rot färben, wenn nichts mehr verfügbar
    if remaining <= 0 and backup_num <= 0:
        catering_cols[i].markdown(f"<span style='color:red'>{meal}: {total_display}</span>", unsafe_allow_html=True)
    else:
        catering_cols[i].markdown(f"{meal}: {total_display}")

st.markdown("---")

# -----------------------------
# Sitz-Detailbereich
# -----------------------------
if st.session_state.selected_seat:
    seat = st.session_state.selected_seat
    st.subheader(f"Sitz {seat}")

    # Sitzdaten anlegen, falls noch nicht vorhanden
    if seat not in st.session_state.seats:
        st.session_state.seats[seat] = {
            "starter": "Keine",
            "hotmeal": "Keine",
            "special": "",
            "quickmeal": False,
            "pad": False  # PAD Checkbox
        }

    seat_data = st.session_state.seats[seat]

    # Vorspeise
    seat_data["starter"] = st.selectbox(
        "Vorspeise",
        ["Keine"] + starters[1:],
        index=(["Keine"] + starters[1:]).index(seat_data["starter"]),
        key=f"starter_{seat}"
    )

    # Hot Meal
    seat_data["hotmeal"] = st.selectbox(
        "Hot Meal",
        ["Keine"] + hotmeals[1:],
        index=(["Keine"] + hotmeals[1:]).index(seat_data["hotmeal"]),
        key=f"hotmeal_{seat}"
    )

    # Quick Meal Checkbox
    seat_data["quickmeal"] = st.checkbox(
        "Quick Meal",
        value=seat_data.get("quickmeal", False),
        key=f"quickmeal_{seat}"
    )

    # PAD Checkbox
    seat_data["pad"] = st.checkbox(
        "PAD (Crew-Kollege)",
        value=seat_data.get("pad", False),
        key=f"pad_{seat}"
    )

    # Special Request
    seat_data["special"] = st.text_input(
        "Special Request",
        value=seat_data["special"],
        key=f"special_{seat}"
    )

    # Speichern Button
    if st.button("Speichern", key=f"save_{seat}"):
        st.session_state.selected_seat = None
        st.success(f"Sitz {seat} gespeichert!")
