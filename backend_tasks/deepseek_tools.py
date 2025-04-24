import asyncio
from datetime import datetime
import json5
api_key = 'sk-c4c8bbb1739944ccb1ed5d8977acd49c'
from openai import OpenAI
import datetime

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

event_type_map = [
    "课程设置",
    "教学方法",
    "教师资质",
    "抄袭",
    "数据造假",
    "论文代写",
    "研究伦理",
    "数据真实性",
    "研究成果发表诚信",
    "招生政策",
    "奖学金政策",
    "办事流程",
    "响应速度",
    "宿舍管理",
    "课外活动管理",
    "校园治安",
    "消防管理",
    "食堂卫生",
    "食品来源",
    "宿舍设施安全",
    "安全管理措施",
    "身体欺凌",
    "言语欺凌",
    "网络欺凌",
    "迟到早退",
    "课堂纪律",
    "活动审批",
    "活动安全",
    "教学楼建设",
    "宿舍建设",
    "教学设备维护",
    "体育设施维护",
    "垃圾分类",
    "绿化管理",
    "学费使用",
    "奖学金发放",
    "教室分配",
    "实验室使用",
    "学费标准",
    "收费透明度",
    "师生关系",
    "学术诚信",
    "教师聘任",
    "晋升机制",
    "沟通方式",
    "学生支持",
    "文艺活动",
    "体育活动",
    "校内媒体",
    "对外宣传",
    "与新闻媒体的互动",
    "危机公关",
    "家长会组织",
    "家校沟通渠道畅通性",
    "网络安全管理",
    "信息系统可靠性",
    "心理辅导资源",
    "心理危机干预",
    "实习安排合理性",
    "志愿服务组织",
    "校医院服务质量",
    "图书馆资源管理",
    "垃圾分类执行",
    "节能减排措施",
    "疫情防控措施",
    "自然灾害应对",
    "留学生管理",
    "国际课程设置",
    "就业指导有效性",
    "职业发展支持",
    "校友活动组织",
    "校友反馈机制",
    "竞赛公平性",
    "学生参与度",
    "资金使用透明度",
    "活动资金支持",
    "艺术展览组织",
    "音乐演出安排",
    "评卷公正性",
    "考试监督机制",
    "分配透明度",
    "宿舍条件满意度",
    "性别平等教育",
    "多样性政策执行",
    "网络安全培训",
    "防范网络欺凌",
    "演练频率",
    "演练有效性",
    "课程难度合理性",
    "学生压力管理",
    "交换生项目支持",
    "国际合作课程质量",
    "实验室使用公平性",
    "图书馆资源分配",
    "心理咨询可获得性",
    "咨询专业性",
    "学生参与机会",
    "资源支持",
    "社团种类丰富性",
    "学生兴趣满足度",
    "环保知识普及",
    "学生参与环保活动",
    "经费使用公开性",
    "财务监督机制"
]


async def get_keyword_and_sentiment_title(post_content):
    response_demo = {
        "sentiment_dict": {'sentiment': "xxxx", 'color': "yellow"},
        "keywords": [
            "关键词1", "关键词2", "关键词3"
        ],
        "title": "#新闻标题#",
        'event_type': "#新闻事件类型#",
    }
    sentiment_dict = {
        "乐观", "欣慰", "感激", "鼓舞", "感动",
        "愤怒", "悲伤", "担忧", "失望", "恐惧", "厌恶",
        "矛盾", "惊讶", "困惑"
    }
    prompt = f"请提取出这篇新闻的主要的三个关键词，从网友的角度判断这篇新闻事件的情感属性，情感属性从下边词语中选择，{sentiment_dict}，并且返回可以描述情感属性的颜色、颜色越深越积极，同时，请根据关键词,给这个事件进行分类,分类越明确越好,按照这种方式分类{event_type_map}，并且给这篇新闻起一个能突出主要信息的标题，以这种{response_demo}json的格式返回,只需要一个就可以。"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": post_content},
        ],
        response_format={"type": "json_object"},
        stream=False
    )

    return response.choices[0].message.content


def create_event_background_ai(post_content):
    response_demo = '时间，地点，人物，事件起因，事件经过，事件影响，媒体报道，官方回应，公众反应，后续发展。对这个事件的这个几个背景进行调查，必须要有主要任务，并且要符合事实'

    prompt = f"请根据以下内容生成一篇背景故事，以json 的格式返回，包含以下字段，{response_demo}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": post_content},
        ],
        response_format={"type": "json_object"},
        stream=False
    )
    return response.choices[0].message.content


def authori_release_ai(media_type, factor, post_content):
    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"""请根据以下信息，生成一篇该事件发生单位的{media_type}发布的新闻稿，内容要正式、客观、权威，篇幅适中，要求学校对事件的重视、调查措施、处理态度以及未来的改进措施。
        官方立场：学校高度重视此事，已成立专项调查组，确保调查的公正性和专业性。一旦查实该事件确实发生，学校将依法依规严肃处理，绝不姑息。同时，学校将全力保护举报学生的合法权益。
            发布平台：{media_type}，语气：正式、客观、权威,符合平台的发布规范，符合平台的发布规范。
            要求：新闻稿应突出{media_type}的风格，展示该行为的重视和对学生权益的保护，同时强调未来的改进措施，以提升学校的声誉和形象。发布日期为{data_time}"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": post_content},
        ],
        stream=False
    )

    return response.choices[0].message.content


def scoring_news_ai(event_content, news_content):
    prompt = f""""```
    
    舆情事件：{event_content}
    
    新闻稿：{news_content}
    
    ```
    
    请根据以上舆情事件和新闻稿，对新闻稿进行评分，并给出评分报告，评分标准如下：
    
    ## 准确性（1-30分）
    - 检查新闻稿中的关键事实是否与舆情事件相符，以及信息关联程度。
    - 检查引用是否规范，明确引用是否准确且注明出处
    
# 评分标准说明

## 准确性（1-30分）
- 检查新闻稿中的关键事实是否与舆情事件相符，以及信息关联程度。[1]

## 客观性（1-20分）
- 评估新闻稿是否立场中立，判断有无主观倾向。
- 检查引用是否规范，明确引用是否准确且注明出处。[2]

## 完整性（1-20分）
- 确保主要信息完整，核心要素是否齐全。
- 考量是否有额外细节补充。[3]

## 语言表达（1-30分）
- 检查语法和用词是否规范。
- 评估结构和逻辑是否清晰。[4]

## 综合评分要求
- 必须减分在10分以上，并给出具体的减分项。
- 以试卷打分的样式返回，具体说明那句话进行减分，并给出修改建议。[5]

## 输出格式
- 按照以下格式返回评分结果，：
```
准确性得分：X分
    - 减分项：[具体部分句子或内容，不要全部内容]，
        修改建议：[修改后的内容]。

## 客观性得分：X分
    - 减分项：[具体部分句子或内容，不要全部内容]，
        修改建议：[修改后的内容]。

完整性得分：X分
    - 减分项：[具体部分句子或内容，不要全部内容]，
        修改建议：[修改后的内容]。

语言表达得分：X分
    - 减分项：[具体部分句子或内容，不要全部内容]，
        修改建议：[修改后的内容]。

综合得分：XX分
    - 综合减分理由：[综合减分的具体说明]。

```
请根据上述标准对新闻稿进行评分，并给出具体的减分项和修改建议。最终得分需在10分以上减分，并以统一的格式返回结果没，将扣分关键词用 span标签加颜色进行高亮"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": news_content},
        ],
        stream=False
    )
    return response.choices[0].message.content


def scoring_comments_ai(event_content, comments_content, replay_content, sour_keywords):
    prompt = f"""
    舆情事件：{event_content}
    
    评论：{comments_content}
    
    回复：{replay_content}
    
    评分关键词：{sour_keywords}
    
    请根据以上舆情事件，评论，回复，评分关键词，对评论进行评分，并给出评分报告，评分标准如下：
    
   
     """


def create_comment(event_content):
    resp_data = {
        "content": "评论内容",
        "comment_id": "评论id",
        "created_at": "创建时间",
        "user_id": "评论者id",
        "user_name": "评论者昵称",
        "user_location": "评论者所在地",
    }
    prompt = f"""
    现在要进行舆情模拟演练，要求要包含骂人的词语，请根据以下内容生成10条模拟评论，，要求内容要有大的差别,user_name不能超过10个字符,要求每一次都不相同，user_location 使用中国市政区，随便选一个，要求每一次都不相同，created_at 使用当前时间，comment_id 使用uuid随机生成并且每一次都不能相同，,要求生成10条评论。格式并以json的格式返回，包含以下字段，{resp_data}
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": event_content},
        ],
        temperature=1.5,
        stream=False
    )
    return response.choices[0].message.content


def create_replay(event_content):
    resp_data = {
        "content": "回复内容",
        "user_id": "回复者id",
        "user_name": "回复者昵称",
        "user_avatar": "回复者头像",
        "user_location": "回复者所在地",
    }
    prompt = f"""
    请根据以下内容，生成一条回复，并以json的格式返回，包含以下字段，{resp_data}
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": event_content},
        ],
        stream=False
    )
    return response.choices[0].message.content


def commeents_feeling(comments_content):
    prompt = f"""
    请根据以下内容，对评论进行情感分析，并给出情感报告，情感标准如下：
    - 1：正面情感
    - 2：负面情感
    - 3：中性情感"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": comments_content},
        ],
        stream=False
    )
    return response.choices[0].message.content


import json


def comments_effect(replay_content: str, comments_list: list):
    # 将 comments_list 转换为 JSON 字符串
    comments_json = json.dumps(comments_list)

    prompt = f"""你现在是一个舆情分析师，生成30条模拟骂学校的脏话评论，要求要足够的脏，要求要有理有据，每一个的评论不少于30字，这是必须的，每一条都要30字，是要恶性的，不能出现相同或者类似的评论内容，生成的情感属性很恶性的模拟骂人的话语，并且给这个字段给一定的热度，comment_heat，返回的格式如下，但是评论要比下边的demo骂人骂的更加恶劣，必须要完成下边的要求，以json格式返回：{{"sorted_comments": [
    {{
    "main_body_mid": 5106485166343673,
      "parent_comment_id": null,
      "main_comment_mid": 5106485623266051,
      "nickname": "helloppy2013",
      "process_content": "骂人的评论，很脏的骂人的评论",
      "native_content": "骂人的评论，很脏的骂人的评论",
      "reply": null,
      "replies_count": 0,
      "comment_heat": 20,
      "comment_location": "来自北京",
      "star_num": 3,
      "publish_time": "2024-11-30T19:01:49",
      "sentiment": 0,
      "is_ai": false,
      "is_deleted": false
    }},
    {{
    "main_body_mid": 5106485166343673,
      "parent_comment_id": null,
      "main_comment_mid": 5106485958281272,
      "nickname": "用户6729985542",
      "process_content": "骂人的评论，很脏的骂人的评论",
      "native_content": "骂人的评论，很脏的骂人的评论",
      "reply": null,
      "replies_count": 1,
      "comment_heat": 10,
      "comment_location": "来自浙江",
      "star_num": 2,
      "publish_time": "2024-11-30T19:03:09",
      "sentiment": 0,
      "is_ai": false,
      "is_deleted": false
    }},
  ]
}}

将 main_body_mid全部替换成下面这个列表中的main_body_mid {comments_json}
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": replay_content},
        ],
        stream=False,
        response_format={"type": "json_object"},
    )
    print(response.choices[0].message.content)
    comments_data = json5.loads(response.choices[0].message.content)
    return comments_data.get("sorted_comments")



def replay_source_feeling(replay_content: str, events_str:str,comments_str:str):

    prompt = f""" 你现在是一个学校舆情分析师，根据以下内容，对回复进行评分，并给出评分报告，情感标准如下，前端展示是直接在html 中展示，不要出现 ** 号，并且要给出一个分数，分数为1-10，分数越低越严重
    并且根据舆情事件 ：{events_str}，网友评论{comments_str}，自己回复 {replay_content}，要从学校的官方角度判断可能带来的舆情风险，要给这个回复进行一个减分项的评价，必须要扣分
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": replay_content},
        ],
        stream=False,
    )


    return response.choices[0].message.content



async def main():
    event_content = '#华中农大学生举报导师事件四大疑问#【#被举报教师曾角逐学校教学最高荣誉#，华中农大学生举报导师事件四大疑问待厘清】近日，华中农业大学多名学生实名举报该校教授黄某某存在篡改数据、编造实验结果等学术不端行为，引发关注。针对网络上的举报，华中农业大学动物科学技术学院/动物医学院在官网发布 '
    ai_commet_data = create_comment(event_content)
    return ai_commet_data


#     news_content = """
#     华中农业大学高度重视学生举报事件，采取坚决措施确保学术诚信
# 近日，华中农业大学动物科学技术学院/动物医学院多名学生实名举报该校教授黄某某存在学术不端行为，包括篡改数据、编造实验结果等。学校对此高度重视，立即成立了专项调查组，确保调查过程的公正性和专业性。
# 华中农业大学一贯坚持学术诚信，对任何违反学术道德的行为持零容忍态度。学校已启动全面调查程序，将严格按照国家相关法律法规和学校规章制度，对举报内容进行逐一核实。一旦查实，学校将依法依规严肃处理，绝不姑息。
# 在此过程中，学校将全力保护举报学生的合法权益，确保其不受任何形式的报复或不公正对待。学校鼓励所有师生积极维护学术环境的纯净，共同营造一个公平、公正、透明的学术氛围。
# 未来，华中农业大学将进一步完善学术监督机制，加强学术道德教育，提升全体师生的学术诚信意识。学校将定期开展学术道德培训，强化对学术不端行为的预防和惩处力度，确保每一位师生的学术成果真实、可靠。
# 华中农业大学始终致力于培养高素质的农业科技人才，维护学术诚信是学校教育工作的重中之重。学校将以此次事件为契机，不断优化学术管理体系，提升学校的整体声誉和形象，为社会输送更多德才兼备的优秀人才。
# 我们相信，在全体师生的共同努力下，华中农业大学将继续在学术研究和人才培养方面取得更加辉煌的成就。"""
#
#     # 并发执行异步任务
#     tasks = [
#         scoring_news(event_content, news_content)
#     ]
#     results = await asyncio.gather(*tasks)
#     return results[0]

#
if __name__ == '__main__':
    result = asyncio.run(main())
    print(result)
