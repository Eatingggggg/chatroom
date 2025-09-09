import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from google.oauth2 import service_account

# Google Sheet 設定
SHEET_NAME = "chatroom"
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
# 從 secrets 讀取 Google Service Account
# creds = ServiceAccountCredentials.from_json_keyfile_dict(
#     st.secrets["gcp_service_account"]), scope
# )
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Streamlit 頁面設定
st.set_page_config(page_title="聊天室", page_icon="💬", layout="wide")
st.title("💬 Streamlit 簡易聊天室")

# 使用者名稱（保存在 session）
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.session_state.username = st.text_input("請輸入你的名字", key="set_user")
    st.stop()

username = st.session_state.username

# 讀取聊天紀錄
messages = sheet.get_all_records()
df = pd.DataFrame(messages)

# 💬 自訂 CSS 美化 + 固定輸入框 + 自動滾動
st.markdown("""
<style>
.chat-container {
    max-height: 70vh;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background-color: #fafafa;
}
.chat-bubble {
    padding: 10px 15px;
    margin: 5px;
    border-radius: 15px;
    max-width: 70%;
    word-wrap: break-word;
}
.user {
    background-color: #DCF8C6;
    margin-left: auto;
    text-align: right;
}
.other {
    background-color: #ECECEC;
    margin-right: auto;
    text-align: left;
}
.timestamp {
    font-size: 10px;
    color: gray;
    margin-top: 3px;
}
.chat-input {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: white;
    padding: 10px;
    border-top: 1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

# 聊天內容區
st.markdown("<div class='chat-container' id='chat-box'>", unsafe_allow_html=True)

if not df.empty:
    for _, row in df.iterrows():
        if row['user'] == username:
            st.markdown(
                f"<div class='chat-bubble user'>"
                f"<b>{row['user']}</b><br>{row['message']}"
                f"<div class='timestamp'>{row['timestamp']}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='chat-bubble other'>"
                f"<b>{row['user']}</b><br>{row['message']}"
                f"<div class='timestamp'>{row['timestamp']}</div></div>",
                unsafe_allow_html=True
            )
else:
    st.info("目前還沒有訊息，快來成為第一個發言的人！")

st.markdown("</div>", unsafe_allow_html=True)

# 📌 JS：自動滾動到底部
st.markdown("""
<script>
var chatBox = document.getElementById("chat-box");
if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}
</script>
""", unsafe_allow_html=True)

# 📌 輸入框固定在底部
with st.form("chat_form", clear_on_submit=True):
    msg = st.text_input("輸入訊息", key="msg", label_visibility="collapsed", placeholder="輸入訊息...")
    submitted = st.form_submit_button("送出")

if submitted and msg:
    sheet.append_row([username, msg, time.strftime("%Y-%m-%d %H:%M:%S")])
    st.experimental_rerun()

# 自動刷新 (每 3 秒)
st.experimental_autorefresh(interval=3000, key="refresh")


