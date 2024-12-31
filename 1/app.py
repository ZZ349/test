import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
from pyecharts.charts import Pie
from pyecharts import options as opts
from collections import Counter
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import jieba  # 导入jieba分词库

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

# 从URL获取中文文本内容并添加调试信息
def fetch_chinese_text_from_url(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        # 使用正则表达式保留中文字符（包括汉字、中文标点符号等）
        cleaned_text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', ' ', text).strip()
        if not cleaned_text:  # 如果文本为空，则抛出异常
            raise ValueError("The fetched content is empty or contains no Chinese characters.")
        return cleaned_text
    except Exception as e:
        st.error(f"Error fetching Chinese content from {url}: {str(e)}")
        return ""

# 分析文本并返回最常见的20个单词及其频率，确保只包含中文词汇
def analyze_chinese_text(text):
    words = list(jieba.cut(text))  # 使用jieba进行中文分词
    chinese_words = [word for word in words if re.match(r'^[\u4e00-\u9fff]+$', word)]  # 只保留纯汉字词汇
    # 去除长度为1的词（可选，根据需求）
    chinese_words = [word for word in chinese_words if len(word) > 1]
    if not chinese_words:  # 如果没有找到任何中文单词，则抛出异常
        raise ValueError("No valid Chinese words found in the provided text after segmentation.")
    return dict(Counter(chinese_words).most_common(20))

# Plotly柱状图
def plotly_bar_chart(top_20_words):
    fig = px.bar(x=list(top_20_words.keys()), y=list(top_20_words.values()), labels={'x': 'Words', 'y': 'Frequency'})
    fig.update_layout(title="Top 20 Words Frequency", xaxis_tickangle=-45)
    return fig

# Pyecharts饼图
def pyecharts_pie_chart(top_20_words):
    pie = Pie()
    pie.add("", list(top_20_words.items()))
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Top 20 Words Distribution"))
    return pie.render_embed()

# Matplotlib柱状图
def matplotlib_bar_chart(top_20_words):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体，这里使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_20_words.keys(), top_20_words.values())
    ax.set_title('Top 20 Words Frequency', fontproperties='SimHei')
    ax.set_xlabel('Words', fontproperties='SimHei')
    ax.set_ylabel('Frequency', fontproperties='SimHei')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig
# 生成词云图
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

def generate_word_cloud(top_20_words):
    # 确保词云可以正确显示中文，选择一个支持中文的字体文件路径（根据您的环境调整）
    font_path = "path/to/simhei.ttf"  # 例如：C:/Windows/Fonts/simhei.ttf

    # 过滤掉非中文词汇（如果需要的话）
    valid_words = {word: freq for word, freq in top_20_words.items() if re.match(r'^[\u4e00-\u9fff]+$', word)}

    if not valid_words:
        raise ValueError("No valid Chinese words found to generate the word cloud.")

    # 创建词云对象，并指定字体路径
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate_from_frequencies(valid_words)

    # 显示词云图
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# Streamlit界面
st.title("中文文本分析工具")
url = st.text_input('请输入要分析的包含中文文本的URL')

if url:
    try:
        text = fetch_chinese_text_from_url(url)
        if not text:
            st.warning("未能从提供的URL中获取有效中文文本。")
        else:
            top_20_words = analyze_chinese_text(text)

            chart_type = st.selectbox('选择要显示的图表类型', ['Word Cloud', 'Bar Chart (Plotly)', 'Bar Chart (Matplotlib)', 'Pie Chart'])
            if chart_type == 'Word Cloud':
                st.pyplot(generate_word_cloud(top_20_words))
            elif chart_type == 'Bar Chart (Plotly)':
                st.plotly_chart(plotly_bar_chart(top_20_words))
            elif chart_type == 'Bar Chart (Matplotlib)':
                st.pyplot(matplotlib_bar_chart(top_20_words))
            elif chart_type == 'Pie Chart':
                st.components.v1.html(pyecharts_pie_chart(top_20_words), width=800, height=600)
    except Exception as e:
        st.error(f"发生错误: {str(e)}")