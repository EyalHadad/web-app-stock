import streamlit as st
import json
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="דאשבורד פיננסי", page_icon="☕", layout="wide")

st.markdown("""
    <style>
    .block-container { direction: rtl; text-align: right; }
    p, h1, h2, h3, h4, h5, h6, li { direction: rtl; text-align: right; }
    /* סידור החצים של המאקרו שיראו טוב בכיווניות מימין לשמאל */
    div[data-testid="stMetricValue"] { direction: ltr; text-align: right; }
    div[data-testid="stMetricDelta"] { direction: ltr; text-align: right; display: flex; flex-direction: row-reverse; justify-content: flex-end; }
    div[data-testid="stMetricDelta"] > div { margin-left: 0.5rem; margin-right: 0; }
    </style>
""", unsafe_allow_html=True)

st.title("☕ סיכום הבוקר של אייל")

# --- חלק 1: תמונת מצב חיה של התיק ---
st.header("📋 תמונת מצב התיק")

@st.cache_data(ttl=1800)
def get_live_portfolio():
    symbols = ["TSLA", "GOOG", "LUMI.TA", "MRVL", "AMZN", "NLR", "RDW"]
    data = []
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev = hist['Close'].iloc[0]
                curr = hist['Close'].iloc[1]
                chg = curr - prev
                chg_pct = (chg / prev) * 100
                data.append({"מניה": sym, "מחיר אחרון": curr, "שינוי ($)": chg, "שינוי (%)": chg_pct})
        except:
            pass
    return pd.DataFrame(data)

df = get_live_portfolio()

if not df.empty:
    # יצירת עמודת צבע לגרף (ירוק חזק לעליות, אדום לירידות)
    df['color'] = df['שינוי (%)'].apply(lambda x: '#00C805' if x >= 0 else '#FF4B4B')
    
    col1, col2 = st.columns([1.2, 2])
    
    with col1:
        def color_red_green(val):
            color = '#00C805' if val > 0 else '#FF4B4B' if val < 0 else 'gray'
            return f'color: {color}; font-weight: bold'
        
       # תצוגת טבלה מעוצבת - הפעם אנחנו משמיטים את עמודת הצבע מהתצוגה!
        st.dataframe(df.drop(columns=['color']).style.map(color_red_green, subset=['שינוי ($)', 'שינוי (%)'])
                     .format({"מחיר אחרון": "{:.2f}", "שינוי ($)": "{:.2f}", "שינוי (%)": "{:.2f}%"}), 
                     use_container_width=True, hide_index=True)
    with col2:
        # גרף מעוצב עם צבעים לפי העליות/ירידות
        st.bar_chart(df, x='מניה', y='שינוי (%)', color='color', use_container_width=True)

st.divider()

# --- חלק 2: תובנות ה-AI ---
st.header("🤖 תובנות הסוכן החכם")

try:
    with open('daily_insights.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    today_date = datetime.now().strftime("%d/%m/%Y")
    st.caption(f"עדכון AI אחרון: {today_date}")
    
    st.info(f"**השורה התחתונה:** {data.get('main_conclusion', '')}")
    
    # חלוקה ל-3 עמודות: מניות | מאקרו | חדשות עולם
    col_stocks, col_macro, col_news = st.columns([1.5, 1, 1.5])
    
    with col_stocks:
        st.subheader("💡 אירועים חריגים במניות")
        stocks = data.get('stocks', [])
        if stocks:
            for stock in stocks:
                st.markdown(f"**{stock['symbol']}** {stock['icon']} | {stock['insight']}")
        else:
            st.write("אין תנודות חריגות במיוחד ביממה האחרונה.")
            
    with col_macro:
        st.subheader("💱 מאקרו ומטבעות")
        macro = data.get('macro', {})
        if macro:
            for key, info in macro.items():
                # שימוש בפונקציית ה-Metric עם Delta שיוצרת אוטומטית חץ ירוק/אדום
                st.metric(label=key, value=info.get("value", "-"), delta=info.get("delta", ""))
                
    with col_news:
        st.subheader("🌍 בעולם הכלכלה")
        news_items = data.get('economy_news', [])
        if news_items:
            for item in news_items:
                st.markdown(f"**{item.get('region', '')}:** {item.get('news', '')}")

except FileNotFoundError:
    st.warning("תובנות ה-AI עדיין לא מוכנות להיום.")
