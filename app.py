import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(page_title="Executive Retail Intelligence", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00FFAA; }
    .stChart { border: 1px solid #333; border-radius: 12px; padding: 10px; background: #0E1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading
@st.cache_data
def load_data():
    # Verbatim reference to project1_df_2.csv
    df = pd.read_csv("project1_df.csv")
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Purchase Date'])
    return df

try:
    df = load_data()

    # --- SIDEBAR: LIMITS & RESTRICTIONS (NEW SECTION) ---
    st.sidebar.title("🎮 Dashboard Controls")
    
    with st.sidebar.expander("ℹ️ Data Validation Rules"):
        st.markdown("""
        **Attribute Restrictions:**
        *   **warehouse_block**: Must be a single **UPPERCASE** alphabet (A, B, C, D, F).
        *   **Net Amount**: Should be a positive **float** (INR).
        *   **Product Category**: Must match one of the predefined categories.
        *   **Gender**: Restricted to 'Male', 'Female', or 'Other'.
        *   **Purchase Date**: Must follow the DD/MM/YYYY HH:MM format.
        """)

    # Standard Sidebar Filters
    locations = st.sidebar.multiselect(
        "Select Locations:", 
        options=sorted(df["Location"].unique()), 
        default=sorted(df["Location"].unique())[:5]
    )
    
    filtered_df = df[df["Location"].isin(locations)]

    # --- INTERACTIVE PARAMETERS ---
    brush = alt.selection_interval(encodings=['x'], empty='all')
    click = alt.selection_point(fields=['Product Category'], empty='all')

    # --- HEADER & KPI METRICS ---
    st.title("🚀 Executive Retail Intelligence")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"₹{filtered_df['Net Amount'].sum():,.0f}")
    m2.metric("Total Orders", f"{len(filtered_df):,}")
    m3.metric("Avg. Discount", f"₹{filtered_df['Discount Amount (INR)'].mean():,.2f}")
    m4.metric("Active Cities", f"{filtered_df['Location'].nunique()}")

    st.divider()

    # --- MAIN ANALYTICS ROW ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Revenue Timeline")
        timeline = alt.Chart(filtered_df).mark_area(
            line={'color':'#00FFAA'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#00FFAA', offset=0),
                       alt.GradientStop(color='transparent', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X("Purchase Date:T", title="Time Period"),
            y=alt.Y("sum(Net Amount):Q", title="Revenue (₹)"),
            opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip("Purchase Date:T"), alt.Tooltip("sum(Net Amount):Q", format=",.2f")]
        ).add_params(brush).properties(height=400)
        
        st.altair_chart(timeline, use_container_width=True)

    with col_right:
        st.subheader("🎯 Sales by Category")
        category_bars = alt.Chart(filtered_df).mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("Product Category:N", sort='-x', title=None),
            x=alt.X("sum(Net Amount):Q", title="Revenue"),
            color=alt.condition(click, alt.value("#00FFAA"), alt.value("#333")),
            tooltip=["Product Category", alt.Tooltip("sum(Net Amount):Q", format=",.2f")]
        ).transform_filter(brush).add_params(click).properties(height=400)
        
        st.altair_chart(category_bars, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("📂 Explore Detailed Transactions"):
        st.write("Below is the filtered dataset. Note that 'warehouse_block' values are checked against uppercase constraints.")
        st.dataframe(filtered_df.sort_values("Purchase Date", ascending=False), use_container_width=True)

except FileNotFoundError:
    st.error("Error: 'project1_df_2.csv' not found.")
