# -*- coding:utf-8 -*-
from time import time, sleep
import requests
import re
from bs4 import BeautifulSoup
import sys


def get_html(current_url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                      '81.0.4044.138 Safari/537.36'
    }
    try:
        response = requests.get(current_url, headers=header)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


def find_all_table_data(table_label):
    result_list = list()
    a_label_list = table_label.find_all(name='a')
    for each_a_label in a_label_list:
        a_name = each_a_label.string
        a_href = each_a_label['href']
        temp_tuple = (a_name, a_href)
        result_list.append(temp_tuple)
    return result_list


def get_more_article_data(article_url):
    sleep(1)
    html = get_html(article_url)
    if html is None:
        return None, None
    soup = BeautifulSoup(html, 'lxml')
    tags_content = soup.find(attrs={'class': 'post-tags'})
    tags_list = list()  # 新建一个空list
    if tags_content is not None:  # 这个地方注意一下，有可能是没有tags的
        tags_all = tags_content.find_all(name='a')
        for tag in tags_all:
            tags_list.append(tag.string)
    else:
        tags_list = []
    like_count_string = soup.find(attrs={'class': 'like-count'}).string
    # print(like_count_string)  # 输出查看获得的赞数
    like_count_list = re.findall(r'\d+', like_count_string)  # 如果考虑效率问题，这个和下面的用哪个比较好？值得思考(注意在这里返回只有一个元素)
    if len(like_count_list) == 0:
        like_count = 0
    else:
        like_count = int(like_count_list[0])
    # like_count = like_count_string.split('(')[1].split(')')[0]  # 是否split的实现也是用了正则表达式？
    return tags_list, like_count


def jump_to_article_page(article_id):
    article_url = 'http://www.cbaigui.com/?p=' + article_id
    return get_more_article_data(article_url)


def get_article_data(article):
    article_id = article['id'].split('-')[1]
    article_date = article.div.findChild(name='div').findChildren(name='div')  # 返回一个List
    article_day = article_date[0].contents[-1].strip('\r\n').replace('\t', '')
    article_month = article_date[2].string.strip("月")
    article_year = article_date[3].string
    comment_count = int(article.find(name='span').contents[-1])
    article_name = article.h2.a.string
    tag_list, like_count = jump_to_article_page(article_id)
    if tag_list is None and like_count is None:
        tag_list = []
        like_count = 0
    article_tuple = (article_id, article_name, article_year + '-' + article_month + '-' + article_day,
                     comment_count, tag_list, like_count)
    return article_tuple


def get_category(index_url):
    sleep(1)
    html = get_html(index_url)
    if html is None:
        return None
    soup = BeautifulSoup(html, 'lxml')  # 利用bs4进行解释，'lxml'参数这里可以再多学习一下。
    index_content = soup.find(attrs={'class': 'entry themeform'})  # 找到所有的指定属性的html内容，返回一个list
    table_list = index_content.find_all(name='table')  # 找到所有的制定标签名字的内容， 返回一个list
    alphabet_index = dict()  # 保存每一个类别下的数据
    for i in range(len(table_list)):
        category = table_list[i].find_previous_sibling(name='p').string
        alphabet_index.setdefault(category, list())
        alphabet_index[category] = find_all_table_data(table_list[i])
    return alphabet_index


def write_to_file(article_tuple):
    article_id = article_tuple[0]  # string
    article_name = article_tuple[1]  # string
    post_date = article_tuple[2]  # string
    comment_count = article_tuple[3]  # int
    tags = article_tuple[4]  # list:string
    like_count = article_tuple[5]  # int
    category_id = article_tuple[6]  # int
    category_name = article_tuple[7]
    # print(article_id, article_name, post_date, comment_count, tags, like_count, category_id, category_name)
    with open('./cbaigui_data.csv', 'a', encoding='utf-8') as f:
        sep = '\t'  # 注意分隔符的选择
        data = article_id + sep + article_name + sep + str(category_id) + sep + category_name + sep + \
            post_date + sep + str(tags) + sep + str(comment_count) + sep + str(like_count) + '\n'
        f.write(data)


def get_first_page_article(current_category_url):  # 获取当前页面下的所有article标签
    cat_name = current_category_url[0]
    print("Current category:", cat_name)
    cat_url = current_category_url[1]
    print("Current page url:", cat_url)
    cat_id = int(cat_url.split('=')[1])
    sleep(2)  # 每次爬取的时候设置时间差（怎么样设置某一个时间段中的随机时间？单位为秒数）
    cat_html = get_html(cat_url)
    if cat_html is None:
        return None, None
    cat_soup = BeautifulSoup(cat_html, 'lxml')
    content = cat_soup.find(attrs={'class': 'content'})
    article_list = content.find_all(name='article')
    # 获取当前页面的所有 article 数据
    for each_article in article_list:
        article_result = get_article_data(each_article)
        write_to_file(article_result + (cat_id, cat_name))
    # 在第一个页面下得到每个类别文档下的所有页面
    paged_list = list()
    paged_count = 1
    paged_count_string = content.findChild(name='nav').findChild(name='span')
    if paged_count_string is not None:
        paged_count = int(paged_count_string.string.split(' ')[1])
    # print(paged_count)
    if paged_count > 1:
        for paged in range(2, paged_count+1):
            paged_list.append(cat_url + "&paged=" + str(paged))  # 产生新的一个页面
    return paged_list, cat_name


def get_other_page_article(current_category_url, category_name):  # 获取当前页面下的所有article标签
    sleep(2)  # 每次爬取的时候设置时间差（怎么样设置某一个时间段中的随机时间？单位为秒数）
    print("Current page url :", current_category_url)
    cat_id = int(current_category_url.split('&')[0].split('=')[1])
    cat_html = get_html(current_category_url)
    if cat_html is None:
        return False
    cat_soup = BeautifulSoup(cat_html, 'lxml')
    content = cat_soup.find(attrs={'class': 'content'})
    article_list = content.find_all(name='article')
    # 获取当前页面的所有 article 数据
    for each_article in article_list:
        article_result = get_article_data(each_article)
        write_to_file(article_result + (cat_id, category_name))
    return True


def get_data(category_list):
    # test_list = alphabet_index_dict['E']  # 得到某一个字母索引别下的所有类别数据，是一个list
    for each_category in category_list:
        paged_list, cat_name = get_first_page_article(each_category)
        if paged_list is None and cat_name is None:
            return False
        for paged in paged_list:
            status = get_other_page_article(paged, cat_name)
            if status is False:
                return False
    return True


def main(begin_url):
    start_time = time()
    alphabet_index_dict = get_category(begin_url)  # 获得每一个字母索引数据，得到一个字典{A:[..],B:.....}
    if alphabet_index_dict is None:
        print("网页为空，无法解析，请查看URL是否正确")
        return None
    for current_index in alphabet_index_dict.keys():
        print("Current Index = ", current_index)
        # print("Current Index = ", 'L')
        status = get_data(alphabet_index_dict[current_index])
        # status = get_data(alphabet_index_dict['L'])
        if status is False:
            print("Page Not Found！")
        print("--------*** Next ***--------")
    # get_data(alphabet_index_dict['L'])
    end_time = time()
    print("Time cost: ", end_time-start_time)


if __name__ == '__main__':
    # url = 'http://www.cbaigui.com/?page_id=1111111111'
    url = 'http://www.cbaigui.com/?page_id=11600'
    sys.exit(main(url))

# 2020/5/15 00:25 已经可以抓取每个类别下面第一页的数据了
# 2020/5/15 9:50 现在要开始爬取每个类别下的多页数据，或者先找到某个页面下的多个页面
