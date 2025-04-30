import json
import os
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

MODEL_NAME = "llama3"
model = OllamaLLM(
    model=MODEL_NAME
)

question_template = """
จากประวัติการตอบคำถามของผู้ใช้ดังนี้:

{context}

กรุณาสร้าง "คำถามใหม่ภาษาไทย" จำนวน 1 ข้อ
ที่เกี่ยวข้องกับนิสัย ความรู้สึก หรือบุคลิกภาพของผู้ใช้
คำถามต้องกระชับ ตรงประเด็น และไม่เกิน 1 ประโยค
"""

summary_template = """
จากข้อมูลการสนทนาทั้งหมดนี้:

{context}

ช่วยสรุปลักษณะนิสัย อารมณ์ และบุคลิกภาพของผู้ใช้
สรุปเป็นภาษาไทย กระชับไม่เกิน 5 บรรทัด
"""

question_prompt = ChatPromptTemplate.from_template(question_template)
summary_prompt = ChatPromptTemplate.from_template(summary_template)

question_chain = question_prompt | model
summary_chain = summary_prompt | model

conversation_log = {
    "questions": [],
    "answers": [],
    "ollama_generated_questions": [],
    "summary": "",
    "all_answers": [],  # ✅ เก็บคำตอบทั้งหมดในที่เดียว
    "model_thoughts": {
        "question_generation": [],
        "summary_generation": {}
    }
}

def handle_conversation(num_questions=5):
    context = ""

    print("💬 เริ่มต้นการสนทนาใหม่! กรุณาตอบตามความรู้สึกจริง พิมพ์ 'exit' เพื่อหยุด\n")

    for i in range(num_questions):
        if i == 0:
            user_question = "ถ้าต้องเลือกหนึ่งคำที่อธิบายตัวคุณวันนี้ จะเลือกคำว่าอะไร?"
        else:
            prompt_text = question_template.replace("{context}", context)
            user_question = model.invoke(prompt_text).strip()

            conversation_log["model_thoughts"]["question_generation"].append({
                "prompt": prompt_text,
                "response": user_question
            })
            conversation_log["ollama_generated_questions"].append(user_question)

        print(f"Q{i+1}: {user_question}")
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("👋 จบการสนทนาแล้ว")
            break

        # เพิ่มคำตอบลง context และ log
        context += f"\nผู้ใช้: {user_input}"
        conversation_log["questions"].append(user_question)
        conversation_log["answers"].append(user_input)

        # ✅ เพิ่มคำตอบพร้อม timestamp ไว้ใน all_answers
        conversation_log["all_answers"].append({
            "timestamp": datetime.now().isoformat(),
            "answer": user_input
        })

    print("\n🧠 กำลังวิเคราะห์บุคลิกและอารมณ์จากข้อมูลทั้งหมดที่มี...\n")

    summary_prompt_text = summary_template.replace("{context}", context)
    summary = model.invoke(summary_prompt_text).strip()

    conversation_log["model_thoughts"]["summary_generation"] = {
        "prompt": summary_prompt_text,
        "response": summary
    }

    conversation_log["summary"] = summary

    print("🧠 ผลวิเคราะห์บุคลิก/อารมณ์ของคุณ:\n")
    print(summary)

    save_conversation_to_json()

def save_conversation_to_json(filename="conversation_log.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(conversation_log, f, ensure_ascii=False, indent=2)
    print(f"\n📁 บันทึกข้อมูลทั้งหมดไว้ที่ไฟล์: {filename}")

if __name__ == "__main__":
    handle_conversation()
