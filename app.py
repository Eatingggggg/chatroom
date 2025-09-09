import streamlit as st
import gspread
from datetime import datetime, timedelta
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
now = datetime.now(tz).replace(tzinfo=None)  # 轉成 naive datetime

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
    display: flex;
    align-items: center;
}

.avatar-letter {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #999;  /* 頭像背景顏色 */
    color: white;            /* 字體顏色 */
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    margin-right: 8px;
}

.user {
    background-color: #84C1FF;
    margin-left: auto;
    text-align: right;
    flex-direction: row-reverse; /* 自己訊息頭像在右邊 */
}

.other {
    background-color: #ECECEC;
    color: black;
    margin-right: auto;
}
.timestamp {
    font-size: 14px;
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
         user_initial = row['user'][0]  # 取名字第一個字
         if row['user'] == username:
             st.markdown(
                 f"<div class='chat-bubble user'>"
                 f"<div class='avatar-letter'>{user_initial}</div>"
                 f"<div><b>{row['user']}</b><br>{row['message']}"
                 f"<div class='timestamp'>{row['timestamp']}</div></div></div>",
                 unsafe_allow_html=True
             )
         else:
             st.markdown(
                 f"<div class='chat-bubble other'>"
                 f"<div class='avatar-letter'>{user_initial}</div>"
                 f"<div><b>{row['user']}</b><br>{row['message']}"
                 f"<div class='timestamp'>{row['timestamp']}</div></div></div>",
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

# 將 Google Sheet 讀取的 timestamp 轉成 naive datetime
df['timestamp_dt'] = pd.to_datetime(df['timestamp'])#.dt.tz_localize(None)  # 移除時區

# 設定線上判定時間（例如 5 分鐘內）
time_threshold = now - timedelta(minutes=5)

# 篩選在線使用者
online_df = df[df['timestamp_dt'] >= time_threshold]
online_users = online_df['user'].unique().tolist()

st.sidebar.markdown(f"**線上人數：{len(online_users)}**")
st.sidebar.markdown("**線上使用者**")
for u in online_users:
    st.sidebar.write(u)






















