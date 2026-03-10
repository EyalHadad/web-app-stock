import os
import json
import yfinance as yf
from google import genai
from datetime import datetime

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=API_KEY)

# הוספנו מדדי מאקרו (תל אביב 125, S&P 500, ומדד עולמי) רק כדי לשאוב מהם כותרות חדשות לכלכלה
symbols = ["TSLA", "GOOG", "LUMI.TA", "MRVL", "AMZN", "NLR", "RDW", "ILS=X", "EURILS=X", "DX-Y.NYB", "^TA125.TA", "SPY", "URTH"]
print("Fetching data from Yahoo Finance...")
raw_data_summary = ""

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[1]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            raw_data_summary += f"\nSymbol: {symbol} | Last Price: {last_close:.2f} | Change: {change_pct:.2f}%\n"
        
        # איסוף כותרות חדשות
        if "=" not in symbol and "DX" not in symbol:
            news = ticker.news
            if news:
                raw_data_summary += "Recent News Titles:\n"
                for item in news[:4]:
                    title = item.get('title', 'No Title Available') 
                    raw_data_summary += f"- {title}\n"
    except Exception as e:
        pass

print("Sending data to Gemini API for analysis...")

prompt = f"""
אתה סוכן פיננסי חכם. הנה הנתונים והחדשות הגולמיים של היממה האחרונה (מניות, מט"ח, ומדדי כלכלה מישראל, ארה"ב והעולם):
{raw_data_summary}

המשימה שלך:
להחזיר את התשובה *אך ורק* בפורמט JSON תקין (ללא טקסט מקדים או סוגר), לפי המבנה הבא:
{{
  "main_conclusion": "משפט אחד מסכם.",
  "stocks": [
    {{"symbol": "TSLA", "icon": "🚀", "insight": "סיכום קצר..."}}
  ],
  "macro": {{
    "דולר-שקל": {{"value": "המחיר הנוכחי במספר", "delta": "האחוז או המספר של השינוי (לדוגמה: -0.05 או 1.2%)"}},
    "אירו-שקל": {{"value": "מחיר", "delta": "שינוי"}},
    "מדד הדולר העולמי": {{"value": "מחיר", "delta": "שינוי"}}
  }},
  "economy_news": [
    {{"region": "🇮🇱 כלכלה - ישראל", "news": "עדכון אחד מעניין מהיממה האחרונה."}},
    {{"region": "🇺🇸 כלכלה - ארה״ב", "news": "עדכון אחד מעניין."}},
    {{"region": "🌍 כלכלה - עולמי (ציין מדינה)", "news": "האירוע הכלכלי הכי מעניין משאר העולם."}}
  ]
}}
"""

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    result_text = response.text.replace("```json", "").replace("```", "").strip()
    parsed_json = json.loads(result_text)
    
    with open('daily_insights.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_json, f, ensure_ascii=False, indent=4)
    print("Successfully saved daily_insights.json")
except Exception as e:
    print("Failed to parse or save JSON from model response:", e)
