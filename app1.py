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
        "app_name": "NORDIC / CORE", 
        "slogan": "理性数据 · 深度掌控",
        "loading": "System Loading...",
        "tab_login": "登 录", "tab_register": "注 册",
        "lbl_email": "邮箱地址", "lbl_pwd": "密码", "ph_email": "user@domain.com",
        "btn_connect": "连接终端", "btn_create": "注册 ID",
        "auth_success": "Access Granted.", "reg_sent": "Verification Sent.",
        "console": "CONTROL", "my_account": "PROFILE",
        "view_api_key": "Access Key", "lbl_uid": "UID:",
        "nav_dashboard": "核心看板", "nav_archive": "冷存储归档",
        "logout": "断开连接",
        "greeting_morning": "Good Morning.", "greeting_afternoon": "Good Afternoon.", "greeting_evening": "Good Evening.",
        "greeting_sub": "系统运行正常。数据已同步。",
        "metric_active": "活跃申请", "metric_interview": "面试进程",
        "metric_offer": "Offer", "metric_rate": "回应率",
        "archive_title": "归档数据库", "archive_sub": "已封存的历史数据记录。",
        "archive_empty": "未检索到归档记录。",
        "btn_restore": "激活记录", "restore_success": "记录已恢复至活跃状态。",
        "restore_ph": "选择记录以恢复...",
        "chart_title": "状态分布透视", "list_title": "动态追踪",
        "manage_title": "数据管理", "manage_hint": "更新状态或变更生命周期。",
        "search_label": "搜索", "search_ph": "定位记录...",
        "input_title": "岗位", "input_company": "公司",
        "input_status": "阶段", "input_loc": "地点",
        "input_note": "备注",
        "col_date": "日期", "col_company": "公司",
        "col_role": "岗位", "col_status": "状态",
        "btn_save": "确认更新", "btn_archive": "移入冷存储", "btn_del": "物理删除",
        "msg_archived": "记录已封存。", "msg_updated": "数据已同步。",
        "msg_deleted": "记录已销毁。",
        "empty_desc": "无活跃数据流。",
        "s_applied": "已投递", "s_interviewing": "面试中", "s_offer": "Offer",
        "s_rejected": "已拒绝", "s_ghosted": "无回音", "s_archived": "已归档"
    },
    "EN": {
        "app_name": "NORDIC / CORE",
        "slogan": "Rational Data. Deep Control.",
        "loading": "System Loading...",
        "tab_login": "LOGIN", "tab_register": "REGISTER",
        "lbl_email": "Email", "lbl_pwd": "Password", "ph_email": "user@domain.com",
        "btn_connect": "CONNECT", "btn_create": "CREATE ID",
        "auth_success": "Access Granted.", "reg_sent": "Verification Sent.",
        "console": "CONTROL", "my_account": "PROFILE",
        "view_api_key": "Access Key", "lbl_uid": "UID:",
        "nav_dashboard": "Dashboard", "nav_archive": "Cold Storage",
        "logout": "Disconnect",
        "greeting_morning": "Good Morning.", "greeting_afternoon": "Good Afternoon.", "greeting_evening": "Good Evening.",
        "greeting_sub": "System operational. Data synced.",
        "metric_active": "Active", "metric_interview": "Interviews",
        "metric_offer": "Offers", "metric_rate": "Response Rate",
        "archive_title": "Archive DB", "archive_sub": "Stored historical records.",
        "archive_empty": "No archived records.",
        "btn_restore": "Restore", "restore_success": "Restored to active.",
        "restore_ph": "Select to restore...",
        "chart_title": "Status Perspective", "list_title": "Activity Track",
        "manage_title": "Data Management", "manage_hint": "Update status or lifecycle.",
        "search_label": "Search", "search_ph": "Locate record...",
        "input_title": "Role", "input_company": "Company",
        "input_status": "Phase", "input_loc": "Location",
        "input_note": "Notes",
        "col_date": "Date", "col_company": "Company",
        "col_role": "Role", "col_status": "Status",
        "btn_save": "Update", "btn_archive": "Archive", "btn_del": "Delete",
        "msg_archived": "Archived.", "msg_updated": "Synced.",
        "msg_deleted": "Deleted.",
        "empty_desc": "No active data stream.",
        "s_applied": "Applied", "s_interviewing": "Interview", "s_offer": "Offer",
        "s_rejected": "Rejected", "s_ghosted": "No Response", "s_archived": "Archived"
    }
}

# ==========================================
# 1. UI 主题配置: "Nordic Deep & Glass"
# ==========================================
THEME = {
    "bg_color": "#F3F4F6",           # 冷石灰 (Stone 100) - 更有质感
    "sidebar_bg": "rgba(255, 255, 255, 0.7)", # 侧边栏高透
    "card_bg_glass": "rgba(255, 255, 255, 0.4)",   # 卡片极透
    "glass_border": "rgba(255, 255, 255, 0.6)",    # 玻璃边缘反光
    "primary": "#334155",            # 板岩 (Slate 700)
    "accent": "#0F172A",             # 黑曜石 (Slate 900)
    "highlight": "#1D4ED8",          # 深海蓝 (Royal Blue 700) - 深沉的高级蓝
    "text_main": "#111827",          # 接近纯黑 (Gray 900)
    "text_light": "#64748B",         # 沉稳灰 (Slate 500)
}

st.set_page_config(page_title="Nordic Core", layout="wide", page_icon="🧊")

def inject_nordic_glass_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: 
                linear-gradient(120deg, #E2E8F0 0%, #F8FAFC 100%);
            font-family: 'Inter', sans-serif;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 极度通透的毛玻璃卡片 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg_glass']};
            backdrop-filter: blur(24px) saturate(140%); /* 强模糊 */
            -webkit-backdrop-filter: blur(24px) saturate(140%);
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.8) !important; /* 顶部高光模拟玻璃厚度 */
            border-radius: 16px; 
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05); /* 极淡的投影 */
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        /* --- 按钮: 克制、深沉 --- */
        /* 主按钮 */
        button[kind="primary"] {{
            background-color: {THEME['highlight']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(29, 78, 216, 0.25); /* 深蓝阴影 */
            transition: all 0.2s ease;
        }}
        button[kind="primary"]:hover {{
            background-color: #1E40AF !important; /* 更深的蓝 */
            transform: translateY(-1px);
        }}
        
        /* 次要按钮: 极简灰线 */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['text_light']} !important;
            color: {THEME['text_main']} !important;
            border-radius: 8px;
            font-weight: 500;
            opacity: 0.8;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['highlight']} !important;
            color: {THEME['highlight']} !important;
            background-color: white !important;
            opacity: 1;
        }}

        /* 语言切换按钮 */
        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 6px;
            font-size: 0.8rem;
            padding: 0.2rem 0.5rem;
        }}

        /* --- 输入框: 沉浸式 --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(203, 213, 225, 0.6) !important; /* Slate 300 */
            border-radius: 8px !important;
            color: {THEME['text_main']};
            font-family: 'Inter', sans-serif;
        }}
        input:focus, textarea:focus {{
            border-color: {THEME['highlight']} !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
        }}

        /* --- 表格: 极简黑灰 --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: rgba(248, 250, 252, 0.5) !important;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            color: {THEME['text_light']};
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid rgba(0,0,0,0.03);
             color: {THEME['text_main']};
             font-size: 0.9rem;
        }}

        /* --- 文字排版 --- */
        h1, h2, h3 {{ 
            color: {THEME['accent']} !important; 
            font-weight: 700 !important; 
            letter-spacing: -0.04em; 
        }}
        p, label, span {{
            color: {THEME['primary']};
            letter-spacing: -0.01em;
        }}
        .caption {{ color: {THEME['text_light']} !important; font-size: 0.8rem; }}
        
        /* 状态指示点 */
        .status-dot {{
            height: 6px; width: 6px;
            background-color: {THEME['highlight']};
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            box-shadow: 0 0 8px {THEME['highlight']};
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
            <div style="text-align: center; margin-bottom: 40px;">
                <div style="font-family: 'JetBrains Mono', monospace; color: {THEME['text_light']}; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px;">EST. 2024</div>
                <h2 style="color: {THEME['accent']}; font-size: 2.2rem; margin: 0; letter-spacing: -2px;">{t('app_name')}</h2>
                <div style="height: 1px; width: 60px; background: {THEME['text_light']}; margin: 15px auto; opacity: 0.3;"></div>
                <p style="color: {THEME['text_light']}; font-size: 0.9rem;">{t('slogan')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 语言切换
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
            if st.button("🇨🇳", key="side_zh", use_container_width=True, type=t_zh):
                st.session_state.language = "ZH"; st.rerun()
        with c2:
            t_en = "primary" if st.session_state.language == "EN" else "secondary"
            if st.button("🇺🇸", key="side_en", use_container_width=True, type=t_en):
                st.session_state.language = "EN"; st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 用户信息 (Black & White style)
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="width: 40px; height: 40px; background: {THEME['accent']}; border-radius: 6px; color: white; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 700;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.9rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.7rem; color: {THEME['text_light']}; font-family: 'JetBrains Mono';">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.caption(f"{t('lbl_uid')}")
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.7rem; margin: 30px 0 10px 5px; font-weight: 700; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
        # 导航 (Primary = Active, Blue Highlight)
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
        # --- 📅 核心看板 ---
        
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.markdown(f"<h1 style='font-size: 2.2rem; font-weight: 300;'>{greet} <strong style='font-weight: 700; color:{THEME['accent']}'>{user.email.split('@')[0]}</strong></h1>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.9rem; font-family: sans-serif; opacity: 0.8;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
             with st.container(border=True):
                st.markdown(f"""
                <div style='text-align: center; padding: 40px; color: {THEME['text_light']};'>
                    <div style='font-size: 2rem; margin-bottom: 10px; opacity: 0.3;'>◌</div>
                    <p style="font-size: 0.9rem;">{t('empty_desc')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # 高通透指标卡 (High Transparency Metrics)
            m1, m2, m3, m4 = st.columns(4)
            
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            def glass_metric(label, value):
                st.markdown(f"""
                <div style="background-color: {THEME['card_bg_glass']}; backdrop-filter: blur(16px); padding: 24px; border: 1px solid {THEME['glass_border']}; border-radius: 12px;">
                    <div style="font-size: 0.7rem; color: {THEME['text_light']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">{label}</div>
                    <div style="font-size: 2.2rem; font-weight: 700; color: {THEME['highlight']}; letter-spacing: -1px; text-shadow: 0 0 20px rgba(29, 78, 216, 0.2);">{value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: glass_metric(t("metric_active"), cnt_active)
            with m2: glass_metric(t("metric_interview"), cnt_int)
            with m3: glass_metric(t("metric_offer"), cnt_off)
            with m4: glass_metric(t("metric_rate"), f"{rate:.1f}%")

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
                        use_container_width=True, hide_index=True, height=260
                    )

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    chart_df = active_df.copy()
                    chart_df['s_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['s_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    # 极简冷色盘 (Nordic Palette) - 减少蓝色占比，加入灰/黑
                    nordic_palette = ['#1E293B', '#334155', '#475569', '#94A3B8', '#1D4ED8'] 
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.8, color_discrete_sequence=nordic_palette)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}", x=0.5, y=0.5, font_size=28, showarrow=False, font_color=THEME['primary'], font_weight=700)]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 控制台
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
                        # 主操作用蓝
                        if b1.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({
                                "title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_updated")); time.sleep(0.5); st.rerun()
                        
                        # 归档用灰线
                        if b2.form_submit_button(t("btn_archive"), type="secondary"):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_archived")); time.sleep(0.5); st.rerun()

                    if st.button(t("btn_del"), type="secondary", key="del_d"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted")); time.sleep(0.5); st.rerun()

    elif st.session_state.page == 'archive':
        # --- 🗃️ 归档数据库 ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 0.9rem; font-family: sans-serif;'>{t('archive_sub')}</p>", unsafe_allow_html=True)
        
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
