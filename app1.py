import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (I18n System)
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        # 通用
        "app_name": "Job Tracker",
        "slogan": "保持节奏，保持平静", # 更心理学的Slogan
        "loading": "🌿 正在整理您的空间...",
        
        # 侧边栏
        "console": "导航",
        "my_account": "我的账户",
        "view_api_key": "查看连接密钥",
        "nav_dashboard": "📌 进度看板",
        "nav_archive": "🗂️ 历史归档", # 新功能
        "logout": "退出休息",
        "lang_select": "语言",

        # 欢迎区
        "greeting_morning": "早上好，",
        "greeting_afternoon": "下午好，",
        "greeting_evening": "晚上好，",
        "greeting_sub": "今天也是充满可能的一天。保持呼吸，按部就班。",

        # 看板指标
        "metric_active": "进行中",
        "metric_interview": "面试",
        "metric_offer": "收获",
        "metric_rate": "回应率",

        # 归档页 (新)
        "archive_title": "📜 申请历史归档",
        "archive_sub": "回顾过往的足迹。每一份经历都是成长的养分。",
        "filter_status": "按状态筛选",
        "filter_company": "搜索公司...",
        "total_records": "共找到 {n} 条记录",
        "col_date": "日期",
        "col_company": "公司",
        "col_role": "岗位",
        "col_status": "最终状态",

        # 管理与图表
        "chart_title": "状态分布",
        "list_title": "最近动态",
        "manage_title": "🌱 岗位管理",
        "manage_hint": "在这里更新进度，或者记录你的想法...",
        "input_title": "岗位",
        "input_company": "公司",
        "input_status": "当前阶段",
        "input_loc": "地点",
        "input_note": "备忘录 / 心得",
        "btn_save": "保存更新",
        "btn_del": "移除记录",
        
        # 状态
        "s_applied": "📝 已投递",
        "s_interviewing": "🎙️ 面试中",
        "s_offer": "✨ 收获 Offer",
        "s_rejected": "🍂 已结束",
        "s_ghosted": "🔕 暂无回音"
    },
    "EN": {
        "app_name": "Job Tracker",
        "slogan": "Stay paced, stay calm.",
        "loading": "🌿 Preparing your space...",
        
        "console": "Navigation",
        "my_account": "My Account",
        "view_api_key": "Connection Key",
        "nav_dashboard": "📌 Dashboard",
        "nav_archive": "🗂️ Archive",
        "logout": "Sign Out",
        "lang_select": "Language",

        "greeting_morning": "Good morning, ",
        "greeting_afternoon": "Good afternoon, ",
        "greeting_evening": "Good evening, ",
        "greeting_sub": "Take a deep breath. Focus on what you can control.",

        "metric_active": "Active",
        "metric_interview": "Interviews",
        "metric_offer": "Offers",
        "metric_rate": "Response Rate",

        "archive_title": "📜 Application Archive",
        "archive_sub": "Review your journey. Every step counts.",
        "filter_status": "Filter by Status",
        "filter_company": "Search Company...",
        "total_records": "Found {n} records",
        "col_date": "Date",
        "col_company": "Company",
        "col_role": "Role",
        "col_status": "Status",

        "chart_title": "Distribution",
        "list_title": "Recent Activity",
        "manage_title": "🌱 Management",
        "manage_hint": "Update progress or jot down your thoughts...",
        "input_title": "Role",
        "input_company": "Company",
        "input_status": "Stage",
        "input_loc": "Location",
        "input_note": "Notes / Thoughts",
        "btn_save": "Save Changes",
        "btn_del": "Remove",

        "s_applied": "📝 Applied",
        "s_interviewing": "🎙️ Interview",
        "s_offer": "✨ Offer",
        "s_rejected": "🍂 Ended",
        "s_ghosted": "🔕 Ghosted"
    }
}

# ==========================================
# 1. 禅意 UI 主题配置 (Zen/Calm Theme)
# ==========================================
THEME = {
    "bg_color": "#F9F9F6",           # 羊皮纸色 (更护眼)
    "sidebar_bg": "#F2F2F0",         # 极淡的灰
    "card_bg": "#FFFFFF",            # 纯白
    "primary": "#7A9E9F",            # 尤加利青 (Eucalyptus) - 镇静、专业
    "primary_light": "#E8F1F2",      # 极淡青
    "text_main": "#4A5568",          # 暖深灰 (避免纯黑刺眼)
    "text_light": "#A0AEC0",         # 柔和灰
    "accent": "#D4A373"              # 暖木色 (用于强调)
}

st.set_page_config(page_title="Job Tracker", layout="wide", page_icon="🌿")

def inject_zen_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        
        /* 全局平滑设置 */
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Inter', 'Noto Sans SC', sans-serif;
            color: {THEME['text_main']};
        }}

        /* 隐藏顶部干扰 */
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* --- 柔和卡片设计 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: 1px solid rgba(0,0,0,0.02) !important; /* 极淡边框 */
            border-radius: 20px; /* 更大的圆角 */
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02); /* 漂浮感的阴影 */
            margin-bottom: 24px;
        }}

        /* --- 侧边栏静谧风 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: none;
        }}
        
        /* 自定义导航按钮 (模拟菜单) */
        .nav-btn-selected {{
            background-color: {THEME['card_bg']};
            color: {THEME['primary']};
            padding: 12px 16px;
            border-radius: 12px;
            font-weight: 600;
            border-left: 4px solid {THEME['primary']};
            margin-bottom: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            transition: all 0.3s ease;
            cursor: default;
        }}
        .nav-btn-normal {{
            color: {THEME['text_main']};
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .nav-btn-normal:hover {{
            background-color: rgba(255,255,255,0.6);
            color: {THEME['primary']};
        }}

        /* --- 字体排版 --- */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 600 !important; 
            letter-spacing: -0.02em;
        }}
        p, label, span {{
            font-weight: 400;
            letter-spacing: 0.01em;
        }}

        /* --- 交互组件柔化 --- */
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 10px rgba(122, 158, 159, 0.2);
        }}
        .stButton>button:hover {{
            background-color: #638586;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(122, 158, 159, 0.3);
        }}
        
        /* 表单输入框去边框化 */
        input[type="text"], input[type="password"], textarea {{
            background-color: #F7F9F9;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            color: {THEME['text_main']};
        }}
        input:focus, textarea:focus {{
            background-color: #FFFFFF;
            border: 1px solid {THEME['primary']} !important;
            box-shadow: 0 0 0 2px {THEME['primary_light']} !important;
        }}

        /* --- 表格极简风 --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: transparent !important;
            border-bottom: 2px solid {THEME['primary_light']};
            font-weight: 600;
            color: {THEME['text_light']};
        }}
        </style>
    """, unsafe_allow_html=True)

inject_zen_css()

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
            st.info(t("loading"))
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
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center; color: {THEME['primary']}; margin-bottom: 5px;'>{t('app_name')}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #999; font-size: 0.9rem; margin-bottom: 30px; font-family: sans-serif;'>{t('slogan')}</p>", unsafe_allow_html=True)
            
            # 语言切换
            lang_idx = 0 if st.session_state.language == 'ZH' else 1
            lang = st.radio("Language", ["中文", "English"], index=lang_idx, horizontal=True, label_visibility="collapsed", key="auth_lang")
            if (lang == "中文" and st.session_state.language != "ZH") or (lang == "English" and st.session_state.language != "EN"):
                st.session_state.language = "ZH" if lang == "中文" else "EN"
                st.rerun()

            tab1, tab2 = st.tabs(["登录", "注册"])
            with tab1:
                with st.form("login_form"):
                    e = st.text_input("邮箱")
                    p = st.text_input("密码", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("进入空间"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.success("Welcome.")
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(str(ex))
            with tab2:
                # 注册逻辑略... (保持不变)
                with st.form("signup_form"):
                    ne = st.text_input("新邮箱")
                    np = st.text_input("设置密码", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("创建账户"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("请查看邮箱验证")
                        except Exception as ex: st.error(str(ex))

# ==========================================
# 4. 主程序 - 侧边栏与导航
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏设计 (Relaxed Navigation) ---
    with st.sidebar:
        # 语言开关
        c1, c2 = st.columns([2, 1])
        with c2:
            if st.toggle("EN", value=(st.session_state.language=='EN')):
                if st.session_state.language != 'EN': st.session_state.language = 'EN'; st.rerun()
            else:
                if st.session_state.language != 'ZH': st.session_state.language = 'ZH'; st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 用户卡片
        with st.container(border=True):
            initial = user.email[0].upper()
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="width: 40px; height: 40px; background: {THEME['primary']}; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">{initial}</div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 600; color: {THEME['text_main']}">{t('my_account')}</div>
                    <div style="font-size: 0.8rem; color: {THEME['text_light']}; overflow: hidden; text-overflow: ellipsis;">{user.email}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.code(user.id, language=None)

        # 导航菜单 (自定义样式)
        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.8rem; margin: 20px 0 10px 5px; font-weight: 600;'>{t('console').upper()}</div>", unsafe_allow_html=True)
        
        # 使用 Streamlit 按钮实现导航
        if st.button(t("nav_dashboard"), key="nav_dash", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'
            st.rerun()
            
        if st.button(t("nav_archive"), key="nav_arch", use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'
            st.rerun()

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
    
    # 状态翻译映射
    status_map = {
        "applied": t("s_applied"), "interviewing": t("s_interviewing"),
        "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted")
    }

    # ==========================================
    # 5. 页面路由
    # ==========================================
    
    # 获取问候语
    hour = datetime.datetime.now().hour
    if hour < 12: greet = t("greeting_morning")
    elif hour < 18: greet = t("greeting_afternoon")
    else: greet = t("greeting_evening")

    if st.session_state.page == 'dashboard':
        # --- 📌 仪表盘页面 ---
        st.markdown(f"## {greet} ✨")
        st.markdown(f"<div style='color:{THEME['text_light']}; margin-top: -15px; margin-bottom: 30px;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)

        if df.empty:
             st.info(t("empty_desc"))
        else:
            # 指标卡片 (更加柔和的指标)
            m1, m2, m3, m4 = st.columns(4)
            # 计算逻辑
            active_cnt = len(df[df['status'].isin(['applied', 'interviewing'])])
            interview_cnt = len(df[df['status'] == 'interviewing'])
            offer_cnt = len(df[df['status'] == 'offer'])
            resp_rate = len(df[df['status'] != 'applied']) / len(df) * 100
            
            # 使用自定义HTML渲染Metric以获得更好的样式
            def zen_metric(label, value, icon):
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid #f0f0f0;">
                    <div style="color: #A0AEC0; font-size: 0.85rem; margin-bottom: 5px;">{label}</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: {THEME['text_main']};">
                        {value} <span style="font-size: 1.2rem;">{icon}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: zen_metric(t("metric_active"), active_cnt, "🌱")
            with m2: zen_metric(t("metric_interview"), interview_cnt, "🎙️")
            with m3: zen_metric(t("metric_offer"), offer_cnt, "✨")
            with m4: zen_metric(t("metric_rate"), f"{resp_rate:.0f}%", "📈")

            st.markdown("<br>", unsafe_allow_html=True)

            # 主内容区
            c1, c2 = st.columns([1.2, 2])
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    # 准备图表数据
                    df['status_label'] = df['status'].map(lambda x: status_map.get(x, x))
                    counts = df['status_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    # 心理学配色：使用非常柔和的自然色
                    calm_colors = ['#A8DADC', '#457B9D', '#F1FAEE', '#E63946', '#1D3557'] # Ocean theme
                    # 或者更莫兰迪:
                    morandi = ['#7c9082', '#9ca8b8', '#d8c4b6', '#e0cdcf', '#aab5a9']

                    fig = px.pie(counts, values='count', names='label', hole=0.75, color_discrete_sequence=morandi)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False,
                        annotations=[dict(text=str(len(df)), x=0.5, y=0.5, font_size=24, showarrow=False, font_color=THEME['text_main'])]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                with st.container(border=True):
                    st.markdown(f"### {t('list_title')}")
                    # 显示最近的5条
                    show_df = df.head(5).copy()
                    show_df['status_display'] = show_df['status'].map(lambda x: status_map.get(x, x))
                    
                    st.dataframe(
                        show_df,
                        column_config={
                            "date_str": st.column_config.TextColumn(t("col_date"), width="small"),
                            "status_display": st.column_config.TextColumn(t("col_status"), width="medium"),
                            "company": st.column_config.TextColumn(t("col_company"), width="medium"),
                            "title": st.column_config.TextColumn(t("col_role"), width="large"),
                        },
                        column_order=("date_str", "company", "title", "status_display"),
                        use_container_width=True, hide_index=True, height=250
                    )

            # 底部：岗位管理
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                st.markdown(f"<div style='color:#999; margin-bottom: 20px;'>{t('manage_hint')}</div>", unsafe_allow_html=True)
                
                # 搜索框美化
                job_list = df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job_str = st.selectbox("Search", [""] + job_list, label_visibility="collapsed", placeholder=t("filter_company"))
                
                if selected_job_str:
                    st.markdown("---")
                    # 找到对应行
                    row_idx = job_list.index(selected_job_str)
                    row = df.iloc[row_idx]
                    
                    with st.form("edit_form"):
                        c_a, c_b = st.columns(2)
                        with c_a:
                            new_t = st.text_input(t("input_title"), value=row['title'])
                            
                            # 状态选择
                            db_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                            curr_k = row['status'] if row['status'] in db_keys else "applied"
                            new_s = st.selectbox(t("input_status"), db_keys, index=db_keys.index(curr_k), 
                                                 format_func=lambda x: status_map.get(x,x))
                        with c_b:
                            new_c = st.text_input(t("input_company"), value=row['company'])
                            new_l = st.text_input(t("input_loc"), value=row['location'])
                        
                        new_d = st.text_area(t("input_note"), value=row['description'])
                        
                        b1, b2 = st.columns([1, 6])
                        if b1.form_submit_button(t("btn_save")):
                            supabase.table("job_applications").update({
                                "title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success("Saved.")
                            time.sleep(0.5); st.rerun()
                    
                    if st.button(t("btn_del"), type="secondary"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning("Deleted.")
                        time.sleep(0.5); st.rerun()

    elif st.session_state.page == 'archive':
        # --- 🗂️ 归档页面 (新功能) ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<div style='color:{THEME['text_light']}; margin-top: -15px; margin-bottom: 30px;'>{t('archive_sub')}</div>", unsafe_allow_html=True)
        
        if df.empty:
            st.info(t("empty_desc"))
        else:
            with st.container(border=True):
                # 筛选工具栏
                c_filter1, c_filter2 = st.columns([2, 1])
                with c_filter1:
                    search_txt = st.text_input(t("filter_company"), placeholder="Google, ByteDance...")
                with c_filter2:
                    # 多选状态
                    db_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                    sel_status = st.multiselect(t("filter_status"), db_keys, format_func=lambda x: status_map.get(x,x))
                
                # 执行筛选
                filtered_df = df.copy()
                if search_txt:
                    filtered_df = filtered_df[filtered_df['company'].str.contains(search_txt, case=False, na=False)]
                if sel_status:
                    filtered_df = filtered_df[filtered_df['status'].isin(sel_status)]
                
                st.markdown(f"<div style='margin: 10px 0; color: {THEME['text_light']}; font-size: 0.9rem;'>{t('total_records').format(n=len(filtered_df))}</div>", unsafe_allow_html=True)
                
                # 完整表格展示
                if not filtered_df.empty:
                    filtered_df['status_display'] = filtered_df['status'].map(lambda x: status_map.get(x,x))
                    
                    st.dataframe(
                        filtered_df,
                        column_config={
                            "date_str": st.column_config.TextColumn(t("col_date")),
                            "company": st.column_config.TextColumn(t("col_company")),
                            "title": st.column_config.TextColumn(t("col_role")),
                            "location": st.column_config.TextColumn(t("input_loc")),
                            "status_display": st.column_config.TextColumn(t("col_status")),
                            "description": st.column_config.TextColumn(t("input_note"), width="large"),
                            "url": st.column_config.LinkColumn("Link", display_text="🔗")
                        },
                        column_order=("date_str", "company", "title", "location", "status_display", "description", "url"),
                        use_container_width=True,
                        hide_index=True,
                        height=500 # 更高的高度以供浏览
                    )
                else:
                    st.caption("No records match your filters.")
