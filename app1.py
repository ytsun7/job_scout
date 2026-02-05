import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 1. 高保真 UI 配置系统 (Morandi Theme)
# ==========================================
THEME = {
    "bg_color": "#f7f7f5",           # 主页面：暖米灰
    "sidebar_bg": "#f0f0ed",         # 侧边栏：稍深的暖灰
    "card_bg": "#ffffff",            # 纯白卡片
    "primary": "#7c9082",            # 莫兰迪绿 (Sage Green)
    "secondary": "#9ca8b8",          # 雾霾蓝
    "text_main": "#454545",          # 深灰字体
    "text_sub": "#8a8a8a",           # 浅灰副标题
    "table_header": "#f4f6f5"        # 表头背景
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

        /* --- Header 修复 --- */
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}
        div[data-testid="stDecoration"] {{ visibility: hidden; }}

        /* --- 侧边栏深度美化 --- */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['sidebar_bg']};
            border-right: 1px solid rgba(0,0,0,0.04);
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }}
        /* 侧边栏内的卡片背景微调 */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: none !important;
        }}
        /* 侧边栏 Expander 样式 */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {{
            background-color: transparent;
            color: {THEME['text_main']};
            font-size: 0.9rem;
        }}
        
        /* --- 主区域卡片样式 --- */
        section[data-testid="stMain"] div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: none !important;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            margin-bottom: 16px;
        }}

        /* --- 通用字体与按钮 --- */
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
        
        /* 侧边栏退出按钮特殊样式 (Ghost Style) */
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

        /* --- 表格美化 --- */
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
            st.info("🎨 正在加载设计资源...")
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
            st.markdown("<p style='text-align: center; color: #888; margin-bottom: 30px;'>优雅地管理您的职业旅程</p>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["用户登录", "注册账户"])
            
            with tab1:
                with st.form("login_form"):
                    e = st.text_input("邮箱地址")
                    p = st.text_input("密码", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("登 录"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            if res.user:
                                st.session_state.user = res.user
                                expires = datetime.datetime.now() + datetime.timedelta(hours=3)
                                cookie_manager.set("sb_access_token", res.session.access_token, expires_at=expires, key="set_at_login")
                                cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=expires, key="set_rt_login")
                                st.success("欢迎回来")
                                time.sleep(1); st.rerun()
                        except Exception as ex: st.error(f"登录失败: {ex}")
            with tab2:
                with st.form("signup_form"):
                    ne = st.text_input("新邮箱")
                    np = st.text_input("设置密码 (6位以上)", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("注 册"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("注册成功！请登录")
                        except Exception as ex: st.error(f"注册失败: {ex}")

# ==========================================
# 4. 主程序逻辑
# ==========================================
if not user:
    auth_ui()
else:
    # --- 💎 侧边栏重构 (高保真版) ---
    with st.sidebar:
        st.markdown(f"### ⚙️ 控制台")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 模拟个人资料卡片
        with st.container(border=True):
            # 获取邮箱首字母用于头像
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
                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #333;">我的账户</p>
                    <p style="margin: 0; font-size: 12px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{user.email}">
                        {user.email}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            # 折叠的 API Key 区域
            with st.expander("🔑 查看 API 密钥"):
                st.caption("在 Chrome 插件中填入此 ID：")
                st.code(user.id, language=None)

        # 视觉导航占位 (增加 App 感)
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("MENU")
        st.markdown(f"""
        <div style="padding: 8px 12px; background-color: white; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {THEME['primary']}; color: {THEME['primary']}; font-weight: 600; font-size: 14px;">
            📊 进度看板
        </div>
        <div style="padding: 8px 12px; color: #888; font-size: 14px;">
            📁 历史归档 <span style="font-size: 10px; background: #eee; padding: 2px 6px; border-radius: 4px; float: right;">Soon</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True) # Spacer
        
        # 退出按钮
        if st.button("🚪 退出安全登录"):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token", key="del_at_logout")
            cookie_manager.delete("sb_refresh_token", key="del_rt_logout")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
            st.rerun()

    # --- 主页面内容 ---
    st.markdown(f"## 早上好，求职者 ✨")
    st.markdown(f"<p style='color:{THEME['text_sub']}; margin-top: -10px; margin-bottom: 30px;'>这里是您的申请进度概览。</p>", unsafe_allow_html=True)

    @st.cache_data(ttl=2)
    def load_my_data(uid):
        try:
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d')
                status_map = {"applied": "📝 已投递", "interviewing": "🎙️ 面试中", "offer": "🎉 Offer", "rejected": "🍂 已结束", "ghosted": "🔕 无回音"}
                df['status_display'] = df['status'].map(lambda x: status_map.get(x, x))
                df = df.reset_index(drop=True)
                df.insert(0, '显示序号', df.index + 1)
            return df
        except Exception as ex:
            return pd.DataFrame()

    df = load_my_data(user.id)

    if not df.empty:
        # 指标卡
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("总申请", len(df))
        col_m2.metric("面试中", len(df[df['status'] == 'interviewing']))
        col_m3.metric("Offer", len(df[df['status'] == 'offer']))
        conversion = len(df[df['status'].isin(['interviewing', 'offer'])])
        rate = conversion / len(df) * 100 if len(df) > 0 else 0
        col_m4.metric("转化率", f"{rate:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # 图表与列表
        c_left, c_right = st.columns([1, 2])
        
        with c_left:
            with st.container(border=True):
                st.markdown("### 📊 状态分布")
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['状态', '数量']
                morandi_colors = ['#7c9082', '#9ca8b8', '#d8c4b6', '#e0cdcf', '#aab5a9']
                
                fig_pie = px.pie(status_counts, values='数量', names='状态', hole=0.7, 
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
                st.markdown("### 📋 最近投递")
                st.dataframe(
                    df.head(10), 
                    column_config={
                        "显示序号": st.column_config.NumberColumn("#", width="small"),
                        "formatted_date": st.column_config.TextColumn("投递日期", width="medium"),
                        "status_display": st.column_config.TextColumn("当前状态", width="medium"),
                        "company": st.column_config.TextColumn("公司名称", width="medium"),
                        "title": st.column_config.TextColumn("岗位", width="large"),
                    },
                    column_order=("显示序号", "formatted_date", "company", "title", "status_display"),
                    use_container_width=True, 
                    hide_index=True,
                    height=300
                )

        # 管理面板
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### 🛠️ 岗位管理中心")
            st.caption("选择一条记录进行状态更新或编辑详情")
            
            job_options = df.apply(lambda x: f"{x['company']} - {x['title']} (ID: {x['显示序号']})", axis=1).tolist()
            sel = st.selectbox("搜索岗位...", ["-- 点击选择 --"] + job_options, label_visibility="collapsed")
            
            if sel != "-- 点击选择 --":
                st.markdown("---")
                display_idx = int(sel.split('(ID: ')[1].replace(')', ''))
                row = df[df['显示序号'] == display_idx].iloc[0]
                
                with st.form("edit_form"):
                    f1, f2 = st.columns(2)
                    with f1:
                        t = st.text_input("岗位名称", value=row['title'])
                        s_list = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                        s_labels = ["📝 已投递", "🎙️ 面试中", "✨ Offer", "🍂 已结束", "🔕 无回音"]
                        curr_code = row['status'] if row['status'] in s_list else "applied"
                        s_idx = s_list.index(curr_code)
                        s = st.selectbox("当前进度", s_list, index=s_idx, format_func=lambda x: s_labels[s_list.index(x)])

                    with f2:
                        c = st.text_input("公司名称", value=row['company'])
                        l = st.text_input("工作地点", value=row['location'])
                    
                    desc = st.text_area("备注 / 职位描述", value=row['description'], height=100)
                    
                    btn_col1, btn_col2 = st.columns([1, 6])
                    with btn_col1:
                        if st.form_submit_button("💾 保存"):
                            supabase.table("job_applications").update({
                                "title": t, "company": c, "status": s, "location": l, "description": desc
                            }).eq("id", row['id']).execute()
                            st.cache_data.clear()
                            st.success("已更新")
                            time.sleep(0.5); st.rerun()
                    
                if st.button("🗑️ 删除此记录", type="secondary"):
                    supabase.table("job_applications").delete().eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.warning("已删除")
                    time.sleep(0.5); st.rerun()

    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 50px; background-color: white; border-radius: 16px;">
            <h2 style="color: {THEME['secondary']}">暂无数据</h2>
            <p style="color: #999;">请使用 Chrome 插件抓取您的第一个职位申请</p>
        </div>
        """, unsafe_allow_html=True)
