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
        "app_name": "JOB SCOUT",
        "slogan": "理性的数据，感知的温度",
        "loading": "系统初始化中...",
        "tab_login": "登 录", "tab_register": "注 册",
        "lbl_email": "邮箱地址", "lbl_pwd": "密码", "ph_email": "name@company.com",
        "btn_connect": "连接系统", "btn_create": "创建 ID",
        "auth_success": "权限已确认。", "reg_sent": "验证邮件已发送。",
        "console": "控制中心", "my_account": "账户概览",
        "view_api_key": "API 密钥", "lbl_uid": "User ID:",
        "nav_dashboard": "核心看板", "nav_archive": "归档数据",
        "logout": "断开连接",
        "greeting_morning": "早上好。", "greeting_afternoon": "下午好。", "greeting_evening": "晚上好。",
        "greeting_sub": "保持专注。数据已同步。",
        "metric_active": "活跃申请数", "metric_interview": "面试进程",
        "metric_offer": "Offer 已获", "metric_rate": "整体回应率",
        "archive_title": "归档数据库", "archive_sub": "已封存的历史数据记录。",
        "archive_empty": "未检索到归档记录。",
        "btn_restore": "激活记录", "restore_success": "记录已恢复至活跃状态。",
        "restore_ph": "选择要恢复的记录...",
        "chart_title": "状态分布", "list_title": "近期动态追踪",
        "manage_title": "数据管理终端", "manage_hint": "点击展开以更新状态、归档或删除记录。",
        "search_label": "搜索", "search_ph": "定位活跃记录...",
        "input_title": "岗位名称", "input_company": "公司主体",
        "input_status": "当前阶段", "input_loc": "工作地点",
        "input_note": "备注 / 随笔",
        "col_date": "日期", "col_company": "公司",
        "col_role": "岗位", "col_status": "状态",
        "btn_save": "确认更新", "btn_archive": "封存归档", "btn_del": "永久删除",
        "msg_archived": "记录已封存。", "msg_updated": "数据已同步。",
        "msg_deleted": "记录已从数据库中永久移除。",
        "empty_desc": "暂无活跃数据流。等待输入。",
        "s_applied": "已投递", "s_interviewing": "面试中", "s_offer": "Offer",
        "s_rejected": "已拒绝", "s_ghosted": "无回音", "s_archived": "已归档",
        "lang_select": "语言 / Language"
    },
    "EN": {
        "app_name": "JOB SCOUT",
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
        "chart_title": "Distribution", "list_title": "Recent Activity Track",
        "manage_title": "Data Management Terminal", "manage_hint": "Click to expand for updates, archive or deletion.",
        "search_label": "Search", "search_ph": "Locate active record...",
        "input_title": "Position", "input_company": "Company",
        "input_status": "Current Phase", "input_loc": "Location",
        "input_note": "Notes / Remarks",
        "col_date": "Date Added", "col_company": "Company Name",
        "col_role": "Role", "col_status": "Status",
        "btn_save": "Update Confirm", "btn_archive": "Archive", "btn_del": "Delete Permanently",
        "msg_archived": "Record archived.", "msg_updated": "Data synchronized.",
        "msg_deleted": "Record permanently deleted from database.",
        "empty_desc": "No active data stream. Waiting for input.",
        "s_applied": "Applied", "s_interviewing": "Interview", "s_offer": "Offer",
        "s_rejected": "Rejected", "s_ghosted": "No Response", "s_archived": "Archived",
        "lang_select": "Language / 语言"
    }
}

# ==========================================
# 1. UI 主题配置
# ==========================================
THEME = {
    "bg_color": "#F7F8F9",            
    "sidebar_bg": "#1E2B2A",          
    "card_bg_glass": "rgba(255, 255, 255, 0.9)",  
    "glass_border": "rgba(0, 0, 0, 0.06)",
    "primary": "#2D3A3A",             
    "accent_gold": "#B0926A",         
    "text_main": "#2C3333",           
    "text_light": "#7A8484",          
    "highlight": "#4B6261",           
}

st.set_page_config(page_title="Nordic Flow", layout="wide", page_icon="📖")

def inject_nordic_glass_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+Pro:wght@300;400;600&family=JetBrains+Mono:wght@300;400&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: radial-gradient(circle at 2px 2px, rgba(0,0,0,0.02) 1px, transparent 0);
            background-size: 40px 40px;
            font-family: 'Source Serif Pro', 'Noto Serif SC', serif;
            color: {THEME['text_main']};
        }}
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 优化后的卡片样式 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg_glass']};
            backdrop-filter: blur(20px);
            border: 1px solid {THEME['glass_border']} !important;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
            margin-bottom: 20px;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: none;
        }}
        section[data-testid="stSidebar"] * {{
            color: #E0E4E4 !important;
        }}
        
        button[kind="primary"] {{
            background-color: {THEME['accent_gold']} !important;
            color: white !important;
            border: none !important;
            border-radius: 4px;
            padding: 0.5rem 1.2rem;
            font-family: 'Playfair Display', serif;
            font-weight: 500;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
        }}
        button[kind="primary"]:hover {{
            background-color: #967A55 !important;
            box-shadow: 0 4px 12px rgba(176, 146, 106, 0.4);
            transform: translateY(-1px);
        }}
        
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            color: {THEME['text_main']} !important;
            border-radius: 4px;
            font-family: 'Source Serif Pro', serif;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['accent_gold']} !important;
            color: {THEME['accent_gold']} !important;
        }}

        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.5) !important;
            border: none !important;
            border-bottom: 1px solid {THEME['glass_border']} !important;
            border-radius: 0px !important;
            padding-left: 0px !important;
            font-family: 'Source Serif Pro', serif;
        }}
        input:focus, textarea:focus {{
            border-bottom: 1px solid {THEME['accent_gold']} !important;
            box-shadow: none !important;
        }}

        h1, h2, h3 {{ 
            color: {THEME['primary']} !important; 
            font-family: 'Playfair Display', serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em; 
        }}
        
        /* 调整 DataFrame 样式 */
        div[data-testid="stDataFrame"] {{ 
            padding: 5px;
            background: transparent; 
        }}

        /* Expander 样式优化 */
        .streamlit-expanderHeader {{
            font-family: 'Playfair Display', serif;
            color: {THEME['primary']};
            font-weight: 600;
        }}
        
        /* Tab 样式 */
        .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
            color: {THEME['text_light']};
            border-bottom-width: 1px;
        }}
        .stTabs [aria-selected="true"] {{
            color: {THEME['accent_gold']} !important;
            border-bottom-color: {THEME['accent_gold']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_nordic_glass_css()

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

if 'cookie_sync_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"<p style='text-align:center; margin-top:100px; font-family:JetBrains Mono; color:{THEME['accent_gold']}'>// {t('loading')}</p>", unsafe_allow_html=True)
            _ = cookie_manager.get_all()
            time.sleep(1.2)
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
# 3. 辅助组件：一致性 UI 语言切换
# ==========================================
def render_language_buttons(key_prefix):
    """渲染符合主题的语言切换按钮组"""
    c1, c2 = st.columns(2)
    with c1:
        if st.button("中文", key=f"{key_prefix}_zh", type="primary" if st.session_state.language == 'ZH' else "secondary", use_container_width=True):
            st.session_state.language = 'ZH'
            st.rerun()
    with c2:
        if st.button("EN", key=f"{key_prefix}_en", type="primary" if st.session_state.language == 'EN' else "secondary", use_container_width=True):
            st.session_state.language = 'EN'
            st.rerun()

# ==========================================
# 4. 登录页 (Layout Optimized)
# ==========================================
def auth_ui():
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 顶部右侧语言切换
    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
       render_language_buttons("auth")

    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 40px;">
                <h1 style="font-size: 2.8rem; margin: 0; color: {THEME['primary']};">{t('app_name')}</h1>
                <div style="width: 30px; height: 1px; background: {THEME['accent_gold']}; margin: 20px auto;"></div>
                <p style="color: {THEME['text_light']}; font-style: italic; font-size: 1rem;">{t('slogan')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            tab1, tab2 = st.tabs([t("tab_login"), t("tab_register")])
            with tab1:
                with st.form("login_form", clear_on_submit=False):
                    e = st.text_input(t("lbl_email"), placeholder=t("ph_email"))
                    p = st.text_input(t("lbl_pwd"), type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("btn_connect"), type="primary", use_container_width=True):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.rerun()
                        except Exception as ex: st.error("Verification Failed.")
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
# 5. 主程序 (Layout Optimized)
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏布局优化 ---
    with st.sidebar:
        # 顶部：Logo 与 版本
        st.markdown(f"""
            <div style="padding: 10px 0 20px 0;">
                <h2 style="color: white !important; font-size: 1.5rem; letter-spacing: 1px;">{t('app_name')}</h2>
                <p style="color: #7A8484 !important; font-size: 0.8rem; font-family: JetBrains Mono;">V1.0(BETA) // BY YSUN</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 用户信息卡片
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 4px; margin-bottom: 30px;">
                <div style="font-size: 0.7rem; color: #7A8484; text-transform: uppercase;">Current User</div>
                <div style="font-family: 'Playfair Display'; font-size: 1.1rem; color: white;">{user.email.split('@')[0]}</div>
            </div>
        """, unsafe_allow_html=True)

        # 导航区
        st.caption("NAVIGATION")
        if st.button(t("nav_dashboard"), use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
        if st.button(t("nav_archive"), use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        # 使用分割线和空白来自然推底
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)

        # 底部：语言切换与退出
        st.caption(t("lang_select"))
        render_language_buttons("sidebar")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("logout"), type="secondary", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token")
            cookie_manager.delete("sb_refresh_token")
            st.rerun()

    # 数据加载
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

    # Dashboard 逻辑
    if st.session_state.page == 'dashboard':
        hour = datetime.datetime.now().hour
        greet = t("greeting_morning") if hour < 12 else (t("greeting_afternoon") if hour < 18 else t("greeting_evening"))
        
        st.markdown(f"""
            <h1 style='font-size: 2.5rem;'>{greet}</h1>
            <p style='color: {THEME['text_light']}; font-style: italic; margin-top: -15px;'>{t('greeting_sub')}</p>
        """, unsafe_allow_html=True)

        if active_df.empty:
            st.info(t('empty_desc'))
        else:
            # 1. 核心指标区 (Metrics)
            m1, m2, m3, m4 = st.columns(4)
            metrics_data = [
                (t("metric_active"), len(active_df[active_df['status'].isin(['applied', 'interviewing'])]), "◈"),
                (t("metric_interview"), len(active_df[active_df['status'] == 'interviewing']), "◇"),
                (t("metric_offer"), len(active_df[active_df['status'] == 'offer']), "⚓"),
                (t("metric_rate"), f"{len(active_df[active_df['status'] != 'applied'])/len(active_df)*100:.1f}%", "⌬")
            ]
            for i, (label, val, icon) in enumerate(metrics_data):
                with [m1, m2, m3, m4][i]:
                    st.markdown(f"""
                        <div style="border-left: 2px solid {THEME['accent_gold']}; padding-left: 15px; margin: 10px 0;">
                            <div style="font-size: 0.75rem; color: {THEME['text_light']}; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
                            <div style="font-family: 'Playfair Display'; font-size: 2.0rem; color: {THEME['primary']}; font-weight: 600;">{val}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 2. 核心内容区
            c_main, c_side = st.columns([3, 1])
            
            with c_main:
                st.markdown(f"### {t('list_title')}")
                with st.container(border=True):
                    show_df = active_df.head(10).copy()
                    show_df['s_disp'] = show_df['status'].map(lambda x: status_map.get(x, x))
                    st.dataframe(show_df, column_config={
                        "date_str": st.column_config.TextColumn(t("col_date"), width="small"),
                        "s_disp": st.column_config.TextColumn(t("col_status"), width="small"),
                        "company": st.column_config.TextColumn(t("col_company"), width="medium"),
                        "title": st.column_config.TextColumn(t("col_role"), width="large"),
                    }, column_order=("date_str", "company", "title", "s_disp"), use_container_width=True, hide_index=True)

            with c_side:
                st.markdown(f"### {t('chart_title')}")
                with st.container(border=True):
                    counts = active_df['status'].map(status_map).value_counts().reset_index()
                    fig = px.pie(counts, values='count', names='status', hole=0.7, color_discrete_sequence=[THEME['accent_gold'], THEME['highlight'], '#D1D5D5', '#E5E7E7'])
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), 
                        height=220, 
                        showlegend=True, 
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 3. 管理区 (Management) - 增加删除功能
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(f"⚙️ {t('manage_title')}", expanded=False):
                st.info(t('manage_hint'), icon="ℹ️")
                
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                sel = st.selectbox(t("search_label"), [""] + job_list, label_visibility="collapsed", placeholder=t("search_ph"))
                
                if sel:
                    row = active_df.iloc[job_list.index(sel)]
                    st.markdown("---")
                    with st.form("edit_v4"):
                        ca, cb = st.columns(2)
                        new_t = ca.text_input(t("input_title"), value=row['title'])
                        new_c = cb.text_input(t("input_company"), value=row['company'])
                        
                        cc, cd = st.columns(2)
                        new_s = cc.selectbox(t("input_status"), list(status_map.keys())[:-1], index=list(status_map.keys()).index(row['status']), format_func=lambda x: status_map[x])
                        new_l = cd.text_input(t("input_loc"), value=row['location'])
                        
                        new_d = st.text_area(t("input_note"), value=row['description'])
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        # 更新按钮布局：[Save] [Archive] [Delete]
                        b1, b2, b3, b4 = st.columns([1, 1, 1, 2])
                        if b1.form_submit_button(t("btn_save"), type="primary"):
                            supabase.table("job_applications").update({"title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()
                        if b2.form_submit_button(t("btn_archive")):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear(); st.rerun()
                        # 新增删除按钮
                        if b3.form_submit_button(t("btn_del")):
                            supabase.table("job_applications").delete().eq("id", row['id']).execute()
                            st.toast(t("msg_deleted"), icon="🗑️")
                            st.cache_data.clear(); st.rerun()

    elif st.session_state.page == 'archive':
        st.markdown(f"## {t('archive_title')}")
        if archived_df.empty:
            st.write(t('archive_empty'))
        else:
            with st.container(border=True):
                st.dataframe(archived_df, column_config={"date_str": t("col_date"), "company": t("col_company"), "title": t("col_role")}, 
                             column_order=("date_str", "company", "title", "description"), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                c1, c2 = st.columns([3, 1])
                with c1:
                    sel_a = st.selectbox(t("btn_restore"), [""] + archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist())
                with c2:
                    st.markdown("<br>", unsafe_allow_html=True) 
                    if sel_a:
                        a_row = archived_df.iloc[archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist().index(sel_a)]
                        if st.button(t("btn_restore"), type="primary", use_container_width=True):
                            supabase.table("job_applications").update({"status": "applied"}).eq("id", a_row['id']).execute()
                            st.cache_data.clear(); st.rerun()
