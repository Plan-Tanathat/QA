import os
import streamlit as st
import json
from datetime import datetime
from test import prompts, model, conversation_log

def run_interactive_conversation(num_questions=5):
    context = ""

    st.title("💬 สนทนากับ AI นักวิเคราะห์บุคลิกภาพ")
    st.markdown("ใส่คำตอบในช่องแล้วกด **Enter** หรือปุ่ม **ส่งคำตอบ** เพื่อคุยกับ AI")

    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.history = []
        st.session_state.user_inputs = []
        st.session_state.finished = False

    # ตั้งคำถาม
    if st.session_state.step == 0:
        model_question = "ถ้าต้องนิยามตัวเองคุณจะนิยามตัวเองว่าอะไร?"
        model_prompt_th = "คำถามเริ่มต้น"
        model_prompt_en = "Initial question without history"
    else:
        model_prompt_th = prompts["question_th"].replace("{context}", context)
        model_prompt_en = prompts["question_en"].replace("{context}", context)
        model_question = model.invoke(model_prompt_th).strip()
        print(f"[Q{st.session_state.step + 1}] AI Question:", model_question)

    # แสดงคำถาม
    st.markdown(f"<h3>❓ คำถามที่ {st.session_state.step + 1}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>{model_question}</p>", unsafe_allow_html=True)

    # แบบฟอร์มรับคำตอบ (รองรับ Enter)
    with st.form(key=f"form_{st.session_state.step}"):
        user_input = st.text_input(" ", key=f"input_{st.session_state.step}", label_visibility="collapsed")
        submitted = st.form_submit_button("📤 ส่งคำตอบ")

    # เมื่อส่งคำตอบ
    if submitted and user_input.strip() != "":
        print(f"[A{st.session_state.step}] User Answer:", user_input.strip())

        timestamp = datetime.now().isoformat()
        context_so_far = "\n".join([f"ผู้ใช้: {x}" for x in st.session_state.user_inputs])

        st.session_state.history.append({
            "timestamp": timestamp,
            "model_prompt": model_prompt_th,
            "model_prompt_en": model_prompt_en,
            "model_question": model_question,
            "user_answer": user_input.strip()
        })

        st.session_state.user_inputs.append(user_input.strip())
        st.session_state.step += 1

        if st.session_state.step >= num_questions:
            st.session_state.finished = True

        st.rerun()

    # แสดงปุ่มวิเคราะห์หลังครบ
    if st.session_state.finished and not st.session_state.get("confirmed_end", False):
        st.subheader("✅ คุณตอบครบ 5 ข้อแล้ว")
        if st.button("🔍 พอแค่นี้ แล้ววิเคราะห์เลย"):
            st.session_state.confirmed_end = True
            st.rerun()

    # สรุป + บันทึกอัตโนมัติ
    if st.session_state.finished and st.session_state.get("confirmed_end", True):
        context = "\n".join([f"ผู้ใช้: {x}" for x in st.session_state.user_inputs])
        summary_th = model.invoke(prompts["summary_th"].replace("{context}", context)).strip()
        summary_en = model.invoke(prompts["summary_en"].replace("{context}", context)).strip()

        conversation_log["conversation"] = st.session_state.history
        conversation_log["summary"] = summary_th
        conversation_log["summary_en"] = summary_en

        st.subheader("🧠 สรุปบุคลิกภาพ (ภาษาไทย):")
        st.success(summary_th)

        st.subheader("🧠 Personality Summary (English):")
        st.info(summary_en)

        # บันทึก JSON
        filename = "conversation_log.json"
        all_logs = []

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    if isinstance(existing_data, dict):
                        all_logs = [existing_data]
                    elif isinstance(existing_data, list):
                        all_logs = existing_data
                except json.JSONDecodeError:
                    all_logs = []

        all_logs.append(conversation_log)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)

        st.success("📁 บันทึกอัตโนมัติแล้วที่: conversation_log.json")

run_interactive_conversation()
