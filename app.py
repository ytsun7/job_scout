import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import pytz 

# --- 配置区 ---
URL = "https://ucabuiwtvhpyqehaytxj.supabase.co"
KEY = "sb_publishable_qRsPp469HJzOmpTc-KM-QQ_dNGZoKRj"

# [修改点 1] 删除手动配置的 LOCAL_TIMEZONE，改为后续动态获取

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- Cookie 与时区管理逻辑 ---
THREE_HOURS = 3 * 60 * 60  # 10800 秒

def set_login_cookies(user_id, email):
    """通过 JS 注入设置身份验证 Cookie"""
    expiry_ts = time.time() + THREE_HOURS
    js_code = f"""
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
    setCookie("job_scout_uid", "{user_id}", {THREE_HOURS});
    setCookie("job_scout_email", "{email}", {THREE_HOURS});
    setCookie("job_scout_expiry", "{expiry_ts}", {THREE_HOURS});
    </script>
    """
    st.components.v1.html(js_code, height=0)

def clear_login_cookies():
    """清除浏览器 Cookie"""
    js_code = """
    <script>
    document.cookie = "job_scout_uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_expiry=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_timezone=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    </script>
    """
    st.components.v1.html(js_code, height=0)

def ensure_timezone_cookie():
    """
    [修改点 2] 自动检测浏览器时区
    如果 Cookie 中没有时区信息，则注入 JS 获取浏览器时区并写入 Cookie。
    """
    # 尝试从 cookie 获取时区
    tz_cookie = st.context.cookies.get("job_scout_timezone")
    
    if not tz_cookie:
        # 如果没有找到 cookie，注入 JS 获取浏览器时区
        # Intl.DateTimeFormat().resolvedOptions().timeZone 会返回如 'Asia/Shanghai'
        js_code = """
        <script>
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.cookie = "job_scout_timezone=" + tz + "; path=/; max-age=31536000";
        </script>
        """
        st.components.v1.html(js_code, height=0)
        return 'UTC' # 首次加载尚未写入，暂时默认 UTC
    return tz_cookie

# --- 初始化 Session State 逻辑 ---
if "user" not in st.session_state:
    c_uid = st.context.cookies.get("job_scout_uid")
    c_email = st.context.cookies.get("job_scout_email")
    c_expiry = st.context.cookies.get("job_scout_expiry")

    if c_uid and c_expiry and time.time() < float(c_expiry):
        st.session_state.user = type('User', (object,), {'id': c_uid, 'email': c_email})
    else:
        st.session_state.user = None

# 获取当前用户时区 (需要在页面加载早期执行)
current_user_timezone = ensure_timezone_cookie()

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
                        st.session_state.user = res.user
                        set_login_cookies(res.user.id, res.user.email)
                        time.sleep(0.5) 
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
if st.session_state.user is None:
    auth_ui()
else:
    st.sidebar.success(f"已登录: {st.session_state.user.email}")
    st.sidebar.info(f"🔑 你的 User ID (用于插件):\n\n{st.session_state.user.id}")
    
    # 可选：在侧边栏显示当前检测到的时区，方便调试
    # st.sidebar.caption(f"当前显示时区: {current_user_timezone}")

    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        st.session_state.user = None
        clear_login_cookies()
        time.sleep(0.5)
        st.rerun()

    st.title("💼 我的申请追踪看板")

    # [修改点 3] 将时区作为参数传入，避免缓存使用了旧时区
    @st.cache_data(ttl=2)
    def load_my_data(uid, target_timezone):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                # 1. 将字符串转换为 datetime 对象，并标记为 UTC 时区
                df['dt_object'] = pd.to_datetime(df['created_at'], utc=True)
                
                # 2. 转换为动态获取的本地时区
                try:
                    df['dt_object'] = df['dt_object'].dt.tz_convert(target_timezone)
                except Exception:
                    # 如果浏览器时区识别失败（极其罕见），回退到 UTC
                    df['dt_object'] = df['dt_object'].dt.tz_convert('UTC')
                
                # 3. 格式化显示
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d %H:%M')
                
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                df.insert(0, '显示序号', df.index)
            return df
        except Exception as ex:
            st.warning(f"数据加载异常: {str(ex)}")
            return pd.DataFrame()

    # 加载数据时传入当前检测到的时区
    df = load_my_data(st.session_state.user.id, current_user_timezone)

    if not df.empty:
        st.subheader("📊 数据概览")
        m1, m2, m3 = st.columns(3)
        total_apps = len(df)
        offers = len(df[df['status'] == 'offer'])
        interviews = len(df[df['status'] == 'interviewing'])
        m1.metric("总申请数", total_apps)
        m2.metric("面试邀约", interviews)
        m3.metric("收到 Offer", offers)

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
            # 趋势图使用转换后的 dt_object 确保按本地日期统计
            df['week'] = df['dt_object'].dt.to_period('W').apply(lambda r: r.start_time)
            trend_df = df.groupby('week').size().reset_index(name='count')
            trend_df = trend_df.sort_values('week')
            fig_trend = px.bar(trend_df, x='week', y='count', labels={'week': '周次', 'count': '申请数'}, color_discrete_sequence=['#0073b1'])
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
                    status_list = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                    current_idx = status_list.index(row['status']) if row['status'] in status_list else 0
                    s = st.selectbox("当前状态", status_list, index=current_idx)
                with c2:
                    c = st.text_input("公司名称", value=row['company'])
                    l = st.text_input("地点", value=row['location'])
                desc = st.text_area("职位描述", value=row['description'], height=150)
                if st.form_submit_button("💾 保存修改"):
                    supabase.table("job_applications").update({"title": t, "company": c, "status": s, "location": l, "description": desc}).eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.rerun()

            if st.button("🗑️ 删除此条记录"):
                supabase.table("job_applications").delete().eq("id", row['id']).execute()
                st.cache_data.clear()
                st.rerun()
    else:
        st.info("目前没有数据。请通过插件在领英上抓取！")
