import pandas as pd
import numpy as np
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# --- 清洗函数 ---
def parse_salary_unit(s):
    if pd.isna(s): return np.nan
    # 在提取数字前，先去掉 ·xx薪 这种描述
    s = str(s).split('·')[0]
    number = re.findall(r'(\d+\.?\d*)', s)
    if not number: return np.nan
    number = float(number[0])
    if '万' in s: return number * 10
    if '千' in s: return number
    return number if number > 100 else number * 10

def clean_salary(salary_str):
    if pd.isna(salary_str): return np.nan, np.nan
    salary_str, is_annual = str(salary_str).strip(), '年' in salary_str
    parts = salary_str.split('-')
    try:
        min_val = parse_salary_unit(parts[0])
        max_val = parse_salary_unit(parts[1] if len(parts) > 1 else parts[0])
        if is_annual: min_val, max_val = min_val / 12, max_val / 12
        return round(min_val, 1), round(max_val, 1)
    except:
        return np.nan, np.nan

def process_data(input_path, output_path):
    """【最终健壮版】完整的数据清洗和处理流程"""
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"错误：找不到 {input_path}。请先运行爬虫。")
        return pd.DataFrame()

    df.columns = df.columns.str.strip()
    df.dropna(subset=['jobId'], inplace=True)
    df.drop_duplicates(subset=['jobId'], inplace=True)
    df[['min_salary', 'max_salary']] = df['jobSalary'].apply(clean_salary).apply(pd.Series)
    df['avg_salary'] = (df['min_salary'] + df['max_salary']) / 2
    df['city'] = df['jobArea'].apply(lambda x: str(x).split('-')[0] if pd.notna(x) else np.nan)
    df.dropna(subset=['avg_salary', 'city'], inplace=True)
    
    if df.empty:
        print("【警告】所有数据在清洗后被过滤。")
        return pd.DataFrame()

    df.rename(columns={
        'jobTitle': '职位名称', 'companyName': '公司名称', 'jobYear': '经验要求',
        'jobDegree': '学历要求', 'companyTypeString': '公司性质', 'companySizeString': '公司规模',
        'jobLabel': '技能标签', 'jobHref': '详情链接', 'city': '城市'
    }, inplace=True)
    
    final_cols = [
        '职位名称', '公司名称', '城市', 'min_salary', 'max_salary', 'avg_salary',
        '经验要求', '学历要求', '公司性质', '公司规模', '技能标签', '详情链接'
    ]
    df_cleaned = df[[col for col in final_cols if col in df.columns]]
    
    df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n数据清洗完成！最终成功处理了 {len(df_cleaned)} 条有效数据。")
    print(f"清洗后的数据已保存至 '{output_path}'")
    return df_cleaned

# 可视化函数 analyze_and_visualize 
def analyze_and_visualize(df, output_dir):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    city_counts = df['城市'].value_counts().nlargest(10)
    plt.figure(figsize=(12, 7)); sns.barplot(x=city_counts.index, y=city_counts.values, palette='viridis')
    plt.title('Python岗位数量Top10城市', fontsize=16); plt.xlabel('城市', fontsize=12); plt.ylabel('岗位数量', fontsize=12)
    plt.xticks(rotation=45, ha='right'); plt.tight_layout(); plt.savefig(f'{output_dir}/job_counts_by_city.png')
    print("已生成 '岗位数量Top10城市' 图表。")

    city_salary = df[df['城市'].isin(city_counts.index)].groupby('城市')['avg_salary'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 7)); sns.barplot(x=city_salary.index, y=city_salary.values, palette='plasma')
    plt.title('Top10热门城市平均薪资 (千/月)', fontsize=16); plt.xlabel('城市', fontsize=12); plt.ylabel('平均薪资 (K/月)', fontsize=12)
    plt.xticks(rotation=45, ha='right'); plt.tight_layout(); plt.savefig(f'{output_dir}/salary_by_city.png')
    print("已生成 'Top10热门城市平均薪资' 图表。")

    all_labels = df['技能标签'].dropna().astype(str)
    if not all_labels.empty:
        text = " ".join(label.strip() for label in all_labels.str.cat(sep=',').split(',') if label.strip())
        if text:
            stopwords = set(['Python', 'python', '后端', '开发', '工程师', '面议'])
            wordcloud = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', width=1000, height=500, background_color='white', stopwords=stopwords, collocations=False, max_words=100).generate(text)
            plt.figure(figsize=(15, 8)); plt.imshow(wordcloud, interpolation='bilinear'); plt.title('岗位热门技能需求词云', fontsize=20); plt.axis('off'); plt.savefig(f'{output_dir}/skills_wordcloud.png')
            print("已生成 '技能关键词词云' 图表。")
        else:
            print("技能标签内容为空，跳过生成词云。")
    else:
        print("无有效的技能标签数据，跳过生成词云。")

if __name__ == '__main__':
    RAW_DATA_PATH = '../data/jobs_raw.csv'
    CLEANED_DATA_PATH = '../data/jobs_cleaned.csv'
    OUTPUT_DIR = '../output'
    
    cleaned_df = process_data(RAW_DATA_PATH, CLEANED_DATA_PATH)
    
    if cleaned_df is not None and not cleaned_df.empty:
        analyze_and_visualize(cleaned_df, OUTPUT_DIR)
        print("\n所有分析图表已生成并保存到 'output' 目录。")
    else:
        print("\n数据处理后为空，无法进行分析。请检查原始数据。")
