# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午1:26
# @Author  : sudoskys
# @File    : __init__.py.py
# @Software: PyCharm
import instructor
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.tagger import WdTaggerSDK
from .settings import CurrentSetting

aclient = instructor.apatch(AsyncOpenAI(
    base_url=CurrentSetting.openai_base_url,
    api_key=CurrentSetting.openai_api_key)
)


class ProductsIntro(BaseModel):
    """
    Extracts the title and description of a product from a list of bullet points.
    """
    title_cn: str = Field(..., description="The title of the product. 中文")
    description_cn: str = Field(..., description="The description of the product. 中文")


app = FastAPI()

SYSTEM = """
你现在是一个电商平台的运营，需要从相关信息和模板中创作出一个商品的标题和介绍
Study the provided copywriting templates to understand the style and emotional expression each one conveys.
Once you have grasped the stylistic elements, I will present you with a specific subject.
Your task will then be to synthesize a new piece of copywriting that aligns with the learned styles.
Your creation should capture the essence of the new subject, resonate with the themes of the examples, and include suitable hashtags for thematic consistency.
"""

USER_TEMPLATE = """
>Template
“峰回路转，雾凇乍现，一缕阳光斜射，刹那间晶莹剔透，宛若仙境，美极了！ #风景 #旅行”
“秋是慢入的,但冷却是突然的,晴不知夏去,一雨方觉秋深！有些情绪不言而喻…… #最美风景 #秋天 #心动的旅行”
“愿新年胜旧年，愿将来胜过往，愿你与旧事归于尽，来年依旧迎花开。#向烟花许个愿 #除夕 #大年三十 #跨年夜”
“你是我最想留住的幸运，我想用我的心，把你永远留在我身边。#情话 #表白 #爱情”
"""


@app.post("/generate_caption")
async def generate_caption(file: UploadFile = File(...)) -> JSONResponse:
    try:
        await file.seek(0)
        raw_input_wd = await WdTaggerSDK(base_url=CurrentSetting.wd_api_endpoint).upload(
            file=await file.read(),
            token="asda",
            general_threshold=0.35,
            character_threshold=0.85
        )
    except Exception as e:
        logger.error(e)
        return JSONResponse({"error": "WD API Error"})
    logger.info(f"Tagging: {raw_input_wd}")
    try:
        model = await aclient.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ProductsIntro,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM
                },
                {
                    "role": "user",
                    "content":
                        USER_TEMPLATE
                        + f"""
                        >仿写任务
                        Tags：{raw_input_wd}
                        """
                },
            ],
        )
        assert isinstance(model, ProductsIntro)
        return JSONResponse(model.model_dump())
    except Exception as e:
        logger.exception(e)
        return JSONResponse({"error": "OpenAI API Error"})
