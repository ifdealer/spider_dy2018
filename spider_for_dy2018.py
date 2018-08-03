# -*- coding:utf-8
import bs4, re, os,requests
from requests import RequestException
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('数据插入成功')
        return True
    print("插入失败!!")
    return False


def get_index_page(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'  #如果请求后出现中文乱码，看一下head中的编码，跟着改
    except RequestException:
        print("请求页面"+ str(url) +"出错")

    soup = bs4.BeautifulSoup(response.text,'html.parser')
    item = soup.find_all('a',attrs={'class':'ulink'})

    href = []
    for i in item:
        href.append(i.get('href'))

    return href


def getin_detailPage(href):
    url = 'https://www.dy2018.com'
    for i in href:
        urls = url+str(i)
        try:
            response = requests.get(urls)
            response.encoding = 'gb2312'
        except RequestException:
            print("请求页面" + str(urls) + "出错")

        soup = bs4.BeautifulSoup(response.text,'html.parser')
        data = {
            '豆瓣评分': '暂无',
            '片名': '暂无',
            '类别': '暂无',
            '产地': '暂无',
            '译名': '暂无',
            '简介': '暂无',
            '磁力链接': '暂无',
            'ftp链接': '暂无',
        }


        #类　　别  片　　名
        p = soup.select('#Zoom > p')
        pattern_title = re.compile(r'<.*?名(\s|.*?)(.*?)</p>')
        pattren_type = re.compile(r'<.*?别(\s|.*?)(.*?)</p>')
        pattren_product = re.compile(r'<.*?地(\s|.*?)(.*?)</p>')
        pattren_product_2 = re.compile(r'<.*?家(\s|.*?)(.*?)</p>')
        pattren_rank = re.compile(r'<.*?豆瓣评分(\s|.*?)(.*?)(/|\d).*?</p>')
        flag = False
        for i in p:
            if '片　　名' in str(i):
                data['片名'] = str(re.match(pattern_title, str(i)).group(2))
            if '类　　别' in str(i):
                data['类别'] = str(re.match(pattren_type, str(i)).group(2))
            if '产　　地' in str(i):
                data['产地'] = str(re.match(pattren_product, str(i)).group(2))
            if '国　　家' in str(i):
                data['产地'] = str(re.match(pattren_product_2, str(i)).group(2))
            if '译　　名' in str(i):
                data['译名'] = str(re.match(pattern_title, str(i)).group(2))
            if '豆瓣评分' in str(i):
                data['豆瓣评分'] = str(re.match(pattren_rank, str(i)).group(2))
            if '简　　介' in str(i):
                flag = True
                continue
            if flag:
                data['简介'] = str(i.get_text()).strip()
                if data['简介']=='':
                    continue
                flag = False

        #获取磁力链接
        magnet = soup.find_all(name='a' ,href = re.compile(r'magnet'))
        for i in magnet:
            data['磁力链接'] = i.get_text()

        #获取ftp链接
        ftp = soup.find_all('a',text=re.compile(r'ftp'))
        for i in ftp:
            data['ftp链接'] = i.get_text()

        print(data)
        save_to_mongo(data)




def main():
    page = 1
    page_url = '_' + str(page)
    url = 'https://www.dy2018.com/html/gndy/dyzz/index' + page_url + '.html'
    for i in range(1,100):
        if i == 1:
            url = 'https://www.dy2018.com/html/gndy/dyzz/index.html'
            href = get_index_page(url)
            getin_detailPage(href)
        elif i >= 2:
            page = i
            page_url = '_'+str(page)
            url = 'https://www.dy2018.com/html/gndy/dyzz/index' + page_url + '.html'
            print('当前为第'+ str(page) +'页')
            href = get_index_page(url)
            getin_detailPage(href)



if __name__ == '__main__':
    main()
