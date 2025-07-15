# Python 职位市场分析平台
全面的Python职位数据分析系统：从数据采集、清洗到可视化展示全流程

## 🚀 项目概述
利用Python技术栈构建的端到端职位分析平台，目标是通过自动化的数据流程揭示Python就业市场趋势。本项目从前程无忧(51job)抓取Python相关职位信息，进行数据处理与分析，并通过可视化图表和Web看板展示分析结果。

## 🌟 核心功能
- ✅ 动态网页爬取 - 攻克JavaScript复杂渲染
- 📊 多维度分析 - 城市分布/薪资水平/技能需求
- 📈 Streamlit看板 - 数据产品级可视化展示
- 🛡️ 高级反爬应对 - 身份验证与行为模拟方案

## 🛠️ 技术架构
mermaid
flowchart LR
    A[Selenium爬虫] --> B[原始数据.csv]
    B --> C[Pandas数据分析]
    C --> D[Matplotlib可视化]
    D --> E[Streamlit Dashboard]

## 运行步骤
1. 克隆仓库：
（1）git clone https://github.com/你的用户名/JobAnalysis.git
（2）cd JobAnalysis

2. 创建虚拟环境（可选）：
（1）python -m venv venv
（2）source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

3. 安装依赖：
pip install -r requirements.txt

4. 运行爬虫（需要先配置你的Cookie，请参考步骤）：
进入scraper目录，打开job_scraper.py，将你的Cookie字符串填入COOKIES_STR变量。然后运行：
python job_scraper.py

5. 运行数据分析：
python analysis/data_analyzer.py

6. 运行Web应用：
streamlit run app.py

## 项目结构
JobAnalysis/
├── .gitignore           # 忽略文件模板
├── README.md            # 项目说明文档
├── requirements.txt     # 依赖库列表
│
├── scraper/             # 爬虫相关
│   ├── job_scraper.py   # 主爬虫脚本
│   └── __init__.py      # 空文件(标识Python包)
│
├── analysis/            # 分析相关
│   ├── data_analyzer.py # 数据分析脚本
│   └── __init__.py      
│
├── drivers/             # 浏览器驱动(如果包含)
│   └── chromedriver.exe
│
├── data/                # 数据(不包含在仓库)
│   ├── jobs_raw.csv     
│   └── jobs_cleaned.csv
│
├── output/              # 分析结果(不包含在仓库)
│   ├── job_counts_by_city.png
│   ├── salary_by_city.png
│   └── skills_wordcloud.png
│
└── app.py               # 主应用文件

scraper/: 爬虫代码
analysis/: 数据分析代码
data/: 数据存储（原始数据和清洗后数据）
output/: 分析结果图表
app.py: Streamlit Web应用

## 技术栈
Python
Selenium (数据采集)
BeautifulSoup (HTML解析)
Pandas, NumPy (数据处理)
Matplotlib, Seaborn, WordCloud (可视化)
Streamlit (Web应用)