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

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# ==========================================
# 1. UI 主题配置: "Nordic Glass & Sitka Edition"
# ==========================================
THEME = {
    "bg_color": "#F3F4F6",           # 冷石灰 (Stone 100)
    "sidebar_bg": "rgba(255, 255, 255, 0.75)", 
    "card_bg_glass": "rgba(255, 255, 255, 0.45)",
    "glass_border": "rgba(255, 255, 255, 0.6)",
    "primary": "#334155",            # 板岩 (Slate 700)
    "accent": "#0F172A",             # 黑曜石 (Slate 900) - 用于替代原蓝色作为主色调
    "highlight": "#1D4ED8",          # 主内容区保留的深蓝点缀
    "text_main": "#111827",          # 接近纯黑
    "text_light": "#64748B",         # 沉稳灰
}

st.set_page_config(page_title="Nordic Core", layout="wide", page_icon="🧊")

def inject_nordic_glass_css():
    st.markdown(f"""
        <style>
        /* 引入 Sitka 类似的衬线字体感，并设定备用字体 */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: linear-gradient(120deg, #E2E8F0 0%, #F8FAFC 100%);
            /* 强制应用 Sitka 字体 */
            font-family: 'Sitka Text', 'Sitka Heading', 'Georgia', serif !important;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 极度通透的毛玻璃卡片 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg_glass']};
            backdrop-filter: blur(24px) saturate(140%);
            -webkit-backdrop-filter: blur(24px) saturate(140%);
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.8) !important;
            border-radius: 16px; 
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.03);
            margin-bottom: 24px;
        }}

        /* --- 侧边栏样式调整：去除蓝色 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        /* 侧边栏按钮逻辑 */
        section[data-testid="stSidebar"] button[kind="primary"] {{
            background-color: {THEME['accent']} !important; /* 使用深色替代蓝色 */
            color: white !important;
            box-shadow: none !important;
            border: none !important;
        }}
        
        section[data-testid="stSidebar"] button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            color: {THEME['text_main']} !important;
        }}
        
        /* --- 全局按钮 --- */
        button[kind="primary"] {{
            background-color: {THEME['highlight']} !important;
            font-family: 'Sitka Text', serif;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
        }}

        /* --- 输入框 --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.5) !important;
            border-radius: 8px !important;
            font-family: 'Sitka Text', serif !important;
        }}

        /* --- 文字排版 --- */
        h1, h2, h3 {{ 
            font-family: 'Sitka Heading', 'Georgia', serif !important;
            color: {THEME['accent']} !important; 
            font-weight: 700 !important; 
            letter-spacing: -0.02em; 
        }}
        p, label, span, div {{
            font-family: 'Sitka Text', serif;
        }}
        
        /* 代码块保持等宽 */
        code {{ font-family: 'JetBrains Mono', monospace !important; }}
        </style>
    """, unsafe_allow_html=True)

inject_nordic_glass_css()

# ==========================================
# 2. 核心逻辑 (Supabase & Auth)
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
# 3. 登录页 UI
# ==========================================
def auth_ui():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 40px;">
                <div style="font-family: 'JetBrains Mono', monospace; color: {THEME['text_light']}; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px;">EST. 2024</div>
                <h2 style="margin: 0; letter-spacing: -1px;">{t('app_name')}</h2>
                <div style="height: 1px; width: 60px; background: {THEME['text_light']}; margin: 15px auto; opacity: 0.3;"></div>
                <p style="color: {THEME['text_light']}; font-size: 0.9rem;">{t('slogan')}</p>
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
                    if st.form_submit_button(t("btn_connect"), type="primary", use_container_width=True):
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
                    if st.form_submit_button(t("btn_create"), type="primary", use_container_width=True):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success(t("reg_sent"))
                        except Exception as ex: st.error(str(ex))

# ==========================================
# 4. 主程序 & 侧边栏
# ==========================================
if not user:
    auth_ui()
else:
    with st.sidebar:
        st.markdown(f"### {t('app_name')}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 用户 Profile
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 32px; height: 32px; background: {THEME['accent']}; border-radius: 4px; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.85rem;">{t('my_account')}</div>
                    <div style="font-size: 0.7rem; color: {THEME['text_light']}; font-family: 'JetBrains Mono';">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.7rem; margin: 25px 0 10px 5px; font-weight: 700; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
        # 导航按钮 (注意：CSS 已将此处的 Primary 改为深黑色)
        if st.button(t("nav_dashboard"), key="nav_d", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
            
        if st.button(t("nav_archive"), key="nav_a", use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True)
        
        # 底部语言切换
        lc1, lc2 = st.columns(2)
        if lc1.button("ZH", use_container_width=True, small=True): st.session_state.language = "ZH"; st.rerun()
        if lc2.button("EN", use_container_width=True, small=True): st.session_state.language = "EN"; st.rerun()
        
        if st.button(t("logout"), type="secondary", hide_label=False, use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token")
            cookie_manager.delete("sb_refresh_token")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
            st.rerun()

    # --- 数据逻辑 ---
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
    active_df = df[df['status'] != 'archived'] if not df.empty else pd.DataFrame()
    archived_df = df[df['status'] == 'archived'] if not df.empty else pd.DataFrame()

    status_map = {
        "applied": t("s_applied"), "interviewing": t("s_interviewing"),
        "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted"),
        "archived": t("s_archived")
    }

    # ==========================================
    # 5. 页面路由: DASHBOARD
    # ==========================================
    if st.session_state.page == 'dashboard':
        hour = datetime.datetime.now().hour
        greet = t("greeting_morning") if hour < 12 else (t("greeting_afternoon") if hour < 18 else t("greeting_evening"))
        
        st.markdown(f"<h1>{greet} {user.email.split('@')[0]}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{THEME['text_light']};'>{t('greeting_sub')}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
            st.info(t("empty_desc"))
        else:
            # 指标卡
            m1, m2, m3, m4 = st.columns(4)
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = (len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100) if len(active_df)>0 else 0
            
            def glass_metric(label, value):
                st.markdown(f"""
                <div style="background-color: {THEME['card_bg_glass']}; backdrop-filter: blur(16px); padding: 20px; border: 1px solid {THEME['glass_border']}; border-radius: 12px;">
                    <div style="font-size: 0.75rem; color: {THEME['text_light']}; text-transform: uppercase; margin-bottom: 8px;">{label}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {THEME['accent']};">{value}</div>
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
                    show_df = active_df.head(8).copy()
                    show_df['s_disp'] = show_df['status'].map(lambda x: status_map.get(x, x))
                    st.dataframe(
                        show_df,
                        column_config={
                            "date_str": t("col_date"),
                            "company": t("col_company"),
                            "title": t("col_role"),
                            "s_disp": t("col_status")
                        },
                        column_order=("date_str", "company", "title", "s_disp"),
                        use_container_width=True, hide_index=True
                    )

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    counts = active_df['status'].map(status_map).value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    fig = px.pie(counts, values='count', names='label', hole=0.7, 
                                 color_discrete_sequence=['#0F172A', '#334155', '#475569', '#94A3B8'])
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220, showlegend=False,
                                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

            # 管理面板
            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected = st.selectbox(t("search_label"), [""] + job_list, placeholder=t("search_ph"))
                
                if selected:
                    row = active_df.iloc[job_list.index(selected)]
                    with st.form("edit_form"):
                        col_a, col_b = st.columns(2)
                        new_t = col_a.text_input(t("input_title"), value=row['title'])
                        new_c = col_b.text_input(t("input_company"), value=row['company'])
                        db_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                        new_s = st.selectbox(t("input_status"), db_keys, index=db_keys.index(row['status']) if row['status'] in db_keys else 0, format_func=lambda x: status_map.get(x,x))
                        
                        if st.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({"title": new_t, "company": new_c, "status": new_s}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.success(t("msg_updated")); time.sleep(0.5); st.rerun()

    # ==========================================
    # 6. 页面路由: ARCHIVE
    # ==========================================
    elif st.session_state.page == 'archive':
        st.markdown(f"## {t('archive_title')}")
        if archived_df.empty:
            st.info(t("archive_empty"))
        else:
            st.dataframe(archived_df[["date_str", "company", "title", "description"]], use_container_width=True, hide_index=True)
            
            sel_archive = st.selectbox(t("btn_restore"), [""] + archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist())
            if sel_archive:
                if st.button(t("btn_restore"), type="primary"):
                    rid = archived_df.iloc[0]['id'] # 简化逻辑
                    supabase.table("job_applications").update({"status": "applied"}).eq("id", rid).execute()
                    st.cache_data.clear(); st.rerun()
