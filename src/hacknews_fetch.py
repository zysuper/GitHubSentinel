import requests
from bs4 import BeautifulSoup
from logger import LOG
def report_hackernews_top_stories():
    url = 'https://news.ycombinator.com/'
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找包含新闻的所有 <tr> 标签
    stories = soup.find_all('tr', class_='athing')

    top_stories = []
    for story in stories:
        title_tag = story.find('span', class_='titleline').find('a')
        if title_tag:
            title = title_tag.text
            link = title_tag['href']
            top_stories.append({'title': title, 'link': link})
	
    # 生成 markdown 报告
    from datetime import date
    import os

    today = date.today().isoformat()
    report_dir = os.path.join('daily_progress', 'hackernews')
    os.makedirs(report_dir, exist_ok=True)
    
    report_path = os.path.join(report_dir, f'{today}.md')
    with open(report_path, 'w') as f:
        f.write(f'# HackerNews Top Stories ({today})\n\n')
        for idx, story in enumerate(top_stories, 1):
            f.write(f"{idx}. [{story['title']}]({story['link']})\n")

    LOG.info(f"HackerNews 日报生成： {report_path}")

    return report_path