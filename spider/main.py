import logging
import math
import os
from datetime import datetime

import pandas as pd
from rich.progress import track

from cruds.Opinion import OpinionService
from spider.utils.get_comments_level_one import get_all_level_one
from spider.utils.get_comments_level_two import get_all_level_two
from spider.utils.get_main_body import get_all_main_body

logging.basicConfig(level=logging.INFO)
from models.models import SessionLocal

opinion_service = OpinionService(SessionLocal())

class WBParser:
    def __init__(self, cookie, q, kind):
        self.cookie = cookie
        # 修改时间戳格式，避免使用冒号和空格
        self.now_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")  # 替换成下划线或短横线
        os.makedirs(f"./spider/WBData_{self.now_stamp}", exist_ok=True)
        os.makedirs(f"./spider/WBData_{self.now_stamp}/Comments_level_1", exist_ok=True)
        os.makedirs(f"./spider/WBData_{self.now_stamp}/Comments_level_2", exist_ok=True)
        self.main_body_filepath = f"./spider/WBData_{self.now_stamp}/{q}_{kind}_{self.now_stamp}.csv"
        self.comments_level_1_filename = f"./spider/WBData_{self.now_stamp}/{q}_{kind}_comments_one.csv"
        self.comments_level_2_filename = f"./spider/WBData_{self.now_stamp}/{q}_{kind}_comments_two.csv"
        self.comments_level_1_dirpath = f"./spider/WBData_{self.now_stamp}/Comments_level_1/"
        self.comments_level_2_dirpath = f"./spider/WBData_{self.now_stamp}/Comments_level_2/"

    def get_main_body(self, q, kind):

        data = get_all_main_body(q, kind, self.cookie)
        data = data.reset_index(drop=True).astype(str).drop_duplicates()

        data.to_csv(self.main_body_filepath, encoding="utf_8_sig")

    def get_comments_level_one(self):
        logging.info(f"开始解析评论...")
        data_list = []

        assert os.path.exists(self.main_body_filepath), "没有找到主题内容，请先获取主体内容"
        main_body = pd.read_csv(self.main_body_filepath, index_col=0)
        logging.info(f"主体内容一共有{main_body.shape[0]:5d}个，现在开始解析...")

        try:
            for ix in track(range(main_body.shape[0]), description=f"解析中..."):
                uid = int(float(main_body.iloc[ix]["uid"]))
                mid = int(float(main_body.iloc[ix]["mid"]))
                final_file_path = f"{self.comments_level_1_dirpath}{uid}_{mid}.csv"

                if os.path.exists(final_file_path):
                    length = pd.read_csv(final_file_path).shape[0]
                    if length > 0:
                        continue

                data = get_all_level_one(uid=uid, mid=mid, cookie=self.cookie)

                data.drop_duplicates(inplace=True)
                data.to_csv(final_file_path, encoding="utf_8_sig")
                opinion_list_dict = data.to_dict(orient='records')
                data_instance_list = []
                for opinion_dict in opinion_list_dict:
                    opinion_info_dict = {}
                    opinion_info_dict['publish_time'] = opinion_dict.pop('发布时间')
                    opinion_info_dict['comment_location'] = opinion_dict.pop('评论地点') if opinion_dict.get(
                        '评论地点', None) else None
                    opinion_info_dict['replies_count'] = opinion_dict.pop('回复数量')
                    opinion_info_dict['star_num'] = opinion_dict.pop('点赞数量')
                    opinion_info_dict['process_content'] = opinion_dict.pop('处理内容')
                    opinion_info_dict['native_content'] = opinion_dict.pop('原生内容')
                    opinion_info_dict['nickname'] = opinion_dict.pop('用户昵称')
                    opinion_info_dict['main_body_mid'] = opinion_dict.pop('main_body_mid')
                    opinion_info_dict['main_comment_mid'] = opinion_dict.pop('mid')
                    opinion_info_dict['comment_heat'] = 0

                    for key, value in opinion_info_dict.items():
                        if isinstance(value, float) and math.isnan(value):
                            opinion_info_dict[key] = None  # or '' if empty string is preferred

                    opinion_info_dict['comment_original_heat'] = (
                            int(opinion_info_dict['replies_count']) * 3 + int(opinion_info_dict['star_num'])
                    )
                    data_instance_list.append(opinion_info_dict)
                opinion_service.create_opinions(data_instance_list)
                data_list.append(data)
            logging.info(f"主体内容一共有{main_body.shape[0]:5d}个，已经解析完毕！")
        except:
            logging.error(f"由于cookie失效等原因，一共解析主体内容{len(data_list):5d}个！")

        if data_list:
            data = pd.concat(data_list).reset_index(drop=True).astype(str).drop_duplicates()
        else:
            data = pd.DataFrame()
        data.to_csv(self.comments_level_1_filename)

    def get_comments_level_two(self):
        data_list = []

        # 获取一级评论
        if os.path.exists(self.comments_level_1_filename):
            comments_level_1_data = pd.read_csv(self.comments_level_1_filename, index_col=0)
        else:
            file_list = [self.comments_level_1_dirpath + item for item in os.listdir(self.comments_level_1_dirpath) if
                         item.endswith('.csv')]
            assert len(file_list) > 0, "没有找到一级评论文件，请先获取一级评论"
            comments_level_1_data = pd.concat([pd.read_csv(file) for file in file_list]).reset_index(drop=True).astype(
                str).drop_duplicates()

        logging.info(
            f"一级评论一共有{comments_level_1_data.shape[0]:5d}个，现在开始解析..."
        )
        try:
            for ix in track(
                    range(comments_level_1_data.shape[0]), description=f"解析中..."
            ):
                main_body_uid = int(float(comments_level_1_data.iloc[ix]["main_body_uid"]))
                mid = int(float(comments_level_1_data.iloc[ix]["mid"]))
                final_file_path = (
                    f"{self.comments_level_2_dirpath}{main_body_uid}_{mid}.csv"
                )

                if os.path.exists(final_file_path):
                    length = pd.read_csv(final_file_path).shape[0]
                    if length > 0:
                        continue

                data = get_all_level_two(uid=main_body_uid, mid=mid, cookie=self.cookie)
                data.drop_duplicates(inplace=True)
                data.to_csv(final_file_path, encoding="utf_8_sig")
                data_list.append(data)
            logging.info(f"一级评论一共有{comments_level_1_data.shape[0]:5d}个，已经解析完毕！")
        except:
            logging.error(f"由于cookie失效等原因，一共解析一级评论{len(data_list):5d}个！")

        data = pd.concat(data_list).reset_index(drop=True).astype(str).drop_duplicates()
        data.to_csv(self.comments_level_2_filename)


if __name__ == "__main__":
    q = '订婚强奸案'  # 话题
    kind = "综合"  # 综合，实时，热门，高级
    cookie = "SCF=Avjqg3kxUV_I1ojCjDF5yvwBaC6rYYz2ZjCmRgBSGhvLxXlTDbTAtoHtWOeGVsZKoBExuM4_ycA14Heo2LCOI4I.; SUB=_2A25K-c52DeRhGeFJ7VQS-SbKwjyIHXVmd0--rDV8PUNbmtANLVTCkW9Nf0_uCA6SiVUYvOC_r-3VUn99qknwcbeB; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWF-ifoyr3Zl-kCB6XxF9Bd5JpX5KzhUgL.FoMNSoq01Knc1K52dJLoIpnLxKqL1h5L1-BLxK-L12eL1KMEehzEehqt; ALF=02_1747274534; SINAGLOBAL=2210661210661.495.1744682536719; ULV=1744682536732:1:1:1:2210661210661.495.1744682536719:; XSRF-TOKEN=4bFeXNSYNy-glWaufVcftSXc; WBPSESS=a0cixqY_BrrwsFzGUaRYscvQz_iiRgJOz5w0XXr4Ct4U-ZvWmJkg3F9dMoF1Kf8cqVn7qym_awMnTw4ynXrqi1nnqphdMmMjJDztsXex9j0wqf9q4TbZTnDt2HwYJxK1GKS0ezDaxuwfp1hpBoODTg=="
    wbparser = WBParser(cookie, q, kind)

    # 获取主题内容
    wbparser.get_main_body(q, kind)
    # 获取一级评论
    wbparser.get_comments_level_one()
    # 获取二级评论
    # wbparser.get_comments_level_two()
