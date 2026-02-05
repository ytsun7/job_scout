import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (完全保留功能并优化)
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        "app_name": "CHRONO FLOW",
        "slogan": "理性的数据，感知的温度",
        "loading": "System Initializing...",
        "tab_login": "登 录", "tab_register": "注 册",
        "lbl_email": "邮箱地址", "lbl_pwd": "密码", "ph_email": "name@company.com",
        "btn_connect": "连接系统", "btn_create": "创建 ID",
        "auth_success": "权限已确认。", "reg_sent": "验证邮件已发送。",
        "console": "CONTROL PANEL", "my_account": "账户概览",
        "view_api_key": "API 密钥", "lbl_uid": "User ID:",
        "nav_dashboard": "核心看板", "nav_archive": "归档数据",
        "logout": "断开连接",
        "greeting_morning": "早安。", "greeting_afternoon": "午安。", "greeting_evening": "晚上好。",
        "greeting_sub": "保持专注。数据已同步。",
        "metric_active": "活跃申请数", "metric_interview": "面试进程",
        "metric_offer": "Offer 已获", "metric_rate": "整体回应率",
        "archive_title": "归档数据库", "archive_sub": "已封存的历史数据记录。",
        "archive_empty": "未检索到归档记录。",
        "btn_restore": "激活记录", "restore_success": "记录已恢复至活跃状态。",
        "restore_ph": "选择要恢复的记录...",
        "chart_title": "状态分布透视", "list_title": "近期动态追踪",
        "manage_title": "数据管理终端", "manage_hint": "更新状态或变更数据生命周期。",
        "search_label": "搜索", "search_ph": "定位活跃记录...",
        "input_title": "岗位名称", "input_company": "公司主体",
        "input_status": "当前阶段", "input_loc": "工作地点",
        "input_note": "备注 / 随笔",
        "col_date": "添加日期", "col_company": "公司名称",
        "col_role": "岗位", "col_status": "当前状态",
        "btn_save": "确认更新", "btn_archive": "封存归档", "btn_del": "永久删除",
        "msg_archived": "记录已封存。", "msg_updated": "数据已同步。",
        "msg_deleted": "记录已销毁。",
        "empty_desc": "暂无活跃数据流。等待输入。",
        "s_applied": "已投递", "s_interviewing": "面试中", "s_offer": "Offer",
        "s_rejected": "已拒绝", "s_ghosted": "无回音", "s_archived": "已归档"
    },
    "EN": {
        "app_name": "CHRONO FLOW",
        "slogan": "Minimal Data, Lucid Control.",
        "loading": "System Initializing...",
        "tab_login": "LOGIN", "tab_register": "REGISTER",
        "lbl_email": "Email", "lbl_pwd": "Password", "ph_email": "name@company.com",
        "btn_connect": "CONNECT", "btn_create": "CREATE ID",
        "auth_success": "Access Granted.", "reg_sent": "Verification email sent.",
        "console": "CONTROL PANEL", "my_account": "ACCOUNT",
        "view_api_key": "API Key", "lbl_uid": "UID:",
        "nav_dashboard": "Dashboard", "nav_archive": "Archive Data",
        "logout": "Disconnect",
        "greeting_morning": "Good Morning.", "greeting_afternoon": "Good Afternoon.", "greeting_evening": "Good Evening.",
        "greeting_sub": "Stay focused. Data synchronized.",
        "metric_active": "Active Applications", "metric_interview": "Interviews",
        "metric_offer": "Offers Received", "metric_rate": "Response Rate",
        "archive_title": "Archive Database", "archive_sub": "Stored historical records.",
        "archive_empty": "No archived records found.",
        "btn_restore": "Restore Record", "restore_success": "Record restored to active status.",
        "restore_ph": "Select record to restore...",
        "chart_title": "Status Perspective", "list_title": "Recent Activity Track",
        "manage_title": "Data Management Terminal", "manage_hint": "Update status or change lifecycle.",
        "search_label": "Search", "search_ph": "Locate active record...",
        "input_title": "Position", "input_company": "Company",
        "input_status": "Current Phase", "input_loc": "Location",
        "input_note": "Notes / Remarks",
        "col_date": "Date Added", "col_company": "Company Name",
        "col_role": "Role", "col_status": "Status",
        "btn_save": "Update Confirm", "btn_archive": "Archive", "btn_del": "Delete Permanently",
        "msg_archived": "Record archived.", "msg_updated": "Data synchronized.",
        "msg_deleted": "Record destroyed.",
        "empty_desc": "No active data stream. Waiting for input.",
        "s_applied": "Applied", "s_interviewing": "Interview", "s_offer": "Offer",
        "s_rejected": "Rejected", "s_ghosted": "No Response", "s_archived": "Archived"
    }
}

# ==========================================
# 1. UI 主题配置: "Nordic Glass & Tech Blue"
# ==========================================
THEME = {
    "bg_color": "#F0F4F8",            # 极冷灰背景
    "sidebar_bg_glass": "rgba(248, 250, 252, 0.7)", # 侧边栏毛玻璃
    "card_bg_glass": "rgba(255, 255, 255, 0.65)",   # 卡片毛玻璃
    "glass_border": "rgba(226, 232, 240, 0.5)",     # 极细的半透明边框
    "primary": "#334155",             # 板岩深灰
    "accent": "#0F172A",              # Slate 900
    "highlight": "#0EA5E9",           # 科技蓝 (Sky 500)
    "text_main": "#1E293B",           # Slate 800
    "text_light": "#64748B",          # Slate 500
}

st.set_page_config(page_title="Chrono Flow", layout="wide", page_icon="🧊")

def inject_nordic_glass_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;500;700&family=Playfair+Display:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 50%), 
                              radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.05) 0px, transparent 50%);
            font-family: 'Sitka', 'Playfair Display', 'Georgia', 'Noto Serif SC', serif;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 毛玻璃卡片 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg_glass']};
            backdrop-filter: blur(16px) saturate(120%);
            -webkit-backdrop-filter: blur(16px) saturate(120%);
            border: 1px solid {THEME['glass_border']} !important;
            border-radius: 12px; 
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg_glass']};
            backdrop-filter: blur(20px) saturate(120%);
            border-right: 1px solid {THEME['glass_border']};
        }}
        
        /* --- 按钮 --- */
        button[kind="primary"] {{
            background-color: {THEME['highlight']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-family: 'Sitka', 'Georgia', serif;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
        }}
        button[kind="primary"]:hover {{
            background-color: #0284C7 !important;
            transform: translateY(-1px);
        }}
        
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['glass_border']} !important;
            color: {THEME['text_main']} !important;
            border-radius: 8px;
            font-family: 'Sitka', 'Georgia', serif;
        }}

        /* --- 标题与文字 --- */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 700 !important; 
            font-family: 'Playfair Display', 'Sitka', serif;
            letter-spacing: -0.01em; 
        }}
        p, label, span {{ font-family: 'Sitka', 'Georgia', serif; }}
        code, .stCode {{ font-family: 'JetBrains Mono', monospace !important; }}
        </style>
    """, unsafe_allow_html=True)

inject_nordic_glass_css()

# ==========================================
# 2. 核心逻辑
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()
cookie_manager = stx.CookieManager(key="main_auth_manager")

if 'cookie_sync_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.write("") 
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.caption(t("loading"))
            _ = cookie_manager.get_all()
            time.sleep(1.0)
    st.session_state.cookie_sync_done = True
    st.rerun()

def get_current_user():
    if 'user' in st.session_state and st.session_state.user is not None:
        return st.session_state.user
    cookies = cookie_manager.get_all()
    at, rt = cookies.get("sb_access_token"), cookies.get("sb_refresh_token")
    if at and rt:
        try:
            session = supabase.auth.set_session(at, rt)
            st.session_state.user = session.user
            return session.user
        except: return None
    return None

user = get_current_user()

# ==========================================
# 3. 登录页 (含中英切换)
# ==========================================
def auth_ui():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-family: 'JetBrains Mono', monospace; color: {THEME['highlight']}; font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 5px;">SYS.V4 // SERIF</div>
                <h2 style="color: {THEME['accent']}; font-size: 2rem; margin: 0; letter-spacing: -1px;">{t('app_name')}</h2>
                <p style="color: {THEME['text_light']}; font-size: 0.9rem; margin-top: 10px; font-style: italic;">{t('slogan')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 登录页语言切换 ---
            c1, c2 = st.columns(2)
            with c1:
                t_zh = "primary" if st.session_state.language == "ZH" else "secondary"
                if st.button("🇨🇳 中文", key="auth_zh", use_container_width=True, type=t_zh):
                    st.session_state.language = "ZH"; st.rerun()
            with c2:
                t_en = "primary" if st.session_state.language == "EN" else "secondary"
                if st.button("🇺🇸 EN", key="auth_en", use_container_width=True, type=t_en):
                    st.session_state.language = "EN"; st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs([t("tab_login"), t("tab_register")])
            with tab1:
                with st.form("login_form"):
                    e = st.text_input(t("lbl_email"), placeholder=t("ph_email"))
                    p = st.text_input(t("lbl_pwd"), type="password")
                    if st.form_submit_button(t("btn_connect"), type="primary", use_container_width=True):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.rerun()
                        except: st.error("Authentication Failed")
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input(t("lbl_email"))
                    np = st.text_input(t("lbl_pwd"), type="password")
                    if st.form_submit_button(t("btn_create"), type="primary", use_container_width=True):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success(t("reg_sent"))
                        except: st.error("Signup Error")

# ==========================================
# 4. 主程序 (含侧边栏中英切换)
# ==========================================
if not user:
    auth_ui()
else:
    with st.sidebar:
        # --- 侧边栏语言切换 ---
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🇨🇳 ZH", key="side_zh", use_container_width=True, type="primary" if st.session_state.language=="ZH" else "secondary"):
                st.session_state.language = "ZH"; st.rerun()
        with sc2:
            if st.button("🇺🇸 EN", key="side_en", use_container_width=True, type="primary" if st.session_state.language=="EN" else "secondary"):
                st.session_state.language = "EN"; st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['highlight']} 100%); border-radius: 8px; color: white; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 700;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.9rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.75rem; color: {THEME['text_light']}; font-family: 'JetBrains Mono';">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.75rem; margin: 30px 0 10px 5px; font-weight: 700; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
        if st.button(t("nav_dashboard"), use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
        if st.button(t("nav_archive"), use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        st.markdown("<div style='flex-grow: 1; height: 30vh;'></div>", unsafe_allow_html=True)
        if st.button(t("logout"), type="secondary", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token")
            cookie_manager.delete("sb_refresh_token")
            st.rerun()

    # --- 数据加载 ---
    @st.cache_data(ttl=5)
    def load_my_data(uid):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['date_str'] = df['dt_object'].dt.strftime('%Y-%m-%d')
                df = df.reset_index(drop=True)
            return df
        except: return pd.DataFrame()

    df = load_my_data(user.id)
    active_df = df[df['status'] != 'archived'] if not df.empty else pd.DataFrame()
    archived_df = df[df['status'] == 'archived'] if not df.empty else pd.DataFrame()
    status_map = {"applied": t("s_applied"), "interviewing": t("s_interviewing"), "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted"), "archived": t("s_archived")}

    # --- 页面路由 ---
    if st.session_state.page == 'dashboard':
        hour = datetime.datetime.now().hour
        greet = t("greeting_morning") if hour < 12 else (t("greeting_afternoon") if hour < 18 else t("greeting_evening"))
        
        st.markdown(f"<h1 style='font-size: 2rem; font-weight: 400;'>{greet} <span style='color:{THEME['highlight']}; font-weight: 700;'>{user.email.split('@')[0]}</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.9rem; margin-top: -5px; font-style: italic;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
            st.info(t("empty_desc"))
        else:
            # 统计指标
            m1, m2, m3, m4 = st.columns(4)
            def glass_metric(label, value, icon):
                st.markdown(f"""
                <div style="background-color: {THEME['card_bg_glass']}; backdrop-filter: blur(16px); padding: 20px 24px; border: 1px solid {THEME['glass_border']}; border-radius: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 0.75rem; color: {THEME['text_light']}; text-transform: uppercase; font-family: 'JetBrains Mono';">{label}</div>
                        <div style="color: {THEME['highlight']};">{icon}</div>
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: {THEME['highlight']}; font-family: 'Playfair Display';">{value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: glass_metric(t("metric_active"), len(active_df[active_df['status'].isin(['applied', 'interviewing'])]), "⚡")
            with m2: glass_metric(t("metric_interview"), len(active_df[active_df['status'] == 'interviewing']), "📅")
            with m3: glass_metric(t("metric_offer"), len(active_df[active_df['status'] == 'offer']), "🎉")
            with m4:
                rate = (len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100) if not active_df.empty else 0
                glass_metric(t("metric_rate"), f"{rate:.1f}%", "📈")

            st.markdown("<br>", unsafe_allow_html=True)
            c_main, c_side = st.columns([2, 1])
            with c_main:
                with st.container(border=True):
                    st.markdown(f"### {t('list_title')}")
                    show_df = active_df.head(5).copy()
                    show_df['s_disp'] = show_df['status'].map(status_map)
                    st.dataframe(show_df, column_config={
                        "date_str": t("col_date"), "company": t("col_company"), "title": t("col_role"), "s_disp": t("col_status")
                    }, column_order=("date_str", "company", "title", "s_disp"), use_container_width=True, hide_index=True)

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    counts = active_df['status'].map(status_map).value_counts().reset_index()
                    fig = px.pie(counts, values='count', names='status', hole=0.7, color_discrete_sequence=[THEME['highlight'], '#64748B', '#CBD5E1'])
                    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job = st.selectbox(t("search_label"), [""] + job_list, placeholder=t("search_ph"), label_visibility="collapsed")
                if selected_job:
                    row = active_df.iloc[job_list.index(selected_job)]
                    with st.form("edit_form"):
                        c_a, c_b = st.columns(2)
                        new_t = c_a.text_input(t("input_title"), value=row['title'])
                        new_c = c_b.text_input(t("input_company"), value=row['company'])
                        new_s = c_a.selectbox(t("input_status"), list(status_map.keys())[:-1], index=list(status_map.keys()).index(row['status']), format_func=lambda x: status_map[x])
                        new_l = c_b.text_input(t("input_loc"), value=row['location'])
                        new_d = st.text_area(t("input_note"), value=row['description'])
                        b1, b2, b3 = st.columns([1,1,2])
                        if b1.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({"title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()
                        if b2.form_submit_button(t("btn_archive"), type="secondary"):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()

    elif st.session_state.page == 'archive':
        st.markdown(f"## {t('archive_title')}")
        if archived_df.empty:
            st.info(t("archive_empty"))
        else:
            with st.container(border=True):
                st.dataframe(archived_df, column_order=("date_str", "company", "title", "description"), use_container_width=True, hide_index=True)
                sel_arc = st.selectbox(t("btn_restore"), [""] + archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist(), placeholder=t("restore_ph"))
                if sel_arc:
                    arc_row = archived_df.iloc[archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist().index(sel_arc)]
                    if st.button(t("btn_restore"), type="primary"):
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", arc_row['id']).execute()
                        st.cache_data.clear(); st.rerun()
