from typing import Dict, Optional

import pandas as pd
from fastapi import UploadFile

from config.nb_logging import logger


async def process_corpus_file(file: UploadFile) -> Optional[Dict]:
    """"""
    try:
        content = await file.read()
        if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(content)
        elif file.filename.endswith(".csv"):
            df = pd.read_csv(content)
        else:
            logger.error(f"Unsupported file type: {file.filename}")
            return None

        # 确保必要的列存在
        required_columns = [
            "语料内容",
            "言论类型",
            "严重程度",
            "出现场景",
            "备注",
        ]

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"缺少必要的列: {col}")

        # 转换为标准格式
        corpus_data = []
        for _, row in df.iterrows():
            corpus_entry = {
                "content": row["语料内容"],
                "speech_type": row["言论类型"],
                "severity": row["严重程度"],
                "scenario": row["出现场景"],
                "notes": row["备注"],
            }
            corpus_data.append(corpus_entry)
        logger.info(f"成功读取语料库文件: {corpus_data}")

        return corpus_data

    except Exception as e:
        logger.error(f"处理语料库文件时出错: {str(e)}")
        return None
