import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (I18n) - 保持深度汉化版
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        "app_name": "NORDIC FLOW",
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
        "app_name": "NORDIC FLOW",
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
    "bg_color": "#F0F4F8",           # 极冷灰背景
    "sidebar_bg_glass": "rgba(248, 250, 252, 0.7)", # 侧边栏毛玻璃
    "card_bg_glass": "rgba(255, 255, 255, 0.65)",   # 卡片毛玻璃
    "glass_border": "rgba(226, 232, 240, 0.5)",     # 极细的半透明边框
    "primary": "#334155",            # 板岩深灰
    "accent": "#0F172A",             # Slate 900
    "highlight": "#0EA5E9",          # 科技蓝 (Sky 500) - 保持高亮
    "text_main": "#1E293B",          # Slate 800
    "text_light": "#64748B",         # Slate 500
}

st.set_page_config(page_title="Nordic Flow", layout="wide", page_icon="🧊")

def inject_nordic_glass_css():
    st.markdown(f"""
        <style>
        /* 引入衬线字体 (Serif) 用于书卷气，引入 JetBrains Mono 用于代码/数字 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;500;700&family=Playfair+Display:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 50%), 
                              radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.05) 0px, transparent 50%);
            /* 核心修改：使用 Sitka / Georgia / Noto Serif SC 打造书卷气 */
            font-family: 'Sitka', 'Playfair Display', 'Georgia', 'Noto Serif SC', serif;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 毛玻璃卡片 (Frosted Glass) --- */
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
        
        /* --- 按钮 (Tech Blue + Serif Font) --- */
        button[kind="primary"] {{
            background-color: {THEME['highlight']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-family: 'Sitka', 'Georgia', serif; /* 字体修改 */
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
        }}
        button[kind="primary"]:hover {{
            background-color: #0284C7 !important;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
            transform: translateY(-1px);
        }}
        
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['glass_border']} !important;
            color: {THEME['text_main']} !important;
            border-radius: 8px;
            font-family: 'Sitka', 'Georgia', serif; /* 字体修改 */
            font-weight: 500;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['highlight']} !important;
            background-color: rgba(14, 165, 233, 0.05) !important;
            color: {THEME['highlight']} !important;
        }}

        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 6px;
            font-size: 0.85rem;
            padding: 0.25rem 0.5rem;
        }}

        /* --- 输入框 (Serif Input) --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(5px);
            border: 1px solid {THEME['glass_border']} !important;
            border-radius: 8px !important;
            color: {THEME['text_main']};
            font-size: 0.9rem;
            font-family: 'Sitka', 'Georgia', serif; /* 字体修改 */
            font-weight: 500;
        }}
        input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {{
            border-color: {THEME['highlight']} !important;
            box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.15) !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }}

        /* --- 表格 (Serif Grid) --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: rgba(241, 245, 249, 0.5) !important;
            border-bottom: 1px solid {THEME['glass_border']};
            color: {THEME['text_light']};
            font-family: 'Sitka', 'Georgia', serif; /* 字体修改 */
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid {THEME['glass_border']};
             color: {THEME['text_main']};
             font-family: 'Sitka', 'Georgia', serif; /* 字体修改 */
        }}

        /* --- 标题与文字 (Advanced Typography) --- */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 700 !important; 
            font-family: 'Playfair Display', 'Sitka', serif; /* 标题用更华丽的衬线 */
            letter-spacing: -0.01em; 
        }}
        p, label, span {{
            color: {THEME['text_main']};
            font-weight: 400;
            font-family: 'Sitka', 'Georgia', serif;
            letter-spacing: 0em;
        }}
        .caption {{ color: {THEME['text_light']} !important; font-style: italic; }}
        
        /* 保持ID和代码显示为等宽字体 */
        code, .stCode {{
            font-family: 'JetBrains Mono', monospace !important;
        }}
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
            time.sleep(1.5)
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
# 3. 登录页
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
            
            c1, c2 = st.columns(2)
            with c1:
                t_zh = "primary" if st.session_state.language == "ZH" else "secondary"
                if st.button("🇨🇳 CN", key="auth_zh", use_container_width=True, type=t_zh):
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
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("btn_connect"), type="primary"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.success(t("auth_success"))
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(str(ex))
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input(t("lbl_email"))
                    np = st.text_input(t("lbl_pwd"), type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("btn_create"), type="primary"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success(t("reg_sent"))
                        except Exception as ex: st.error(str(ex))

# ==========================================
# 4. 主程序
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏 ---
    with st.sidebar:
        c1, c2 = st.columns(2)
        with c1:
            t_zh = "primary" if st.session_state.language == "ZH" else "secondary"
            if st.button("🇨🇳 CN", key="side_zh", use_container_width=True, type=t_zh):
                st.session_state.language = "ZH"; st.rerun()
        with c2:
            t_en = "primary" if st.session_state.language == "EN" else "secondary"
            if st.button("🇺🇸 EN", key="side_en", use_container_width=True, type=t_en):
                st.session_state.language = "EN"; st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['highlight']} 100%); border-radius: 8px; color: white; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 700; box-shadow: 0 2px 5px rgba(14, 165, 233, 0.3);">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.9rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.75rem; color: {THEME['text_light']}; font-family: 'JetBrains Mono';">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.caption(f"{t('lbl_uid')}")
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.75rem; margin: 30px 0 10px 5px; font-weight: 700; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
        if st.button(t("nav_dashboard"), key="nav_d", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
            
        if st.button(t("nav_archive"), key="nav_a", use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        st.markdown("<div style='flex-grow: 1; height: 100px;'></div>", unsafe_allow_html=True)
        if st.button(t("logout"), type="secondary", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token", key="del_at")
            cookie_manager.delete("sb_refresh_token", key="del_rt")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
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
                df.insert(0, 'id_display', df.index + 1)
            return df
        except: return pd.DataFrame()

    df = load_my_data(user.id)
    
    active_df = pd.DataFrame()
    archived_df = pd.DataFrame()
    if not df.empty:
        active_df = df[df['status'] != 'archived']
        archived_df = df[df['status'] == 'archived']

    status_map = {
        "applied": t("s_applied"), "interviewing": t("s_interviewing"),
        "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted"),
        "archived": t("s_archived")
    }

    # ==========================================
    # 5. 页面路由
    # ==========================================
    hour = datetime.datetime.now().hour
    if hour < 12: greet = t("greeting_morning")
    elif hour < 18: greet = t("greeting_afternoon")
    else: greet = t("greeting_evening")

    if st.session_state.page == 'dashboard':
        # --- 📅 看板 ---
        
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.markdown(f"<h1 style='font-size: 2rem; font-weight: 400;'>{greet} <span style='color:{THEME['highlight']}; font-weight: 700;'>{user.email.split('@')[0]}</span></h1>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.9rem; margin-top: -5px; font-style: italic;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
             with st.container(border=True):
                st.markdown(f"""
                <div style='text-align: center; padding: 40px; color: {THEME['text_light']};'>
                    <div style='font-size: 2rem; margin-bottom: 15px; color: {THEME['highlight']}; opacity: 0.5;'>⟲</div>
                    <p style="font-size: 0.9rem;">{t('empty_desc')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            m1, m2, m3, m4 = st.columns(4)
            
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            def glass_metric(label, value, icon):
                st.markdown(f"""
                <div style="background-color: {THEME['card_bg_glass']}; backdrop-filter: blur(16px); padding: 20px 24px; border: 1px solid {THEME['glass_border']}; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 0.75rem; color: {THEME['text_light']}; text-transform: uppercase; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;">{label}</div>
                        <div style="color: {THEME['highlight']}; opacity: 0.8;">{icon}</div>
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: {THEME['highlight']}; letter-spacing: -0.05em; text-shadow: 0 2px 10px rgba(14, 165, 233, 0.2); font-family: 'Playfair Display', serif;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: glass_metric(t("metric_active"), cnt_active, "⚡")
            with m2: glass_metric(t("metric_interview"), cnt_int, "📅")
            with m3: glass_metric(t("metric_offer"), cnt_off, "🎉")
            with m4: glass_metric(t("metric_rate"), f"{rate:.1f}%", "📈")

            st.markdown("<br>", unsafe_allow_html=True)

            c_main, c_side = st.columns([2, 1])
            
            with c_main:
                with st.container(border=True):
                    st.markdown(f"### {t('list_title')}")
                    show_df = active_df.head(5).copy()
                    show_df['s_disp'] = show_df['status'].map(lambda x: status_map.get(x, x))
                    
                    st.dataframe(
                        show_df,
                        column_config={
                            "date_str": st.column_config.TextColumn(t("col_date"), width="small"),
                            "s_disp": st.column_config.TextColumn(t("col_status"), width="small"),
                            "company": st.column_config.TextColumn(t("col_company")),
                            "title": st.column_config.TextColumn(t("col_role"), width="medium"),
                        },
                        column_order=("date_str", "company", "title", "s_disp"),
                        use_container_width=True, hide_index=True, height=240
                    )

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    chart_df = active_df.copy()
                    chart_df['s_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['s_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    tech_palette = [THEME['highlight'], '#64748B', '#94A3B8', '#CBD5E1', '#E2E8F0'] 
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.75, color_discrete_sequence=tech_palette)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=240, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=THEME['text_main'], font_weight=700)]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                c_title, c_hint = st.columns([1, 2])
                with c_title:
                    st.markdown(f"### {t('manage_title')}")
                with c_hint:
                    st.caption(t("manage_hint"))
                
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job_str = st.selectbox(t("search_label"), [""] + job_list, label_visibility="collapsed", placeholder=t("search_ph"))
                
                if selected_job_str:
                    st.markdown("---")
                    row_idx = job_list.index(selected_job_str)
                    row = active_df.iloc[row_idx]
                    
                    with st.form("edit_form"):
                        c_a, c_b = st.columns(2)
                        with c_a:
                            new_t = st.text_input(t("input_title"), value=row['title'])
                            db_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                            curr_k = row['status'] if row['status'] in db_keys else "applied"
                            new_s = st.selectbox(t("input_status"), db_keys, index=db_keys.index(curr_k), format_func=lambda x: status_map.get(x,x))
                        with c_b:
                            new_c = st.text_input(t("input_company"), value=row['company'])
                            new_l = st.text_input(t("input_loc"), value=row['location'])
                        
                        new_d = st.text_area(t("input_note"), value=row['description'], height=80)
                        
                        b1, b2, b3 = st.columns([1.5, 1.5, 4])
                        if b1.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({
                                "title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_updated")); time.sleep(0.5); st.rerun()
                        
                        if b2.form_submit_button(t("btn_archive"), type="secondary"):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_archived")); time.sleep(0.5); st.rerun()

                    if st.button(t("btn_del"), type="secondary", key="del_d"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted")); time.sleep(0.5); st.rerun()

    elif st.session_state.page == 'archive':
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 0.9rem; font-style: italic;'>{t('archive_sub')}</p>", unsafe_allow_html=True)
        
        if archived_df.empty:
            with st.container(border=True):
                 st.markdown(f"""
                 <div style='text-align: center; padding: 40px; color: {THEME['text_light']};'>
                    <div style='font-size: 2rem; margin-bottom: 15px; opacity: 0.3;'>🗃️</div>
                    <p style="font-size: 0.9rem;">{t('archive_empty')}</p>
                 </div>
                 """, unsafe_allow_html=True)
        else:
            with st.container(border=True):
                archived_df['display_status'] = t("s_archived")
                
                st.dataframe(
                    archived_df,
                    column_config={
                        "date_str": st.column_config.TextColumn(t("col_date")),
                        "company": st.column_config.TextColumn(t("col_company")),
                        "title": st.column_config.TextColumn(t("col_role")),
                        "description": st.column_config.TextColumn(t("input_note"), width="large"),
                        "display_status": st.column_config.TextColumn(t("col_status"))
                    },
                    column_order=("date_str", "company", "title", "display_status", "description"),
                    use_container_width=True, hide_index=True
                )
                
                st.markdown("---")
                archive_list = archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                sel_archive = st.selectbox(t("btn_restore"), [""] + archive_list, label_visibility="collapsed", placeholder=t("restore_ph"))
                
                if sel_archive:
                    row_idx = archive_list.index(sel_archive)
                    row = archived_df.iloc[row_idx]
                    st.caption(f"Selected: {row['title']} @ {row['company']}")
                    
                    c_res, c_del = st.columns([1.5, 6])
                    if c_res.button(t("btn_restore"), type="primary"):
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success(t("restore_success")); time.sleep(0.5); st.rerun()
                    
                    if c_del.button(t("btn_del"), key="del_a", type="secondary"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted")); time.sleep(0.5); st.rerun()
