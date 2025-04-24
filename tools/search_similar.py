import random

from elasticsearch import Elasticsearch

# 连接到 Elasticsearch
# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

es = Elasticsearch([{'host': '10.245.153.195', 'port': 9200,'scheme': 'http'}],http_auth=("elastic", "elastic_store@tzw.com"))
#
# # 创建索引
index_name = "events"

def search_similar_articles(mid, min_term_freq=2, min_doc_freq=2, max_query_terms=20, stop_words=None):
    # 根据 mid 获取对应的文档
    result = es.search(index=index_name, body={
        "query": {
            "term": {"mid": mid}
        }
    })

    if not result['hits']['hits']:
        return []

    # 获取 content_show 内容
    content_show = result['hits']['hits'][0]['_source']['content_show']

    # 使用 more_like_this 查询相似文章
    similar_articles = es.search(index=index_name, body={
        "query": {
            "more_like_this": {
                "fields": ["content_show", "title"],  # 结合 content_show 和 title 字段
                "like": content_show,
                "min_term_freq": min_term_freq,
                "min_doc_freq": min_doc_freq,
                "max_query_terms": max_query_terms,
                "stop_words": stop_words,  # 设置停用词
                "analyzer": "ik_smart"  # 使用中文分词器
            }
        },
        "sort": [
            {"_score": {"order": "desc"}}  # 按照相似度分数降序排列
        ]
    })

    # 返回相似文章的详细信息
    return [
        {'real_mid': hit['_source']['mid'], 'content_show': hit['_source']['content_show'],
         'title': hit['_source']['title'], 'publish_time': hit['_source']['publish_time'],
         'nickname': hit['_source']['nickname'], 'event_heat':int(random.uniform(0,20)),
         'score': hit['_score']}  # 添加相似度分数
        for hit in similar_articles['hits']['hits']
    ]
# #
# # # 示例调用
# similar_articles = search_similar_articles(mid=5032163447932248)
# # print("Similar articles found:", similar_articles)