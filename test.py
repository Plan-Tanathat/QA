import json
import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# เลือกโมเดล
MODEL_NAME = "llama3"

# โหลดโมเดล
model = OllamaLLM(model=MODEL_NAME)

# Template สำหรับสร้างคำถาม (ภาษาไทย)
question_template = """
จากประวัติการตอบคำถามของผู้ใช้ดังนี้:

{context}

กรุณาสร้าง "คำถามใหม่ภาษาไทย" จำนวน 1 ข้อ
ที่เกี่ยวข้องกับนิสัย ความรู้สึก หรือบุคลิกภาพของผู้ใช้
คำถามต้องกระชับ ตรงประเด็น และไม่เกิน 1 ประโยค
"""

# Template สำหรับสรุปผลวิเคราะห์ (ภาษาไทย)
summary_template = """
จากข้อมูลการสนทนาทั้งหมดนี้:

{context}

ช่วยสรุปลักษณะนิสัย อารมณ์ และบุคลิกภาพของผู้ใช้
สรุปเป็นภาษาไทย กระชับไม่เกิน 5 บรรทัด
"""

# เตรียม prompt templates
question_prompt = ChatPromptTemplate.from_template(question_template)
summary_prompt = ChatPromptTemplate.from_template(summary_template)

question_chain = question_prompt | model
summary_chain = summary_prompt | model

# เก็บข้อมูลทั้งหมด
conversation_log = {
    "questions": [],
    "answers": [],
    "ollama_generated_questions": [],
    "summary": "",
    "model_thoughts": {
        "question_generation": [],
        "summary_generation": {}
    }
}

def load_previous_conversation(filename="conversation_log.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    return None

def handle_conversation(num_questions=5):
    old_data = load_previous_conversation()
    context = ""

    if old_data:
        print("🗂️ เจอข้อมูลการสนทนาเก่า กำลังนำมาใช้ต่อยอด...")
        for q, a in zip(old_data.get("questions", []), old_data.get("answers", [])):
            context += f"\nผู้ใช้: {a}"
        conversation_log["questions"].extend(old_data.get("questions", []))
        conversation_log["answers"].extend(old_data.get("answers", []))
        conversation_log["ollama_generated_questions"].extend(old_data.get("ollama_generated_questions", []))
        conversation_log["model_thoughts"]["question_generation"].extend(old_data.get("model_thoughts", {}).get("question_generation", []))

    print("💬 เริ่มต้นการสนทนาใหม่! กรุณาตอบตามความรู้สึกจริง พิมพ์ 'exit' เพื่อหยุด\n")

    for i in range(num_questions):
        if i == 0 and not context:
            user_question = "ถ้าต้องเลือกหนึ่งคำที่อธิบายตัวคุณวันนี้ จะเลือกคำว่าอะไร?"
        else:
            # เตรียม prompt ที่ส่งเข้าไป
            prompt_text = question_template.replace("{context}", context)
            user_question = model.invoke(prompt_text).strip()

            # เก็บสิ่งที่ Model คิดและตอบ
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

        context += f"\nผู้ใช้: {user_input}"
        conversation_log["questions"].append(user_question)
        conversation_log["answers"].append(user_input)

    print("\n🧠 กำลังวิเคราะห์บุคลิกและอารมณ์จากข้อมูลทั้งหมดที่มี...\n")

    # เตรียม prompt สรุป
    summary_prompt_text = summary_template.replace("{context}", context)
    summary = model.invoke(summary_prompt_text).strip()

    # เก็บสิ่งที่ Model คิดตอนสรุป
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
