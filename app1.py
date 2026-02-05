import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 0. 国际化配置 (I18n System)
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = 'ZH' # 默认中文

def t(key):
    """获取翻译文本的辅助函数"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

TRANSLATIONS = {
    "ZH": {
        "app_name": "Job Tracker Pro",
        "slogan": "优雅地管理您的职业旅程",
        "login_tab": "用户登录",
        "signup_tab": "注册账户",
        "email_label": "邮箱地址",
        "password_label": "密码",
        "new_email": "新邮箱",
        "set_password": "设置密码 (6位以上)",
        "login_btn": "登 录",
        "signup_btn": "注 册",
        "welcome_back": "欢迎回来",
        "reg_success": "注册成功！请登录",
        "login_fail": "登录失败",
        "reg_fail": "注册失败",
        "loading_design": "🎨 正在加载设计资源...",
        
        # 侧边栏
        "console": "⚙️ 控制台",
        "my_account": "我的账户",
        "view_api_key": "🔑 查看 API 密钥",
        "api_hint": "在 Chrome 插件中填入此 ID：",
        "menu_dashboard": "📊 进度看板",
        "menu_archive": "📁 历史归档",
        "logout": "🚪 退出安全登录",
        "lang_select": "🌐 语言 / Language",

        # 主页
        "greeting": "早上好，求职者 ✨",
        "greeting_sub": "这里是您的申请进度概览。",
        "metric_total": "总申请",
        "metric_interview": "面试中",
        "metric_offer": "Offer",
        "metric_rate": "转化率",
        
        # 图表与列表
        "chart_status": "📊 状态分布",
        "list_recent": "📋 最近投递",
        "col_no": "#",
        "col_date": "投递日期",
        "col_status": "当前状态",
        "col_company": "公司名称",
        "col_title": "岗位",
        
        # 管理面板
        "manage_title": "🛠️ 岗位管理中心",
        "manage_caption": "选择一条记录进行状态更新或编辑详情",
        "search_placeholder": "搜索岗位...",
        "select_default": "-- 点击选择 --",
        "input_title": "岗位名称",
        "input_progress": "当前进度",
        "input_company": "公司名称",
        "input_location": "工作地点",
        "input_desc": "备注 / 职位描述",
        "btn_save": "💾 保存",
        "btn_delete": "🗑️ 删除此记录",
        "msg_updated": "已更新",
        "msg_deleted": "已删除",
        "empty_title": "暂无数据",
        "empty_desc": "请使用 Chrome 插件抓取您的第一个职位申请",

        # 状态映射
        "status_applied": "📝 已投递",
        "status_interviewing": "🎙️ 面试中",
        "status_offer": "🎉 Offer",
        "status_rejected": "🍂 已结束",
        "status_ghosted": "🔕 无回音"
    },
    "EN": {
        "app_name": "Job Tracker Pro",
        "slogan": "Manage your career journey elegantly",
        "login_tab": "Login",
        "signup_tab": "Sign Up",
        "email_label": "Email Address",
        "password_label": "Password",
        "new_email": "New Email",
        "set_password": "Password (6+ chars)",
        "login_btn": "Login",
        "signup_btn": "Register",
        "welcome_back": "Welcome back",
        "reg_success": "Success! Please login.",
        "login_fail": "Login failed",
        "reg_fail": "Registration failed",
        "loading_design": "🎨 Loading resources...",

        # Sidebar
        "console": "⚙️ Console",
        "my_account": "My Account",
        "view_api_key": "🔑 API Key",
        "api_hint": "Use this ID in Chrome Extension:",
        "menu_dashboard": "📊 Dashboard",
        "menu_archive": "📁 Archive",
        "logout": "🚪 Logout",
        "lang_select": "🌐 Language",

        # Main
        "greeting": "Good Morning ✨",
        "greeting_sub": "Here is an overview of your applications.",
        "metric_total": "Total",
        "metric_interview": "Interviewing",
        "metric_offer": "Offers",
        "metric_rate": "Conversion",

        # Chart & List
        "chart_status": "📊 Status Distribution",
        "list_recent": "📋 Recent Applications",
        "col_no": "#",
        "col_date": "Date",
        "col_status": "Status",
        "col_company": "Company",
        "col_title": "Role",

        # Management
        "manage_title": "🛠️ Job Management",
        "manage_caption": "Select a record to update status or edit details",
        "search_placeholder": "Search jobs...",
        "select_default": "-- Select a Job --",
        "input_title": "Job Title",
        "input_progress": "Current Stage",
        "input_company": "Company",
        "input_location": "Location",
        "input_desc": "Notes / Description",
        "btn_save": "💾 Save Changes",
        "btn_delete": "🗑️ Delete Record",
        "msg_updated": "Updated successfully",
        "msg_deleted": "Deleted successfully",
        "empty_title": "No Data Yet",
        "empty_desc": "Use the Chrome Extension to track your first job.",

        # Status Mapping
        "status_applied": "📝 Applied",
        "status_interviewing": "🎙️ Interview",
        "status_offer": "🎉 Offer",
        "status_rejected": "🍂 Rejected",
        "status_ghosted": "🔕 Ghosted"
    }
}

# ==========================================
# 1. 高保真 UI 配置系统 (Morandi Theme)
# ==========================================
THEME = {
    "bg_color": "#f7f7f5",
    "sidebar_bg": "#f0f0ed",
    "card_bg": "#ffffff",
    "primary": "#7c9082",
    "secondary": "#9ca8b8",
    "text_main": "#454545",
    "text_sub": "#8a8a8a",
    "table_header": "#f4f6f5"
}

st.set_page_config(page_title="Job Tracker Pro", layout="wide", page_icon="💼")

def inject_morandi_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Inter', sans-serif;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}

        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: 1px solid rgba(0,0,0,0.04);
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }}
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: none !important;
        }}
        section[data-testid="stSidebar"] .streamlit-expanderHeader {{
            background-color: transparent;
            color: {THEME['text_main']};
            font-size: 0.9rem;
        }}
        
        section[data-testid="stMain"] div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: none !important;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            margin-bottom: 16px;
        }}

        h1, h2, h3 {{ color: {THEME['text_main']} !important; font-weight: 600 !important; }}
        
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(124, 144, 130, 0.2);
        }}
        .stButton>button:hover {{
            background-color: #6a7d70;
            box-shadow: 0 6px 12px rgba(124, 144, 130, 0.3);
            transform: translateY(-1px);
            color: white !important;
        }}
        
        section[data-testid="stSidebar"] .stButton>button {{
            background-color: transparent;
            border: 1px solid {THEME['text_sub']};
            color: {THEME['text_main']};
            box-shadow: none;
        }}
        section[data-testid="stSidebar"] .stButton>button:hover {{
            border-color: #e74c3c;
            color: #e74c3c;
            background-color: white;
        }}

        div[data-testid="stDataFrame"] {{ border: none !important; }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: {THEME['table_header']} !important;
            border-bottom: 1px solid #eee;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

inject_morandi_css()

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
            st.info(t("loading_design"))
            _ = cookie_manager.get_all()
            time.sleep(1)
    st.session_state.cookie_sync_done = True
    st.rerun()

def get_current_user():
    if 'user' in st.session_state and st.session_state.user is not None:
        return st.session_state.user
    cookies = cookie_manager.get_all()
    at = cookies.get("sb_access_token")
    rt = cookies.get("sb_refresh_token")
    if at and rt:
        try:
            session = supabase.auth.set_session(at, rt)
            st.session_state.user = session.user
            return session.user
        except: return None
    return None

user = get_current_user()

# ==========================================
# 3. 身份验证界面
# ==========================================
def auth_ui():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"<h1 style='text-align: center; color: {THEME['primary']};'>Job Tracker</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #888; margin-bottom: 30px;'>{t('slogan')}</p>", unsafe_allow_html=True)
            
            # 语言切换 (登录页)
            lang = st.selectbox(t("lang_select"), ["中文", "English"], index=0 if st.session_state.language == 'ZH' else 1, key="auth_lang_select")
            if (lang == "中文" and st.session_state.language != "ZH") or (lang == "English" and st.session_state.language != "EN"):
                st.session_state.language = "ZH" if lang == "中文" else "EN"
                st.rerun()

            tab1, tab2 = st.tabs([t("login_tab"), t("signup_tab")])
            
            with tab1:
                with st.form("login_form"):
                    e = st.text_input(t("email_label"))
                    p = st.text_input(t("password_label"), type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("login_btn")):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                expires = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=expires, key="set_at_login")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=expires, key="set_rt_login")
                                st.success(t("welcome_back"))
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(f"{t('login_fail')}: {ex}")
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input(t("new_email"))
                    np = st.text_input(t("set_password"), type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(t("signup_btn")):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success(t("reg_success"))
                        except Exception as ex: st.error(f"{t('reg_fail')}: {ex}")

# ==========================================
# 4. 主程序逻辑
# ==========================================
if not user:
    auth_ui()
else:
    # --- 💎 侧边栏重构 (双语版) ---
    with st.sidebar:
        # 语言切换器放在侧边栏最上方
        with st.container(border=True):
             # 简单的单选按钮切换
             sel_lang = st.radio(t("lang_select"), ["中文", "English"], 
                                 index=0 if st.session_state.language == 'ZH' else 1, 
                                 horizontal=True, 
                                 label_visibility="collapsed")
             
             # 状态更新逻辑
             new_lang = "ZH" if sel_lang == "中文" else "EN"
             if new_lang != st.session_state.language:
                 st.session_state.language = new_lang
                 st.rerun()

        st.markdown(f"### {t('console')}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            initial = user.email[0].upper() if user.email else "U"
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; padding-bottom: 0px;">
                <div style="
                    width: 42px; height: 42px; 
                    background-color: {THEME['primary']}; 
                    color: white; 
                    border-radius: 50%; 
                    display: flex; align-items: center; justify-content: center; 
                    font-weight: 600; font-size: 18px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    {initial}
                </div>
                <div style="overflow: hidden;">
                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #333;">{t('my_account')}</p>
                    <p style="margin: 0; font-size: 12px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{user.email}">
                        {user.email}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            with st.expander(t("view_api_key")):
                st.caption(t("api_hint"))
                st.code(user.id, language=None)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("MENU")
        st.markdown(f"""
        <div style="padding: 8px 12px; background-color: white; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {THEME['primary']}; color: {THEME['primary']}; font-weight: 600; font-size: 14px;">
            {t('menu_dashboard')}
        </div>
        <div style="padding: 8px 12px; color: #888; font-size: 14px;">
            {t('menu_archive')} <span style="font-size: 10px; background: #eee; padding: 2px 6px; border-radius: 4px; float: right;">Soon</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True) 
        
        if st.button(t("logout")):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token", key="del_at_logout")
            cookie_manager.delete("sb_refresh_token", key="del_rt_logout")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
            st.rerun()

    # --- 主页面内容 ---
    st.markdown(f"## {t('greeting')}")
    st.markdown(f"<p style='color:{THEME['text_sub']}; margin-top: -10px; margin-bottom: 30px;'>{t('greeting_sub')}</p>", unsafe_allow_html=True)

    @st.cache_data(ttl=2)
    def load_my_data(uid):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d')
                df = df.reset_index(drop=True)
                df.insert(0, 'display_index', df.index + 1)
            return df
        except Exception as ex:
            return pd.DataFrame()

    df = load_my_data(user.id)

    # 动态状态映射 (根据当前语言)
    current_status_map = {
        "applied": t("status_applied"),
        "interviewing": t("status_interviewing"),
        "offer": t("status_offer"),
        "rejected": t("status_rejected"),
        "ghosted": t("status_ghosted")
    }

    if not df.empty:
        # 为了显示，创建一个新列
        df['status_display'] = df['status'].map(lambda x: current_status_map.get(x, x))

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric(t("metric_total"), len(df))
        col_m2.metric(t("metric_interview"), len(df[df['status'] == 'interviewing']))
        col_m3.metric(t("metric_offer"), len(df[df['status'] == 'offer']))
        conversion = len(df[df['status'].isin(['interviewing', 'offer'])])
        rate = conversion / len(df) * 100 if len(df) > 0 else 0
        col_m4.metric(t("metric_rate"), f"{rate:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)

        c_left, c_right = st.columns([1, 2])
        
        with c_left:
            with st.container(border=True):
                st.markdown(f"### {t('chart_status')}")
                # 统计时使用显示用的中文/英文状态
                status_counts = df['status_display'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                morandi_colors = ['#7c9082', '#9ca8b8', '#d8c4b6', '#e0cdcf', '#aab5a9']
                
                fig_pie = px.pie(status_counts, values='count', names='status', hole=0.7, 
                                color_discrete_sequence=morandi_colors)
                fig_pie.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20), 
                    height=280, 
                    showlegend=False,
                    annotations=[dict(text=str(len(df)), x=0.5, y=0.5, font_size=24, showarrow=False, font_color=THEME['text_main'])]
                )
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)

        with c_right:
             with st.container(border=True):
                st.markdown(f"### {t('list_recent')}")
                st.dataframe(
                    df.head(10), 
                    column_config={
                        "display_index": st.column_config.NumberColumn(t("col_no"), width="small"),
                        "formatted_date": st.column_config.TextColumn(t("col_date"), width="medium"),
                        "status_display": st.column_config.TextColumn(t("col_status"), width="medium"),
                        "company": st.column_config.TextColumn(t("col_company"), width="medium"),
                        "title": st.column_config.TextColumn(t("col_title"), width="large"),
                    },
                    column_order=("display_index", "formatted_date", "company", "title", "status_display"),
                    use_container_width=True, 
                    hide_index=True,
                    height=300
                )

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"### {t('manage_title')}")
            st.caption(t("manage_caption"))
            
            job_options = df.apply(lambda x: f"{x['company']} - {x['title']} (ID: {x['display_index']})", axis=1).tolist()
            sel = st.selectbox(t("search_placeholder"), [t("select_default")] + job_options, label_visibility="collapsed")
            
            if sel != t("select_default"):
                st.markdown("---")
                display_idx = int(sel.split('(ID: ')[1].replace(')', ''))
                row = df[df['display_index'] == display_idx].iloc[0]
                
                with st.form("edit_form"):
                    f1, f2 = st.columns(2)
                    with f1:
                        t_input = st.text_input(t("input_title"), value=row['title'])
                        
                        # 状态反向查找逻辑
                        # status_list 是数据库里的原始 key: ['applied', ...]
                        db_status_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                        # display_labels 是当前语言对应的显示文本
                        display_labels = [current_status_map[k] for k in db_status_keys]
                        
                        curr_code = row['status'] if row['status'] in db_status_keys else "applied"
                        s_idx = db_status_keys.index(curr_code)
                        
                        # Selectbox 返回的是 Key (db_status_keys), 显示的是 Value (display_labels)
                        s_selected = st.selectbox(
                            t("input_progress"), 
                            db_status_keys, 
                            index=s_idx, 
                            format_func=lambda x: current_status_map.get(x, x)
                        )

                    with f2:
                        c_input = st.text_input(t("input_company"), value=row['company'])
                        l_input = st.text_input(t("input_location"), value=row['location'])
                    
                    desc = st.text_area(t("input_desc"), value=row['description'], height=100)
                    
                    btn_col1, btn_col2 = st.columns([1, 6])
                    with btn_col1:
                        if st.form_submit_button(t("btn_save")):
                            supabase.table("job_applications").update({
                                "title": t_input, "company": c_input, "status": s_selected, "location": l_input, "description": desc
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_updated"))
                            time.sleep(0.5); st.rerun()
                    
                if st.button(t("btn_delete"), type="secondary"):
                    supabase.table("job_applications").delete().eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.warning(t("msg_deleted"))
                    time.sleep(0.5); st.rerun()

    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 50px; background-color: white; border-radius: 16px;">
            <h2 style="color: {THEME['secondary']}">{t('empty_title')}</h2>
            <p style="color: #999;">{t('empty_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
