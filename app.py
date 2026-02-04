import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import time

# --- 1. 配置区 ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- 2. 免登录逻辑配置 (3小时) ---
THREE_HOURS = 3 * 60 * 60 

def set_login_cookies(user_id, email):
    """
    通过 JS 注入设置持久化 Cookie。
    注意：线上环境必须带上 path=/ 和 SameSite=Lax。
    """
    expiry_ts = time.time() + THREE_HOURS
    js_code = f"""
    <script>
    (function() {{
        function setCookie(name, value, seconds) {{
            var date = new Date();
            date.setTime(date.getTime() + (seconds * 1000));
            var expires = "; expires=" + date.toUTCString();
            // 确保 path 覆盖整个域名，SameSite 处理跨域刷新
            document.cookie = name + "=" + (value || "")  + expires + "; path=/; SameSite=Lax";
        }}
        setCookie("job_scout_uid", "{user_id}", {THREE_HOURS});
        setCookie("job_scout_email", "{email}", {THREE_HOURS});
        setCookie("job_scout_expiry", "{expiry_ts}", {THREE_HOURS});
        console.log("Persistence success: {user_id}");
    }})();
    </script>
    """
    # 线上环境：使用 html 组件直接渲染，不包裹在 st.empty 中以保证稳定性
    st.components.v1.html(js_code, height=0)

def clear_login_cookies():
    """清除物理 Cookie"""
    js_code = """
    <script>
    document.cookie = "job_scout_uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_expiry=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. 登录态恢复逻辑 ---
# 线上刷新时，st.context.cookies 的获取有时会有延迟，这里做健壮性处理
if "user" not in st.session_state:
    st.session_state.user = None

# 如果当前没登录，尝试从浏览器提取状态
if st.session_state.user is None:
    cookies = st.context.cookies
    c_uid = cookies.get("job_scout_uid")
    c_expiry = cookies.get("job_scout_expiry")
    c_email = cookies.get("job_scout_email")

    if c_uid and c_expiry:
        try:
            if time.time() < float(c_expiry):
                st.session_state.user = type('User', (object,), {
                    'id': c_uid, 
                    'email': c_email if c_email else "User"
                })
        except:
            pass

# --- 4. 身份验证界面 ---
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
                        # 重要：先将信息存入 session_state
                        st.session_state.user = res.user
                        # 触发 JS 写入 Cookie
                        set_login_cookies(res.user.id, res.user.email)
                        
                        # 线上环境修复核心：
                        # 1. 显示成功信息提示
                        st.success("验证通过，正在同步浏览器凭证...")
                        # 2. 强制等待，确保浏览器有足够时间处理 JS Cookie 写入请求
                        time.sleep(1.5) 
                        # 3. 此时再 rerun，Cookie 已经落盘
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

# --- 5. 主程序逻辑 ---
if st.session_state.user is None:
    auth_ui()
else:
    # 侧边栏
    st.sidebar.success(f"已登录: {st.session_state.user.email}")
    st.sidebar.info(f"🔑 你的 User ID:\n\n{st.session_state.user.id}")
    
    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        st.session_state.user = None
        clear_login_cookies()
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

    df = load_my_data(st.session_state.user.id)

    if not df.empty:
        st.subheader("📊 数据概览")
        m1, m2, m3 = st.columns(3)
        m1.metric("总申请数", len(df))
        m2.metric("面试邀约", len(df[df['status'] == 'interviewing']))
        m3.metric("收到 Offer", len(df[df['status'] == 'offer']))

        st.write("---")
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("**状态分布**")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['状态', '数量']
            color_map = {"applied": "#0073b1", "interviewing": "#f39c12", "offer": "#27ae60", "rejected": "#e74c3c", "ghosted": "#95a5a6"}
            fig_pie = px.pie(status_counts, values='数量', names='状态', hole=0.4, color='状态', color_discrete_map=color_map)
            fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.markdown("**投递周趋势**")
            df['week'] = df['dt_object'].dt.to_period('W').apply(lambda r: r.start_time)
            trend_df = df.groupby('week').size().reset_index(name='count')
            trend_df = trend_df.sort_values('week')
            fig_trend = px.bar(trend_df, x='week', y='count', color_discrete_sequence=['#0073b1'])
            fig_trend.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()
        st.subheader("📋 投递明细列表")
        st.dataframe(df[['显示序号', 'formatted_date', 'title', 'company', 'location', 'status']], use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🛠️ 条目管理")
        job_options = df.apply(lambda x: f"序号 {x['显示序号']}: {x['title']} @ {x['company']}", axis=1).tolist()
        sel = st.selectbox("请选择要操作的行:", ["-- 请选择 --"] + job_options)
        
        if sel != "-- 请选择 --":
            display_idx = int(sel.split(':')[0].replace('序号 ', ''))
            row = df[df['显示序号'] == display_idx].iloc[0]
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    t = st.text_input("岗位名称", value=row['title'])
                    s = st.selectbox("状态", ["applied", "interviewing", "offer", "rejected", "ghosted"], 
                                     index=["applied", "interviewing", "offer", "rejected", "ghosted"].index(row['status']))
                with c2:
                    c = st.text_input("公司", value=row['company'])
                    l = st.text_input("地点", value=row['location'])
                desc = st.text_area("描述", value=row['description'], height=150)
                if st.form_submit_button("💾 保存修改"):
                    supabase.table("job_applications").update({"title": t, "company": c, "status": s, "location": l, "description": desc}).eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.rerun()

            if st.button("🗑️ 删除此记录"):
                supabase.table("job_applications").delete().eq("id", row['id']).execute()
                st.cache_data.clear()
                st.rerun()
    else:
        st.info("目前没有数据。请通过插件在领英上抓取！")
