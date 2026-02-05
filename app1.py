import streamlit as st
import extra_streamlit_components as stx 
from supabase import create_client
import pandas as pd
import plotly.express as px
import time
import datetime

# ==========================================
# 1. UI 配置中心 (方便后期修改颜色和样式)
# ==========================================
UI_CONFIG = {
    "primary_color": "#0073b1",    # 领英蓝
    "bg_light": "#f3f6f8",         # 浅灰背景
    "success_green": "#27ae60",    # 成功绿
    "warning_orange": "#f39c12",   # 警告橙
    "card_border_radius": "12px"   # 卡片圆角
}

st.set_page_config(page_title="Job Tracker Pro", layout="wide")

def inject_custom_css():
    st.markdown(f"""
        <style>
        /* 全局背景色优化 */
        .stApp {{
            background-color: {UI_CONFIG["bg_light"]};
        }}
        
        /* 自定义卡片样式 */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: white;
            border-radius: {UI_CONFIG["card_border_radius"]};
            border: 1px solid #e0e0e0 !important;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        /* 标题字体加粗 */
        h1, h2, h3 {{
            color: #333333;
            font-weight: 700 !important;
        }}
        
        /* 按钮美化 */
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid {UI_CONFIG["primary_color"]};
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: {UI_CONFIG["primary_color"]};
            color: white;
        }}
        
        /* 隐藏冗余组件 */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. 核心逻辑 (保持功能不变)
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()
cookie_manager = stx.CookieManager(key="auth_cookie_manager")

# Cookie 同步机制 (防闪烁)
if 'cookie_sync_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner("🚀 正在载入个人看板..."):
            _ = cookie_manager.get_all()
            time.sleep(1) 
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
# 3. 身份验证界面 (UI 增强版)
# ==========================================
def auth_ui():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.write("# 🔐 职业追踪系统")
        st.caption("管理你的领英申请，掌握每一个求职进度")
        with st.container(border=True):
            tab1, tab2 = st.tabs(["👋 返回登录", "🆕 建立账号"])
            with tab1:
                with st.form("login"):
                    e = st.text_input("邮箱")
                    p = st.text_input("密码", type="password")
                    if st.form_submit_button("登录"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                            exp = datetime.datetime.now() + datetime.timedelta(hours=3)
                            cookie_manager.set("sb_access_token", res.session.access_token, expires_at=exp)
                            cookie_manager.set("sb_refresh_token", res.session.refresh_token, expires_at=exp)
                            st.success("验证成功，正在进入...")
                            time.sleep(1); st.rerun()
                        except Exception as ex: st.error(f"登录失败: {ex}")
            with tab2:
                with st.form("signup"):
                    ne = st.text_input("邮箱地址")
                    np = st.text_input("设置密码 (6位以上)", type="password")
                    if st.form_submit_button("立即注册"):
                        try:
                            supabase.auth.sign_up({"email": ne, "password": np})
                            st.success("注册成功！请直接登录")
                        except Exception as ex: st.error(f"注册失败: {ex}")

# ==========================================
# 4. 主程序界面 (专业看板版)
# ==========================================
if not user:
    auth_ui()
else:
    # --- 侧边栏优化 ---
    with st.sidebar:
        st.markdown(f"### 👤 当前用户\n**{user.email}**")
        with st.expander("🔑 我的 API 密钥"):
            st.code(user.id, language=None)
        
        st.divider()
        if st.button("🚪 退出安全登录"):
            supabase.auth.sign_out()
            st.session_state.user = None
            cookie_manager.delete("sb_access_token")
            cookie_manager.delete("sb_refresh_token")
            if 'cookie_sync_done' in st.session_state: del st.session_state.cookie_sync_done
            st.rerun()

    # --- 主标题区域 ---
    st.title("💼 求职申请追踪看板")
    
    @st.cache_data(ttl=2)
    def load_my_data(uid):
        res = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['dt_object'] = pd.to_datetime(df['created_at'])
            df['date'] = df['dt_object'].dt.strftime('%Y-%m-%d')
            # 状态 Emoji 映射
            status_map = {"applied": "📝 Applied", "interviewing": "🎯 Interview", "offer": "🎉 Offer", "rejected": "❌ Rejected", "ghosted": "👻 Ghosted"}
            df['status_label'] = df['status'].map(lambda x: status_map.get(x, x))
            df = df.reset_index(drop=True)
            df.insert(0, 'No', df.index + 1)
        return df

    df = load_my_data(user.id)

    if not df.empty:
        # --- 顶部统计指标 (Metrics) ---
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("总申请记录", len(df))
        with m2: st.metric("面试邀约", len(df[df['status'] == 'interviewing']), delta_color="normal")
        with m3: st.metric("收到 Offer", len(df[df['status'] == 'offer']))
        with m4: 
            rate = f"{(len(df[df['status'].isin(['interviewing', 'offer'])])/len(df)*100):.1f}%"
            st.metric("转化率", rate)

        # --- 图表区域 ---
        c_left, c_right = st.columns([1, 1.5])
        with c_left:
            with st.container(border=True):
                st.subheader("📌 状态分布")
                fig_pie = px.pie(df, names='status_label', hole=0.6, 
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
                st.plotly_chart(fig_pie, use_container_width=True)

        with c_right:
            with st.container(border=True):
                st.subheader("📈 投递趋势")
                df_trend = df.groupby('date').size().reset_index(name='count')
                fig_line = px.line(df_trend, x='date', y='count', markers=True)
                fig_line.update_traces(line_color=UI_CONFIG["primary_color"])
                fig_line.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=250, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_line, use_container_width=True)

        # --- 数据列表 (Advanced Table) ---
        st.subheader("📋 详细申请列表")
        st.dataframe(
            df,
            column_config={
                "No": st.column_config.NumberColumn("序号", width="small"),
                "date": "投递日期",
                "company": st.column_config.TextColumn("公司", help="招聘企业名称"),
                "title": "岗位名称",
                "status_label": st.column_config.TextColumn("当前状态"),
                "location": "工作地点"
            },
            column_order=("No", "date", "company", "title", "location", "status_label"),
            use_container_width=True,
            hide_index=True
        )

        # --- 管理区域 (Form) ---
        st.markdown("### 🛠️ 条目管理")
        with st.container(border=True):
            job_list = df.apply(lambda x: f"#{x['No']} | {x['company']} - {x['title']}", axis=1).tolist()
            sel_job = st.selectbox("选择要修改或查看的记录：", ["-- 请选择岗位 --"] + job_list)
            
            if sel_job != "-- 请选择岗位 --":
                idx = int(sel_job.split('|')[0].replace('#', '').strip())
                row = df[df['No'] == idx].iloc[0]
                
                with st.form("edit_area", clear_on_submit=False):
                    f1, f2, f3 = st.columns([2, 2, 1])
                    with f1:
                        new_t = st.text_input("岗位", value=row['title'])
                        new_c = st.text_input("公司", value=row['company'])
                    with f2:
                        s_list = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                        new_s = st.selectbox("修改状态", s_list, index=s_list.index(row['status']) if row['status'] in s_list else 0)
                        new_l = st.text_input("地点", value=row['location'])
                    with f3:
                        st.write("操作提示")
                        st.caption("修改信息后点击下方保存。")
                    
                    new_d = st.text_area("职位描述 (Markdown)", value=row['description'], height=100)
                    
                    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
                    if btn_col1.form_submit_button("💾 保存更新"):
                        supabase.table("job_applications").update({
                            "title": new_t, "company": new_c, "status": new_s, "location": new_l, "description": new_d
                        }).eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.success("更新成功！")
                        time.sleep(0.5); st.rerun()
                    
                    if btn_col2.form_submit_button("🗑️ 删除记录"):
                        supabase.table("job_applications").delete().eq("id", row['id']).execute()
                        st.cache_data.clear()
                        st.warning("记录已移除")
                        time.sleep(0.5); st.rerun()
    else:
        # 空状态处理
        _, c_empty, _ = st.columns([1, 2, 1])
        with c_empty:
            st.info("💡 暂时没有抓取到数据，快去 LinkedIn 看看心仪的职位吧！")
            st.image("https://img.icons8.com/illustrations/printable/空状态.png", use_column_width=True) # 示意图
