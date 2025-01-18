import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# App title
st.title("Stock Market Visualizer")
st.markdown("Analyze stock market data with interactive charts.")

# Sidebar inputs
st.sidebar.header("User Input")

# Function to fetch stock data
def get_stock_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Candlestick chart with overlays
def plot_candlestick(data, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'))
    
    # Moving averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='20-Day SMA'))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], mode='lines', name='50-Day SMA'))

    # Bollinger Bands
    data['Upper_BB'] = data['SMA_20'] + 2 * data['Close'].rolling(window=20).std()
    data['Lower_BB'] = data['SMA_20'] - 2 * data['Close'].rolling(window=20).std()
    fig.add_trace(go.Scatter(x=data.index, y=data['Upper_BB'], mode='lines', name='Upper BB', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower_BB'], mode='lines', name='Lower BB', line=dict(dash='dot')))

    fig.update_layout(title=f"{ticker} Candlestick Chart with Overlays",
                      xaxis_title="Date",
                      yaxis_title="Price",
                      template="plotly_dark")
    return fig

# Upload portfolio CSV/Excel
def upload_portfolio():
    uploaded_file = st.sidebar.file_uploader("Upload Portfolio (CSV/Excel):", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    return None

# Export charts
def export_chart(fig, filename):
    fig.write_image(filename)
    st.success(f"Chart saved as {filename}")

# User inputs
selected_stock = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, MSFT):", "AAPL")
start_date = st.sidebar.date_input("Start Date:", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date:", pd.to_datetime("2023-01-01"))

# Portfolio analysis
portfolio_data = upload_portfolio()
if portfolio_data is not None:
    st.subheader("Uploaded Portfolio Data")
    st.dataframe(portfolio_data)

# Fetch data and plot
if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching stock data..."):
        stock_data = get_stock_data(selected_stock, start_date, end_date)

        if stock_data is not None:
            st.success(f"Data fetched for {selected_stock}")

            # Display data
            st.subheader(f"Raw Data for {selected_stock}")
            st.dataframe(stock_data)

            # Candlestick chart
            st.subheader(f"Candlestick Chart for {selected_stock}")
            candlestick_fig = plot_candlestick(stock_data, selected_stock)
            st.plotly_chart(candlestick_fig)

            # Export chart as PNG
            if st.sidebar.button("Export Chart as PNG"):
                buffer = BytesIO()
                candlestick_fig.write_image(buffer, format="png")
                st.download_button(
                    label="Download PNG",
                    data=buffer.getvalue(),
                    file_name=f"{selected_stock}_chart.png",
                    mime="image/png"
                )

            # Export chart as HTML
            if st.sidebar.button("Export Chart as HTML"):
                buffer = BytesIO()
                candlestick_fig.write_html(buffer)
                st.download_button(
                    label="Download HTML",
                    data=buffer.getvalue(),
                    file_name=f"{selected_stock}_chart.html",
                    mime="text/html"
                )

# Save configurations
if st.sidebar.button("Save Configuration"):
    config = {
        "stock": selected_stock,
        "start_date": str(start_date),
        "end_date": str(end_date)
    }
    config_df = pd.DataFrame([config])
    st.download_button(
        label="Download Configuration",
        data=config_df.to_csv(index=False).encode("utf-8"),
        file_name="stock_visualizer_config.csv",
        mime="text/csv"
    )

st.info("Use the sidebar to adjust inputs and explore features like portfolio analysis and chart export.")
