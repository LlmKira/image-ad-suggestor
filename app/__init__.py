# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午1:26
# @Author  : sudoskys
# @File    : __init__.py.py
# @Software: PyCharm
import json

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
    Refer Given Info,Extracts the title and description of a product from a list of bullet points.
    """
    title: str = Field(..., description="商品标题.")
    description: str = Field(...,
                             description="商品介绍."
                             )
    tags: list[str] = Field(..., description="Exp: ['#风景', '#旅行']")


app = FastAPI()

SYSTEM = """
你现在是一个电商平台的运营，需要从相关信息和模板中创作出一个商品的标题和介绍
Study the provided copywriting templates to understand the style and emotional expression each one conveys.
Once you have grasped the stylistic elements, I will present you with a specific subject.
Your task will then be to synthesize a new piece of copywriting that aligns with the learned styles.
Your creation should capture the essence of the new subject, resonate with the themes of the examples, and include suitable hashtags for thematic consistency.
"""

# Load templates into memory
with open('template.json', 'r') as f:
    templates = json.load(f)

logger.info(f"Loaded {len(templates)} templates")


@app.get("/templates")
async def get_templates():
    return templates


@app.post("/generate_caption")
async def generate_caption(template_id: str, file: UploadFile = File(...)) -> JSONResponse:
    try:
        user_template = templates[template_id]
    except KeyError:
        return JSONResponse(content={"error": "Invalid template_id"}, status_code=400)
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
        return JSONResponse(content={"error": "WD API Error"}, status_code=500)
    logger.info(f"Tagging: {raw_input_wd}")
    try:
        task = (">参考模板" + user_template + f"""\n\n>仿写任务 \nTags：{raw_input_wd}""")
        logger.info(f"PromptTask: {task}")
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
                    "content": task
                },
            ],
        )
        assert isinstance(model, ProductsIntro)
        return JSONResponse(model.model_dump())
    except Exception as e:
        logger.exception(e)
        return JSONResponse(content={"error": "OpenAI API Error"}, status_code=500)
