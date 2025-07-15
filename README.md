# 🐍 Python 职位市场分析平台

> **全面的Python职位数据分析系统**：从数据采集、清洗到可视化展示全流程

![Python职位分析](docs/demo.png)  
*项目可视化展示效果图*

## 🚀 项目概述
利用Python技术栈构建的端到端职位分析平台，通过自动化数据流程揭示Python就业市场趋势。本项目从前程无忧(51job)抓取Python相关职位信息，进行深度数据清洗与分析，最终通过交互式可视化图表展示分析结果。

## 🌟 核心功能
- ✅ **动态网页爬取** - 攻克JavaScript复杂渲染与"假分页"反爬策略
- 📊 **多维度分析** - 城市分布/薪资水平/技能需求全面覆盖
- 📈 **Streamlit看板** - 数据产品级可视化展示
- 🛡️ **数据安全** - Cookie验证与浏览器行为模拟

## 🛠️ 技术架构
```mermaid
flowchart LR
    A[Selenium爬虫] --> B[原始数据.csv]
    B --> C[Pandas数据分析]
    C --> D[Matplotlib可视化]
    D --> E[Streamlit Dashboard]
    E --> F[交互式Web看板]
⚙️ 运行步骤
1. 克隆仓库
bash
git clone https://github.com/你的用户名/JobAnalysis.git
cd JobAnalysis
2. 创建虚拟环境（可选）
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. 安装依赖
bash
pip install -r requirements.txt
4. 配置并运行爬虫
打开 scraper/job_scraper.py
在代码顶部找到 COOKIES_STR 变量
将您的Cookie字符串填入该变量
运行爬虫：
bash
python scraper/job_scraper.py
5. 运行数据分析
bash
python analysis/data_analyzer.py
6. 启动Web应用
bash
streamlit run app.py
📂 项目结构
code
JobAnalysis/
├── .gitignore           # 忽略文件配置
├── README.md            # 项目文档
├── requirements.txt     # 依赖库列表
├── app.py               # Web应用入口
│
├── scraper/             # 爬虫模块
│   ├── job_scraper.py   # 主爬虫脚本
│   └── __init__.py      
│
├── analysis/            # 分析模块
│   ├── data_analyzer.py # 数据分析脚本
│   └── __init__.py      
│
├── data/                # 数据存储[.gitignore]
│   ├── jobs_raw.csv     
│   └── jobs_cleaned.csv
│
├── output/              # 分析结果[.gitignore]
│   ├── job_counts_by_city.png
│   ├── salary_by_city.png
│   └── skills_wordcloud.png
│
└── docs/                # 文档资源
    └── demo.png         # 项目截图
💻 技术栈
核心语言与框架
Python 3.x - 主要开发语言
Streamlit - 数据应用框架
Selenium - 浏览器自动化工具
数据处理
类别	工具	用途
数据采集	BeautifulSoup	HTML解析
数据清洗	Pandas	数据清洗与转换
数据分析	NumPy	数值计算
文本处理	re	正则表达式
可视化
类型	库	输出
静态图表	Matplotlib	基础图表
统计图表	Seaborn	高级图表
词云图	WordCloud	技能词云
📊 分析维度
分析维度	实现技术	输出图表
城市分布	Pandas分组聚合	水平条形图
薪资水平	正则解析+聚类	箱线图+散点图
技能需求	文本分词+词频统计	WordCloud词云
💡 使用建议
爬虫配置：定期更新Cookie确保爬虫有效性
可视化优化：调整图表参数提升视觉效果
功能扩展：在Web应用中添加更多交互控件
提示：完整数据可在运行项目后生成于data/和output/目录

⁉️ 常见问题
Q: 为什么爬虫无法获取数据？
A: 请确保：

已更新有效的Cookie
目标网站未修改布局结构
Q: 图表无法正常显示？
A: 请尝试：

升级依赖：pip install --upgrade matplotlib pandas
检查输出文件路径
Q: Web应用报路径错误？
A: 确认你已：

运行了爬虫和分析脚本
所有文件都在项目根目录下运行