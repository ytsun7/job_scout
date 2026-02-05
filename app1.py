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
# 定义莫兰迪色板
THEME = {
    "bg_color": "#f7f7f5",           # 暖米灰背景 (Warm Grey)
    "card_bg": "#ffffff",            # 纯白卡片
    "primary": "#7c9082",            # 莫兰迪绿 (Sage Green) - 主按钮/强调
    "secondary": "#9ca8b8",          # 雾霾蓝 (Dusty Blue) - 次要元素
    "accent": "#d8c4b6",             # 奶茶色 (Beige) - 装饰
    "text_main": "#454545",          # 深灰字体 (非纯黑)
    "text_sub": "#8a8a8a",           # 浅灰副标题
    "table_header": "#f2f4f3"        # 极淡的绿色背景用于表头
}

st.set_page_config(page_title="Job Tracker Pro", layout="wide", page_icon="💼")

def inject_morandi_css():
    st.markdown(f"""
        <style>
        /* --- 全局重置与字体 --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        .stApp {{
            background-color: {THEME['bg_color']};
            font-family: 'Inter', sans-serif;
            color: {THEME['text_main']};
        }}

        /* --- 关键修复：Header 处理 --- */
        /* 不要隐藏 header，否则侧边栏按钮会消失。改为背景透明 */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        /* 仅隐藏顶部的彩虹装饰条 */
        div[data-testid="stDecoration"] {{
            visibility: hidden;
        }}

        /* --- 卡片化容器 --- */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: {THEME['card_bg']};
            border: none !important;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 极柔和阴影 */
            margin-bottom: 16px;
        }}

        /* --- 标题样式 --- */
        h1, h2, h3 {{
            color: {THEME['text_main']} !important;
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }}
        h1 {{ font-size: 2.2rem !important; }}
        h3 {{ font-size: 1.3rem !important; margin-top: 0 !important; }}

        /* --- 按钮美化 --- */
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(124, 144, 130, 0.2);
        }}
        .stButton>button:hover {{
            background-color: #6a7d70;
            box-shadow: 0 6px 12px rgba(124, 144, 130, 0.3);
            transform: translateY(-1px);
            color: white !important;
        }}
        /* 次要按钮 */
        button[kind="secondary"] {{
            background-color: transparent;
            color: {THEME['text_sub']};
            border: 1px solid #eee;
        }}

        /* --- 表格 (DataFrame) 深度美化 --- */
        div[data-testid="stDataFrame"] {{
            border: none !important;
        }}
        div[class*="stDataFrame"] div[class*="ColumnHeaders"] {{
            background-color: {THEME['table_header']} !important;
            border-bottom: 1px solid #eee;
        }}

        /* --- 侧边栏 --- */
        section[data-testid="stSidebar"] {{
            background-color: #fdfdfd;
            border-right: 1px solid rgba(0,0,0,0.02);
        }}

        /* --- 隐藏页脚和汉堡菜单(可选) --- */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

inject_morandi_css()

# ==========================================
# 2. 核心连接逻辑 (保持不变)
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()
cookie_manager = stx.CookieManager(key="main_auth_manager")

# Cookie 同步 (防闪烁)
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
                    submit = st.form_submit_button("登 录")
                    if submit:
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
    # --- 极简侧边栏 ---
    with st.sidebar:
        st.markdown(f"### 👤 个人中心")
        st.caption(f"{user.email}")
        st.markdown("---")
        st.info("💡 提示：保持积极，保持耐心。")
        st.markdown("<br>"*10, unsafe_allow_html=True)
        if st.button("退出登录"):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token", key="del_at_logout")
            cookie_manager.delete("sb_refresh_token", key="del_rt_logout")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
            st.rerun()

    # --- 顶部欢迎语 ---
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
                # 状态映射
                status_map = {"applied": "📝 已投递", "interviewing": "🎙️ 面试中", "offer": "🎉 Offer", "rejected": "🍂 已结束", "ghosted": "🔕 无回音"}
                df['status_display'] = df['status'].map(lambda x: status_map.get(x, x))
                df = df.reset_index(drop=True)
                df.insert(0, '显示序号', df.index + 1)
            return df
        except Exception as ex:
            return pd.DataFrame()

    df = load_my_data(user.id)

    if not df.empty:
        # --- 模块 1: 关键指标 (Metrics) ---
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("总申请", len(df))
        col_m2.metric("面试中", len(df[df['status'] == 'interviewing']))
        col_m3.metric("Offer", len(df[df['status'] == 'offer']))
        conversion = len(df[df['status'].isin(['interviewing', 'offer'])])
        rate = conversion / len(df) * 100 if len(df) > 0 else 0
        col_m4.metric("转化率", f"{rate:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- 模块 2: 图表与列表 ---
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

        # --- 模块 3: 沉浸式管理面板 ---
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
