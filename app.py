import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import pytz 

# --- 配置区 ---
URL = "https://ucabuiwtvhpyqehaytxj.supabase.co"
KEY = "sb_publishable_qRsPp469HJzOmpTc-KM-QQ_dNGZoKRj"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- Cookie 管理与时区自动检测 ---
THREE_HOURS = 3 * 60 * 60

def set_login_cookies(user_id, email):
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
    js_code = """
    <script>
    document.cookie = "job_scout_uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_expiry=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "job_scout_timezone=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    </script>
    """
    st.components.v1.html(js_code, height=0)

def get_browser_timezone():
    """
    尝试获取浏览器时区。
    如果 Cookie 中没有，注入 JS 写入 Cookie，并返回 None (等待下一次运行读取)。
    """
    # 1. 尝试读取 Cookie
    tz_cookie = st.context.cookies.get("job_scout_timezone")
    if tz_cookie:
        return tz_cookie
    
    # 2. 如果没有 Cookie，注入 JS 获取并写入
    # 使用 session_state 防止无限循环刷新
    if "tz_inject_run" not in st.session_state:
        st.session_state.tz_inject_run = True
        js_code = """
        <script>
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.cookie = "job_scout_timezone=" + tz + "; path=/; max-age=31536000";
        // 稍微延迟后刷新页面，让 Python 能读到 Cookie
        setTimeout(function(){ window.parent.location.reload(); }, 500);
        </script>
        """
        st.components.v1.html(js_code, height=0)
        time.sleep(1) # 等待 JS 执行
    
    return None # 暂时未获取到

# --- 初始化 Session ---
if "user" not in st.session_state:
    c_uid = st.context.cookies.get("job_scout_uid")
    c_email = st.context.cookies.get("job_scout_email")
    c_expiry = st.context.cookies.get("job_scout_expiry")

    if c_uid and c_expiry and time.time() < float(c_expiry):
        st.session_state.user = type('User', (object,), {'id': c_uid, 'email': c_email})
    else:
        st.session_state.user = None

# --- 身份验证界面 ---
def auth_ui():
    st.title("🔐 登录中心")
    tab1, tab2 = st.tabs(["用户登录", "新用户注册"])
    with tab1:
        with st.form("login_form"):
            e = st.text_input("邮箱")
            p = st.text_input("密码", type="password")
            if st.form_submit_button("立即登录"):
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
    # ---------------------------------------------------------
    # 侧边栏：时区控制中心 (核心修改)
    # ---------------------------------------------------------
    st.sidebar.success(f"已登录: {st.session_state.user.email}")
    
    with st.sidebar.expander("🌍 时区设置", expanded=True):
        # 获取自动检测的时区
        detected_tz = get_browser_timezone()
        
        # 常见时区列表
        common_timezones = ['Asia/Shanghai', 'Europe/Berlin', 'Europe/London', 'America/New_York', 'UTC']
        
        # 确定下拉框的默认值
        default_ix = 0
        if detected_tz and detected_tz in common_timezones:
            default_ix = common_timezones.index(detected_tz)
        elif detected_tz:
            # 如果检测到的时区不在常用列表中，把它加进去
            common_timezones.insert(0, detected_tz)
            default_ix = 0
        else:
            # 没检测到，默认 UTC
            default_ix = common_timezones.index('UTC')

        # 让用户拥有最终决定权
        selected_timezone = st.selectbox(
            "当前显示时区:", 
            common_timezones, 
            index=default_ix,
            help="默认为自动检测的本地时区，您也可以手动修改。"
        )
        
        if detected_tz:
            st.caption(f"🔍 已自动检测: {detected_tz}")
        else:
            st.caption("⏳ 正在检测浏览器时区...")

    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        st.session_state.user = None
        clear_login_cookies()
        time.sleep(0.5)
        st.rerun()

    st.title("💼 我的申请追踪看板")

    # ---------------------------------------------------------
    # 数据加载函数 (传入 selected_timezone 以确保响应修改)
    # ---------------------------------------------------------
    @st.cache_data(ttl=2)
    def load_my_data(uid, target_tz):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                # 1. 强制转换为 UTC 时间对象
                df['dt_object'] = pd.to_datetime(df['created_at'], utc=True)
                
                # 2. 转换到目标时区
                try:
                    df['dt_object'] = df['dt_object'].dt.tz_convert(target_tz)
                except Exception:
                    df['dt_object'] = df['dt_object'].dt.tz_convert('UTC')
                
                # 3. 格式化字符串
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d %H:%M')
                
                # 4. 生成辅助列
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                df.insert(0, '显示序号', df.index)
            return df
        except Exception as ex:
            st.warning(f"数据加载异常: {str(ex)}")
            return pd.DataFrame()

    # 加载数据
    df = load_my_data(st.session_state.user.id, selected_timezone)

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
            # 使用转换后的本地时间计算“周”
            df['week'] = df['dt_object'].dt.to_period('W').apply(lambda r: r.start_time)
            trend_df = df.groupby('week').size().reset_index(name='count')
            trend_df = trend_df.sort_values('week')
            fig_trend = px.bar(trend_df, x='week', y='count', labels={'week': '周次', 'count': '申请数'}, color_discrete_sequence=['#0073b1'])
            fig_trend.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()

        st.subheader("📋 投递明细列表")
        # 显示格式化后的时间
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
