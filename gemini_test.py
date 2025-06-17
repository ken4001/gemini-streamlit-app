import streamlit as st
import pandas as pd
import google.generativeai as genai

# 頁面設定
st.set_page_config(page_title="📊 AI 數據 + Gemini 聊天", layout="wide")
st.markdown("<h1 style='text-align: center;'>📊 數據分析 + 🤖 Gemini AI 聊天</h1>", unsafe_allow_html=True)

# 安全讀取 API 金鑰
try:
    api_key = st.secrets["genai"]["api_key"]
except Exception:
    st.error("❌ 無法取得 API 金鑰，請確認 .streamlit/secrets.toml 設定")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 初始化 session state
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# 內部函式
def add_message(role, content):
    if st.session_state.current_chat is None:
        new_key = f"chat_{len(st.session_state.chat_histories) + 1}"
        st.session_state.current_chat = new_key
        st.session_state.chat_histories[new_key] = []
    st.session_state.chat_histories[st.session_state.current_chat].append({"role": role, "content": content})

# 左右欄位
col1, col2 = st.columns([1, 1])

# ------------------- 📂 CSV 上傳區 -------------------
with col1:
    st.header("📂 CSV 上傳與顯示")
    uploaded_file = st.file_uploader("請上傳 CSV 檔案", type=["csv"])
    df = None
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"檔案 {uploaded_file.name} 讀取成功！")

        if st.checkbox("📑 顯示資料表"):
            st.dataframe(df)

        if st.checkbox("📊 顯示數據摘要"):
            st.markdown("### 數據摘要")
            st.write(f"- 行數：{df.shape[0]}，欄位數：{df.shape[1]}")
            st.write("欄位列表：", df.columns.tolist())
            st.write(df.describe())

# ------------------- 🤖 Gemini 聊天區 -------------------
with col2:
    st.header("🤖 Gemini AI 聊天")

    # 💬 新聊天按鈕，會把 user_input 的第一句當標題
    if st.button("💬 新聊天"):
        if "user_input" in st.session_state and st.session_state.user_input.strip():
            first_line = st.session_state.user_input.strip().split("\n")[0][:30]
            new_key = f"chat_{len(st.session_state.chat_histories) + 1}"
            st.session_state.chat_histories[new_key] = [{"role": "user", "content": st.session_state.user_input}]
            st.session_state.current_chat = new_key
        else:
            st.session_state.current_chat = None
        st.session_state.user_input = ""  # 清空輸入欄

    # 聊天紀錄下拉選單（用第一句話當標題）
    chat_titles = []
    for key, history in st.session_state.chat_histories.items():
        first_user_msg = next((msg["content"] for msg in history if msg["role"] == "user"), None)
        title = first_user_msg[:30] if first_user_msg else "空白對話"
        chat_titles.append((key, title))
    chat_select_map = {title: key for key, title in chat_titles}
    selected_title = st.selectbox("📜 選擇聊天記錄", [""] + [title for _, title in chat_titles], index=0)

    if selected_title:
        st.session_state.current_chat = chat_select_map[selected_title]
    elif st.session_state.current_chat not in st.session_state.chat_histories:
        st.session_state.current_chat = None

    # 顯示目前聊天內容
    chat_log = st.session_state.chat_histories.get(st.session_state.current_chat, []) if st.session_state.current_chat else []
    for msg in chat_log:
        if msg["role"] == "user":
            st.markdown(f"**你:** {msg['content']}")
        else:
            st.markdown(f"**Gemini:** {msg['content']}")

    # 使用者輸入框
    user_input = st.text_area("請輸入你的問題...", height=150, key="user_input")

    if st.button("🚀 送出問題給 Gemini AI"):
        if user_input.strip() == "":
            st.warning("請輸入問題")
        else:
            add_message("user", user_input)

            # 加上數據摘要進 Prompt（若有上傳 CSV）
            prompt = user_input
            if df is not None:
                summary = (
                    f"數據摘要:\n"
                    f"行數：{df.shape[0]}，欄位數：{df.shape[1]}\n"
                    f"欄位名稱：{', '.join(df.columns.tolist())}\n"
                    f"統計資訊：\n{df.describe().to_string()}\n\n"
                )
                prompt = summary + user_input

            # Gemini 回覆
            with st.spinner("Gemini 思考中..."):
                try:
                    response = model.generate_content(prompt)
                    answer = response.text.strip()
                    add_message("assistant", answer)
                    st.success("✅ Gemini 回覆如下：")
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
