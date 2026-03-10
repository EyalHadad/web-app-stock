import streamlit as st
import json
import yfinance as yf
import pandas as pd
from datetime import datetime

# הגדרת הדף - תצוגה רחבה שתופסת את כל המסך
st.set_page_config(page_title="דאשבורד פיננסי", page_icon="☕", layout="wide")

# עיצוב מותאם אישית - יישור לימין וכיווניות
st.markdown("""
    <style>
    .block-container { direction: rtl; text-align: right; }
    p, h1, h2, h3, h4, h5, h6, li { direction: rtl; text-align: right; }
    div[data-testid="stMetricValue"], div[data-testid="stMetricDelta"] { direction: ltr; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("☕ סיכום הבוקר של אייל")

# --- חלק 1: תמונת מצב חיה של התיק (מבוסס על נתונים בזמן אמת) ---
st.header("📋 תמונת מצב התיק")

# פונקציה שמושכת נתונים ושומרת אותם בזיכרון לחצי שעה כדי שהאתר יטען מהר
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
                data.append({"מניה": sym, "מחיר אחרון": round(curr, 2), "שינוי ($)": round(chg, 2), "שינוי (%)": round(chg_pct, 2)})
        except:
            pass
    return pd.DataFrame(data)

df = get_live_portfolio()

if not df.empty:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        # פונקציה לצביעת הטבלה (ירוק לעליות, אדום לירידות)
        def color_red_green(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
            return f'color: {color}; font-weight: bold'
        
        # תצוגת טבלה מעוצבת
        st.dataframe(df.style.map(color_red_green, subset=['שינוי ($)', 'שינוי (%)']), 
                     use_container_width=True, hide_index=True)
    
    with col2:
        # גרף עמודות שממחיש את השינוי היומי באחוזים
        st.bar_chart(df.set_index('מניה')['שינוי (%)'], color="#1f77b4")

st.divider()

# --- חלק 2: תובנות ה-AI מהבוקר ---
st.header("🤖 תובנות הסוכן החכם")

try:
    with open('daily_insights.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    today_date = datetime.now().strftime("%d/%m/%Y")
    st.caption(f"עדכון AI אחרון: {today_date}")
    
    st.info(f"**השורה התחתונה:** {data.get('main_conclusion', 'אין תובנות מיוחדות הבוקר.')}")
    
    st.subheader("💡 אירועים חריגים במניות")
    stocks = data.get('stocks', [])
    if stocks:
        for stock in stocks:
            st.markdown(f"**{stock['symbol']}** {stock['icon']} | {stock['insight']}")
    else:
        st.write("הסוכן לא זיהה חדשות דרמטיות או תנודות חריגות במיוחד ביממה האחרונה.")
        
    st.subheader("💱 מאקרו ומטבעות")
    macro = data.get('macro', {})
    if macro:
        cols = st.columns(3)
        with cols[0]:
            st.metric(label="דולר-שקל", value=macro.get("דולר-שקל", "-").split(" ")[0])
        with cols[1]:
            st.metric(label="אירו-שקל", value=macro.get("אירו-שקל", "-").split(" ")[0])
        with cols[2]:
            st.metric(label="מדד הדולר (DXY)", value=macro.get("מדד הדולר העולמי", "-").split(" ")[0])
    
except FileNotFoundError:
    st.warning("תובנות ה-AI עדיין לא מוכנות להיום.")
