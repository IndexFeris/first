import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import random

# 起始条目，最终条目，每页条数
page_indexs = range(0, 250, 25)

# 租房小组链接
baseUrls = [#'https://www.douban.com/group/226224/' #深圳租房
            'https://www.douban.com/group/537027/' #整租-深圳租房
            #'https://www.douban.com/group/538237/' #深圳租房【推荐★★★★★】
            ]

# cookie，注意
cookie = 'll="118282"; bid=-9My1UsByc4; __gads=ID=d0fcc7a2dda33dcd-22e065ca17cb0031:T=1629805877:RT=1629805' \
         '877:S=ALNI_MYEv5hu3YHzT0e8VyzCwBNyR1USyQ; douban-fav-remind=1; __yadk_uid=wUppFeNVp5gKvyPZrN66BPifbT' \
         'jqjzFj; __utmc=30149280; __utmz=30149280.1631529697.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|u' \
         'tmctr=(not%20provided); _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1631862033%2C%22https%3A%2F%2Fwww.google.com.hk' \
         '%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.16317205.1629805878.1631529697.1631862034.3; __utmt=1; ap_v=0,6.0; db' \
         'cl2="178180528:5F5odcVULSY"; ck=qLCr; push_noty_num=0; push_doumail_num=0; __utmv=30149280.17818; _pk_id.100001.8cb4=9d5377b' \
         '79995fc47.1631529695.2.1631862152.1631529894.; __utmb=30149280.16.9.1631862153007'


# 下载每个页面
def download_all_htmls():
    htmls = []
    for baseUrl in baseUrls:
        for idx in page_indexs:

            UA = 'Chrome/93.0.4577.82'
            url = f"{baseUrl}?start={idx}"
            print("download_all_htmls craw html:", url)
            r = requests.get(url,
                             headers={"User-Agent": UA, "Cookie": cookie})
            if r.status_code != 200:
                print('download_all_htmls,r.status_code', r.status_code)
            htmls.append(r.text)
    return htmls


htmls = download_all_htmls()

# 保存每个标题名称，以便后续去重
datasKey = []


# 解析单个HTML，得到数据
def parse_single_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    article_items = (
        soup.find("table", class_="olt")
            .find_all("tr", class_="")
    )

    datas = []

    for article_item in article_items:

        # 文章标题
        title = article_item.find("td", class_="title").get_text().strip()
        # 文章链接
        link = article_item.find("a")["href"]
        # 文章时间
        time = article_item.find("td", class_="time").get_text()

        # 匹配洪浪北、兴东关键字
        res1 = re.search("洪浪北|兴东", title)
        # 筛选一房、两房
        res2 = re.search("一房|单间|一室|1房|1室|二房|二室|2房|2室", title)

        # 找到地点和一房匹配的标题和之前存储的列表中不存在的
        if res1 is not None and res2 is not None and not title in datasKey:
            print(title, link, time)
            datasKey.append(title)
            datas.append({
                "title": title,
                "link": link,
                "time": time
            })
    return datas


all_datas = []

# 遍历所有爬取到的html，并解析
for html in htmls:
    all_datas.extend(parse_single_html(html))

df = pd.DataFrame(all_datas)
# 将数据转成Excel
df.to_excel("test.xlsx")
