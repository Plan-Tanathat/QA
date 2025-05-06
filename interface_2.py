import os
import json
import re
from datetime import datetime
import streamlit as st
from main import prompts, model, conversation_log
from main import question_chain_th, question_chain_en, summary_chain_th, summary_chain_en

def extract_question_only(text):
    matches = re.findall(r"([^?.!]{5,200}\?)", text)
    return matches[0].strip() if matches else text.strip()

def extract_top_season(score_text):
    season_scores = {}
    for line in score_text.splitlines():
        match = re.match(r"(ฤดู.+?\(.*?\)):\s*([0-9]+)", line)
        if match:
            season = match.group(1).strip()
            score = int(match.group(2))
            season_scores[season] = score
    top_season = max(season_scores.items(), key=lambda x: x[1])[0] if season_scores else ""
    return season_scores, top_season

def run_interactive_conversation(num_questions=5):
    context = ""

    st.title("💬 Chat with a Personality Analysis AI")
    st.markdown("Just type your answer in the box and hit Submit Answer to start chatting with the AI")

    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.history = []
        st.session_state.user_inputs = []
        st.session_state.finished = False
        st.session_state.confirmed_end = False

    if not st.session_state.confirmed_end:
        if st.session_state.step == 0:
            model_question_th = "ถ้าต้องนิยามตัวเองคุณจะนิยามตัวเองว่าอย่างไร?"
            model_question_en = "If you had to define yourself in one sentence, what would it be?"
            model_prompt_th = "คำถามเริ่มต้น"
            model_prompt_en = "Initial question without history"
        else:
            context = "\n".join([f"ผู้ใช้: {x}" for x in st.session_state.user_inputs])
            full_th = question_chain_th.invoke({"context": context}).strip()
            full_en = question_chain_en.invoke({"context": context}).strip()
            model_question_th = extract_question_only(full_th)
            model_question_en = extract_question_only(full_en)
            model_prompt_th = prompts["question_th"].replace("{context}", context)
            model_prompt_en = prompts["question_en"].replace("{context}", context)

        st.markdown(f"<h3>❓ คำถามที่ {st.session_state.step + 1}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 20px;'>❓ <b>คำถาม (TH):</b> {model_question_th}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px;'>🌐 <b>Question (EN):</b> {model_question_en}</p>", unsafe_allow_html=True)

        with st.form(key=f"form_{st.session_state.step}"):
            user_input = st.text_input(" ", key=f"input_{st.session_state.step}", label_visibility="collapsed")
            submitted = st.form_submit_button("📤 ส่งคำตอบ")

        if submitted and user_input.strip() != "":
            timestamp = datetime.now().isoformat()
            st.session_state.history.append({
                "timestamp": timestamp,
                "model_prompt": model_prompt_th,
                "model_prompt_en": model_prompt_en,
                "model_question_th": model_question_th,
                "model_question_en": model_question_en,
                "user_answer": user_input.strip()
            })

            st.session_state.user_inputs.append(user_input.strip())
            st.session_state.step += 1

            if st.session_state.step >= num_questions:
                st.session_state.finished = True

            st.rerun()

        if st.session_state.finished:
            if st.button("🔍 พอแค่นี้ แล้ววิเคราะห์เลย"):
                st.session_state.confirmed_end = True
                st.rerun()

    if st.session_state.confirmed_end:
        context = "\n".join([f"ผู้ใช้: {x}" for x in st.session_state.user_inputs])
        summary_th = summary_chain_th.invoke({"context": context}).strip()
        summary_en = summary_chain_en.invoke({"context": context}).strip()

        score_prompt = prompts["season_scores"].replace("{context}", context)
        season_scores_text = model.invoke(score_prompt).strip()
        season_scores, top_season = extract_top_season(season_scores_text)

        summary_th += f"\n\n🌤️ ฤดูที่สอดคล้องกับบุคลิกภาพมากที่สุด: **{top_season}**"

        conversation_log["conversation"] = st.session_state.history
        conversation_log["summary"] = summary_th
        conversation_log["summary_en"] = summary_en
        conversation_log["season_scores"] = season_scores
        conversation_log["top_season"] = top_season

        # 🎯 ผลวิเคราะห์
        st.subheader("🎯 ฤดูเด่นที่สุด (Top Season):")
        st.success(top_season)

        image_path = f"img/{top_season}.png"
        if os.path.exists(image_path):
            st.image(image_path, caption=f"🌸 บุคลิกของคุณคือ {top_season}", use_container_width=True)

        else:
            st.warning(f"🔍 ไม่พบภาพสำหรับฤดู: {top_season}")

        st.subheader("🧠 สรุปบุคลิกภาพ (ภาษาไทย):")
        st.success(summary_th)

        st.subheader("🧠 Personality Summary (English):")
        st.info(summary_en)

        st.subheader("🌸 คะแนนฤดู (Season Scores):")
        for season, score in season_scores.items():
            st.markdown(f"- **{season}**: {score}")

        st.divider()
        st.subheader("🕘 ประวัติคำถาม-คำตอบย้อนหลัง")
        for entry in st.session_state.history[:-1]:  # ตัดคำถามล่าสุด
            st.markdown(f"**❓ {entry['model_question_th']}**")
            st.markdown(f"💬 _{entry['user_answer']}_")

        # Save JSON
        filename = "conversation_log.json"
        all_logs = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    all_logs = [existing_data] if isinstance(existing_data, dict) else existing_data
                except json.JSONDecodeError:
                    all_logs = []

        all_logs.append(conversation_log)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)

        st.success("📁 บันทึกอัตโนมัติแล้วที่: conversation_log.json")

run_interactive_conversation()