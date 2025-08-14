import pandas as pd
import numpy as np
import re
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# --- 清洗函数 ---
def parse_salary_value(num_str, unit):
    """根据明确的单位来解析数值"""
    try:
        num = float(num_str)
        if unit == '万':
            return num * 10  # 统一转换为千
        if unit == '千':
            return num
        if unit == '元/天':
            return num * 21.75 / 1000 # 按每月21.75个工作日计算，并转换为千
        return num # 如果没有单位，则假定为千
    except (ValueError, TypeError):
        return np.nan

def clean_salary(salary_str):
    """
    【最终健壮版】薪资清洗函数，能正确处理单位不一致和日薪等复杂情况。
    """
    if pd.isna(salary_str) or not isinstance(salary_str, str) or '面议' in salary_str:
        return np.nan, np.nan

    salary_str = salary_str.strip()
    
    # 优先处理日薪情况
    if '元/天' in salary_str:
        nums = re.findall(r'(\d+\.?\d*)', salary_str)
        if nums:
            daily_salary = float(nums[0])
            # 将日薪转换为月薪（千元单位）
            monthly_k = daily_salary * 21.75 / 1000
            return round(monthly_k, 1), round(monthly_k, 1)
        return np.nan, np.nan

    # 识别主要单位（万、千）
    unit = '千' # 默认单位
    if '万' in salary_str:
        unit = '万'
    
    # 去掉福利描述，如 "·15薪"
    salary_str = salary_str.split('·')[0]
    
    # 提取所有数字部分
    nums = re.findall(r'(\d+\.?\d*)', salary_str)
    
    if len(nums) == 0:
        return np.nan, np.nan
    
    if len(nums) == 1:
        # 单个薪资，如 "1.5万"
        val = parse_salary_value(nums[0], unit)
        return round(val, 1), round(val, 1)
    
    if len(nums) >= 2:
        # 薪资范围，如 "1-1.5万" 或 "8千-1.2万"
        min_val_str, max_val_str = nums[0], nums[1]
        
        # 关键逻辑：如果max_val_str后面有'万'，则min_val_str也应该按'万'处理
        # 适用于 "8千-1.2万" -> 8千, 12千 的情况
        temp_parts = salary_str.split('-')
        min_unit = '千' if '千' in temp_parts[0] else unit
        max_unit = '万' if '万' in temp_parts[1] else unit

        # 如果最大值单位是万，最小值单位是千，但最小值大于10（不合理），则认为它也是万
        if max_unit == '万' and min_unit == '千' and float(min_val_str) > 10:
             min_unit = '万'
        
        # 修正 "1-1.5万" 的情况，让 '1' 继承 '万' 的单位
        if '万' in temp_parts[1] and '千' not in temp_parts[0] and '万' not in temp_parts[0]:
            min_unit = '万'

        min_val = parse_salary_value(min_val_str, min_unit)
        max_val = parse_salary_value(max_val_str, max_unit)
        
        return round(min_val, 1), round(max_val, 1)
        
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
        'jobLabel': '技能标签', 'jobHref': '详情链接', 'city': '城市','min_salary': '最低薪资',
        'max_salary': '最高薪资','avg_salary': '平均薪资'
    }, inplace=True)
    
    final_cols = [
        '职位名称', '公司名称', '城市', '最低薪资', '最高薪资', '平均薪资',
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

    city_salary = df[df['城市'].isin(city_counts.index)].groupby('城市')['平均薪资'].mean().sort_values(ascending=False)
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
    # 从 analysis 目录上升到项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent 
    
    # 定义数据文件和输出目录的绝对路径
    RAW_DATA_PATH = BASE_DIR / 'data' / 'jobs_raw.csv'
    CLEANED_DATA_PATH = BASE_DIR / 'data' / 'jobs_cleaned.csv'
    OUTPUT_DIR = BASE_DIR / 'output'

    print(f"🚀 开始处理数据: {RAW_DATA_PATH}")
    cleaned_df = process_data(RAW_DATA_PATH, CLEANED_DATA_PATH)
    
    if cleaned_df is not None and not cleaned_df.empty:
        print("✅ 数据清洗完成。")
        print("📊 开始生成分析图表...")
        analyze_and_visualize(cleaned_df, OUTPUT_DIR)
        print(f"\n🎉 所有分析图表已生成并保存到 '{OUTPUT_DIR}' 目录。")
    else:
        print("\n🛑 数据处理失败或处理后为空，无法进行分析。")