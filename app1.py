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
        "app_name": "职位申请追踪", 
        "slogan": "清晰记录每一步职业旅程",
        "loading": "正在加载...",
        "tab_login": "登录", "tab_register": "注册",
        "lbl_email": "邮箱", "lbl_pwd": "密码", "ph_email": "name@example.com",
        "btn_connect": "登录系统", "btn_create": "注册账户",
        "auth_success": "登录成功", "reg_sent": "验证邮件已发送",
        "console": "菜单", "my_account": "我的账户",
        "view_api_key": "API 密钥", "lbl_uid": "用户 ID:",
        "nav_dashboard": "概览看板", "nav_archive": "历史归档",
        "logout": "退出登录",
        "greeting_morning": "早上好，", "greeting_afternoon": "下午好，", "greeting_evening": "晚上好，",
        "greeting_sub": "欢迎回来，查看您的进度。",
        "metric_active": "进行中", "metric_interview": "面试",
        "metric_offer": "Offer", "metric_rate": "回复率",
        "archive_title": "归档记录", "archive_sub": "这里存放已结束或搁置的申请记录。",
        "archive_empty": "暂无归档记录。",
        "btn_restore": "恢复", "restore_success": "记录已恢复到看板。",
        "restore_ph": "选择要恢复的记录...",
        "chart_title": "状态分布", "list_title": "最近动态",
        "manage_title": "记录管理", "manage_hint": "修改信息或更改状态。",
        "search_label": "搜索", "search_ph": "查找记录...",
        "input_title": "岗位名称", "input_company": "公司",
        "input_status": "当前状态", "input_loc": "地点",
        "input_note": "备注",
        "col_date": "日期", "col_company": "公司",
        "col_role": "岗位", "col_status": "状态",
        "btn_save": "保存修改", "btn_archive": "归档", "btn_del": "删除",
        "msg_archived": "已归档。", "msg_updated": "保存成功。",
        "msg_deleted": "已删除。",
        "empty_desc": "暂无数据。",
        "s_applied": "已投递", "s_interviewing": "面试中", "s_offer": "Offer",
        "s_rejected": "已拒绝", "s_ghosted": "无回音", "s_archived": "已归档"
    },
    "EN": {
        "app_name": "Job Application Tracker",
        "slogan": "Track your career journey clearly.",
        "loading": "Loading...",
        "tab_login": "Login", "tab_register": "Register",
        "lbl_email": "Email", "lbl_pwd": "Password", "ph_email": "name@example.com",
        "btn_connect": "Login", "btn_create": "Sign Up",
        "auth_success": "Login successful.", "reg_sent": "Verification email sent.",
        "console": "Menu", "my_account": "Account",
        "view_api_key": "API Key", "lbl_uid": "User ID:",
        "nav_dashboard": "Dashboard", "nav_archive": "Archive",
        "logout": "Logout",
        "greeting_morning": "Good Morning,", "greeting_afternoon": "Good Afternoon,", "greeting_evening": "Good Evening,",
        "greeting_sub": "Welcome back. Check your progress.",
        "metric_active": "Active", "metric_interview": "Interviews",
        "metric_offer": "Offers", "metric_rate": "Response Rate",
        "archive_title": "Archive", "archive_sub": "Stored historical records.",
        "archive_empty": "No archived records.",
        "btn_restore": "Restore", "restore_success": "Restored successfully.",
        "restore_ph": "Select to restore...",
        "chart_title": "Distribution", "list_title": "Recent Activity",
        "manage_title": "Manage Record", "manage_hint": "Edit details or change status.",
        "search_label": "Search", "search_ph": "Find record...",
        "input_title": "Role", "input_company": "Company",
        "input_status": "Status", "input_loc": "Location",
        "input_note": "Notes",
        "col_date": "Date", "col_company": "Company",
        "col_role": "Role", "col_status": "Status",
        "btn_save": "Save", "btn_archive": "Archive", "btn_del": "Delete",
        "msg_archived": "Archived.", "msg_updated": "Saved.",
        "msg_deleted": "Deleted.",
        "empty_desc": "No data yet.",
        "s_applied": "Applied", "s_interviewing": "Interview", "s_offer": "Offer",
        "s_rejected": "Rejected", "s_ghosted": "No Response", "s_archived": "Archived"
    }
}

# ==========================================
# 1. UI 主题配置: Nordic Mineral & Linen
# ==========================================
THEME = {
    # 背景：温暖的亚麻/石灰岩色
    "bg_color": "#F4F3F0",           
    
    # 侧边栏：稍深一点的石灰
    "sidebar_bg": "#EBEAE6",         
    
    # 卡片：高通透的白，带一点暖调
    "card_bg_glass": "rgba(255, 255, 255, 0.65)", 
    
    # 边框：极细的深岩色
    "glass_border": "rgba(74, 93, 88, 0.1)",       
    
    # 核心高亮色：深海藻绿 / 矿物青 (Deep Mineral Green)
    "highlight": "#4A5D58",          
    
    # 辅助色/文字色
    "primary": "#2C3333",            # 深炭黑 (Charcoal) - 主文字
    "accent": "#1A1C1C",             # 近乎黑 - 标题
    "text_main": "#2C3333",          
    "text_light": "#7D8582",         # 矿物灰
}

st.set_page_config(page_title="Job Tracker", layout="wide", page_icon="📓")

def inject_custom_css():
    st.markdown(f"""
        <style>
        /* Sitka 字体 + 衬线体 */
        .stApp {{
            background-color: {THEME['bg_color']};
            /* 添加极其细腻的噪点纹理，增加纸张感 */
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
            font-family: 'Sitka', 'Georgia', 'Times New Roman', serif !important;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 磨砂玻璃卡片 (Mineral Glass) --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg_glass']};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid {THEME['glass_border']} !important;
            border-radius: 6px; 
            padding: 30px;
            /* 阴影改为更自然的漫射光 */
            box-shadow: 0 10px 30px rgba(44, 51, 51, 0.04);
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: 1px solid rgba(74, 93, 88, 0.08);
        }}
        
        /* --- 按钮样式 --- */
        
        /* 主按钮：矿物青 */
        button[kind="primary"] {{
            background-color: {THEME['highlight']} !important;
            color: #F4F3F0 !important; /* 字体色与背景呼应 */
            border: none !important;
            border-radius: 4px;
            padding: 0.5rem 1.5rem;
            font-family: 'Sitka', serif;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(74, 93, 88, 0.2);
        }}
        button[kind="primary"]:hover {{
            background-color: #374642 !important; /* 更深的矿物色 */
            transform: translateY(-1px);
            box-shadow: 0 6px 15px rgba(74, 93, 88, 0.3);
        }}
        
        /* 次要按钮：细线框 */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {THEME['text_light']} !important;
            color: {THEME['text_main']} !important;
            border-radius: 4px;
            font-family: 'Sitka', serif;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['highlight']} !important;
            color: {THEME['highlight']} !important;
            background-color: rgba(255,255,255,0.5) !important;
        }}

        /* 语言切换按钮 */
        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 4px;
            font-size: 0.9rem;
        }}

        /* --- 输入框 (纸张感) --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: rgba(255,255,255,0.5) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(74, 93, 88, 0.15) !important;
            border-radius: 4px !important;
            color: {THEME['text_main']};
            font-family: 'Sitka', serif !important;
        }}
        input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {{
            border-color: {THEME['highlight']} !important;
            background-color: #FFF !important;
            box-shadow: 0 0 0 1px rgba(74, 93, 88, 0.1) !important;
        }}

        /* --- 表格 (Clean & Minimal) --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: rgba(74, 93, 88, 0.03) !important;
            border-bottom: 1px solid rgba(74, 93, 88, 0.1);
            color: {THEME['text_main']};
            font-family: 'Sitka', serif;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: bold;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid rgba(74, 93, 88, 0.05);
             color: {THEME['text_main']};
             font-family: 'Sitka', serif;
        }}

        /* --- 字体排版 --- */
        h1, h2, h3 {{ 
            color: {THEME['accent']} !important; 
            font-family: 'Sitka', serif !important;
            font-weight: 700 !important; 
        }}
        p, label, span, div {{
            color: {THEME['text_main']};
            font-family: 'Sitka', serif !important;
        }}
        .caption {{ color: {THEME['text_light']} !important; font-style: italic; }}
        
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

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
                <h2 style="color: {THEME['accent']}; font-size: 2.5rem; margin: 0; font-weight: normal;">{t('app_name')}</h2>
                <div style="height: 1px; width: 40px; background: {THEME['highlight']}; margin: 20px auto; opacity: 0.5;"></div>
                <p style="color: {THEME['text_light']}; font-size: 1rem; font-style: italic;">{t('slogan')}</p>
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
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="width: 40px; height: 40px; background: {THEME['highlight']}; border-radius: 4px; color: #F4F3F0; display: flex; align-items: center; justify-content: center; font-family: 'Sitka', serif; font-size: 1.2rem;">
                    {user.email[0].upper()}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: bold; font-size: 0.9rem; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.8rem; color: {THEME['text_light']};">{user.email.split('@')[0]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.caption(f"{t('lbl_uid')}")
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.8rem; margin: 30px 0 10px 5px; font-weight: bold; text-transform: uppercase;'>{t('console')}</div>", unsafe_allow_html=True)
        
        # 导航 (Primary = Dark Mineral Green via CSS override)
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
            st.markdown(f"<h1 style='font-size: 2.5rem; font-weight: normal; margin-bottom: 0;'>{greet}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='font-size: 2.5rem; font-weight: bold; margin-top: 0;'>{user.email.split('@')[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 1rem; margin-top: 10px;'>{t('greeting_sub')}</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if active_df.empty:
             with st.container(border=True):
                st.markdown(f"""
                <div style='text-align: center; padding: 60px; color: {THEME['text_light']};'>
                    <div style='font-size: 2rem; margin-bottom: 15px; opacity: 0.3;'>✒️</div>
                    <p style="font-size: 1rem;">{t('empty_desc')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # 矿物色调指标卡
            m1, m2, m3, m4 = st.columns(4)
            
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            def paper_metric(label, value):
                st.markdown(f"""
                <div style="background-color: {THEME['card_bg_glass']}; padding: 20px; border: 1px solid {THEME['glass_border']}; border-radius: 4px;">
                    <div style="font-size: 0.8rem; color: {THEME['text_light']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">{label}</div>
                    <div style="font-size: 2rem; font-weight: bold; color: {THEME['highlight']}; font-family: 'Sitka', serif;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: paper_metric(t("metric_active"), cnt_active)
            with m2: paper_metric(t("metric_interview"), cnt_int)
            with m3: paper_metric(t("metric_offer"), cnt_off)
            with m4: paper_metric(t("metric_rate"), f"{rate:.1f}%")

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
                    
                    # 北欧自然矿物配色 (Mineral Palette)
                    mineral_palette = ['#4A5D58', '#6B705C', '#A5A58D', '#B7B7A4', '#D4D4CE'] 
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.8, color_discrete_sequence=mineral_palette)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}", x=0.5, y=0.5, font_size=28, showarrow=False, font_color=THEME['highlight'], font_family="Sitka")]
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
                        # 操作按钮
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
        # --- 🗃️ 归档页 ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 1rem; font-style: italic;'>{t('archive_sub')}</p>", unsafe_allow_html=True)
        
        if archived_df.empty:
            with st.container(border=True):
                 st.markdown(f"""
                 <div style='text-align: center; padding: 40px; color: {THEME['text_light']};'>
                    <p style="font-size: 1rem;">{t('archive_empty')}</p>
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
