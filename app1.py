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
        "app_name": "CAREER CRM", # 改个更符合CRM风格的名字
        "slogan": "智能追踪，掌控未来",
        "loading": "Loading Dashboard...",
        
        "tab_login": "登 录",
        "tab_register": "注 册",
        "lbl_email": "工作邮箱",
        "lbl_pwd": "密码",
        "ph_email": "name@example.com",
        "btn_connect": "进入系统",
        "btn_create": "创建账户",
        "auth_success": "身份验证通过",
        "reg_sent": "验证邮件已发送",
        
        "console": "MAIN MENU",
        "my_account": "PROFILE",
        "view_api_key": "API 连接密钥",
        "lbl_uid": "User ID:",
        "nav_dashboard": "概览看板",
        "nav_archive": "历史归档",
        "logout": "安全退出",

        "greeting_morning": "Good Morning,",
        "greeting_afternoon": "Good Afternoon,",
        "greeting_evening": "Good Evening,",
        "greeting_sub": "欢迎回来。这是您今天的申请进度摘要。",

        "metric_active": "活跃申请",
        "metric_interview": "面试日程",
        "metric_offer": "Offer 收录",
        "metric_rate": "反馈转化率",

        "archive_title": "Archived Data",
        "archive_sub": "已归档的历史申请记录数据库。",
        "archive_empty": "当前无归档数据。",
        "btn_restore": "恢复记录",
        "restore_success": "记录已恢复至活跃看板。",
        "restore_ph": "搜索并恢复记录...",

        "chart_title": "申请漏斗分析",
        "list_title": "最新动态追踪",
        "manage_title": "详情管理",
        "manage_hint": "编辑详细信息或变更生命周期状态。",
        "search_label": "搜索",
        "search_ph": "查找活跃岗位...",
        
        "input_title": "岗位名称",
        "input_company": "公司 / 机构",
        "input_status": "当前阶段",
        "input_loc": "工作地点",
        "input_note": "备注说明",
        
        "col_date": "添加日期",
        "col_company": "公司名称",
        "col_role": "岗位",
        "col_status": "当前状态",
        
        "btn_save": "保存变更",
        "btn_archive": "移入归档",
        "btn_del": "删除记录",
        
        "msg_archived": "记录已归档。",
        "msg_updated": "数据已更新。",
        "msg_deleted": "记录已删除。",
        "empty_desc": "暂无活跃数据，请开始追踪。",

        "s_applied": "已投递",
        "s_interviewing": "面试中",
        "s_offer": "Offer",
        "s_rejected": "已拒绝",
        "s_ghosted": "无回音",
        "s_archived": "已归档"
    },
    "EN": {
        "app_name": "CAREER CRM",
        "slogan": "Track smartly, control the future.",
        "loading": "Loading Dashboard...",
        
        "tab_login": "LOGIN",
        "tab_register": "REGISTER",
        "lbl_email": "Work Email",
        "lbl_pwd": "Password",
        "ph_email": "name@example.com",
        "btn_connect": "Dashboard Login",
        "btn_create": "Create Account",
        "auth_success": "Authenticated.",
        "reg_sent": "Verification email sent.",

        "console": "MAIN MENU",
        "my_account": "PROFILE",
        "view_api_key": "API Access Key",
        "lbl_uid": "User ID:",
        "nav_dashboard": "Overview",
        "nav_archive": "Archive",
        "logout": "Log Out",

        "greeting_morning": "Good Morning,",
        "greeting_afternoon": "Good Afternoon,",
        "greeting_evening": "Good Evening,",
        "greeting_sub": "Welcome back. Here is your application summary.",

        "metric_active": "Active Jobs",
        "metric_interview": "Interviews",
        "metric_offer": "Offers",
        "metric_rate": "Response Rate",

        "archive_title": "Archived Data",
        "archive_sub": "Stored historical application records.",
        "archive_empty": "No archived records found.",
        "btn_restore": "Restore",
        "restore_success": "Restored to active dashboard.",
        "restore_ph": "Search to restore...",

        "chart_title": "Funnel Analytics",
        "list_title": "Recent Activities",
        "manage_title": "Details Management",
        "manage_hint": "Edit details or change lifecycle status.",
        "search_label": "Search",
        "search_ph": "Search active jobs...",
        
        "input_title": "Position",
        "input_company": "Company",
        "input_status": "Stage",
        "input_loc": "Location",
        "input_note": "Notes",
        
        "col_date": "Date Added",
        "col_company": "Company Name",
        "col_role": "Role",
        "col_status": "Status",
        
        "btn_save": "Save Changes",
        "btn_archive": "Archive",
        "btn_del": "Delete",
        
        "msg_archived": "Record archived.",
        "msg_updated": "Data updated.",
        "msg_deleted": "Record deleted.",
        "empty_desc": "No active data found.",

        "s_applied": "Applied",
        "s_interviewing": "Interview",
        "s_offer": "Offer",
        "s_rejected": "Rejected",
        "s_ghosted": "No Response",
        "s_archived": "Archived"
    }
}

# ==========================================
# 1. UI 主题配置: "Loanza Fintech Style"
# ==========================================
THEME = {
    "bg_color": "#F4F7FE",           # Loanza 标志性的淡蓝灰背景
    "sidebar_bg": "#FFFFFF",         # 纯白侧边栏
    "card_bg": "#FFFFFF",            # 纯白卡片
    "primary": "#4318FF",            # Electric Blue/Purple (电光紫) - 核心特征
    "primary_light": "#F2EFFF",      # 极淡的紫色背景，用于按钮悬停
    "text_main": "#1B2559",          # 深海军蓝 (Dark Navy) - 替代纯黑，更高级
    "text_light": "#A3AED0",         # 柔和的蓝灰文字
    "success": "#05CD99",            # 鲜艳的薄荷绿
    "card_shadow": "0px 18px 40px rgba(112, 144, 176, 0.12)" # 弥散阴影
}

st.set_page_config(page_title="Career CRM", layout="wide", page_icon="📊")

def inject_loanza_css():
    st.markdown(f"""
        <style>
        /* 引入 DM Sans 字体 - 现代 SaaS 常用字体 */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'DM Sans', sans-serif;
            color: {THEME['text_main']};
        }}

        /* 隐藏原生头部 */
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 核心卡片样式 (Borderless & Soft Shadow) --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: none !important; /* 去掉边框 */
            border-radius: 20px; /* 大圆角 */
            padding: 24px;
            box-shadow: {THEME['card_shadow']}; /* 关键：弥散阴影 */
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            box-shadow: 10px 0 30px rgba(0,0,0,0.02); /* 侧边栏微弱阴影 */
            border-right: none;
        }}
        
        /* --- 按钮 (Vibrant & Rounded) --- */
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 16px; /* 较圆润 */
            padding: 0.6rem 1.5rem;
            font-weight: 700;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            background-color: #3311db; /* 深一点的紫 */
            box-shadow: 0 10px 20px rgba(67, 24, 255, 0.2); /* 彩色投影 */
            transform: translateY(-2px);
            color: white !important;
        }}
        
        /* 次要按钮 */
        button[kind="secondary"] {{
            background-color: #F4F7FE !important; /* 淡灰背景 */
            border: none !important;
            color: {THEME['primary']} !important;
            font-weight: 700 !important;
        }}
        button[kind="secondary"]:hover {{
            background-color: {THEME['primary_light']} !important;
            color: {THEME['primary']} !important;
        }}

        /* 语言切换按钮 (Pill Style) */
        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 50px;
            font-size: 0.8rem;
            padding: 0.3rem 0.8rem;
        }}

        /* --- 输入框 (Clean & Filled) --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: #F4F7FE; /* 浅色填充背景 */
            border: 1px solid transparent !important;
            border-radius: 16px !important;
            color: {THEME['text_main']};
            font-weight: 500;
        }}
        input:focus, textarea:focus {{
            background-color: #FFFFFF;
            border: 1px solid {THEME['primary']} !important;
            box-shadow: 0 0 0 3px {THEME['primary_light']} !important;
        }}

        /* --- 表格 (Modern SaaS Grid) --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: white !important;
            border-bottom: 1px solid #E9EDF7;
            color: {THEME['text_light']};
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 700;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid #F4F7FE;
             color: {THEME['text_main']};
             font-weight: 500;
        }}

        /* --- 字体排版 --- */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 700 !important; 
            letter-spacing: -0.02em;
        }}
        p, label {{
            color: {THEME['text_light']};
            font-weight: 500;
        }}
        
        /* 自定义指标卡样式 */
        .metric-card {{
            background: white;
            border-radius: 20px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            /* 移除了额外的阴影，由容器统一管理 */
        }}
        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }}
        </style>
    """, unsafe_allow_html=True)

inject_loanza_css()

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
            # 标题区
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, {THEME['primary']} 0%, #868CFF 100%); border-radius: 12px; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px;">C</div>
                <h2 style="color: {THEME['text_main']}; font-size: 1.8rem; margin: 0;">{t('app_name')}</h2>
                <p style="color: {THEME['text_light']}; font-size: 0.9rem; margin-top: 5px;">{t('slogan')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 语言切换
            c1, c2 = st.columns(2)
            with c1:
                t_zh = "primary" if st.session_state.language == "ZH" else "secondary"
                if st.button("🇨🇳 中文", key="auth_zh", use_container_width=True, type=t_zh):
                    st.session_state.language = "ZH"; st.rerun()
            with c2:
                t_en = "primary" if st.session_state.language == "EN" else "secondary"
                if st.button("🇺🇸 English", key="auth_en", use_container_width=True, type=t_en):
                    st.session_state.language = "EN"; st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs([t("tab_login"), t("tab_register")])
            with tab1:
                with st.form("login_form"):
                    e = st.text_input(t("lbl_email"), placeholder=t("ph_email"))
                    p = st.text_input(t("lbl_pwd"), type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("btn_connect")):
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
                    if st.form_submit_button(t("btn_create")):
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
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="width: 48px; height: 48px; background: {THEME['primary_light']}; border-radius: 50%; color: {THEME['primary']}; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.9rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.75rem; color: {THEME['text_light']};">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.caption(f"{t('lbl_uid')}")
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.75rem; margin: 30px 0 10px 5px; font-weight: 700; letter-spacing: 1px;'>{t('console')}</div>", unsafe_allow_html=True)
        
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
        # --- 📅 看板 ---
        
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.markdown(f"<h1 style='font-size: 2rem; color: {THEME['text_main']}'>{greet}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 1rem;'>{t('greeting_sub')}</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
             st.markdown(f"""
             <div style='text-align: center; padding: 60px; color: {THEME['text_light']}; background: white; border-radius: 20px; box-shadow: {THEME['card_shadow']};'>
                <div style='font-size: 2rem; margin-bottom: 10px; opacity: 0.5;'>📊</div>
                <p style="font-size: 0.9rem;">{t('empty_desc')}</p>
             </div>
             """, unsafe_allow_html=True)
        else:
            # 现代卡片式指标
            m1, m2, m3, m4 = st.columns(4)
            
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            # 使用 HTML 渲染 Loanza 风格的指标卡
            def loanza_metric(label, value, icon, bg_color, icon_color):
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon" style="background-color: {bg_color}; color: {icon_color};">
                        {icon}
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: {THEME['text_light']}; margin-bottom: 2px;">{label}</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: {THEME['text_main']};">{value}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: loanza_metric(t("metric_active"), cnt_active, "⚡", "#F4F7FE", THEME['primary'])
            with m2: loanza_metric(t("metric_interview"), cnt_int, "📅", "#FFF7EB", "#FFAA0B") # Orange
            with m3: loanza_metric(t("metric_offer"), cnt_off, "🎉", "#EEFBF6", "#05CD99") # Green
            with m4: loanza_metric(t("metric_rate"), f"{rate:.1f}%", "📈", "#EBF3FE", "#2B3674") # Navy

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
                        use_container_width=True, hide_index=True, height=250
                    )

            with c_side:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    chart_df = active_df.copy()
                    chart_df['s_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['s_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    # Loanza 风格配色
                    tech_palette = ['#4318FF', '#6AD2FF', '#EFF4FB', '#A3AED0', '#1B2559'] 
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.7, color_discrete_sequence=tech_palette)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}", x=0.5, y=0.5, font_size=20, showarrow=False, font_color=THEME['text_main'], font_weight="bold")]
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
                sel_archive = st.selectbox(t("btn_restore"), [""] + archive_list, label_visibility="collapsed", placeholder=t("restore_ph"))
                
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
