import json
import os
import re
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

MODEL_NAME = "llama3"

def load_prompts(filepath):
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

# โหลด prompt จาก system_prompt.txt
prompts = load_prompts("system_prompt.txt")

# สร้าง Model และ Prompt Chain
model = OllamaLLM(model=MODEL_NAME, system=prompts["system"])

question_prompt_th = ChatPromptTemplate.from_template(prompts["question_th"])
summary_prompt_th = ChatPromptTemplate.from_template(prompts["summary_th"])
next_question_prompt_th = ChatPromptTemplate.from_template(prompts["next_question_th"])
question_prompt_en = ChatPromptTemplate.from_template(prompts["question_en"])
summary_prompt_en = ChatPromptTemplate.from_template(prompts["summary_en"])
next_question_prompt_en = ChatPromptTemplate.from_template(prompts["next_question_en"])

question_chain_th = question_prompt_th | model
summary_chain_th = summary_prompt_th | model
next_question_chain_th = next_question_prompt_th | model
question_chain_en = question_prompt_en | model
summary_chain_en = summary_prompt_en | model
next_question_chain_en = next_question_prompt_en | model

conversation_log = {
    "conversation": [],
    "summary": "",
    "summary_en": "",
    "season_scores": "",
    "top_season": ""
}

def handle_conversation(num_questions=5):
    context = ""

    print("💬 เริ่มต้นการสนทนาใหม่! พิมพ์ 'exit' เพื่อหยุด\n")

    for i in range(num_questions):
        timestamp = datetime.now().isoformat()

        if i == 0:
            model_question = "Q1 (TH): ถ้าต้องนิยามตัวเองคุณจะนิยามตัวเองว่าอะไร?\nQ1 (EN): How would you describe yourself in one sentence?"
            model_prompt_th = "คำถามเริ่มต้น"
            model_prompt_en = "Initial question without history"
        elif i >= 3:
            model_question_th = next_question_chain_th.invoke({"context": context}).strip()
            model_question_en = next_question_chain_en.invoke({"context": context}).strip()
            model_question = f"Q{i+1} (TH): {model_question_th}\nQ{i+1} (EN): {model_question_en}"
        else:
            model_question_th = question_chain_th.invoke({"context": context}).strip()
            model_question_en = question_chain_en.invoke({"context": context}).strip()
            model_question = f"Q{i+1} (TH): {model_question_th}\nQ{i+1} (EN): {model_question_en}"

        print(f"\n{model_question}")
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

    summary_th = summary_chain_th.invoke({"context": context}).strip()
    summary_en = summary_chain_en.invoke({"context": context}).strip()

    # วิเคราะห์คะแนนฤดู
    score_prompt = prompts["season_scores"].replace("{context}", context)
    season_scores_text = model.invoke(score_prompt).strip()

    # แปลงคะแนนเป็น dict
    season_scores = {}
    for line in season_scores_text.splitlines():
        match = re.match(r"(ฤดู.+?):\s*([0-9]+)", line)
        if match:
            season = match.group(1).strip()
            score = int(match.group(2))
            season_scores[season] = score

    # หาฤดูที่ได้คะแนนสูงสุด
    top_season = max(season_scores.items(), key=lambda x: x[1])[0]
    summary_th += f"\n\n🌤️ ฤดูที่สอดคล้องกับบุคลิกมากที่สุด: **{top_season}**"

    # อัปเดต log
    conversation_log["summary"] = summary_th
    conversation_log["summary_en"] = summary_en
    conversation_log["season_scores"] = season_scores
    conversation_log["top_season"] = top_season

    print("🧠 สรุปบุคลิกภาพ (ภาษาไทย):\n")
    print(summary_th)
    print("\n🧠 Personality Summary (English):\n")
    print(summary_en)
    print("\n🌸 คะแนนฤดู:\n")
    for s, score in season_scores.items():
        print(f"- {s}: {score}")
    print(f"\n🎯 ฤดูเด่นที่สุด: {top_season}")

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

    all_logs.append(conversation_log)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, ensure_ascii=False, indent=2)

    print(f"\n📁 บันทึกลงไฟล์เรียบร้อย: {filename}")


if __name__ == "__main__":
    handle_conversation()
