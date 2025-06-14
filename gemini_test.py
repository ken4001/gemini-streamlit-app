# app.py
import streamlit as st
import google.generativeai as genai

# ✅ 設定 API 金鑰（請替換）
genai.configure(api_key="AIzaSyCCdzozwXKJZAQp2N-2a7dRGIyjIsjnyLQ")

# ✅ 使用 gemini-1.5-flash 模型
model = genai.GenerativeModel('gemini-1.5-flash')

# ✅ 建立簡單的介面
st.set_page_config(page_title="💬 Gemini 聊天機器人")
st.title("🤖 Gemini Chat App")

user_input = st.text_area("請輸入你的問題", height=150)

if st.button("🚀 送出"):
    if user_input.strip() == "":
        st.warning("⚠️ 請輸入問題再按送出")
    else:
        with st.spinner("AI 回覆中，請稍候..."):
            try:
                response = model.generate_content(user_input)
                st.success("✅ Gemini 回覆如下：")
                st.write(response.text)
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")
