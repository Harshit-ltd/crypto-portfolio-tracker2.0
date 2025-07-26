import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime

# Load portfolio from JSON
def load_portfolio():
    with open("portfolio.json", "r") as file:
        return json.load(file)

# Save portfolio back to JSON
def save_portfolio(portfolio):
    with open("portfolio.json", "w") as file:
        json.dump(portfolio, file, indent=4)

# Get real-time prices from CoinGecko
def get_prices(symbols):
    ids = ",".join(symbols)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,inr"
    response = requests.get(url)
    return response.json()

# App configuration
st.set_page_config(page_title="💰 Crypto Portfolio Tracker", layout="wide")
st.title("💼 Real-Time Crypto Portfolio Tracker")
st.markdown("Track your crypto investments live with real-time data from CoinGecko 🚀")

# Load portfolio
portfolio = load_portfolio()
symbols = list(portfolio.keys())

# Get prices
price_data = get_prices(symbols)

# Sidebar for user inputs and settings
st.sidebar.header("⚙️ Portfolio Settings")
currency_display = st.sidebar.radio("Display Currency", ["USD", "INR"])

# Option to add new coin (interactive)
if st.sidebar.checkbox("➕ Add New Coin"):
    with st.sidebar.form("add_coin_form"):
        new_symbol = st.text_input("Coin Symbol (e.g. bitcoin)").lower()
        amount = st.number_input("Amount", min_value=0.0, value=0.0)
        buy_price = st.number_input("Buy Price (USD)", min_value=0.0, value=0.0)
        alert_price = st.number_input("Alert Above (USD)", min_value=0.0, value=0.0)
        submit = st.form_submit_button("Add to Portfolio")

        if submit and new_symbol and amount > 0:
            portfolio[new_symbol] = {
                "amount": amount,
                "buy_price": buy_price,
                "alert_above": alert_price
            }
            save_portfolio(portfolio)
            st.success(f"✅ Added {new_symbol} to portfolio! Refresh the app.")

# Portfolio display
rows = []
total_usd = 0
total_inr = 0
alerts = []

st.markdown("### 📈 Portfolio Summary")

for symbol in symbols:
    info = portfolio[symbol]
    amount = info["amount"]
    buy_price = info["buy_price"]
    alert_above = info.get("alert_above")

    symbol_data = price_data.get(symbol, {})
    current_usd = symbol_data.get("usd", 0)
    current_inr = symbol_data.get("inr", 0)

    value_usd = current_usd * amount
    value_inr = current_inr * amount
    gain_usd = value_usd - (buy_price * amount)

    total_usd += value_usd
    total_inr += value_inr

    if alert_above and current_usd > alert_above:
        alerts.append(f"🚨 {symbol.upper()} crossed ${alert_above}! Current: ${current_usd}")

    rows.append({
        "Token": symbol.capitalize(),
        "Amount": amount,
        "Buy Price (USD)": f"${buy_price}",
        "Current Price (USD)": f"${current_usd}",
        "Value (USD)": f"${value_usd:,.2f}",
        "Gain/Loss (USD)": f"${gain_usd:,.2f}",
        "Value (INR)": f"₹{value_inr:,.2f}"
    })

df = pd.DataFrame(rows)

if currency_display == "USD":
    st.dataframe(df[["Token", "Amount", "Buy Price (USD)", "Current Price (USD)", "Value (USD)", "Gain/Loss (USD)"]],
                 use_container_width=True)
else:
    st.dataframe(df[["Token", "Amount", "Value (INR)"]], use_container_width=True)

# Show totals
st.markdown("### 💹 Portfolio Overview")
col1, col2 = st.columns(2)
col1.metric("Total Portfolio Value (USD)", f"${total_usd:,.2f}")
col2.metric("Total Portfolio Value (INR)", f"₹{total_inr:,.2f}")

# Show alerts
if alerts:
    st.warning("⚠️ Alerts Triggered:")
    for alert in alerts:
        st.write(alert)

# Footer
st.caption(f"⏱ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")