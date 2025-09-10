import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO

# Data setup
daily_dates = ["01/09/2025", "02/09/2025", "03/09/2025", "04/09/2025", "05/09/2025", "06/09/2025", "07/09/2025"]
weeks_list = ["Week 1", "Week 2", "Week 3", "Week 4"]
months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
years_list = [2025 + i for i in range(10)]
current_week = "Week 1"
current_month = "September"
current_year = 2025

# Load or initialize data with fallback to default structure
def load_data(filename, default_data):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
            for key in default_data:
                if key in loaded_data:
                    default_data[key].update(loaded_data[key])
                else:
                    default_data[key] = loaded_data.get(key, default_data[key])
    return default_data

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Initial data
if "prod_daily_data" not in st.session_state:
    st.session_state.prod_daily_data = load_data("prod_daily_data.json", {
        "daily": {date: {"Production Type": "3Kg", "Opening Stock (kg)": 0, "Produced Stock": 0, "Sold Stock": 0, 
                         "Damaged Stock": 0, "Shortage": 0, "Delivered": 0, "Walk In": 0, "Stock Available": 0, 
                         "Finish Time": ""} for date in daily_dates},
        "weekly": {week: {"Production Type": "3Kg", "Opening Stock (kg)": 0, "Produced Stock": 0, "Sold Stock": 0, 
                          "Damaged Stock": 0, "Shortage": 0, "Delivered": 0, "Walk In": 0, "Stock Available": 0, 
                          "Finish Time": ""} for week in weeks_list},
        "monthly": {month: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Produced Stock": 0, 
                            "Sum of Sold Stock": 0, "Sum of Damaged Stock": 0, "Sum of Shortages": 0, 
                            "Sum of Delivered Stock": 0, "Sum of Walk Ins": 0, "Sum of Stock Available": 0, 
                            "Sum of Finish Time": ""} for month in months_list},
        "yearly": {year: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Produced Stock": 0, 
                          "Sum of Sold Stock": 0, "Sum of Damaged Stock": 0, "Sum of Shortages": 0, 
                          "Sum of Delivered Stock": 0, "Sum of Walk Ins": 0, "Sum of Stock Available": 0, 
                          "Sum of Finish Time": ""} for year in years_list}
    })
if "plas_daily_data" not in st.session_state:
    st.session_state.plas_daily_data = load_data("plas_daily_data.json", {
        "daily": {date: {"Production Type": "3Kg", "Opening Stock (kg)": 0, "Purchase Plastic (kg)": 0, 
                         "Raw Materials Used (kg)": 0, "Rejects (kg)": 0, "Closing Stock (kg)": 0, 
                         "Counted Plastics (kg)": 0} for date in daily_dates},
        "weekly": {week: {"Production Type": "3Kg", "Opening Stock (kg)": 0, "Purchase Plastic (kg)": 0, 
                          "Raw Materials Used (kg)": 0, "Rejects (kg)": 0, "Closing Stock (kg)": 0, 
                          "Counted Plastics (kg)": 0} for week in weeks_list},
        "monthly": {month: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Purchased Plastic": 0, 
                            "Sum of Raw Materials Used": 0, "Sum of Rejects": 0, "Sum of Closing Stock": 0, 
                            "Sum of Counted Plastics": 0} for month in months_list},
        "yearly": {year: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Purchased Plastic": 0, 
                          "Sum of Raw Materials Used": 0, "Sum of Rejects": 0, "Sum of Closing Stock": 0, 
                          "Sum of Counted Plastics": 0} for year in years_list}
    })
if "del_daily_data" not in st.session_state:
    st.session_state.del_daily_data = load_data("del_daily_data.json", {
        "daily": {date: {"Production Type": "3Kg", "Opening Stock": 0, "Closing Stock": 0, "Sales Stock": 0, 
                         "Credit": 0, "COD": 0, "Total Sales Amount": 0, "Credit Balance": 0, "Total Credit Paid": 0, 
                         "Outstanding Credit Balance": 0, "Total Money on Hand": 0} for date in daily_dates},
        "weekly": {week: {"Production Type": "3Kg", "Opening Stock": 0, "Closing Stock": 0, "Sales Stock": 0, 
                          "Credit": 0, "COD": 0, "Total Sales Amount": 0, "Credit Balance": 0, "Total Credit Paid": 0, 
                          "Outstanding Credit Balance": 0, "Total Money on Hand": 0} for week in weeks_list},
        "monthly": {month: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Closing Stock": 0, 
                            "Sum of Sales Stock": 0, "Sum of Credit": 0, "Sum of COD": 0, "Sum of Total Sales Amount": 0, 
                            "Sum of Credit Balance": 0, "Sum of Total Credit Paid": 0, "Sum of Outstanding Credit": 0, 
                            "Sum of Total Money on Hand": 0} for month in months_list},
        "yearly": {year: {"Production Type": "3Kg", "Sum of Opening Stock": 0, "Sum of Closing Stock": 0, 
                          "Sum of Sales Stock": 0, "Sum of Credit": 0, "Sum of COD": 0, "Sum of Total Sales Amount": 0, 
                          "Sum of Credit Balance": 0, "Sum of Total Credit Paid": 0, "Sum of Outstanding Credit": 0, 
                          "Sum of Total Money on Hand": 0} for year in years_list}
    })

# Calculation functions
def calculate_prod(row):
    return {
        "Stock Available": round(float(row.get("Opening Stock (kg)", 0)) + float(row.get("Produced Stock", 0)) - 
                               float(row.get("Sold Stock", 0)) - float(row.get("Damaged Stock", 0)) - 
                               float(row.get("Shortage", 0)), 2)
    }

def calculate_plas(row):
    return {
        "Closing Stock (kg)": round(float(row.get("Opening Stock (kg)", 0)) + float(row.get("Purchase Plastic (kg)", 0)) - 
                                float(row.get("Raw Materials Used (kg)", 0)) - float(row.get("Rejects (kg)", 0)), 2)
    }

def calculate_del(row):
    return {
        "Closing Stock": round(float(row.get("Opening Stock", 0) - float(row.get("Sales Stock", 0)), 2)),
        "Total Sales Amount": round(float(row.get("Credit", 0)) + float(row.get("COD", 0)), 2),
        "Outstanding Credit Balance": round(float(row.get("Credit Balance", 0)) - float(row.get("Total Credit Paid", 0)), 2)
    }

# Update higher-level data
def update_higher_tables(prod_data, plas_data, del_data):
    prod_week = prod_data["weekly"][current_week]
    prod_daily = [prod_data["daily"][date] for date in daily_dates]
    prod_week.update({
        "Opening Stock (kg)": float(prod_daily[0].get("Opening Stock (kg)", 0)),
        "Produced Stock": sum(float(d.get("Produced Stock", 0)) for d in prod_daily),
        "Sold Stock": sum(float(d.get("Sold Stock", 0)) for d in prod_daily),
        "Damaged Stock": sum(float(d.get("Damaged Stock", 0)) for d in prod_daily),
        "Shortage": sum(float(d.get("Shortage", 0)) for d in prod_daily),
        "Delivered": sum(float(d.get("Delivered", 0)) for d in prod_daily),
        "Walk In": sum(float(d.get("Walk In", 0)) for d in prod_daily),
        "Stock Available": calculate_prod(prod_week)["Stock Available"],
        "Finish Time": prod_daily[-1].get("Finish Time", "")
    })
    prod_month = prod_data["monthly"][current_month]
    prod_month.update({
        "Sum of Opening Stock": prod_week["Opening Stock (kg)"],
        "Sum of Produced Stock": prod_week["Produced Stock"],
        "Sum of Sold Stock": prod_week["Sold Stock"],
        "Sum of Damaged Stock": prod_week["Damaged Stock"],
        "Sum of Shortages": prod_week["Shortage"],
        "Sum of Delivered Stock": prod_week["Delivered"],
        "Sum of Walk Ins": prod_week["Walk In"],
        "Sum of Stock Available": prod_week["Stock Available"],
        "Sum of Finish Time": ""
    })
    prod_year = prod_data["yearly"][current_year]
    prod_year.update({k.replace("Sum of ", ""): v for k, v in prod_month.items() if k != "Production Type"})

    plas_week = plas_data["weekly"][current_week]
    plas_daily = [plas_data["daily"][date] for date in daily_dates]
    plas_week.update({
        "Opening Stock (kg)": float(plas_daily[0].get("Opening Stock (kg)", 0)),
        "Purchase Plastic (kg)": sum(float(d.get("Purchase Plastic (kg)", 0)) for d in plas_daily),
        "Raw Materials Used (kg)": sum(float(d.get("Raw Materials Used (kg)", 0)) for d in plas_daily),
        "Rejects (kg)": sum(float(d.get("Rejects (kg)", 0)) for d in plas_daily),
        "Closing Stock (kg)": calculate_plas(plas_week)["Closing Stock (kg)"],
        "Counted Plastics (kg)": sum(float(d.get("Counted Plastics (kg)", 0)) for d in plas_daily)
    })
    plas_month = plas_data["monthly"][current_month]
    plas_month.update({k.replace("Sum of ", ""): v for k, v in plas_week.items()})
    plas_year = plas_data["yearly"][current_year]
    plas_year.update({k.replace("Sum of ", ""): v for k, v in plas_month.items()})

    del_week = del_data["weekly"][current_week]
    del_daily = [del_data["daily"][date] for date in daily_dates]
    del_week.update({
        "Opening Stock": float(del_daily[0].get("Opening Stock", 0)),
        "Sales Stock": sum(float(d.get("Sales Stock", 0)) for d in del_daily),
        "Closing Stock": calculate_del(del_week)["Closing Stock"],
        "Credit": sum(float(d.get("Credit", 0)) for d in del_daily),
        "COD": sum(float(d.get("COD", 0)) for d in del_daily),
        "Total Sales Amount": calculate_del(del_week)["Total Sales Amount"],
        "Credit Balance": sum(float(d.get("Credit Balance", 0)) for d in del_daily),
        "Total Credit Paid": sum(float(d.get("Total Credit Paid", 0)) for d in del_daily),
        "Outstanding Credit Balance": calculate_del(del_week)["Outstanding Credit Balance"],
        "Total Money on Hand": sum(float(d.get("Total Money on Hand", 0)) for d in del_daily)
    })
    del_month = del_data["monthly"][current_month]
    del_month.update({k.replace("Sum of ", ""): v for k, v in del_week.items()})
    del_year = del_data["yearly"][current_year]
    del_year.update({k.replace("Sum of ", ""): v for k, v in del_month.items()})

# Function to display tables and charts with export
def display_tables(data, prefix, tab_color):
    st.subheader(f"{prefix} Daily")
    daily_df = pd.DataFrame([{**{"Date": date}, **data["daily"][date]} for date in daily_dates])
    edited_daily = st.data_editor(daily_df, key=f"{prefix}_daily", num_rows="dynamic", on_change=update_data, args=(data, "daily", daily_dates))
    for date in daily_dates:
        data["daily"][date].update({k: v for k, v in edited_daily.get(date, {}).items() if k != "Date"})
        if prefix == "Production":
            data["daily"][date].update(calculate_prod(data["daily"][date]))
        elif prefix == "Plastic":
            data["daily"][date].update(calculate_plas(data["daily"][date]))
        elif prefix == "Delivery":
            data["daily"][date].update(calculate_del(data["daily"][date]))
    st.table(daily_df)
    if st.button("Show Chart", key=f"{prefix}_daily_chart"):
        with st.expander("Chart"):
            numeric_cols = [col for col in daily_df.columns if col != "Date" and daily_df[col].dtype in [int, float]]
            if numeric_cols:
                st.bar_chart(daily_df[numeric_cols].set_index("Date"))
    if st.button("Export to Excel", key=f"{prefix}_daily_export"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            daily_df.to_excel(writer, sheet_name=f"{prefix} Daily", index=False)
        st.download_button(label="Download Excel", data=output.getvalue(), file_name=f"{prefix}_daily_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader(f"{prefix} Weekly")
    weekly_df = pd.DataFrame([{**{"Week": week}, **data["weekly"][week]} for week in weeks_list])
    edited_weekly = st.data_editor(weekly_df, key=f"{prefix}_weekly", num_rows="dynamic", on_change=update_data, args=(data, "weekly", weeks_list))
    for week in weeks_list:
        data["weekly"][week].update({k: v for k, v in edited_weekly.get(week, {}).items() if k != "Week"})
        if prefix == "Production":
            data["weekly"][week].update(calculate_prod(data["weekly"][week]))
        elif prefix == "Plastic":
            data["weekly"][week].update(calculate_plas(data["weekly"][week]))
        elif prefix == "Delivery":
            data["weekly"][week].update(calculate_del(data["weekly"][week]))
    st.table(weekly_df)
    if st.button("Show Chart", key=f"{prefix}_weekly_chart"):
        with st.expander("Chart"):
            numeric_cols = [col for col in weekly_df.columns if col != "Week" and weekly_df[col].dtype in [int, float]]
            if numeric_cols:
                st.bar_chart(weekly_df[numeric_cols].set_index("Week"))
    if st.button("Export to Excel", key=f"{prefix}_weekly_export"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            weekly_df.to_excel(writer, sheet_name=f"{prefix} Weekly", index=False)
        st.download_button(label="Download Excel", data=output.getvalue(), file_name=f"{prefix}_weekly_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader(f"{prefix} Monthly")
    monthly_df = pd.DataFrame([{**{"Month": month}, **data["monthly"][month]} for month in months_list])
    edited_monthly = st.data_editor(monthly_df, key=f"{prefix}_monthly", num_rows="dynamic", on_change=update_data, args=(data, "monthly", months_list))
    for month in months_list:
        data["monthly"][month].update({k: v for k, v in edited_monthly.get(month, {}).items() if k != "Month"})
    st.table(monthly_df)
    if st.button("Show Chart", key=f"{prefix}_monthly_chart"):
        with st.expander("Chart"):
            numeric_cols = [col for col in monthly_df.columns if col != "Month" and monthly_df[col].dtype in [int, float]]
            if numeric_cols:
                st.bar_chart(monthly_df[numeric_cols].set_index("Month"))
    if st.button("Export to Excel", key=f"{prefix}_monthly_export"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            monthly_df.to_excel(writer, sheet_name=f"{prefix} Monthly", index=False)
        st.download_button(label="Download Excel", data=output.getvalue(), file_name=f"{prefix}_monthly_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader(f"{prefix} Yearly")
    yearly_df = pd.DataFrame([{**{"Year": year}, **data["yearly"][year]} for year in years_list])
    edited_yearly = st.data_editor(yearly_df, key=f"{prefix}_yearly", num_rows="dynamic", on_change=update_data, args=(data, "yearly", years_list))
    for year in years_list:
        data["yearly"][year].update({k: v for k, v in edited_yearly.get(year, {}).items() if k != "Year"})
    st.table(yearly_df)
    if st.button("Show Chart", key=f"{prefix}_yearly_chart"):
        with st.expander("Chart"):
            numeric_cols = [col for col in yearly_df.columns if col != "Year" and yearly_df[col].dtype in [int, float]]
            if numeric_cols:
                st.bar_chart(yearly_df[numeric_cols].set_index("Year"))
    if st.button("Export to Excel", key=f"{prefix}_yearly_export"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            yearly_df.to_excel(writer, sheet_name=f"{prefix} Yearly", index=False)
        st.download_button(label="Download Excel", data=output.getvalue(), file_name=f"{prefix}_yearly_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Callback to update data and save
def update_data(data, level, keys):
    for widget_key in st.session_state:
        if level in widget_key and isinstance(st.session_state[widget_key], dict):
            edited_data = st.session_state[widget_key]
            break
    else:
        return

    for key in keys:
        if key in edited_data:
            data[level][key].update({k: v for k, v in edited_data[key].items() if k != list(edited_data[key].keys())[0]})
            if level == "daily" and "Production" in st.session_state and st.session_state.prod_daily_data == data:
                data[level][key].update(calculate_prod(data[level][key]))
            elif level == "daily" and "Plastic" in st.session_state and st.session_state.plas_daily_data == data:
                data[level][key].update(calculate_plas(data[level][key]))
            elif level == "daily" and "Delivery" in st.session_state and st.session_state.del_daily_data == data:
                data[level][key].update(calculate_del(data[level][key]))
            elif level == "weekly" and "Production" in st.session_state and st.session_state.prod_daily_data == data:
                data[level][key].update(calculate_prod(data[level][key]))
            elif level == "weekly" and "Plastic" in st.session_state and st.session_state.plas_daily_data == data:
                data[level][key].update(calculate_plas(data[level][key]))
            elif level == "weekly" and "Delivery" in st.session_state and st.session_state.del_daily_data == data:
                data[level][key].update(calculate_del(data[level][key]))

    if data == st.session_state.prod_daily_data:
        save_data("prod_daily_data.json", data)
    elif data == st.session_state.plas_daily_data:
        save_data("plas_daily_data.json", data)
    elif data == st.session_state.del_daily_data:
        save_data("del_daily_data.json", data)
    update_higher_tables(st.session_state.prod_daily_data, st.session_state.plas_daily_data, st.session_state.del_daily_data)

# Streamlit app with CSS
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .main-header {
            color: #007bff;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px #28a745;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #f8f9fa;
            border-bottom: 2px solid #007bff;
        }
        .stTabs [data-baseweb="tab"][title="Production"] {
            background-color: #007bff;
            color: white;
        }
        .stTabs [data-baseweb="tab"][title="Production"]:hover {
            background-color: #0056b3;
        }
        .stTabs [data-baseweb="tab"][title="Plastic"] {
            background-color: #28a745;
            color: white;
        }
        .stTabs [data-baseweb="tab"][title="Plastic"]:hover {
            background-color: #218838;
        }
        .stTabs [data-baseweb="tab"][title="Delivery"] {
            background-color: #6f42c1;
            color: white;
        }
        .stTabs [data-baseweb="tab"][title="Delivery"]:hover {
            background-color: #5a2a9d;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 4px 4px 0 0;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
            color: #333;
            border: 1px solid #dee2e6;
            border-bottom: none;
        }
        .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            background-color: #e9ecef;
        }
        .stTabs [aria-selected="true"] {
            border: 1px solid #007bff;
        }
        table[data-testid="stTable"][title="Production Daily"],
        table[data-testid="stTable"][title="Production Weekly"],
        table[data-testid="stTable"][title="Production Monthly"],
        table[data-testid="stTable"][title="Production Yearly"] {
            background-color: #e6f0fa;
        }
        table[data-testid="stTable"][title="Plastic Daily"],
        table[data-testid="stTable"][title="Plastic Weekly"],
        table[data-testid="stTable"][title="Plastic Monthly"],
        table[data-testid="stTable"][title="Plastic Yearly"] {
            background-color: #e6f3e6;
        }
        table[data-testid="stTable"][title="Delivery Daily"],
        table[data-testid="stTable"][title="Delivery Weekly"],
        table[data-testid="stTable"][title="Delivery Monthly"],
        table[data-testid="stTable"][title="Delivery Yearly"] {
            background-color: #f0e6f6;
        }
        th, td {
            border: 1px solid #dee2e6;
            padding: 8px;
            text-align: left;
            color: #333;
        }
        th {
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #ffffff;
        }
        tr:hover {
            background-color: #dfefff;
        }
        .stDataFrame {
            border: 1px solid #dee2e6;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
    </style>
""", unsafe_allow_html=True)

# Heading
st.markdown("<h1 class='main-header'>Reports App</h1>", unsafe_allow_html=True)

# Tabs for different reports
tabs = st.tabs(["Production", "Plastic", "Delivery"])

# Display tables in each tab
with tabs[0]:
    display_tables(st.session_state.prod_daily_data, "Production", "#007bff")
with tabs[1]:
    display_tables(st.session_state.plas_daily_data, "Plastic", "#28a745")
with tabs[2]:
    display_tables(st.session_state.del_daily_data, "Delivery", "#6f42c1")