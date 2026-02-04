import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import time

# --- 配置区 (从 Secrets 读取) --- 
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- 3 小时免登录逻辑处理 ---
THREE_HOURS = 3 * 60 * 60  # 10800 秒

def get_session():
    """检查并获取当前会话"""
    # 1. 先看内存 session_state 是否有有效用户
    if "user" in st.session_state and st.session_state.user:
        if time.time() - st.session_state.get("login_time", 0) < THREE_HOURS:
            return st.session_state.user
    
    # 2. 如果内存没有，尝试从浏览器 Cookie 读取 (Streamlit 1.30+ 官方支持)
    # 注意：st.context.cookies 是只读的，写入需要通过 st.rerun 或前端脚本
    cookie_user_id = st.context.cookies.get("job_scout_uid")
    cookie_expiry = st.context.cookies.get("job_scout_expiry")
    
    if cookie_user_id and cookie_expiry:
        if time.time() < float(cookie_expiry):
            # 这里构造一个简单的 user 对象保持逻辑兼容
            user_obj = type('User', (object,), {
                'id': cookie_user_id, 
                'email': st.context.cookies.get("job_scout_email", "User")
            })
            st.session_state.user = user_obj
            st.session_state.login_time = float(cookie_expiry) - THREE_HOURS
            return user_obj
            
    return None

# --- 身份验证界面 ---
def auth_ui():
    st.title("🔐 登录中心")
    tab1, tab2 = st.tabs(["用户登录", "新用户注册"])
    
    with tab1:
        with st.form("login_form"):
            e = st.text_input("邮箱")
            p = st.text_input("密码", type="password")
            submit = st.form_submit_button("立即登录")
            
            if submit:
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                    if res.user:
                        expiry_timestamp = time.time() + THREE_HOURS
                        # 将登录信息存入 session_state
                        st.session_state.user = res.user
                        st.session_state.login_time = time.time()
                        
                        # 注入一段简单的 JavaScript 来设置浏览器 Cookie，实现跨刷新持久化
                        # 这里的 cookie 会保存 3 小时
                        js = f"""
                        <script>
                        function setCookie(name, value, seconds) {{
                            var expires = "";
                            if (seconds) {{
                                var date = new Date();
                                date.setTime(date.getTime() + (seconds * 1000));
                                expires = "; expires=" + date.toUTCString();
                            }}
                            document.cookie = name + "=" + (value || "")  + expires + "; path=/";
                        }}
                        setCookie("job_scout_uid", "{res.user.id}", {THREE_HOURS});
                        setCookie("job_scout_email", "{res.user.email}", {THREE_HOURS});
                        setCookie("job_scout_expiry", "{expiry_timestamp}", {THREE_HOURS});
                        </script>
                        """
                        st.components.v1.html(js, height=0)
                        time.sleep(0.5) # 给 cookie 写入一点时间
                        st.rerun()
                except Exception as ex:
                    st.error(f"登录失败: {str(ex)}")

    with tab2:
        with st.form("signup_form"):
            ne = st.text_input("新邮箱")
            np = st.text_input("设置密码 (至少6位)")
            if st.form_submit_button("提交注册"):
                try:
                    supabase.auth.sign_up({"email": ne, "password": np})
                    st.success("注册成功！请直接登录")
                except Exception as ex:
                    st.error(f"注册失败: {str(ex)}")

# --- 主程序逻辑 ---
current_user = get_session()

if current_user is None:
    auth_ui()
else:
    # 侧边栏
    st.sidebar.success(f"已登录: {current_user.email}")
    
    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        # 清除内存状态
        st.session_state.user = None
        # 清除 Cookie (通过设置过期时间为过去)
        js_logout = """
        <script>
        document.cookie = "job_scout_uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "job_scout_email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "job_scout_expiry=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        </script>
        """
        st.components.v1.html(js_logout, height=0)
        time.sleep(0.5)
        st.rerun()

    st.title("💼 我的申请追踪看板")

    @st.cache_data(ttl=2)
    def load_my_data(uid):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d %H:00')
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                df.insert(0, '显示序号', df.index)
            return df
        except Exception as ex:
            return pd.DataFrame()

    df = load_my_data(current_user.id)

    if not df.empty:
        # --- 这里保持你原来的看板布局功能不变 ---
        st.subheader("📊 数据概览")
        m1, m2, m3 = st.columns(3)
        m1.metric("总申请数", len(df))
        m2.metric("面试邀约", len(df[df['status'] == 'interviewing']))
        m3.metric("收到 Offer", len(df[df['status'] == 'offer']))

        st.divider()
        st.subheader("📋 投递明细列表")
        st.dataframe(df[['显示序号', 'formatted_date', 'title', 'company', 'location', 'status']], use_container_width=True, hide_index=True)
        
        # ... (管理、删除、更新等后续代码保持不变) ...
        # 注意：为了回复简洁，此处省略了你原本的 Plotly 图表和管理表单部分，
        # 实际操作时，请确保这部分代码在 current_user 登录成功的大括号内。
        # 你原本的编辑功能和图表代码直接接在后面即可。
    else:
        st.info("目前没有数据。请通过插件在领英上抓取！")
