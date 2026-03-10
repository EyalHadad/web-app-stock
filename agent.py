import os
import json
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# הגדרת התחברות ל-API של ג'מיני (את המפתח נגדיר בנפרד בהמשך בסודות של גיטהאב)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=API_KEY)

# רשימת הנכסים שלנו (המניות שלך + מט"ח)
# LUMI.TA זה לאומי בתל אביב, ILS=X זה דולר-שקל, EURILS=X זה אירו-שקל, DX-Y.NYB זה מדד הדולר
symbols = ["TSLA", "GOOG", "LUMI.TA", "MRVL", "AMZN", "NLR", "RDW", "ILS=X", "EURILS=X", "DX-Y.NYB"]

print("Fetching data from Yahoo Finance...")
raw_data_summary = ""

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        # משיכת מחיר אחרון
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[1]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            raw_data_summary += f"\nSymbol: {symbol} | Last Price: {last_close:.2f} | Change: {change_pct:.2f}%\n"
        
        # משיכת כותרות חדשות (רק למניות, פחות רלוונטי למט"ח במבנה הזה)
        if "=" not in symbol and "DX" not in symbol:
            news = ticker.news
            if news:
                raw_data_summary += "Recent News Titles:\n"
                for item in news[:3]: # ניקח רק את 3 הכתבות האחרונות כדי לא להעמיס
                    raw_data_summary += f"- {item['title']}\n"
    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")

print("Sending data to Gemini API for analysis...")

# בניית הפרומפט שינחה את המודל איך לנתח ואיך להחזיר את התשובה
prompt = f"""
אתה סוכן פיננסי חכם שעוזר לי לעקוב אחרי תיק ההשקעות שלי.
הנה הנתונים והחדשות הגולמיים של היממה האחרונה עבור המניות ושערי המט"ח שלי:
{raw_data_summary}

המשימה שלך:
1. לנתח את הנתונים ולמצוא רק דברים מעניינים באמת (זינוקים, התרסקויות, או חדשות דרמטיות). אל תדווח על תנודות שגרתיות של פחות מ-2%.
2. להחזיר את התשובה *אך ורק* בפורמט JSON תקין (ללא טקסט מקדים או סוגר), לפי המבנה הבא:

{{
  "date": "תאריך של היום",
  "main_conclusion": "משפט אחד שמסכם את האירוע המרכזי של היום בשוק, על בסיס הנתונים.",
  "stocks": [
    {{"symbol": "TSLA", "icon": "🚀", "insight": "סיכום קצר של למה המניה עלתה/ירדה והאם יש חדשות משמעותיות."}}
  ],
  "macro": {{
    "דולר-שקל": "המחיר הנוכחי ומגמה קצרה",
    "אירו-שקל": "המחיר הנוכחי",
    "מדד הדולר העולמי": "המחיר הנוכחי ומגמה"
  }}
}}

חשוב: אם עבור מניה מסוימת אין שום דבר מעניין (תנודה קלה ואין חדשות מיוחדות), אל תכניס אותה בכלל למערך ה-stocks. אני רוצה לראות רק מה שדורש התייחסות.
"""

# קריאה למודל (נשתמש במודל הפלאש המהיר והזול)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)

# ניקוי התשובה (לפעמים המודל מוסיף תגיות markdown של קוד, ננקה אותן כדי שישאר רק JSON טהור)
result_text = response.text.replace("```json", "").replace("```", "").strip()

# שמירה לקובץ
try:
    parsed_json = json.loads(result_text)
    with open('daily_insights.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_json, f, ensure_ascii=False, indent=4)
    print("Successfully saved daily_insights.json")
except Exception as e:
    print("Failed to parse or save JSON from model response:", e)
    print("Raw response was:", result_text)
