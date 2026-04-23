import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #2F4A5C, #567C8D, #C8D9E6);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #2F4A5C;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* KPI CARDS */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 15px;
    padding: 15px;
    color: #2F4A5C;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
}
/* KPI DELTA COLOR FIX */
[data-testid="stMetricDelta"] {
    color: white !important;
}

[data-testid="stMetricDelta"] svg {
    fill: white !important;
}

/* BUTTON */
button {
    background-color: #567C8D !important;
    color: white !important;
    border-radius: 10px;
}

/* HEADINGS */
h1, h2, h3 {
    color: #2F4A5C;
}



</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("python_dataset.csv")

# ---------------- CLEAN DATA ----------------
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df.columns = df.columns.str.strip().str.lower()

# ---------------- TITLE ----------------
col1, col2 = st.columns([1,4])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=80)

with col2:
    st.markdown("<h1 style='text-align:center;'>E-Commerce Analytics Dashboard</h1>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- INFO BOX ----------------
st.markdown("""
<div style="background: linear-gradient(90deg, #567C8D, #2F4A5C); padding: 20px; border-radius: 15px; color: white;">

Welcome to the <b>E-Commerce Analytics Dashboard</b><br><br>

- Analyze revenue, profit, and orders in real-time<br>
- Explore trends across categories and regions<br>
- Identify top-performing segments instantly<br>
- Use interactive filters for deep insights<br>
- Discover hidden patterns with advanced visuals<br><br>

Turn data into smart business decisions!

</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Filters")

category = st.sidebar.multiselect(
    "Select Category",
    options=df["product_category"].unique(),
    default=df["product_category"].unique()
)

region = st.sidebar.multiselect(
    "Select Region",
    options=df["customer_region"].unique(),
    default=df["customer_region"].unique()
)

min_price = int(df["price"].min())
max_price = int(df["price"].max())

price_range = st.sidebar.slider(
    "💰 Select Price Range",
    min_price,
    max_price,
    (min_price, max_price)
)

if st.sidebar.button("Reset Filters"):
    category = df["product_category"].unique()
    region = df["customer_region"].unique()

# ---------------- FILTER DATA ----------------
filtered_df = df[
    (df["product_category"].isin(category)) &
    (df["customer_region"].isin(region)) &
    (df["price"].between(price_range[0], price_range[1]))
]

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"{filtered_df['total_revenue'].sum():,.0f}", "+12%")
col2.metric("🛒 Orders", f"{filtered_df['quantity_sold'].sum():,.0f}", "+8%")
col3.metric("📈 Profit", f"{filtered_df['profit'].sum():,.0f}", "+5%")
col4.metric("⭐ Rating", f"{filtered_df['rating'].mean():.2f}", "+2%")

st.markdown("---")

# ---------------- VISUALS ----------------

fig1 = px.treemap(
    filtered_df,
    path=["customer_region", "product_category"],
    values="total_revenue",
    title="Revenue Distribution"
)
st.plotly_chart(fig1, use_container_width=True)

# Trend
if "order_date" in filtered_df.columns:
    filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])
    trend = filtered_df.groupby("order_date")["total_revenue"].sum().reset_index()

    fig_trend = px.line(trend, x="order_date", y="total_revenue",
                        title="Revenue Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

# Sunburst
fig2 = px.sunburst(
    filtered_df,
    path=["product_category", "payment_method"],
    values="total_revenue",
    title="Category vs Payment Method"
)
st.plotly_chart(fig2, use_container_width=True)

# Heatmap
pivot = filtered_df.pivot_table(
    values="total_revenue",
    index="customer_region",
    columns="product_category",
    aggfunc="sum"
)

fig3 = px.imshow(pivot, text_auto=True, title="Revenue Heatmap")
st.plotly_chart(fig3, use_container_width=True)

# Scatter
fig4 = px.scatter(
    filtered_df,
    x="price",
    y="profit",
    size="quantity_sold",
    color="product_category",
    title="Price vs Profit",
    hover_data=["customer_region"]
)
st.plotly_chart(fig4, use_container_width=True)

# Top 5
top5 = filtered_df.groupby("product_category")["total_revenue"].sum().sort_values(ascending=False).head(5)

fig5 = px.bar(top5, title="Top 5 Categories")
st.plotly_chart(fig5, use_container_width=True)

# ---------------- INSIGHTS ----------------
st.markdown("### Smart Insights")

if not filtered_df.empty:
    best_cat = filtered_df.groupby("product_category")["total_revenue"].sum().idxmax()
    best_reg = filtered_df.groupby("customer_region")["total_revenue"].sum().idxmax()

    st.markdown(f"""
<div style="
background: rgba(255,255,255,0.1);
padding: 15px;
border-radius: 12px;
color: white;
font-size: 16px;
backdrop-filter: blur(10px);
">

<b>Top Category:</b> {best_cat} <br><br>
<b>Best Region:</b> {best_reg} <br><br>
<b>Total Profit:</b> {int(filtered_df['profit'].sum())}

</div>
""", unsafe_allow_html=True)
else:
    st.warning("No data available for selected filters")
