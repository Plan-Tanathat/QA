import json
import pandas as pd

# โหลดไฟล์ JSON
with open("conversation_log.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ถ้าเป็น list ของหลาย session
if isinstance(data, list):
    rows = []
    for session in data:
        for entry in session["conversation"]:
            rows.append({
                "Timestamp": entry.get("timestamp", ""),
                "Question (TH)": entry.get("model_question_th", entry.get("model_question", "")),
                "Question (EN)": entry.get("model_question_en", ""),
                "Answer": entry.get("user_answer", ""),
                "Top Season": session.get("top_season", ""),
                "Summary (TH)": session.get("summary", ""),
                "Summary (EN)": session.get("summary_en", "")
            })
    df = pd.DataFrame(rows)
else:
    print("⚠️ ข้อมูล JSON ไม่อยู่ในรูปแบบที่คาดไว้")

# แปลงเป็น Excel
df.to_excel("conversation_log.xlsx", index=False, engine='openpyxl')
print("✅ บันทึกเรียบร้อย: conversation_log.xlsx")
