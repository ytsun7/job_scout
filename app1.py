import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (I18n)
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        "app_name": "CAREER FLOW", # 更现代、冷峻的名字
        "slogan": "理性的数据，感知的温度",
        "loading": "System Initializing...",
        
        "console": "CONTROL",
        "my_account": "ACCOUNT",
        "view_api_key": "API Access Key",
        "nav_dashboard": "Dashboard",
        "nav_archive": "Archive Database",
        "logout": "Disconnect",

        "greeting_morning": "Good Morning.",
        "greeting_afternoon": "Good Afternoon.",
        "greeting_evening": "Good Evening.",
        "greeting_sub": "保持专注。一切尽在掌控。",

        "metric_active": "Active Applications",
        "metric_interview": "Interviews",
        "metric_offer": "Offers Received",
        "metric_rate": "Response Rate",

        "archive_title": "Archive Database",
        "archive_sub": "已归档的历史数据记录。",
        "archive_empty": "No archived records found.",
        "btn_restore": "Restore Record",
        "restore_success": "Record restored to active status.",

        "chart_title": "Status Analytics",
        "list_title": "Recent Activity",
        "manage_title": "Record Management",
        "manage_hint": "更新状态或管理数据生命周期。",
        "input_title": "Position",
        "input_company": "Company",
        "input_status": "Current Phase",
        "input_loc": "Location",
        "input_note": "Notes / Remarks",
        
        "col_date": "添加日期",
        "col_company": "公司名称",
        "col_role": "岗位",
        "col_status": "当前状态",
        
        "btn_save": "Update Record",
        "btn_archive": "Archive",
        "btn_del": "Delete",
        
        "msg_archived": "Record moved to archive.",
        "msg_updated": "Database updated.",
        "msg_deleted": "Record permanently deleted.",
        "empty_desc": "暂无活跃数据。等待新数据录入。",

        "s_applied": "Applied",
        "s_interviewing": "Interview",
        "s_offer": "Offer",
        "s_rejected": "Rejected",
        "s_ghosted": "No Response",
        "s_archived": "Archived"
    },
    "EN": {
        "app_name": "CAREER FLOW",
        "slogan": "Rational Data, Perceived Warmth.",
        "loading": "System Initializing...",
        
        "console": "CONTROL",
        "my_account": "ACCOUNT",
        "view_api_key": "API Access Key",
        "nav_dashboard": "Dashboard",
        "nav_archive": "Archive Database",
        "logout": "Disconnect",

        "greeting_morning": "Good Morning.",
        "greeting_afternoon": "Good Afternoon.",
        "greeting_evening": "Good Evening.",
        "greeting_sub": "Stay focused. Everything is under control.",

        "metric_active": "Active Applications",
        "metric_interview": "Interviews",
        "metric_offer": "Offers Received",
        "metric_rate": "Response Rate",

        "archive_title": "Archive Database",
        "archive_sub": "Stored historical records.",
        "archive_empty": "No archived records found.",
        "btn_restore": "Restore Record",
        "restore_success": "Record restored to active status.",

        "chart_title": "Status Analytics",
        "list_title": "Recent Activity",
        "manage_title": "Record Management",
        "manage_hint": "Update status or manage data lifecycle.",
        "input_title": "Position",
        "input_company": "Company",
        "input_status": "Current Phase",
        "input_loc": "Location",
        "input_note": "Notes / Remarks",
        
        "col_date": "Date Added",
        "col_company": "Company Name",
        "col_role": "Role",
        "col_status": "Status",
        
        "btn_save": "Update Record",
        "btn_archive": "Archive",
        "btn_del": "Delete",
        
        "msg_archived": "Record moved to archive.",
        "msg_updated": "Database updated.",
        "msg_deleted": "Record permanently deleted.",
        "empty_desc": "No active data. Waiting for input.",

        "s_applied": "Applied",
        "s_interviewing": "Interview",
        "s_offer": "Offer",
        "s_rejected": "Rejected",
        "s_ghosted": "No Response",
        "s_archived": "Archived"
    }
}

# ==========================================
# 1. UI 主题配置: "Slate & Glass" (板岩与玻璃)
# ==========================================
THEME = {
    "bg_color": "#F8FAFC",           # 极冷灰 (Cool Grey 50) - 干净、科技
    "sidebar_bg": "#FFFFFF",         # 纯白侧边栏 - 极致整洁
    "card_bg": "#FFFFFF",            # 纯白卡片
    "primary": "#334155",            # 板岩深灰 (Slate 700) - 专业、清冷
    "accent": "#0F172A",             # 近乎黑的蓝 (Slate 900) - 强调
    "highlight": "#38BDF8",          # 电光蓝 (Sky 400) - 科技感点缀
    "text_main": "#1E293B",          # Slate 800
    "text_light": "#94A3B8",         # Slate 400
    "border_color": "#E2E8F0"        # Slate 200 - 极细分割线
}

st.set_page_config(page_title="Career Flow", layout="wide", page_icon="⚓")

def inject_tech_css():
    st.markdown(f"""
        <style>
        /* 引入 Inter 字体 - 现代 UI 的标配 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {THEME['text_main']};
        }}

        /* 隐藏原生头部 */
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 极简卡片 (Minimalist Cards) --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: 1px solid {THEME['border_color']} !important;
            border-radius: 8px; /* 小圆角，更硬朗 */
            padding: 24px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* 极细微阴影，仿佛浮在表面 */
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 (Sidebar) --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: 1px solid {THEME['border_color']};
        }}
        
        /* --- 按钮 (Buttons) - 扁平化高科技风 --- */
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            letter-spacing: 0.5px;
        }}
        .stButton>button:hover {{
            background-color: {THEME['accent']};
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
            transform: translateY(-1px);
        }}
        
        /* 次要按钮 (Outline) */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['border_color']} !important;
            color: {THEME['text_main']} !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['text_main']} !important;
            background-color: {THEME['bg_color']} !important;
        }}

        /* --- 语言切换按钮 --- */
        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 6px;
            font-size: 0.85rem;
            padding: 0.2rem 0.5rem;
        }}

        /* --- 表单输入框 (Clean Inputs) --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: #FFFFFF;
            border: 1px solid {THEME['border_color']} !important;
            border-radius: 6px !important;
            color: {THEME['text_main']};
            font-size: 0.9rem;
        }}
        input:focus, textarea:focus {{
            border-color: {THEME['primary']} !important;
            box-shadow: 0 0 0 2px rgba(51, 65, 85, 0.1) !important;
        }}

        /* --- 表格 (Data Grid) --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: #F1F5F9 !important; /* 浅灰表头 */
            border-top: 1px solid {THEME['border_color']};
            border-bottom: 1px solid {THEME['border_color']};
            color: {THEME['text_main']};
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid {THEME['border_color']};
             font-size: 0.9rem;
             color: #475569;
        }}

        /* --- 文字排版 --- */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 600 !important; 
            letter-spacing: -0.025em; /* 紧凑字距 */
        }}
        p, label {{
            color: {THEME['text_main']};
            font-weight: 400;
        }}
        
        /* 状态指示器 */
        .status-dot {{
            height: 8px;
            width: 8px;
            background-color: {THEME['highlight']};
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_tech_css()

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
            st.caption(t("loading")) # 使用 caption 显示加载，更低调
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
# 3. 登录页 UI (Professional & Clean)
# ==========================================
def auth_ui():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            # 极简 Logo 区
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-family: 'JetBrains Mono', monospace; color: {THEME['highlight']}; font-size: 0.9rem; letter-spacing: 2px;">SYSTEM_V2.0</div>
                <h2 style="color: {THEME['accent']}; font-size: 1.8rem; margin-top: 10px; letter-spacing: -1px;">{t('app_name')}</h2>
                <div style="width: 40px; height: 2px; background: {THEME['border_color']}; margin: 15px auto;"></div>
                <p style="color: {THEME['text_light']}; font-size: 0.9rem;">{t('slogan')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 语言切换 (Buttons)
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
            tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
            with tab1:
                with st.form("login_form"):
                    e = st.text_input("Email", placeholder="name@company.com")
                    p = st.text_input("Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("CONNECT"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.success("Access Granted.")
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(str(ex))
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input("Email")
                    np = st.text_input("Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("CREATE ID"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("Verification email sent.")
                        except Exception as ex: st.error(str(ex))

# ==========================================
# 4. 主程序 - Tech/Calm Style
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏 (SaaS Dashboard Style) ---
    with st.sidebar:
        # 国旗切换
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
        
        # 用户信息 (Minimal)
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 32px; height: 32px; background: {THEME['primary']}; border-radius: 4px; color: white; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 600;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 600; font-size: 0.85rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.7rem; color: {THEME['text_light']}; font-family: 'JetBrains Mono';">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.caption("UID:")
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.7rem; margin: 30px 0 10px 5px; font-weight: 600; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
        # 导航按钮
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
        # --- 📅 看板 (Dashboard) ---
        
        # 头部 (Minimal Header)
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.markdown(f"<h1 style='font-size: 1.8rem; font-weight: 400;'>{greet} <strong style='font-weight: 600;'>{user.email.split('@')[0]}</strong></h1>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.9rem; margin-top: -10px; font-family: sans-serif;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
             st.markdown(f"""
             <div style='text-align: center; padding: 60px; color: {THEME['text_light']}; border: 1px dashed {THEME['border_color']}; border-radius: 8px;'>
                <div style='font-size: 1.5rem; margin-bottom: 10px;'>📡</div>
                <p style="font-size: 0.9rem;">{t('empty_desc')}</p>
             </div>
             """, unsafe_allow_html=True)
        else:
            # 科技感指标 (Data Widgets)
            m1, m2, m3, m4 = st.columns(4)
            
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            def tech_metric(label, value, delta=None):
                st.markdown(f"""
                <div style="background-color: white; padding: 20px 24px; border: 1px solid {THEME['border_color']}; border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: {THEME['text_light']}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">{label}</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: {THEME['text_main']}; letter-spacing: -0.05em;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: tech_metric(t("metric_active"), cnt_active)
            with m2: tech_metric(t("metric_interview"), cnt_int)
            with m3: tech_metric(t("metric_offer"), cnt_off)
            with m4: tech_metric(t("metric_rate"), f"{rate:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            # 数据可视化与列表
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
                        use_container_width=True, hide_index=True, height=220
                    )

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    chart_df = active_df.copy()
                    chart_df['s_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['s_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    # 冷色调配色 (Cool & Tech)
                    tech_palette = ['#334155', '#94A3B8', '#CBD5E1', '#E2E8F0', '#0EA5E9'] 
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.8, color_discrete_sequence=tech_palette)
                    fig.update_layout(
                        margin=dict(t=0, b=0, l=0, r=0), height=220, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=THEME['text_main'])]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 控制台 (Edit Console)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                c_title, c_hint = st.columns([1, 2])
                with c_title:
                    st.markdown(f"### {t('manage_title')}")
                with c_hint:
                    st.caption(t("manage_hint"))
                
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job_str = st.selectbox("Search", [""] + job_list, label_visibility="collapsed", placeholder="Select record to edit...")
                
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
                        
                        b1, b2, b3 = st.columns([1, 1, 4])
                        if b1.form_submit_button(t("btn_save")):
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
        # --- 🗃️ 归档页 ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 0.9rem;'>{t('archive_sub')}</p>", unsafe_allow_html=True)
        
        if archived_df.empty:
            st.info(t("archive_empty"))
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
                sel_archive = st.selectbox("Restore Record", [""] + archive_list, label_visibility="collapsed", placeholder="Select to restore...")
                
                if sel_archive:
                    row_idx = archive_list.index(sel_archive)
                    row = archived_df.iloc[row_idx]
                    st.caption(f"Selected: {row['title']} @ {row['company']}")
                    
                    c_res, c_del = st.columns([1, 6])
                    if c_res.button(t("btn_restore"), type="primary"):
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success(t("restore_success")); time.sleep(0.5); st.rerun()
                    
                    if c_del.button(t("btn_del"), key="del_a", type="secondary"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted")); time.sleep(0.5); st.rerun()
