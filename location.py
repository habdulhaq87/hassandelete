import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from sqlalchemy import create_engine

# ─────────────────────────────────────────────
# DATABASE CONFIG
# ─────────────────────────────────────────────
DATABASE_URL = "postgresql://neondb_owner:npg_r6VLBflOHj2q@ep-soft-violet-a9zhhjgl-pooler.gwc.azure.neon.tech/neondb?sslmode=require"
TABLE_NAME = "location"
EXPECTED_COLUMNS = ["name", "latitude", "longitude", "elevation", "description"]

# ─────────────────────────────────────────────
# CONNECTION HANDLER
# ─────────────────────────────────────────────
def get_engine():
    return create_engine(DATABASE_URL)

def bulk_insert(df):
    try:
        with get_engine().begin() as conn:
            df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        return True, f"✅ {len(df)} rows inserted into '{TABLE_NAME}'"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
# STREAMLIT PAGE
# ─────────────────────────────────────────────
def show_location_page():
    st.title("📍 Location Table Manager")
    tab1, tab2, tab3 = st.tabs(["📥 Upload CSV", "📊 View Data", "📈 Graphs"])

    # ────── TAB 1: Upload CSV
    with tab1:
        st.subheader("Bulk Upload CSV")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, header=None)
                df.columns = EXPECTED_COLUMNS
                if list(df.columns) != EXPECTED_COLUMNS:
                    st.error("❌ Column mismatch.")
                    st.markdown(f"**Expected:** `{EXPECTED_COLUMNS}`")
                    st.markdown(f"**Uploaded:** `{list(df.columns)}`")
                else:
                    success, message = bulk_insert(df)
                    st.success(message) if success else st.error(f"❌ Failed: {message}")
                    if success:
                        st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Error reading CSV: {e}")

        with st.expander("📋 Expected CSV Format"):
            st.code(", ".join(EXPECTED_COLUMNS))

    # ────── TAB 2: View Data
    with tab2:
        st.subheader("📍 Location Data Viewer")
        try:
            with get_engine().connect() as conn:
                df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

            if df.empty:
                st.info("No data available.")
            else:
                st.dataframe(df)
                st.write("### 📈 Summary")
                st.write(df.describe(numeric_only=True))

                if df["latitude"].notna().all() and df["longitude"].notna().all():
                    fig = px.scatter_mapbox(
                        df,
                        lat="latitude",
                        lon="longitude",
                        hover_name="name",
                        hover_data=["elevation", "description"],
                        zoom=6,
                        height=500
                    )
                    fig.update_layout(mapbox_style="open-street-map")
                    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig)
        except Exception as e:
            st.error(f"❌ Failed to load data: {e}")

    # ────── TAB 3: Graphs
    with tab3:
        st.subheader("📈 Data Visualization")
        try:
            with get_engine().connect() as conn:
                df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

            if df.empty:
                st.info("No data available.")
            else:
                col1, col2 = st.columns(2)

                with col1:
                    st.write("### Elevation Distribution")
                    fig = px.histogram(df, x="elevation", nbins=20, title="Elevation Histogram")
                    st.plotly_chart(fig)

                with col2:
                    st.write("### Locations Count")
                    count_df = df['name'].value_counts().reset_index()
                    count_df.columns = ['Location Name', 'Count']
                    fig = px.bar(count_df, x="Location Name", y="Count", title="Location Name Frequency")
                    st.plotly_chart(fig)
        except Exception as e:
            st.error(f"❌ Visualization error: {e}")
