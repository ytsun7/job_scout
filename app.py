import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- 初始化 Session State ---
# 必须放在脚本最顶端，防止访问未定义的键
if "user" not in st.session_state:
    st.session_state.user = None

# --- 配置区 ---
# 安全提示：URL 和 KEY 现在从 Streamlit Secrets 中读取，不再硬编码在代码里
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    # 使用从 Secrets 获取的参数初始化客户端
    return create_client(URL, KEY)

supabase = init_connection()

# --- 身份验证界面 ---
def auth_ui():
    st.title("🔐 登录中心")
    tab1, tab2 = st.tabs(["用户登录", "新用户注册"])
    
    with tab1:
        with st.form("login_form"):
            e = st.text_input("邮箱")
            p = st.text_input("密码", type="password")
            submit = st.form_submit_button("立即登录")
            
            if submit:
                try:
                    # 尝试登录
                    res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                    if res.user:
                        st.session_state.user = res.user
                        st.rerun() # 立即触发重绘
                except Exception as ex:
                    st.error(f"登录失败: {str(ex)}")

    with tab2:
        with st.form("signup_form"):
            ne = st.text_input("新邮箱")
            np = st.text_input("设置密码 (至少6位)")
            if st.form_submit_button("提交注册"):
                try:
                    supabase.auth.sign_up({"email": ne, "password": np})
                    st.success("注册成功！请直接登录")
                except Exception as ex:
                    st.error(f"注册失败: {str(ex)}")

# --- 主程序逻辑 ---
if st.session_state.user is None:
    auth_ui()
else:
    # 侧边栏
    st.sidebar.success(f"已登录: {st.session_state.user.email}")
    st.sidebar.info(f"🔑 你的 User ID (用于插件):\n\n{st.session_state.user.id}")
    
    if st.sidebar.button("🚪 退出登录"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    st.title("💼 我的申请追踪看板")

    @st.cache_data(ttl=2)
    def load_my_data(uid):
        try:
            # 获取数据
            response = supabase.table("job_applications").select("*").eq("user_id", uid).order('created_at', desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['dt_object'] = pd.to_datetime(df['created_at'])
                df['formatted_date'] = df['dt_object'].dt.strftime('%Y-%m-%d %H:00')
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                df.insert(0, '显示序号', df.index)
            return df
        except Exception as ex:
            st.warning(f"数据加载异常: {str(ex)}")
            return pd.DataFrame()

    df = load_my_data(st.session_state.user.id)

    if not df.empty:
        # --- 1. 数据统计与可视化 ---
        st.subheader("📊 数据概览")
        
        m1, m2, m3 = st.columns(3)
        total_apps = len(df)
        offers = len(df[df['status'] == 'offer'])
        interviews = len(df[df['status'] == 'interviewing'])
        
        m1.metric("总申请数", total_apps)
        m2.metric("面试邀约", interviews)
        m3.metric("收到 Offer", offers)

        st.write("---")
        
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("**状态分布**")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['状态', '数量']
            color_map = {
                "applied": "#0073b1", "interviewing": "#f39c12", 
                "offer": "#27ae60", "rejected": "#e74c3c", "ghosted": "#95a5a6"
            }
            fig_pie = px.pie(
                status_counts, values='数量', names='状态', 
                hole=0.4, color='状态', color_discrete_map=color_map
            )
            fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.markdown("**投递周趋势**")
            df['week'] = df['dt_object'].dt.to_period('W').apply(lambda r: r.start_time)
            trend_df = df.groupby('week').size().reset_index(name='count')
            trend_df = trend_df.sort_values('week')
            
            fig_trend = px.bar(
                trend_df, x='week', y='count',
                labels={'week': '周次', 'count': '申请数'},
                color_discrete_sequence=['#0073b1']
            )
            fig_trend.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
            st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()

        # --- 2. 列表区域 ---
        st.subheader("📋 投递明细列表")
        st.dataframe(
            df[['显示序号', 'formatted_date', 'title', 'company', 'location', 'status']], 
            use_container_width=True, 
            hide_index=True
        )

        st.divider()

        # --- 3. 内容管理 ---
        st.subheader("🛠️ 条目管理")
        job_options = df.apply(lambda x: f"序号 {x['显示序号']}: {x['title']} @ {x['company']}", axis=1).tolist()
        sel = st.selectbox("请选择要操作的行:", ["-- 请选择 --"] + job_options)
        
        if sel != "-- 请选择 --":
            display_idx = int(sel.split(':')[0].replace('序号 ', ''))
            row = df[df['显示序号'] == display_idx].iloc[0]
            
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    t = st.text_input("岗位名称", value=row['title'])
                    status_list = ["applied", "interviewing", "offer", "rejected", "ghosted"]
                    # 安全获取索引
                    current_idx = status_list.index(row['status']) if row['status'] in status_list else 0
                    s = st.selectbox("当前状态", status_list, index=current_idx)
                with c2:
                    c = st.text_input("公司名称", value=row['company'])
                    l = st.text_input("地点", value=row['location'])
                
                desc = st.text_area("职位描述", value=row['description'], height=150)
                
                if st.form_submit_button("💾 保存修改"):
                    supabase.table("job_applications").update({
                        "title": t, "company": c, "status": s, "location": l, "description": desc
                    }).eq("id", row['id']).execute()
                    st.cache_data.clear()
                    st.rerun()

            if st.button("🗑️ 删除此条记录"):
                supabase.table("job_applications").delete().eq("id", row['id']).execute()
                st.cache_data.clear()
                st.rerun()
    else:
        st.info("目前没有数据。请通过插件在领英上抓取！")
