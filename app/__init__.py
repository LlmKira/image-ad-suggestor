# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午1:26
# @Author  : sudoskys
# @File    : __init__.py.py
# @Software: PyCharm

import instructor
import toml
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.tagger import WdTaggerSDK
from .settings import CurrentSetting

SYSTEM = """
你现在是一个电商平台的运营，需要从相关信息和模板中创作出一个商品的标题和介绍。 !important

Study the provided copywriting templates to understand the style and emotional expression each one conveys.
Once you have grasped the stylistic elements, I will present you with a specific subject.
Your task will then be to synthesize a new piece of copywriting that aligns with the learned styles.
Your creation should capture the essence of the new subject, resonate with the themes of the examples, and include suitable hashtags for thematic consistency.
"""


class ProductsIntro(BaseModel):
    """
    Extracts the title and description of a product from a list of bullet points.
    """
    title_cn: str = Field(..., description="此商品的标题.")
    description_cn: str = Field(...,
                                description="此商品的描述.")
    tags: list[str] = Field(..., description="Exp: ['#风景', '#旅行']")


aclient = instructor.apatch(AsyncOpenAI(
    base_url=CurrentSetting.openai_base_url,
    api_key=CurrentSetting.openai_api_key)
)

app = FastAPI()

MESSAGE_TEMPLATE = toml.load('template.toml')
logger.info(f"Loaded {len(MESSAGE_TEMPLATE)} templates...")


class MappingDefault(dict):
    def __missing__(self, key):
        return key


def get_template(content, *,
                 tags: str):
    return content.format_map(
        MappingDefault(
            tags=tags
        )
    )


@app.get("/templates")
async def get_templates():
    return MESSAGE_TEMPLATE


@app.post("/generate_caption")
async def generate_caption(template_id: str, file: UploadFile = File(...)) -> JSONResponse:
    try:
        user_template = MESSAGE_TEMPLATE[template_id]["template"]
    except KeyError as e:
        logger.error(f"Invalid template_id: {template_id}, {e}")
        return JSONResponse(content={"error": "Invalid template_id"}, status_code=400)
    try:
        await file.seek(0)
        raw_input_wd = await WdTaggerSDK(base_url=CurrentSetting.wd_api_endpoint).upload(
            file=await file.read(),
            token="asda",
            general_threshold=0.35,
            character_threshold=0.85
        )
        tag_result = raw_input_wd["tag_result"]
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": "WD API Error"}, status_code=500)
    logger.info(f"Tagging: {raw_input_wd}")
    try:
        task = get_template(content=user_template, tags=tag_result)
        # task = (">参考模板\n" + user_template + f"""\n\n>仿写任务\n商品标签：{raw_input_wd}""")
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
