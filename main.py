import json
import os
from datetime import datetime
import logging
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import re

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

model_en = OllamaLLM(model="llama3", system="You are an insightful English-language reasoning assistant. Generate clear and thoughtful analysis.")
model_th = OllamaLLM(model="llama3", system="คุณเป็นนักแปลไทยที่แปลอย่างเป็นธรรมชาติและไพเราะ")

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

prompts = load_prompts("system_prompt.txt")

question_prompt_th = ChatPromptTemplate.from_template(prompts["question_th"])
summary_prompt_th = ChatPromptTemplate.from_template(prompts["summary_th"])
next_question_prompt_th = ChatPromptTemplate.from_template(prompts["next_question_th"])
question_prompt_en = ChatPromptTemplate.from_template(prompts["question_en"])
summary_prompt_en = ChatPromptTemplate.from_template(prompts["summary_en"])
next_question_prompt_en = ChatPromptTemplate.from_template(prompts["next_question_en"])

question_chain_th = question_prompt_th | model_th
summary_chain_th = summary_prompt_th | model_th
next_question_chain_th = next_question_prompt_th | model_th
question_chain_en = question_prompt_en | model_en
summary_chain_en = summary_prompt_en | model_en
next_question_chain_en = next_question_prompt_en | model_en

conversation_log = {
    "conversation": [],
    "summary_th": "",
    "summary_en": "",
    "season_scores": {}
}

def extract_question_only(text):
    matches = re.findall(r"([^?.!]{5,200}\?)", text)
    return matches[0].strip() if matches else text.strip()

def extract_season_scores(text):
    pattern = r"(?:score|คะแนน)\s*:\s*(.*?)\s*(?:\n|$)"
    match = re.search(pattern, text)
    if match:
        scores_text = match.group(1)
        pairs = re.findall(r"([\wฤดู]+)\s*(\d{1,3})", scores_text)
        return {name: int(score) for name, score in pairs if int(score) <= 100}
    return {}

def handle_conversation(num_questions=10):
    context = ""
    print("💬 เริ่มต้นการสนทนาใหม่! พิมพ์ 'exit' เพื่อหยุด\n")

    for i in range(num_questions):
        timestamp = datetime.now().isoformat()

        if i == 0:
            model_question = "Q1 (EN): How would you describe yourself in one sentence?"
            model_prompt_en = "Initial question without history"
            model_question_th = model_th.invoke(f"แปลคำถามนี้เป็นไทยให้ฟังดูเป็นธรรมชาติและเป็นมิตร: {model_question}").strip()
        elif i >= 3:
            model_question_en = next_question_chain_en.invoke({"context": context}).strip()
            model_question_th = model_th.invoke(f"แปลคำถามนี้เป็นไทยให้ฟังดูเป็นธรรมชาติและเป็นมิตร: {model_question_en}").strip()
            model_prompt_en = prompts["next_question_en"].replace("{context}", context)
        else:
            model_question_en = question_chain_en.invoke({"context": context}).strip()
            model_question_th = model_th.invoke(f"แปลคำถามนี้เป็นไทยให้ฟังดูเป็นธรรมชาติและเป็นมิตร: {model_question_en}").strip()
            model_prompt_en = prompts["question_en"].replace("{context}", context)

        logging.debug(f"[QUESTION EN] {model_question_en}")
        logging.debug(f"[QUESTION TH] {model_question_th}")

        print(f"Q{i+1} (EN): {model_question_en}")
        print(f"Q{i+1} (TH): {model_question_th}")
        user_answer = input("You: ").strip()

        if user_answer.lower() == "exit":
            print("👋 จบการสนทนาแล้ว")
            break

        logging.debug(f"[USER ANSWER] {user_answer}")
        context += f"\nผู้ใช้: {user_answer}"

        conversation_log["conversation"].append({
            "timestamp": timestamp,
            "model_prompt_en": model_prompt_en,
            "model_question_en": model_question_en,
            "model_question_th": model_question_th,
            "user_answer": user_answer
        })

    print("\n🧠 กำลังวิเคราะห์บุคลิกและอารมณ์จากข้อมูลทั้งหมดที่มี...\n")
    logging.debug("[SUMMARY] Generating summary from context...")

    summary_en = summary_chain_en.invoke({"context": context}).strip()
    summary_th = model_th.invoke(f"กรุณาแปลสรุปนี้ให้เป็นภาษาไทยอย่างเป็นธรรมชาติ:\n\n{summary_en}").strip()

    logging.debug(f"[SUMMARY EN] {summary_en}")
    logging.debug(f"[SUMMARY TH] {summary_th}")

    season_scores = extract_season_scores(summary_th)

    conversation_log["summary_th"] = summary_th
    conversation_log["summary_en"] = summary_en
    conversation_log["season_scores"] = season_scores

    print("🧠 ผลวิเคราะห์ (ภาษาไทย):\n")
    print(summary_th)
    print("\n🧠 Summary (English):\n")
    print(summary_en)

    print("\n📊 คะแนนฤดู:")
    for season, score in season_scores.items():
        print(f"- {season}: {score}")

    save_conversation_to_json()

def save_conversation_to_json(filename="conversation_log.json"):
    logging.debug(f"[SAVE] Saving to {filename}")
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
                logging.warning("⚠️ ไฟล์ว่าง/เสียหาย กำลังเริ่มใหม่...")
                all_logs = []
    else:
        all_logs = []

    all_logs.append(conversation_log)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, ensure_ascii=False, indent=2)

    print(f"\n📁 เพิ่ม session ใหม่เรียบร้อย → บันทึกไว้ที่: {filename}")

if __name__ == "__main__":
    handle_conversation()
