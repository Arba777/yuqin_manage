import asyncio
import json5
from backend_tasks.deepseek_tools import get_keyword_and_sentiment_title
from cruds.Event import EventService
from dependencies.db_session import get_db_session_direct

db_session = get_db_session_direct()

event_services = EventService(db_session)


async def create_keys_and_insentments_title():
    for i in range(0, 200):
        event_list_dict = {}
        events = event_services.get_events_update_keywords(skip=i, limit=30)
        for event in events:
            event_dict = {}
            content_show = event.content_show.replace('展开c', '')
            resp_key = await get_keyword_and_sentiment_title(content_show)
            print(resp_key)
            resp_dict = json5.loads(resp_key)
            sentiment_dict = resp_dict.get('sentiment_dict')
            event_dict['sentiment'] = sentiment_dict.get('sentiment')
            event_dict['color'] = sentiment_dict.get('color')
            event_dict['keywords'] = resp_dict.get('keywords')
            event_dict['title'] = resp_dict.get('title')
            event_dict['content_show'] = event.content_show.replace('展开c', '')
            event_dict['event_type'] = resp_dict.get('event_type')
            event_list_dict[event.mid] = event_dict
        event_services.update_events(event_list_dict)
        print(f'第{i}页完成')
        print(event_list_dict, "*" * 10)


if __name__ == '__main__':
    asyncio.run(create_keys_and_insentments_title())
