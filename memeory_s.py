# memory_storage.py
import json
import os
from datetime import datetime

MEMORY_FILE = "user_answer_memory.json"

def load_memory():
    """โหลด memory ทั้งหมด"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user_answer(user_answer):
    """บันทึกคำตอบของผู้ใช้ลง memory"""
    memory = load_memory()

    memory.append({
        "timestamp": datetime.now().isoformat(),
        "answer": user_answer
    })

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

    print("✅ บันทึกคำตอบสำเร็จ!")

def get_memory_summary():
    """สรุปจำนวนคำตอบที่มีอยู่"""
    memory = load_memory()
    total_answers = len(memory)

    if total_answers == 0:
        return "ยังไม่มีข้อมูลการตอบเลยครับ"

    latest_answer = memory[-1]["answer"]

    summary = f"""
📚 สรุปข้อมูล:
- จำนวนคำตอบที่เก็บไว้ทั้งหมด: {total_answers}
- คำตอบล่าสุด: "{latest_answer}"
"""
    return summary.strip()
