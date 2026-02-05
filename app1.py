import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (完全保留功能)
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
        "slogan": "求职历程的历史注脚",
        "loading": "系统初始化...",
        "tab_login": "登 录", "tab_register": "注 册",
        "lbl_email": "邮箱地址", "lbl_pwd": "密码", "ph_email": "name@company.com",
        "btn_connect": "连接系统", "btn_create": "创建 ID",
        "auth_success": "权限已确认。", "reg_sent": "验证邮件已发送。",
        "console": "控制面板", "my_account": "账户概览",
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
        "slogan": "The Historical Footnote of Your Career.",
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
# 1. UI 配置: "Vintage Scholar & Prussian Blue"
# ==========================================
THEME = {
    "bg_color": "#F4F1EA",             # 象牙纸张色
    "card_bg": "#FFFFFF",
    "primary": "#1A2F4B",              # 普鲁士蓝
    "accent": "#9F825B",               # 烟草金
    "text_main": "#2F2F2F",            # 炭灰
    "text_light": "#8C8C8C",           # 浅灰
    "border": "#E1DBC9"                # 纸张边缘色
}

st.set_page_config(page_title="Chrono Flow", layout="wide", page_icon="📖")

def inject_custom_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Noto+Serif+SC:wght@300;500&family=JetBrains+Mono&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Noto Serif SC', serif;
            color: {THEME['text_main']};
        }}

        /* 隐藏顶部装饰 */
        header[data-testid="stHeader"], div[data-testid="stDecoration"] {{ visibility: hidden; }}

        /* 卡片设计 */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']} !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 0px !important; /* 经典书页直角 */
            padding: 2rem !important;
            box-shadow: 5px 5px 0px rgba(0,0,0,0.02);
            margin-bottom: 2rem;
        }}

        /* 侧边栏 */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['primary']} !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        section[data-testid="stSidebar"] * {{ color: #D9D9D9 !important; }}

        /* 按钮 */
        button[kind="primary"] {{
            background-color: {THEME['primary']} !important;
            border: 1px solid {THEME['primary']} !important;
            color: #FFFFFF !important;
            border-radius: 0px;
            font-family: 'Playfair Display', serif;
            letter-spacing: 1px;
            padding: 0.5rem 2rem;
        }}
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['accent']} !important;
            color: {THEME['accent']} !important;
            border-radius: 0px;
        }}
        
        /* 表单输入 */
        input, textarea, div[data-baseweb="select"] > div {{
            background-color: #FDFDFD !important;
            border-radius: 0px !important;
            border: 1px solid {THEME['border']} !important;
        }}

        /* 标题 */
        h1, h2, h3 {{ 
            font-family: 'Playfair Display', serif !important; 
            letter-spacing: -0.5px;
            color: {THEME['primary']} !important;
        }}
        
        /* 数据表 */
        div[data-testid="stDataFrame"] {{ border: 1px solid {THEME['border']}; }}

        /* Tab 样式 */
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
        }}
        .stTabs [aria-selected="true"] {{
            color: {THEME['primary']} !important;
            border-bottom-color: {THEME['primary']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. 核心后端逻辑 (保持不变)
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()
cookie_manager = stx.CookieManager(key="main_auth_manager")

if 'cookie_sync_done' not in st.session_state:
    st.write("") 
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
# 3. 登录 UI
# ==========================================
def auth_ui():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h1 style="font-size: 2.5rem; margin: 0;">{t('app_name')}</h1>
                    <p style="color: {THEME['accent']}; font-style: italic;">{t('slogan')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 恢复中英切换功能
            lang_col1, lang_col2 = st.columns(2)
            with lang_col1:
                if st.button("中文 (ZH)", use_container_width=True, type="primary" if st.session_state.language == "ZH" else "secondary"):
                    st.session_state.language = "ZH"; st.rerun()
            with lang_col2:
                if st.button("English (EN)", use_container_width=True, type="primary" if st.session_state.language == "EN" else "secondary"):
                    st.session_state.language = "EN"; st.rerun()

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
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp)
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp)
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
# 4. 主程序
# ==========================================
if not user:
    auth_ui()
else:
    with st.sidebar:
        # 侧边栏语言切换
        sc1, sc2 = st.columns(2)
        if sc1.button("ZH", key="szh"): st.session_state.language = "ZH"; st.rerun()
        if sc2.button("EN", key="sen"): st.session_state.language = "EN"; st.rerun()
        
        st.markdown(f"<div style='margin: 2rem 0; text-align: center;'><h2 style='color: white !important;'>{t('app_name')}</h2></div>", unsafe_allow_html=True)
        
        st.markdown(f"**{t('my_account')}**")
        st.caption(user.email)
        
        if st.button(t("nav_dashboard"), use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
        if st.button(t("nav_archive"), use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        st.markdown("<div style='height: 50vh;'></div>", unsafe_allow_html=True)
        if st.button(t("logout"), use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token")
            cookie_manager.delete("sb_refresh_token")
            st.rerun()

    # 数据处理逻辑 (完全保留)
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
    status_map = {"applied": t("s_applied"), "interviewing": t("s_interviewing"), "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted"), "archived": t("s_archived")}

    if st.session_state.page == 'dashboard':
        hour = datetime.datetime.now().hour
        greet = t("greeting_morning") if hour < 12 else (t("greeting_afternoon") if hour < 18 else t("greeting_evening"))
        
        st.markdown(f"<h1>{greet} <span style='color:{THEME['accent']}'>{user.email.split('@')[0]}</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{THEME['text_light']}'>{t('greeting_sub')}</p>", unsafe_allow_html=True)

        if active_df.empty:
            st.info(t("empty_desc"))
        else:
            # 指标卡片
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric(t("metric_active"), len(active_df[active_df['status'].isin(['applied', 'interviewing'])]))
            with m2: st.metric(t("metric_interview"), len(active_df[active_df['status'] == 'interviewing']))
            with m3: st.metric(t("metric_offer"), len(active_df[active_df['status'] == 'offer']))
            with m4:
                rate = (len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100) if not active_df.empty else 0
                st.metric(t("metric_rate"), f"{rate:.1f}%")

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
                    fig = px.pie(counts, values='count', names='status', hole=0.7, color_discrete_sequence=[THEME['primary'], THEME['accent'], '#D4D4D4'])
                    fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=180, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

            # 数据管理
            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                sel = st.selectbox(t("search_label"), [""] + job_list, placeholder=t("search_ph"))
                if sel:
                    row = active_df.iloc[job_list.index(sel)]
                    with st.form("edit_v5"):
                        c1, c2 = st.columns(2)
                        nt = c1.text_input(t("input_title"), value=row['title'])
                        nc = c2.text_input(t("input_company"), value=row['company'])
                        ns = c1.selectbox(t("input_status"), list(status_map.keys())[:-1], index=list(status_map.keys()).index(row['status']), format_func=lambda x: status_map[x])
                        nl = c2.text_input(t("input_loc"), value=row['location'])
                        nd = st.text_area(t("input_note"), value=row['description'])
                        
                        b1, b2, b3 = st.columns([1,1,1])
                        if b1.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({"title": nt, "company": nc, "status": ns, "location": nl, "description": nd}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()
                        if b2.form_submit_button(t("btn_archive")):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()
                        if b3.form_submit_button(t("btn_del")):
                            supabase.table("job_applications").delete().eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()

    elif st.session_state.page == 'archive':
        st.markdown(f"## {t('archive_title')}")
        if archived_df.empty:
            st.info(t("archive_empty"))
        else:
            with st.container(border=True):
                st.dataframe(archived_df, column_order=("date_str", "company", "title", "description"), use_container_width=True, hide_index=True)
                sel_a = st.selectbox(t("btn_restore"), [""] + archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist())
                if sel_a:
                    a_idx = archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist().index(sel_a)
                    if st.button(t("btn_restore"), type="primary"):
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", archived_df.iloc[a_idx]['id']).execute()
                        st.cache_data.clear(); st.rerun()
