import json
import os
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

MODEL_NAME = "llama3"

def load_prompts(filepath):
    """โหลดทุก prompt จากไฟล์เดียว"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}
    current_key = None
    buffer = []

    for line in content.splitlines():
        if line.startswith("===") and line.endswith("==="):
            if current_key and buffer:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = line.strip("=").strip()
            buffer = []
        else:
            buffer.append(line)
    if current_key and buffer:
        sections[current_key] = "\n".join(buffer).strip()

    return sections

# โหลด prompt ทั้งหมดจากไฟล์เดียว
prompts = load_prompts("system_prompt.txt")

model = OllamaLLM(model=MODEL_NAME, system=prompts["system"])

# ใช้ template
question_prompt_th = ChatPromptTemplate.from_template(prompts["question_th"])
summary_prompt_th = ChatPromptTemplate.from_template(prompts["summary_th"])
question_prompt_en = ChatPromptTemplate.from_template(prompts["question_en"])
summary_prompt_en = ChatPromptTemplate.from_template(prompts["summary_en"])

# Chain
question_chain_th = question_prompt_th | model
summary_chain_th = summary_prompt_th | model
question_chain_en = question_prompt_en | model
summary_chain_en = summary_prompt_en | model

conversation_log = {
    "conversation": [],
    "summary": "",
    "summary_en": ""
}

def handle_conversation(num_questions=5):
    context = ""

    print("💬 เริ่มต้นการสนทนาใหม่! พิมพ์ 'exit' เพื่อหยุด\n")

    for i in range(num_questions):
        timestamp = datetime.now().isoformat()

        if i == 0:
            model_question = "ถ้าต้องนิยามตัวเองคุณจะนิยามตัวเองว่าอะไร?"
            model_prompt_th = "คำถามเริ่มต้น"
            model_prompt_en = "Initial question without history"
        else:
            model_prompt_th = prompts["question_th"].replace("{context}", context)
            model_prompt_en = prompts["question_en"].replace("{context}", context)
            model_question = model.invoke(model_prompt_th).strip()

        print(f"Q{i+1}: {model_question}")
        user_answer = input("You: ").strip()

        if user_answer.lower() == "exit":
            print("👋 จบการสนทนาแล้ว")
            break

        context += f"\nผู้ใช้: {user_answer}"

        conversation_log["conversation"].append({
            "timestamp": timestamp,
            "model_prompt": model_prompt_th,
            "model_prompt_en": model_prompt_en,
            "model_question": model_question,
            "user_answer": user_answer
        })

    print("\n🧠 กำลังวิเคราะห์บุคลิกและอารมณ์จากข้อมูลทั้งหมดที่มี...\n")

    summary_th = model.invoke(prompts["summary_th"].replace("{context}", context)).strip()
    summary_en = model.invoke(prompts["summary_en"].replace("{context}", context)).strip()

    conversation_log["summary"] = summary_th
    conversation_log["summary_en"] = summary_en

    print("🧠 ผลวิเคราะห์ (ไทย):\n")
    print(summary_th)
    print("\n🧠 Summary (English):\n")
    print(summary_en)

    save_conversation_to_json()

def save_conversation_to_json(filename="conversation_log.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                if isinstance(existing_data, dict):
                    all_logs = [existing_data]
                elif isinstance(existing_data, list):
                    all_logs = existing_data
                else:
                    all_logs = []
            except json.JSONDecodeError:
                print("⚠️ ไฟล์ว่าง/เสียหาย กำลังเริ่มใหม่...")
                all_logs = []
    else:
        all_logs = []

    # Add New session
    all_logs.append(conversation_log)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, ensure_ascii=False, indent=2)

    print(f"\n📁 เพิ่ม session ใหม่เรียบร้อย → บันทึกไว้ที่: {filename}")


if __name__ == "__main__":
    handle_conversation()
