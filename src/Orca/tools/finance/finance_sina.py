import requests
from bs4 import BeautifulSoup

async def finance_sina_news():
    """从新浪财经网站获取最新财经新闻"""
    base_url = "https://finance.sina.com.cn/"
    response = requests.get(base_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    news_link = soup.find_all('div', class_="m-hdline")[0]
    all_links = []
    for item in news_link.find_all('a'):
        if item.get('href').startswith('http'):
            new_link = item.get('href')
        else:
            new_link = base_url + item.get('href')[1:]
        all_links.append(new_link)
    news_list = []
    for link in all_links:
        response = requests.get(link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.strip().replace('\xa0', '').replace('\u200c',"")
        try:
            newspaper_name = soup.find('div', class_="date-source").find_all('a')[0].text.strip()
            publish_time = soup.find('div', class_="date-source").find_all('span')[0].text.strip()
        except:
            newspaper_name = ""
            publish_time = ""
        try:
            content = soup.find('div', class_="article").text.replace("海量资讯、精准解读，尽在新浪财经APP", "").strip().replace('\xa0', '').replace('\u200c',"")
        except:
            continue
        
        news_list.append({
            "title": title,
            "newspaper_name": newspaper_name,
            "publish_time": publish_time,
            "content": content
        })
    return news_list 