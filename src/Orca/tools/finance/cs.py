import requests
from bs4 import BeautifulSoup

async def cs_news():
    """从中国证券报网站获取最新财经新闻"""
    base_url = "https://www.cs.com.cn/xwzx/"
    response = requests.get(base_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = []
    for j in range(3):
        for i in range(7):
            # 获取新闻列表中的每条新闻的链接
            "/html/body/div[5]/div/div/div[1]/div[j]/ul/li[i]/a"

            try:
                news_link = soup.find_all('div', class_="ch_l space_b3")[j].find_all('ul')[0].find_all('li')[i].find_all('a')[0].get('href')
            except IndexError:
                continue
            if news_link.startswith('http'):
                full_url = news_link
            else:
                full_url = base_url + news_link
            # 获取每条新闻的详细内容
            detail_response = requests.get(full_url)
            detail_response.encoding = 'utf-8'
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
            # 解析标题、报社、时间和内容
            try:
                title = detail_soup.find('h1').text.strip().replace('\xa0', '').replace('\u200c',"")
                newspaper_name = detail_soup.find_all('em')[1].text.strip()
                publish_time = detail_soup.find('time').text.strip()
                content = detail_soup.find('section').text.strip().replace('\xa0', '').replace('\u200c',"")
                if len(content) < 50:
                    continue
                news_list.append({
                    "title": title,
                    "newspaper_name": newspaper_name,
                    "publish_time": publish_time,
                    "content": content
                })
            except:
                continue

    return news_list 