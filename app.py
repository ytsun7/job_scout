import streamlit as st
import extra_streamlit_components as stx # 必须先 pip install extra-streamlit-components
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# --- 配置区 ---
URL = "https://ucabuiwtvhpyqehaytxj.supabase.co"
KEY = "sb_publishable_qRsPp469HJzOmpTc-KM-QQ_dNGZoKRj"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- Cookie 管理器初始化 ---
# 注意：这行代码必须在页面加载早期运行
cookie_manager = stx.CookieManager(key="auth_cookie_manager")

# --- 核心：持久化登录逻辑 ---
def get_current_user():
    """尝试从 Cookie 获取 Token 并恢复 Supabase 会话"""
    # 1. 检查 Session State 是否已经有用户
    if 'user' in st.session_state and st.session_state.user is not None:
        return st.session_state.user

    # 2. 如果没有，尝试从 Cookie 读取 Token
    cookies = cookie_manager.get_all()
    access_token = cookies.get("sb_access_token")
    refresh_token = cookies.get("sb_refresh_token")

    if access_token and refresh_token:
        try:
            # 使用 Token 恢复会话，这比单纯存 UID 安全得多
            session = supabase.auth.set_session(access_token, refresh_token)
            st.session_state.user = session.user
            return session.user
        except Exception as e:
            # Token 过期或无效
            return None
    return None

# 初始化用户状态
user = get_current_user()

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
                        
                        # --- 修改：写入 Supabase Token 到 Cookie ---
                        # 设置 7 天过期，实现免登录
                        expires = datetime.datetime.now() + datetime.timedelta(days=7)
                        cookie_manager.set("sb_access_token", res.session.access_token, expires_at=expires, key="set_at")
                        cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=expires, key="set_rt")
                        
                        st.success("登录成功！")
                        time.sleep(1) # 等待 Cookie 写入
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
if not user:
    auth_ui()
else:
    # 侧边栏
    st.sidebar.success(f"已登录: {user.email}")
    st.sidebar.info(f"🔑 你的 User ID (用于插件):\n\n{user.id}")
    
    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        st.session_state.user = None
        
        # --- 修改：清除 Cookie ---
        cookie_manager.delete("sb_access_token", key="del_at")
        cookie_manager.delete("sb_refresh_token", key="del_rt")
        
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
            st.warning(f"数据加载异常: {str(ex)}")
            return pd.DataFrame()

    df = load_my_data(user.id)

    if not df.empty:
        # --- 1. 数据统计与可视化 ---
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
            df['week'] = df['dt_object'].dt.to_period('W').apply(lambda r: r.start_time)
            trend_df = df.groupby('week').size().reset_index(name='count')
            trend_df = trend_df.sort_values('week')
            fig_trend = px.bar(trend_df, x='week', y='count', labels={'week': '周次', 'count': '申请数'}, color_discrete_sequence=['#0073b1'])
            fig_trend.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()

        # --- 2. 列表区域 ---
        st.subheader("📋 投递明细列表")
        st.dataframe(df[['显示序号', 'formatted_date', 'title', 'company', 'location', 'status']], use_container_width=True, hide_index=True)
        st.divider()

        # --- 3. 内容管理 ---
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
