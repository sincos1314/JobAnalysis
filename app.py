import streamlit as st
import pandas as pd
import os

# 获取当前app.py文件所在的目录
BASE_DIR = os.path.dirname(__file__)

# 基于该目录构建数据和图表文件的【绝对路径】
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'jobs_cleaned.csv')
CITY_COUNT_IMG_PATH = os.path.join(BASE_DIR, 'output', 'job_counts_by_city.png')
CITY_SALARY_IMG_PATH = os.path.join(BASE_DIR, 'output', 'salary_by_city.png')
SKILLS_WORDCLOUD_IMG_PATH = os.path.join(BASE_DIR, 'output', 'skills_wordcloud.png')


# --- 页面主逻辑 ---
st.set_page_config(page_title="Python职位市场分析看板", layout="wide")

st.title("Python 职位市场分析看板")
st.write("数据来源：前程无忧 (51job.com)")

# 检查所有必需的文件是否存在
required_files_exist = os.path.exists(CLEANED_DATA_PATH) and \
                       os.path.exists(CITY_COUNT_IMG_PATH) and \
                       os.path.exists(CITY_SALARY_IMG_PATH)

# 如果文件不齐全，显示错误信息
if not required_files_exist:
    st.error("错误：必需的数据或图表文件不存在！")
    st.info("请按照以下步骤操作：")
    st.code("""
    1. 确保你的终端位于项目根目录 (JobAnalysis) 下。
    2. 运行爬虫: python scraper/job_scraper.py
    3. 运行分析器: python analysis/data_analyzer.py
    4. 重新启动Streamlit应用: streamlit run app.py
    """)
    # 额外提供调试信息，显示程序正在查找的路径
    st.subheader("调试信息：")
    st.write(f"正在查找数据文件于: `{CLEANED_DATA_PATH}` - {'找到' if os.path.exists(CLEANED_DATA_PATH) else '未找到'}")
    st.write(f"正在查找图表1于: `{CITY_COUNT_IMG_PATH}` - {'找到' if os.path.exists(CITY_COUNT_IMG_PATH) else '未找到'}")
    st.write(f"正在查找图表2于: `{CITY_SALARY_IMG_PATH}` - {'找到' if os.path.exists(CITY_SALARY_IMG_PATH) else '未找到'}")

# 如果文件都存在，则正常显示内容
else:
    st.header("热门城市分析")
    col1, col2 = st.columns(2)
    with col1:
        st.image(CITY_COUNT_IMG_PATH, caption='Top 10 城市Python岗位数量', use_column_width=True)
    with col2:
        st.image(CITY_SALARY_IMG_PATH, caption='Top 10 热门城市平均月薪 (K/月)', use_column_width=True)

    # 词云图是可选的，单独检查它是否存在
    if os.path.exists(SKILLS_WORDCLOUD_IMG_PATH):
        st.header("热门技能需求")
        st.image(SKILLS_WORDCLOUD_IMG_PATH, caption='岗位技能需求词云', use_column_width=True)
    else:
        st.warning("技能需求词云图未生成，可能是原始数据中缺少相关标签。")

    st.header("职位数据详情")
    try:
        df = pd.read_csv(CLEANED_DATA_PATH)
        # 使用st.dataframe可以更好地展示表格，并提供交互功能
        st.dataframe(df)
    except Exception as e:
        st.error(f"加载数据表格失败: {e}")

