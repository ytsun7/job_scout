import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 1. UI 配置中心
# ==========================================
UI_CONFIG = {
    "primary_color": "#0073b1",    # 领英蓝
    "bg_light": "#f3f6f8",         # 浅灰背景
    "success_green": "#27ae60",
    "warning_orange": "#f39c12",
    "card_border_radius": "12px"
}

st.set_page_config(page_title="Job Tracker Pro", layout="wide")

def inject_custom_css():
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {UI_CONFIG["bg_light"]}; }}
        /* 卡片容器样式 */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: white;
            border-radius: {UI_CONFIG["card_border_radius"]};
            border: 1px solid #e0e0e0 !important;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        /* 按钮样式优化 */
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid {UI_CONFIG["primary_color"]};
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: {UI_CONFIG["primary_color"]};
            color: white;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. 核心连接逻辑
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()
cookie_manager = stx.CookieManager(key="main_auth_manager")

# 防止闪烁的同步机制
if 'cookie_sync_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner("🚀 正在载入个人看板..."):
            _ = cookie_manager.get_all()
            time.sleep(1) 
    st.session_state.cookie_sync_done = True
    st.rerun()

def get_current_user():
    if 'user' in st.session_state and st.session_state.user is not None:
        return st.session_state.user
    cookies = cookie_manager.get_all()
    at = cookies.get("sb_access_token")
    rt = cookies.get("sb_refresh_token")
    if at and rt:
        try:
            session = supabase.auth.set_session(at, rt)
            st.session_state.user = session.user
            return session.user
        except: return None
    return None

user = get_current_user()

# ==========================================
# 3. 身份验证界面
# ==========================================
def auth_ui():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.write("# 🔐 登录中心")
        with st.container(border=True):
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
                                expires = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=expires, key="set_at_login")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=expires, key="set_rt_login")
                                st.success("登录成功！")
                                time.sleep(1)
                                st.rerun()
                        except Exception as ex: st.error(f"登录失败: {ex}")
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input("新邮箱")
                    np = st.text_input("设置密码 (至少6位)", type="password")
                    if st.form_submit_button("提交注册"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("注册成功！请直接登录")
                        except Exception as ex: st.error(f"注册失败: {ex}")

# ==========================================
# 4. 主程序逻辑
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏 ---
    with st.sidebar:
        st.success(f"已登录: {user.email}")
        st.info(f"🔑 你的 User ID (用于插件):\n\n{user.id}")
        if st.button("🚪 退出登录"):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token", key="del_at_logout")
            cookie_manager.delete("sb_refresh_token", key="del_rt_logout")
            if 'cookie_sync_done' in st.session_state:
                del st.session_state.cookie_sync_done
            st.rerun()

    st.title("💼 我的申请追踪看板")

    @st.cache_data(ttl=2)
    def load_my_data(uid):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d')
                status_map = {"applied": "📝 Applied", "interviewing": "🎯 Interview", "offer": "🎉 Offer", "rejected": "❌ Rejected", "ghosted": "👻 Ghosted"}
                df['status_display'] = df['status'].map(lambda x: status_map.get(x, x))
                df = df.reset_index(drop=True)
                df.insert(0, '显示序号', df.index + 1)
            return df
        except Exception as ex:
            st.warning(f"数据加载异常: {str(ex)}")
            return pd.DataFrame()

    df = load_my_data(user.id)

    if not df.empty:
        # --- 数据统计指标 ---
        st.subheader("📊 数据概览")
        m1, m2, m3 = st.columns(3)
        m1.metric("总申请数", len(df))
        m2.metric("面试邀约", len(df[df['status'] == 'interviewing']))
        m3.metric("收到 Offer", len(df[df['status'] == 'offer']))

        st.divider()

        # --- 图表区域：仅保留状态分布 ---
        col_chart, col_empty = st.columns([1.5, 1]) # 让饼图稍微靠左展示
        with col_chart:
            with st.container(border=True):
                st.markdown("**岗位状态分布**")
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['状态', '数量']
                fig_pie = px.pie(status_counts, values='数量', names='状态', hole=0.5, 
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=350, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)

        # --- 列表区域 ---
        st.subheader("📋 投递明细列表")
        st.dataframe(
            df, 
            column_config={
                "显示序号": st.column_config.NumberColumn("No.", width="small"),
                "formatted_date": "日期",
                "status_display": "进度状态",
                "company": "公司",
                "title": "岗位"
            },
            column_order=("显示序号", "formatted_date", "company", "title", "location", "status_display"),
            use_container_width=True, 
            hide_index=True
        )

        # --- 条目管理 ---
        st.divider()
        st.subheader("🛠️ 条目管理")
        with st.container(border=True):
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
                        supabase.table("job_applications").update({
                            "title": t, "company": c, "status": s, "location": l, "description": desc
                        }).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success("修改已保存！")
                        time.sleep(0.5)
                        st.rerun()

                if st.button("🗑️ 删除此条记录"):
                    supabase.table("job_applications").delete().eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.warning("记录已删除")
                    time.sleep(0.5)
                    st.rerun()
    else:
        st.info("目前没有数据。请通过插件在领英上抓取！")
