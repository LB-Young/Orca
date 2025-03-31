import requests
from bs4 import BeautifulSoup

async def stcn_news():
    """从证券时报网站获取最新财经新闻"""
    base_url = "https://www.stcn.com/"
    response = requests.get(base_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    news_link = soup.find_all('ul', class_='index-quick-news-list')[0]
    all_links = []
    for item in news_link.find_all('a'):
        new_link = base_url + item.get('href')[1:]
        all_links.append(new_link)
    news_list = []
    for link in all_links:
        response = requests.get(link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', class_='detail-title').text.strip().replace('\xa0', '').replace('\u200c',"")
        try:
            newspaper_name = soup.find('div', class_='detail-info').find_all('span')[0].text.strip()
            publish_time = soup.find('div', class_='detail-info').find_all('span')[1].text.strip()
        except:
            newspaper_name = ""
            publish_time = ""
        content = soup.find('div', class_='detail-content').text.strip().replace('\xa0', '').replace('\u200c',"")
        news_list.append({
            "title": title,
            "newspaper_name": newspaper_name,
            "publish_time": publish_time,
            "content": content
        })
    return news_list 