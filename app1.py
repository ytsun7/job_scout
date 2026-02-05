import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化与文案配置 (I18n) - 语气更温暖
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        "app_name": "My Career Journal", # 改个更有温度的名字
        "slogan": "记录每一次尝试，拥抱每一种可能",
        "loading": "☕ 正在准备您的书桌...",
        
        "console": "书签",
        "my_account": "通行证",
        "view_api_key": "🔑 连接密钥",
        "nav_dashboard": "📅 今日看板",
        "nav_archive": "🗃️ 记忆归档",
        "logout": "合上日记",

        "greeting_morning": "早安,",
        "greeting_afternoon": "午安,",
        "greeting_evening": "晚安,",
        "greeting_sub": "深呼吸。今天也是闪闪发光的一天 ✨",

        "metric_active": "正在进行",
        "metric_interview": "约见",
        "metric_offer": "好消息",
        "metric_rate": "回音",

        "archive_title": "🗃️ 记忆归档室",
        "archive_sub": "这里存放着过去的足迹。每一段经历都算数。",
        "archive_empty": "📭 归档室里空空如也，去写下新故事吧。",
        "btn_restore": "♻️ 放回桌面",
        "restore_success": "已把这条记录放回桌面",

        "chart_title": "我的状态分布",
        "list_title": "最近的足迹",
        "manage_title": "✍️ 记录与整理",
        "manage_hint": "修改进度，或者写下当时的心情...",
        "input_title": "想去的岗位",
        "input_company": "公司",
        "input_status": "到了哪一步",
        "input_loc": "城市",
        "input_note": "随笔 / 备忘",
        
        "col_date": "添加日期",
        "col_company": "公司名称",
        "col_role": "岗位",
        "col_status": "当前状态",
        
        "btn_save": "💾 保存笔记",
        "btn_archive": "📂 封存入库",
        "btn_del": "🗑️ 擦除记录",
        
        "msg_archived": "已封存，休息一下吧",
        "msg_updated": "笔记已更新",
        "msg_deleted": "痕迹已擦除",
        "empty_desc": "📝 还没有活跃的记录。去寻找心动的机会吧！",

        "s_applied": "🌱 已投递",
        "s_interviewing": "🎙️ 交流中",
        "s_offer": "🎉 收获 Offer",
        "s_rejected": "🍂 已翻篇",
        "s_ghosted": "🔕 暂无回音",
        "s_archived": "🔒 已封存"
    },
    "EN": {
        "app_name": "My Career Journal",
        "slogan": "Record every step, embrace every possibility.",
        "loading": "☕ Preparing your desk...",
        
        "console": "Bookmarks",
        "my_account": "Passport",
        "view_api_key": "🔑 Key",
        "nav_dashboard": "📅 Today's View",
        "nav_archive": "🗃️ The Vault",
        "logout": "Close Journal",

        "greeting_morning": "Good morning,",
        "greeting_afternoon": "Good afternoon,",
        "greeting_evening": "Good evening,",
        "greeting_sub": "Breathe in. You are doing great today ✨",

        "metric_active": "Active",
        "metric_interview": "Meeting",
        "metric_offer": "Good News",
        "metric_rate": "Replies",

        "archive_title": "🗃️ The Archive",
        "archive_sub": "Stored memories. Every experience counts.",
        "archive_empty": "📭 The vault is empty. Go write new stories.",
        "btn_restore": "♻️ Restore",
        "restore_success": "Restored to desk",

        "chart_title": "My Journey Stats",
        "list_title": "Recent Footprints",
        "manage_title": "✍️ Edit & Reflect",
        "manage_hint": "Update progress or jot down your thoughts...",
        "input_title": "Role",
        "input_company": "Company",
        "input_status": "Stage",
        "input_loc": "City",
        "input_note": "Diary / Notes",
        
        "col_date": "Date Added",
        "col_company": "Company Name",
        "col_role": "Role",
        "col_status": "Status",
        
        "btn_save": "💾 Save Note",
        "btn_archive": "📂 Archive",
        "btn_del": "🗑️ Erase",
        
        "msg_archived": "Archived. Take a rest.",
        "msg_updated": "Note updated",
        "msg_deleted": "Erased",
        "empty_desc": "📝 No active records yet. Go find some sparks!",

        "s_applied": "🌱 Applied",
        "s_interviewing": "🎙️ Talking",
        "s_offer": "🎉 Offer",
        "s_rejected": "🍂 Past",
        "s_ghosted": "🔕 Silent",
        "s_archived": "🔒 Archived"
    }
}

# ==========================================
# 1. "Cozy Journal" UI 主题配置
# ==========================================
THEME = {
    "bg_color": "#FFFBF0",           # 暖蛋壳色/米黄 (Warm Eggshell)
    "sidebar_bg": "#F7F3E8",         # 稍深一点的米色
    "card_bg": "#FFFFFF",            # 纯白卡片
    "primary": "#88B04B",            # 草木绿 (Greenery) - 治愈
    "primary_dark": "#607d34",
    "accent_blue": "#8CACD3",        # 雾霾蓝
    "accent_pink": "#EFAAC4",        # 柔粉
    "accent_orange": "#F4A261",      # 暖橙
    "text_main": "#595959",          # 暖深灰 (不刺眼)
    "text_light": "#9D9D9D",
    "border_color": "#EFE6D5"        # 纸张边框色
}

st.set_page_config(page_title="Career Journal", layout="wide", page_icon="📔")

def inject_cozy_css():
    st.markdown(f"""
        <style>
        /* 引入圆体字 Quicksand */
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            background-image: radial-gradient({THEME['border_color']} 1px, transparent 1px);
            background-size: 20px 20px; /* 点阵纸纹理 */
            font-family: 'Quicksand', 'Noto Sans SC', sans-serif;
            color: {THEME['text_main']};
        }}

        /* 隐藏原生头部 */
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* --- 卡片 (Card) --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: 2px solid {THEME['border_color']} !important;
            border-radius: 24px; /* 更大的圆角 */
            padding: 30px;
            box-shadow: 4px 4px 0px rgba(239, 230, 213, 0.8); /* 卡通风格的硬阴影 */
            margin-bottom: 24px;
        }}

        /* --- 侧边栏 (Sidebar) --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: 2px solid {THEME['border_color']};
        }}
        
        /* --- 按钮 (Buttons) - 像糖果/药丸 --- */
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 50px; /* 胶囊形状 */
            padding: 0.6rem 1.5rem;
            font-weight: 700;
            transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Q弹效果 */
            box-shadow: 0 4px 6px rgba(136, 176, 75, 0.3);
        }}
        .stButton>button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(136, 176, 75, 0.4);
            background-color: {THEME['primary_dark']};
        }}
        
        /* 次要按钮 */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 2px dashed {THEME['text_light']} !important;
            color: {THEME['text_light']} !important;
            box-shadow: none !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['accent_orange']} !important;
            color: {THEME['accent_orange']} !important;
            background-color: #FFF !important;
        }}

        /* --- 语言切换按钮 (Flags) --- */
        /* 让它们看起来像贴纸 */
        div[data-testid="stHorizontalBlock"] button {{
            border-radius: 16px;
            font-size: 1.1rem;
        }}

        /* --- 表单输入框 (Inputs) --- */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] > div {{
            background-color: #FDFDFD;
            border: 2px solid {THEME['border_color']} !important;
            border-radius: 16px !important;
            color: {THEME['text_main']};
            transition: all 0.2s;
        }}
        input:focus, textarea:focus {{
            border-color: {THEME['primary']} !important;
            background-color: #FFF;
        }}

        /* --- 表格 (Notebook Style) --- */
        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: transparent !important;
            border-bottom: 2px dashed {THEME['primary']}; /* 虚线表头 */
            font-weight: 700;
            color: {THEME['primary']};
            text-transform: uppercase;
            font-size: 0.85rem;
        }}
        div[class*="stDataFrame"] div[class*="DataCell"] {{
             border-bottom: 1px solid #F0F0F0; /* 横线本子效果 */
        }}
        
        /* 标题字体 */
        h1, h2, h3 {{ 
            color: {THEME['text_main']} !important; 
            font-weight: 700 !important; 
        }}
        </style>
    """, unsafe_allow_html=True)

inject_cozy_css()

# ==========================================
# 2. 核心逻辑 (Supabase & Cookie)
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
# 3. 登录页 UI (Warm & Inviting)
# ==========================================
def auth_ui():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            # 卡通风格标题
            st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="color: {THEME['primary']}; font-size: 2.5rem; margin-bottom: 0;">📔</h1>
                <h2 style="color: {THEME['text_main']}; margin-top: 0;">{t('app_name')}</h2>
                <p style="color: {THEME['text_light']}; font-style: italic;">{t('slogan')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 语言切换 (国旗贴纸)
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
            tab1, tab2 = st.tabs(["🔑 登录", "✨ 注册"])
            with tab1:
                with st.form("login_form"):
                    e = st.text_input("Email")
                    p = st.text_input("Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("📖 打开日记"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp, key="set_at")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp, key="set_rt")
                                st.success("Welcome back.")
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(str(ex))
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input("New Email")
                    np = st.text_input("New Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("✨ 开始记录"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("Please check your email.")
                        except Exception as ex: st.error(str(ex))

# ==========================================
# 4. 主程序 - 舒适手帐风
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏 (Bookmark Style) ---
    with st.sidebar:
        # 国旗切换
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
        # 用户卡片 (ID Card)
        with st.container(border=True):
            initial = user.email[0].upper()
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
                <div style="width: 60px; height: 60px; background: {THEME['primary']}; border-radius: 50%; border: 4px solid #FFF; box-shadow: 0 4px 8px rgba(0,0,0,0.1); color: white; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;">
                    {initial}
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: 700; color: {THEME['text_main']}; font-size: 0.9rem;">{user.email.split('@')[0]}</div>
                    <div style="font-size: 0.75rem; color: {THEME['text_light']}; font-family: monospace;">ID: {user.id[:8]}...</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(t("view_api_key")):
                st.code(user.id, language=None)

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.8rem; margin: 30px 0 10px 10px; font-weight: 700; letter-spacing: 1px;'>{t('console').upper()}</div>", unsafe_allow_html=True)
        
        # 导航按钮
        if st.button(t("nav_dashboard"), key="nav_d", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
            st.session_state.page = 'dashboard'; st.rerun()
            
        if st.button(t("nav_archive"), key="nav_a", use_container_width=True, type="primary" if st.session_state.page == 'archive' else "secondary"):
            st.session_state.page = 'archive'; st.rerun()

        st.markdown("<div style='flex-grow: 1; height: 80px;'></div>", unsafe_allow_html=True)
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
        # --- 📅 看板 (My Day) ---
        
        # 头部欢迎
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.markdown(f"<h1 style='font-size: 2.2rem;'>{greet} <span style='color:{THEME['primary']}'>{user.email.split('@')[0]}</span> 🌿</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{THEME['text_light']}; font-size: 1.1rem;'>{t('greeting_sub')}</p>", unsafe_allow_html=True)
        
        if active_df.empty:
             st.markdown(f"""
             <div style='text-align: center; padding: 40px; color: {THEME['text_light']};'>
                <div style='font-size: 4rem;'>🪁</div>
                <p>{t('empty_desc')}</p>
             </div>
             """, unsafe_allow_html=True)
        else:
            # 贴纸风格的指标卡 (Stickers)
            m1, m2, m3, m4 = st.columns(4)
            
            # 计算
            cnt_active = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            cnt_int = len(active_df[active_df['status'] == 'interviewing'])
            cnt_off = len(active_df[active_df['status'] == 'offer'])
            rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
            # 渲染贴纸函数
            def sticker(label, value, emoji, bg_color, text_color):
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 20px; border-radius: 20px; text-align: center; box-shadow: 0 4px 0 rgba(0,0,0,0.05); transition: transform 0.2s;">
                    <div style="font-size: 2rem; margin-bottom: 5px;">{emoji}</div>
                    <div style="font-weight: 700; font-size: 1.5rem; color: {text_color};">{value}</div>
                    <div style="font-size: 0.8rem; color: {text_color}; opacity: 0.8;">{label}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m1: sticker(t("metric_active"), cnt_active, "🌱", "#E8F5E9", "#2E7D32") # 浅绿
            with m2: sticker(t("metric_interview"), cnt_int, "🎙️", "#FFF3E0", "#EF6C00") # 浅橙
            with m3: sticker(t("metric_offer"), cnt_off, "✨", "#F3E5F5", "#7B1FA2") # 浅紫
            with m4: sticker(t("metric_rate"), f"{rate:.0f}%", "💌", "#E3F2FD", "#1565C0") # 浅蓝

            st.markdown("<br>", unsafe_allow_html=True)

            # 笔记本风格布局
            c_main, c_side = st.columns([2, 1.2])
            
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
                    # 手绘风配色
                    chart_df = active_df.copy()
                    chart_df['s_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['s_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    
                    # 舒适粉笔配色
                    cozy_palette = ['#88B04B', '#FF6F61', '#6B5B95', '#F7CAC9', '#92A8D1']
                    
                    fig = px.pie(counts, values='count', names='label', hole=0.6, color_discrete_sequence=cozy_palette)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(text=f"{len(active_df)}\nTotal", x=0.5, y=0.5, font_size=16, showarrow=False, font_color=THEME['text_light'])]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 管理卡片 (Sticky Note Style)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                st.caption(t("manage_hint"))
                
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job_str = st.selectbox("Search", [""] + job_list, label_visibility="collapsed", placeholder="Select a job note...")
                
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
                        
                        new_d = st.text_area(t("input_note"), value=row['description'], height=100)
                        
                        b1, b2, b3 = st.columns([1.5, 1.5, 4])
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
        # --- 🗃️ 归档页 (The Vault) ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<p style='color:{THEME['text_light']}'>{t('archive_sub')}</p>", unsafe_allow_html=True)
        
        if archived_df.empty:
            st.markdown(f"""
             <div style='text-align: center; padding: 60px; color: {THEME['text_light']}; border: 2px dashed {THEME['border_color']}; border-radius: 20px;'>
                <div style='font-size: 3rem; opacity: 0.5;'>📦</div>
                <p>{t('archive_empty')}</p>
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
                sel_archive = st.selectbox("Restore Record", [""] + archive_list, label_visibility="collapsed", placeholder="Select to restore...")
                
                if sel_archive:
                    row_idx = archive_list.index(sel_archive)
                    row = archived_df.iloc[row_idx]
                    st.info(f"Selected: {row['title']} @ {row['company']}")
                    
                    c_res, c_del = st.columns([1, 6])
                    if c_res.button(t("btn_restore"), type="primary"):
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success(t("restore_success")); time.sleep(0.5); st.rerun()
                    
                    if c_del.button(t("btn_del"), key="del_a", type="secondary"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted")); time.sleep(0.5); st.rerun()
