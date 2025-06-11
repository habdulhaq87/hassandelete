import streamlit as st
from location import show_location_page

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(page_title="Geological DB Uploader", layout="wide")

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Select Table", ["Location", "Rock Units", "Measurements", "Samples"])

# ─────────────────────────────────────────────
# ROUTING TO MODULES
# ─────────────────────────────────────────────
if selected_page == "Location":
    show_location_page()
else:
    st.warning("⚠️ Upload UI for this table is not yet implemented.")
