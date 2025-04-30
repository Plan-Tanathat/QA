# analyze_logs.py
import json
import os
from collections import Counter
from datetime import datetime

LOG_FOLDER = "logs"

# คำที่ใช้วิเคราะห์แนวโน้มเบื้องต้น
positive_keywords = ["ดี", "ชอบ", "สนุก", "พอใจ", "มีพลัง", "ตื่นเต้น", "สงบ", "รัก"]
negative_keywords = ["เครียด", "เหนื่อย", "กดดัน", "เบื่อ", "ไม่มีแรง", "โกรธ", "เศร้า", "สับสน"]

def load_all_conversations():
    data = []
    for file in os.listdir(LOG_FOLDER):
        if file.endswith(".json"):
            path = os.path.join(LOG_FOLDER, file)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    log = json.load(f)
                    if "conversation" in log:
                        data.extend(log["conversation"])
                except Exception as e:
                    print(f"❌ อ่านไฟล์ {file} ไม่ได้: {e}")
    return data

def analyze_behavior(conversations):
    total = len(conversations)
    if total == 0:
        print("❗ ไม่พบข้อมูลใน logs/")
        return

    word_counter = Counter()
    pos_count = 0
    neg_count = 0
    neutral_count = 0
    total_words = 0
    longest_answer = ""
    timestamps = []

    for entry in conversations:
        answer = entry["user_answer"]
        words = answer.split()
        word_counter.update(words)
        total_words += len(words)
        timestamps.append(entry["timestamp"])

        # วิเคราะห์แนวโน้มอารมณ์
        lowered = answer.lower()
        if any(word in lowered for word in positive_keywords):
            pos_count += 1
        elif any(word in lowered for word in negative_keywords):
            neg_count += 1
        else:
            neutral_count += 1

        if len(answer) > len(longest_answer):
            longest_answer = answer

    avg_length = total_words / total if total else 0
    common_words = word_counter.most_common(10)

    print(f"\n📊 สรุปผลจาก {total} ข้อความ ({len(set(timestamps))} session):\n")
    print(f"- ความยาวเฉลี่ยของคำตอบ: {avg_length:.2f} คำ")
    print(f"- คำที่ใช้บ่อยที่สุด: {[w for w, _ in common_words]}")
    print(f"- แนวโน้มคำตอบ:")
    print(f"    • เชิงบวก: {pos_count} ครั้ง")
    print(f"    • เชิงลบ: {neg_count} ครั้ง")
    print(f"    • เป็นกลาง: {neutral_count} ครั้ง")
    print(f"- คำตอบที่ยาวที่สุด:\n  \"{longest_answer}\"")

if __name__ == "__main__":
    print("🔍 กำลังวิเคราะห์ conversation logs...")
    all_data = load_all_conversations()
    analyze_behavior(all_data)
