import streamlit as st
import json

# הגדרת כיווניות מימין לשמאל (RTL) כדי שיהיה נוח לקריאה בעברית
st.set_page_config(page_title="סיכום בוקר פיננסי", page_icon="☕", layout="centered")
st.markdown("""
    <style>
    .block-container { direction: rtl; text-align: right; }
    p, h1, h2, h3, h4, h5, h6 { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("☕ סיכום הבוקר של אייל")

# ניסיון לקרוא את קובץ הנתונים שהסוכן אמור לייצר
try:
    with open('daily_insights.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    st.caption(f"📅 עדכון אחרון: {data.get('date', 'לא ידוע')}")
    
    st.header("🎯 השורה התחתונה")
    # הצגת המסקנה המרכזית עם תיבה מודגשת
    st.info(data.get('main_conclusion', 'אין תובנות מיוחדות הבוקר.'))
    
    st.divider()
    
    st.subheader("📊 מניות במוקד")
    # מעבר על כל מניה שהסוכן מצא בה משהו מעניין
    stocks = data.get('stocks', [])
    if stocks:
        for stock in stocks:
            st.write(f"**{stock['symbol']}** {stock['icon']} | {stock['insight']}")
    else:
        st.write("אין חדשות דרמטיות על המניות בתיק שלך היום.")
        
    st.divider()
    
    st.subheader("💱 מאקרו ומטבעות")
    macro = data.get('macro', {})
    if macro:
        for key, value in macro.items():
            st.write(f"**{key}:** {value}")
    else:
        st.write("אין שינויים חריגים בגזרת המאקרו.")

except FileNotFoundError:
    # מה שיוצג כל עוד הסוכן עדיין לא רץ בפעם הראשונה
    st.warning("הסוכן עדיין לא רץ היום! 🤖 הנתונים יופיעו כאן ברגע שהוא יסיים את הסריקה הראשונה שלו.")
    st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=800&auto=format&fit=crop", caption="המערכת בהקמה...")
