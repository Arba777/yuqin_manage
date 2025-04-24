# parse_html.py
import datetime
import logging
import re
from datetime import datetime, timedelta

import pandas as pd
from lxml import html, etree

from cruds.Event import EventService
from models.models import SessionLocal

event_service = EventService(SessionLocal())


def parse_html(html_text, q):
    lst = []
    event_list = []
    tree = html.fromstring(html_text)
    total_page = tree.xpath('//ul[@node-type="feed_list_page_morelist"]/li/a//text()')[-1]
    total_page = int(re.findall(r"[\d]+", total_page)[0])
    div_list = tree.xpath('//*[@id="pl_feedlist_index"]//div[@action-type="feed_list_item"]')
    for div in div_list:
        try:
            mid = div.xpath('./@mid')[0].strip()
        except IndexError:
            mid = None
        try:
            title = div.xpath('.//p[@node-type="feed_list_content"]/a[1]/text()')[0].strip()
            if '超话' in title:
                title = div.xpath('.//p[@node-type="feed_list_content"]/a[2]/text()')[0].strip()
            if title == '展开':
                title = None
        except IndexError:
            title = None
        try:
            nickname = div.xpath('.//a[@nick-name]/@nick-name')[0].strip()
        except IndexError:
            nickname = None
        try:
            personal_href = div.xpath('.//a[@nick-name]/@href')[0]
        except IndexError:
            personal_href = None
        try:
            publish_time = div.xpath('.//div[@class="from"]/a[1]//text()')[0].strip()
        except IndexError:
            publish_time = None
        try:
            event_source = div.xpath('.//div[@class="from"]/a[2]//text()')[0].strip()
        except IndexError:
            event_source = None
        try:
            content_show = ''.join(div.xpath('.//p[@node-type="feed_list_content"]//text()')).strip()
        except IndexError:
            content_show = None
        try:
            content_all = ''.join(div.xpath('.//p[@node-type="feed_list_content_full"]//text()')).strip() if len(
                div.xpath('.//p[@node-type="feed_list_content_full"]')) > 0 else None
        except IndexError:
            content_all = None
        try:
            # 定位到目标内容的 div
            content_div = div.xpath('.//div[@class="card"]/div[@class="card-feed"]/div[@class="content"]')[0]

            # 移除 class 为 "info" 和 "from" 的 div
            for unwanted_div in content_div.xpath('.//div[@class="info"] | .//div[@class="from"]'):
                unwanted_div.getparent().remove(unwanted_div)

                # 将处理后的 content_div 转换为 HTML 字符串
                content_html = etree.tostring(content_div, encoding="unicode", method="html")

        except IndexError:
            content_html = None
        try:
            retweet_num = div.xpath('.//div[@class="card-act"]/ul[1]/li[1]//text()')[-1].strip()
        except IndexError:
            retweet_num = None
        try:
            comment_num = div.xpath('.//div[@class="card-act"]/ul[1]/li[2]//text()')[-1].strip()
        except IndexError:
            comment_num = None
        try:
            star_num = div.xpath('.//div[@class="card-act"]/ul[1]/li[3]//text()')[3].strip()
        except IndexError:
            star_num = None
        try:
            uid = re.findall(r"com/(.*)\?", personal_href)[0].strip()
        except (IndexError, TypeError) as e:
            logging.error(e)
            uid = None

        item = [
            mid,
            uid,
            title,
            nickname,
            personal_href,
            publish_time,
            event_source,
            content_show,
            content_all,
            content_html,
            retweet_num,
            comment_num,
            star_num,
        ]
        event_item = {
            "mid": mid,
            "uid": uid,
            "title": title,
            "nickname": nickname,
            "personal_href": personal_href,
            "event_source": event_source,
            "content_show": content_show,
            "content_all": content_all,
            "content_html": content_html,
            "publish_time": publish_time,
            'retweets': retweet_num,
            "comment_num": comment_num,
            "star_num": star_num
        }

        lst.append(item)
        event_list.append(event_item)

    columns = [
        "mid",
        'uid',
        "事件标题",
        "个人昵称",
        "个人主页",
        "发布时间",
        "内容来自",
        "展示内容",
        "全部内容",
        '展示内容元素',
        "转发数量",
        "评论数量",
        "点赞数量",
    ]
    data = pd.DataFrame(lst, columns=columns)
    return data, total_page, event_list


def process_time(publish_time):
    now = datetime.now()

    if publish_time is None:
        return None

    # Handle "人数" and "今天"
    if "人数" in publish_time:
        publish_time = " ".join(publish_time.split()[:-1])
        publish_time = publish_time.replace("今天 ", "今天")

    if "今天" in publish_time:
        today = now.strftime("%Y-%m-%d")
        publish_time = publish_time.replace("今天", today)
        return f"{today} {now.strftime('%H:%M:%S')}"

    # Handle "分钟前"
    if "分钟前" in publish_time:
        match = re.search(r"(\d+)分钟前", publish_time)
        if match:
            minutes = int(match.group(1))
            publish_time = (now - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
            return publish_time

    try:
        if re.match(r'\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}:\d{2}', publish_time):
            return datetime.strptime(publish_time, "%Y年%m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M:%S")

        elif re.match(r'\d{1,2}月\d{1,2}日 \d{1,2}:\d{2}', publish_time):
            year = now.year if "今年" in publish_time else (
                now.year if now.month >= int(publish_time.split('月')[0]) else now.year - 1)
            time_str = f"{year}年{publish_time}"
            return datetime.strptime(time_str, "%Y年%m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M:%S")

        else:
            raise ValueError("Unsupported time format.")
    except Exception as e:
        print(f"Failed to parse time: {publish_time}. Error: {e}")
        return None


def extract_base_url(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.findall(r"(.*)\?", url)
    return match[0] if match else url


def process_dataframe(data):
    # data.insert(
    #     1, "uid", data["个人主页"].map(lambda href: re.findall(r"com/(.*)\?", href)[0] if pd.notna(href) else None)
    # )
    data["个人主页"] = "https:" + data["个人主页"]
    data["个人主页"] = data["个人主页"].map(extract_base_url)
    data["发布时间"] = data["发布时间"].map(process_time)
    # data.iloc[:, 6:] = data.iloc[:, 6:].applymap(
    #     lambda x: x.replace("\n", "").replace(" ", "") if x else None
    # )  # 清楚掉 \n 和 空格
    data["全部内容"] = data["全部内容"].map(
        lambda x: x[:-2] if x else None
    )  # 清除掉收起
    data.iloc[:, -3:] = data.iloc[:, -3:].replace(["转发", "评论", "赞"], 0)
    data.iloc[:, -3:] = data.iloc[:, -3:].applymap(
        lambda x: 0 if x in ["转发", "评论", "赞"] else x
    )
    return data


def process_event_list(event_list):
    for event in event_list:
        data = event['retweets']
        if event['retweets'] == '转发' or not event['retweets']:
            event['retweets'] = 0
        if event['comment_num'] == '评论' or not event['comment_num']:
            event['comment_num'] = 0
        if event['star_num'] == '赞' or not event['star_num']:
            event['star_num'] = 0
        if event['retweets']:
            event['retweets'] = int(event['retweets'])
        if event['comment_num']:
            event['comment_num'] = int(event['comment_num'])
        if event['star_num']:
            event['star_num'] = int(event['star_num'])
        if event['personal_href']:
            event['personal_href'] = 'https:' + event['personal_href']
        else:
            event['personal_href'] = ''
        event['publish_time'] = process_time(event['publish_time'])
        event['original_heat'] = event['star_num'] + 3 * event['comment_num'] + 5 * event['retweets']
        event['event_heat'] = 0
        event['is_hot'] = True if event['event_heat'] >= 50 else False
    return event_list


def get_dataframe_from_html_text(html_text, q):
    data, total_page, event_list = parse_html(html_text, q)
    process_dataframe(data)
    event_data_list = process_event_list(event_list)
    event_service.create_events(event_data_list)
    return data, total_page
