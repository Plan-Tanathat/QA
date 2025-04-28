# analyze_memory.py
import json
import os

MEMORY_FILE = "answer_memory.json"

def load_memory():
    """โหลด memory ทั้งหมด"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def analyze_memory():
    """วิเคราะห์ข้อมูล memory"""
    memory = load_memory()
    total_answers = len(memory)

    if total_answers == 0:
        return "ยังไม่มีข้อมูลการตอบเลยครับ"

    summary_text = f"""
📚 ข้อมูลการตอบ:
- จำนวนคำตอบทั้งหมด: {total_answers}
- ตัวอย่างคำตอบ 5 ข้อแรก:
"""

    # ดึงตัวอย่างคำตอบ (ไม่เกิน 5 ข้อ)
    for i, item in enumerate(memory[:5]):
        summary_text += f"\n  {i+1}. {item['answer']} (เวลา: {item['timestamp']})"

    return summary_text.strip()
