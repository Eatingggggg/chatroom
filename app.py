import streamlit as st
import gspread
from datetime import datetime
import pandas as pd
import time
from google.oauth2.service_account import Credentials
import pytz
from streamlit_autorefresh import st_autorefresh

# 自動刷新 (每 3 秒)
st_autorefresh(interval=10000, key="chat_refresh")

# 設定時區，例如台北
tz = pytz.timezone("Asia/Taipei")

# # 取得當前時間
# now = datetime.now(tz)

# Google Sheet 設定
SHEET_NAME = "chatroom"
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]


creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Streamlit 頁面設定
st.set_page_config(page_title="聊天室", page_icon="💬", layout="wide")
st.title("💬 Streamlit 簡易聊天室")

# 使用者名稱（保存在 session）
# if "username" not in st.session_state:
#     st.session_state.username = ""

# if not st.session_state.username:
#     st.session_state.username = st.text_input("請輸入你的名字", key="set_user")
#     st.stop()
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.username == "":
    username_input = st.text_input("請輸入你的名字")
    if username_input:
        st.session_state.username = username_input
    st.stop()

username = st.session_state.username

# 讀取聊天紀錄
# messages = sheet.get_all_records()
# df = pd.DataFrame(messages)
df = pd.DataFrame(sheet.get_all_records())
df = df.tail(50)  # 只顯示最後 50 筆

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
    color: white;  /* 預設文字顏色白色 */
}
.user {
    background-color: #84C1FF;  /* 自己輸入訊息顏色 */
    color: black;
    margin-left: auto;
    text-align: right;
}
.other {
    background-color: #ECECEC;  /* 他人訊息顏色 */
    color: black;  /* 他人訊息文字顏色黑色 */
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
         # 取得當前時間
         now = datetime.now(tz)
         # 寫入 Google Sheet
         sheet.append_row([username, msg, now.strftime("%Y-%m-%d %H:%M:%S")])
         
         # 更新 session_state 訊息數量，用於觸發重新渲染
         st.session_state['last_update'] = time.time()
last_update = st.session_state.get('last_update', None)












