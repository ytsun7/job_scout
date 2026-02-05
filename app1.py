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
        "slogan": "保持节奏，保持平静",
        "loading": "🌿 正在整理您的空间...",
        
        # 侧边栏
        "console": "导航",
        "my_account": "我的账户",
        "view_api_key": "查看连接密钥",
        "nav_dashboard": "📌 进度看板",
        "nav_archive": "🗂️ 历史归档",
        "logout": "退出休息",

        # 欢迎区
        "greeting_morning": "早上好，",
        "greeting_afternoon": "下午好，",
        "greeting_evening": "晚上好，",
        "greeting_sub": "今天也是充满可能的一天。保持呼吸，按部就班。",

        # 指标
        "metric_active": "进行中",
        "metric_interview": "面试",
        "metric_offer": "收获",
        "metric_rate": "回应率",

        # 归档页
        "archive_title": "📜 归档室",
        "archive_sub": "这里存放已封存的记录。它们是你经历的一部分。",
        "archive_empty": "归档室是空的。",
        "btn_restore": "♻️ 恢复到看板",
        "restore_success": "记录已恢复到活跃看板",

        # 看板与管理
        "chart_title": "活跃状态分布",
        "list_title": "最近动态 (活跃)",
        "manage_title": "🌱 岗位管理",
        "manage_hint": "更新进度，或将其归档以保持专注...",
        "input_title": "岗位",
        "input_company": "公司",
        "input_status": "当前阶段",
        "input_loc": "地点",
        "input_note": "备忘录",
        
        "btn_save": "保存更新",
        "btn_archive": "📂 移入归档", # 新按钮
        "btn_del": "彻底删除",
        
        "msg_archived": "已移入归档室",
        "msg_updated": "已更新",
        "msg_deleted": "已删除",
        "empty_desc": "暂无活跃申请，请去抓取一些新机会吧。",

        # 状态
        "s_applied": "📝 已投递",
        "s_interviewing": "🎙️ 面试中",
        "s_offer": "✨ 收获 Offer",
        "s_rejected": "🍂 已结束",
        "s_ghosted": "🔕 暂无回音",
        "s_archived": "🗂️ 已归档"
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

        "greeting_morning": "Good morning, ",
        "greeting_afternoon": "Good afternoon, ",
        "greeting_evening": "Good evening, ",
        "greeting_sub": "Take a deep breath. Focus on what you can control.",

        "metric_active": "Active",
        "metric_interview": "Interviews",
        "metric_offer": "Offers",
        "metric_rate": "Response Rate",

        "archive_title": "📜 The Archive",
        "archive_sub": "Stored records of your past journey.",
        "archive_empty": "The archive is empty.",
        "btn_restore": "♻️ Restore",
        "restore_success": "Restored to dashboard",

        "chart_title": "Active Distribution",
        "list_title": "Recent Activity (Active)",
        "manage_title": "🌱 Management",
        "manage_hint": "Update progress, or archive to stay focused...",
        "input_title": "Role",
        "input_company": "Company",
        "input_status": "Stage",
        "input_loc": "Location",
        "input_note": "Notes",
        
        "btn_save": "Save Changes",
        "btn_archive": "📂 Archive",
        "btn_del": "Delete Permanently",
        
        "msg_archived": "Moved to Archive",
        "msg_updated": "Updated",
        "msg_deleted": "Deleted",
        "empty_desc": "No active applications.",

        "s_applied": "📝 Applied",
        "s_interviewing": "🎙️ Interview",
        "s_offer": "✨ Offer",
        "s_rejected": "🍂 Ended",
        "s_ghosted": "🔕 Ghosted",
        "s_archived": "🗂️ Archived"
    }
}

# ==========================================
# 1. 禅意 UI 主题配置
# ==========================================
THEME = {
    "bg_color": "#F9F9F6",           # 羊皮纸色
    "sidebar_bg": "#F2F2F0",         # 极淡灰
    "card_bg": "#FFFFFF",            # 纯白
    "primary": "#7A9E9F",            # 尤加利青
    "primary_light": "#E8F1F2",      
    "text_main": "#4A5568",          
    "text_light": "#A0AEC0",
    "archived_tag": "#E2E8F0"        # 归档标签色
}

st.set_page_config(page_title="Job Tracker", layout="wide", page_icon="🌿")

def inject_zen_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Inter', 'Noto Sans SC', sans-serif;
            color: {THEME['text_main']};
        }}

        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}
        #MainMenu, footer {{ visibility: hidden; }}

        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: 1px solid rgba(0,0,0,0.02) !important;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02);
            margin-bottom: 24px;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: none;
        }}
        
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 10px rgba(122, 158, 159, 0.2);
        }}
        .stButton>button:hover {{
            background-color: #638586;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(122, 158, 159, 0.3);
        }}
        
        /* 次要按钮 (如归档) */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid #CBD5E0 !important;
            color: {THEME['text_main']} !important;
            box-shadow: none !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: {THEME['primary']} !important;
            color: {THEME['primary']} !important;
            background-color: white !important;
        }}

        /* 表格去边框 */
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
# 3. 登录 UI
# ==========================================
def auth_ui():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center; color: {THEME['primary']}; margin-bottom: 5px;'>{t('app_name')}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #999; font-size: 0.9rem; margin-bottom: 30px;'>{t('slogan')}</p>", unsafe_allow_html=True)
            
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
# 4. 主程序
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏 ---
    with st.sidebar:
        c1, c2 = st.columns([2, 1])
        with c2:
            if st.toggle("EN", value=(st.session_state.language=='EN')):
                if st.session_state.language != 'EN': st.session_state.language = 'EN'; st.rerun()
            else:
                if st.session_state.language != 'ZH': st.session_state.language = 'ZH'; st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
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

        st.markdown(f"<div style='color:{THEME['text_light']}; font-size: 0.8rem; margin: 20px 0 10px 5px; font-weight: 600;'>{t('console').upper()}</div>", unsafe_allow_html=True)
        
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

    # --- 数据加载与分流 ---
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
    
    # 拆分活跃数据和归档数据
    active_df = pd.DataFrame()
    archived_df = pd.DataFrame()
    
    if not df.empty:
        # 核心逻辑：状态为 'archived' 的进入历史，其他的在看板
        active_df = df[df['status'] != 'archived']
        archived_df = df[df['status'] == 'archived']

    status_map = {
        "applied": t("s_applied"), "interviewing": t("s_interviewing"),
        "offer": t("s_offer"), "rejected": t("s_rejected"), "ghosted": t("s_ghosted"),
        "archived": t("s_archived")
    }

    # ==========================================
    # 5. 页面路由逻辑
    # ==========================================
    hour = datetime.datetime.now().hour
    if hour < 12: greet = t("greeting_morning")
    elif hour < 18: greet = t("greeting_afternoon")
    else: greet = t("greeting_evening")

    if st.session_state.page == 'dashboard':
        # --- 📌 仪表盘 (仅显示活跃数据) ---
        st.markdown(f"## {greet} ✨")
        st.markdown(f"<div style='color:{THEME['text_light']}; margin-top: -15px; margin-bottom: 30px;'>{t('greeting_sub')}</div>", unsafe_allow_html=True)

        if active_df.empty:
             st.info(t("empty_desc"))
        else:
            # 活跃指标
            m1, m2, m3, m4 = st.columns(4)
            active_cnt = len(active_df[active_df['status'].isin(['applied', 'interviewing'])])
            interview_cnt = len(active_df[active_df['status'] == 'interviewing'])
            offer_cnt = len(active_df[active_df['status'] == 'offer'])
            resp_rate = len(active_df[active_df['status'] != 'applied']) / len(active_df) * 100
            
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

            c1, c2 = st.columns([1.2, 2])
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"### {t('chart_title')}")
                    # 图表仅使用 active_df
                    chart_df = active_df.copy()
                    chart_df['status_label'] = chart_df['status'].map(lambda x: status_map.get(x, x))
                    counts = chart_df['status_label'].value_counts().reset_index()
                    counts.columns = ['label', 'count']
                    calm_colors = ['#A8DADC', '#457B9D', '#F1FAEE', '#E63946', '#1D3557']
                    morandi = ['#7c9082', '#9ca8b8', '#d8c4b6', '#e0cdcf', '#aab5a9']

                    fig = px.pie(counts, values='count', names='label', hole=0.75, color_discrete_sequence=morandi)
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False,
                        annotations=[dict(text=str(len(active_df)), x=0.5, y=0.5, font_size=24, showarrow=False, font_color=THEME['text_main'])]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                with st.container(border=True):
                    st.markdown(f"### {t('list_title')}")
                    # 列表仅显示 active_df
                    show_df = active_df.head(5).copy()
                    show_df['status_display'] = show_df['status'].map(lambda x: status_map.get(x, x))
                    
                    st.dataframe(
                        show_df,
                        column_config={
                            "date_str": st.column_config.TextColumn(t("col_date"), width="small"),
                            "status_display": st.column_config.TextColumn(t("input_status"), width="medium"),
                            "company": st.column_config.TextColumn(t("col_company"), width="medium"),
                            "title": st.column_config.TextColumn(t("input_title"), width="large"),
                        },
                        column_order=("date_str", "company", "title", "status_display"),
                        use_container_width=True, hide_index=True, height=250
                    )

            # --- 岗位管理区 (含归档功能) ---
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"### {t('manage_title')}")
                st.markdown(f"<div style='color:#999; margin-bottom: 20px;'>{t('manage_hint')}</div>", unsafe_allow_html=True)
                
                # 仅能搜索活跃岗位
                job_list = active_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                selected_job_str = st.selectbox("Search", [""] + job_list, label_visibility="collapsed", placeholder="Search active jobs...")
                
                if selected_job_str:
                    st.markdown("---")
                    row_idx = job_list.index(selected_job_str)
                    row = active_df.iloc[row_idx]
                    
                    with st.form("edit_form"):
                        c_a, c_b = st.columns(2)
                        with c_a:
                            new_t = st.text_input(t("input_title"), value=row['title'])
                            # 状态选择不包含 'archived'，因为要通过按钮触发
                            db_keys = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                            curr_k = row['status'] if row['status'] in db_keys else "applied"
                            new_s = st.selectbox(t("input_status"), db_keys, index=db_keys.index(curr_k), format_func=lambda x: status_map.get(x,x))
                        with c_b:
                            new_c = st.text_input(t("input_company"), value=row['company'])
                            new_l = st.text_input(t("input_loc"), value=row['location'])
                        
                        new_d = st.text_area(t("input_note"), value=row['description'])
                        
                        # 按钮布局：保存 | 归档 | 删除
                        b1, b2, b3 = st.columns([1.5, 1.5, 4])
                        
                        # 保存
                        if b1.form_submit_button(t("btn_save")):
                            supabase.table("job_applications").update({
                                "title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_updated"))
                            time.sleep(0.5); st.rerun()
                        
                        # 归档按钮 (Secondary Style)
                        if b2.form_submit_button(t("btn_archive"), type="secondary"):
                            supabase.table("job_applications").update({"status": "archived"}).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success(t("msg_archived"))
                            time.sleep(0.5); st.rerun()

                    # 删除按钮放在外面防止误触
                    if st.button(t("btn_del"), type="secondary", key="del_dash"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted"))
                        time.sleep(0.5); st.rerun()

    elif st.session_state.page == 'archive':
        # --- 🗂️ 归档页面 (只显示 archived 数据) ---
        st.markdown(f"## {t('archive_title')}")
        st.markdown(f"<div style='color:{THEME['text_light']}; margin-top: -15px; margin-bottom: 30px;'>{t('archive_sub')}</div>", unsafe_allow_html=True)
        
        if archived_df.empty:
            st.info(t("archive_empty"))
        else:
            with st.container(border=True):
                # 简单列表展示归档内容
                archived_df['display_status'] = t("s_archived") # 统一显示为"已归档"
                
                st.dataframe(
                    archived_df,
                    column_config={
                        "date_str": st.column_config.TextColumn(t("input_note")),
                        "company": st.column_config.TextColumn(t("input_company")),
                        "title": st.column_config.TextColumn(t("input_title")),
                        "description": st.column_config.TextColumn(t("input_note"), width="large"),
                        "display_status": st.column_config.TextColumn("Status")
                    },
                    column_order=("date_str", "company", "title", "display_status", "description"),
                    use_container_width=True, hide_index=True
                )
                
                st.markdown("---")
                # 归档恢复功能
                st.markdown(f"**{t('manage_title')}**")
                archive_list = archived_df.apply(lambda x: f"{x['company']} - {x['title']}", axis=1).tolist()
                sel_archive = st.selectbox("Select to restore", [""] + archive_list, label_visibility="collapsed")
                
                if sel_archive:
                    row_idx = archive_list.index(sel_archive)
                    row = archived_df.iloc[row_idx]
                    st.caption(f"Selected: {row['title']} @ {row['company']}")
                    
                    c_res, c_del = st.columns([1, 6])
                    
                    # 恢复按钮：重置为 applied (或者你可以选择变为 interviewing)
                    if c_res.button(t("btn_restore"), type="primary"):
                        # 恢复默认为 'applied' 状态，或者你可以保留之前的状态需要更复杂的逻辑
                        # 这里为了简单，恢复为 'applied' 并提示用户去更新
                        supabase.table("job_applications").update({"status": "applied"}).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success(t("restore_success"))
                        time.sleep(0.5); st.rerun()
                    
                    if c_del.button(t("btn_del"), key="del_arch", type="secondary"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning(t("msg_deleted"))
                        time.sleep(0.5); st.rerun()
