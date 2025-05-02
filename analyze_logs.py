# analyze_logs.py
import json
from collections import Counter
from datetime import datetime

LOG_FILE = "conversation_log.json"

# คำที่ใช้วิเคราะห์แนวโน้มเบื้องต้น
positive_keywords = ["ดี", "ชอบ", "สนุก", "พอใจ", "มีพลัง", "ตื่นเต้น", "สงบ", "รัก"]
negative_keywords = ["เครียด", "เหนื่อย", "กดดัน", "เบื่อ", "ไม่มีแรง", "โกรธ", "เศร้า", "สับสน"]

def load_all_conversations():
    if not LOG_FILE.endswith(".json"):
        raise ValueError("LOG_FILE ควรเป็นชื่อไฟล์ .json ไม่ใช่โฟลเดอร์")

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ โหลดไฟล์ไม่ได้: {e}")
        return []

def analyze_behavior(sessions):
    all_entries = []
    word_counter = Counter()
    pos_count = neg_count = neutral_count = total_words = 0
    longest_answer = ""

    for session in sessions:
        conv = session.get("conversation", [])
        for entry in conv:
            answer = entry["user_answer"]
            words = answer.split()
            word_counter.update(words)
            total_words += len(words)

            lowered = answer.lower()
            if any(word in lowered for word in positive_keywords):
                pos_count += 1
            elif any(word in lowered for word in negative_keywords):
                neg_count += 1
            else:
                neutral_count += 1

            if len(answer) > len(longest_answer):
                longest_answer = answer

            all_entries.append(entry)

    total = len(all_entries)
    avg_length = total_words / total if total else 0
    common_words = word_counter.most_common(10)

    print(f"\n📊 วิเคราะห์ทั้งหมด {len(sessions)} session ({total} คำตอบ):\n")
    print(f"- ความยาวเฉลี่ยของคำตอบ: {avg_length:.2f} คำ")
    print(f"- คำที่ใช้บ่อยที่สุด: {[w for w, _ in common_words]}")
    print(f"- แนวโน้มคำตอบ:")
    print(f"    • เชิงบวก: {pos_count} ครั้ง")
    print(f"    • เชิงลบ: {neg_count} ครั้ง")
    print(f"    • เป็นกลาง: {neutral_count} ครั้ง")
    print(f"- คำตอบที่ยาวที่สุด:\n  \"{longest_answer}\"")

    print("\n🧠 สรุปภาษาไทยจากแต่ละ session:")
    for i, session in enumerate(sessions, 1):
        print(f"\n📌 Session {i}:")
        print(f"📅 เวลา: {session['conversation'][0]['timestamp']}")
        print("📝 Summary (TH):", session.get("summary", "[ไม่มี]"))
        print("🌐 Summary (EN):", session.get("summary_en", "[ไม่มี]"))

if __name__ == "__main__":
    print("🔍 กำลังวิเคราะห์ conversation logs...")
    all_sessions = load_all_conversations()
    analyze_behavior(all_sessions)
