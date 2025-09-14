import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

# ---------------- STYLING ---------------- #
st.markdown("""
    <style>
        h1, h2, h3 {
            color: #1a237e;
            font-family: 'Arial Black', sans-serif;
        }
        .stDataFrame th {
            background-color: #263238 !important;
            color: white !important;
        }
        .stDownloadButton button {
            background-color: #1e88e5;
            color: white;
            border-radius: 8px;
            padding: 6px 12px;
            border: none;
        }
        .stDownloadButton button:hover {
            background-color: #1565c0;
        }
        /* Tab colors */
        div[data-baseweb="tab-list"] > div[role="tab"] {
            background-color: #eeeeee;
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            margin-right: 4px;
        }
        div[data-baseweb="tab-list"] > div[role="tab"][aria-selected="true"] {
            background-color: #1e88e5;
            color: white !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- SPLASH / LOADING ---------------- #
if "splash" not in st.session_state:
    st.session_state.splash = True

if st.session_state.splash:
    st.markdown(
        "<div style='text-align:center; padding:100px;'>"
        "<h1 style='font-size:60px; color:#1e88e5;'>Business Reports</h1>"
        "<p style='font-size:20px;'>Loading your dashboards...</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.session_state.splash = False
    st.stop()

# ---------------- DOWNLOAD FUNCTION ---------------- #
def download_buttons(df, name):
    if df.empty:
        st.info("No data to download yet.")
        return
    
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"{name}.csv", "text/csv")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    st.download_button(
        "⬇️ Download Excel",
        buffer.getvalue(),
        f"{name}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------- CALCULATION FUNCTIONS ---------------- #
def calculate_production(df):
    if not df.empty:
        df["Stock Available"] = (
            df["Opening Stock (kg)"]
            + df["Produced Stock"]
            - df["Sold Stock"]
            - df["Damaged Stock"]
            - df["Shortage"]
            - df["Deliverd"]
            - df["Walk In"]
        )
    return df

def calculate_plastic(df):
    if not df.empty:
        df["Closing Stock (kg)"] = (
            df["Opening Stock (kg)"]
            + df["Purchase Plastic (kg)"]
            - df["Raw Materials Used (kg)"]
            - df["Rejects (kg)"]
        )
    return df

def calculate_delivery(df):
    if not df.empty:
        df["Closing stock"] = df["Opening Stock"] - df["Sales stock"]
        df["Total Sales amount"] = df["Credit"] + df["COD"]
        df["Outstanding Credit Balance"] = df["Credit"] - df["Total Credit Paid"]
        df["Total Money on Hand2"] = df["COD"] + df["Total Credit Paid"]
    return df

# ---------------- SUMMARY + CHARTS ---------------- #
def show_summary(df, date_col="Date", color="Blues", chart_title="Summary Trends"):
    if df.empty:
        st.info("No data available for summary.")
        return
    
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)

    numeric_cols = df.select_dtypes(include=["number"]).columns

    weekly = df[numeric_cols].resample("W").sum()
    monthly = df[numeric_cols].resample("ME").sum()  # fixed offset alias
    yearly = df[numeric_cols].resample("YE").sum()

    st.subheader("📅 Weekly Summary")
    st.dataframe(weekly.style.background_gradient(cmap=color), width="stretch")

    st.subheader("📅 Monthly Summary")
    st.dataframe(monthly.style.background_gradient(cmap=color), width="stretch")

    st.subheader("📅 Yearly Summary")
    st.dataframe(yearly.style.background_gradient(cmap=color), width="stretch")

    for label, summary in [("Weekly", weekly), ("Monthly", monthly), ("Yearly", yearly)]:
        if summary.empty:
            continue

        st.markdown(f"### 📈 {label} {chart_title} - Line Chart")
        fig, ax = plt.subplots(figsize=(8, 3))
        summary.plot(ax=ax, marker="o")
        ax.set_title(f"{label} {chart_title}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        st.pyplot(fig)

        st.markdown(f"### 📊 {label} {chart_title} - Bar Chart")
        fig, ax = plt.subplots(figsize=(8, 3))
        summary.plot(kind="bar", ax=ax)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", label_type="edge", padding=2)
        ax.set_title(f"{label} {chart_title}")
        ax.set_xlabel("Period")
        ax.set_ylabel("Values")
        st.pyplot(fig)

    # 📈 Extra: Cumulative Closing Stock Trend
    if "Closing Stock (kg)" in df.columns or "Closing stock" in df.columns or "Stock Available" in df.columns:
        st.subheader("📊 Cumulative Closing Stock Trend")
        col = None
        if "Stock Available" in df.columns:
            col = "Stock Available"
        elif "Closing Stock (kg)" in df.columns:
            col = "Closing Stock (kg)"
        elif "Closing stock" in df.columns:
            col = "Closing stock"

        if col:
            fig, ax = plt.subplots(figsize=(8, 3))
            df[col].cumsum().plot(ax=ax, color="purple", marker="o")
            ax.set_title("Cumulative Closing Stock")
            ax.set_xlabel("Date")
            ax.set_ylabel("Cumulative Stock")
            st.pyplot(fig)

# ---------------- INITIALIZE SESSION STATE ---------------- #
if "production" not in st.session_state:
    st.session_state.production = pd.DataFrame(columns=[
        "Date", "Production Type", "Opening Stock (kg)", "Produced Stock",
        "Sold Stock", "Damaged Stock", "Shortage", "Deliverd", "Walk In",
        "Stock Available", "Finish Time"
    ])

if "plastic" not in st.session_state:
    st.session_state.plastic = pd.DataFrame(columns=[
        "Date", "Production Type", "Opening Stock (kg)",
        "Purchase Plastic (kg)", "Raw Materials Used (kg)",
        "Rejects (kg)", "Closing Stock (kg)", "Counted Plastics (kg)"
    ])

if "delivery" not in st.session_state:
    st.session_state.delivery = pd.DataFrame(columns=[
        "Date", "Production Type", "Opening Stock", "Closing stock",
        "Sales stock", "Credit", "COD", "Total Sales amount",
        "Credit Balance", "Total Credit Paid",
        "Outstanding Credit Balance", "Total Money on Hand2"
    ])

# ---------------- APP LAYOUT ---------------- #
st.title("📊 Business Reports Dashboard")

tabs = st.tabs(["🏭 Production", "🛍️ Plastic", "🚚 Delivery"])

# ---------------- PRODUCTION TAB ---------------- #
with tabs[0]:
    st.header("Production Report")
    with st.form("production_form", clear_on_submit=True):
        date = st.date_input("Date")
        prod_type = st.text_input("Production Type")

        opening = st.session_state.production.iloc[-1]["Stock Available"] if not st.session_state.production.empty else 0
        opening_stock = st.number_input("Opening Stock (kg)", value=int(opening))
        produced = st.number_input("Produced Stock", value=0)
        sold = st.number_input("Sold Stock", value=0)
        damaged = st.number_input("Damaged Stock", value=0)
        shortage = st.number_input("Shortage", value=0)
        deliverd = st.number_input("Deliverd", value=0)
        walk_in = st.number_input("Walk In", value=0)
        finish_time = st.text_input("Finish Time")

        if st.form_submit_button("Add Record"):
            new_row = {
                "Date": date, "Production Type": prod_type,
                "Opening Stock (kg)": opening_stock, "Produced Stock": produced,
                "Sold Stock": sold, "Damaged Stock": damaged,
                "Shortage": shortage, "Deliverd": deliverd,
                "Walk In": walk_in, "Stock Available": 0,
                "Finish Time": finish_time
            }
            st.session_state.production = pd.concat(
                [st.session_state.production, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.session_state.production = calculate_production(st.session_state.production)

    st.subheader("Production Table")
    st.dataframe(st.session_state.production.style.background_gradient(cmap="Blues"), width="stretch")
    download_buttons(st.session_state.production, "production_report")
    show_summary(st.session_state.production, "Date", "Blues", "Production Totals")

# ---------------- PLASTIC TAB ---------------- #
with tabs[1]:
    st.header("Plastic Report")
    with st.form("plastic_form", clear_on_submit=True):
        date = st.date_input("Date")
        prod_type = st.text_input("Production Type")

        opening = st.session_state.plastic.iloc[-1]["Closing Stock (kg)"] if not st.session_state.plastic.empty else 0
        opening_stock = st.number_input("Opening Stock (kg)", value=int(opening))
        purchase = st.number_input("Purchase Plastic (kg)", value=0)
        used = st.number_input("Raw Materials Used (kg)", value=0)
        rejects = st.number_input("Rejects (kg)", value=0)
        counted = st.number_input("Counted Plastics (kg)", value=0)

        if st.form_submit_button("Add Record"):
            new_row = {
                "Date": date, "Production Type": prod_type,
                "Opening Stock (kg)": opening_stock,
                "Purchase Plastic (kg)": purchase,
                "Raw Materials Used (kg)": used,
                "Rejects (kg)": rejects,
                "Closing Stock (kg)": 0,
                "Counted Plastics (kg)": counted
            }
            st.session_state.plastic = pd.concat(
                [st.session_state.plastic, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.session_state.plastic = calculate_plastic(st.session_state.plastic)

    st.subheader("Plastic Table")
    st.dataframe(st.session_state.plastic.style.background_gradient(cmap="Greens"), width="stretch")
    download_buttons(st.session_state.plastic, "plastic_report")
    show_summary(st.session_state.plastic, "Date", "Greens", "Plastic Totals")

# ---------------- DELIVERY TAB ---------------- #
with tabs[2]:
    st.header("Delivery Report")
    with st.form("delivery_form", clear_on_submit=True):
        date = st.date_input("Date")
        prod_type = st.text_input("Production Type")

        opening = st.session_state.delivery.iloc[-1]["Closing stock"] if not st.session_state.delivery.empty else 0
        opening_stock = st.number_input("Opening Stock", value=int(opening))
        sales = st.number_input("Sales stock", value=0)
        credit = st.number_input("Credit", value=0)
        cod = st.number_input("COD", value=0)
        credit_balance = st.number_input("Credit Balance", value=0)
        paid = st.number_input("Total Credit Paid", value=0)

        if st.form_submit_button("Add Record"):
            new_row = {
                "Date": date, "Production Type": prod_type,
                "Opening Stock": opening_stock, "Closing stock": 0,
                "Sales stock": sales, "Credit": credit,
                "COD": cod, "Total Sales amount": 0,
                "Credit Balance": credit_balance,
                "Total Credit Paid": paid,
                "Outstanding Credit Balance": 0,
                "Total Money on Hand2": 0
            }
            st.session_state.delivery = pd.concat(
                [st.session_state.delivery, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.session_state.delivery = calculate_delivery(st.session_state.delivery)

    st.subheader("Delivery Table")
    st.dataframe(st.session_state.delivery.style.background_gradient(cmap="Oranges"), width="stretch")
    download_buttons(st.session_state.delivery, "delivery_report")
    show_summary(st.session_state.delivery, "Date", "Oranges", "Delivery Totals")