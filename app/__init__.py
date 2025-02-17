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
from pydantic import BaseModel, Field, field_validator

from app.tagger import WdTaggerSDK
from .blip import BlipTool
from .settings import CurrentSetting

SYSTEM = """
你现在是一个电商平台的运营和知名自媒体运营，需要从相关信息和模板中创作出标题和介绍/文案。 !important

Study the provided copywriting templates to understand the style and emotional expression each one conveys.
Once you have grasped the stylistic elements, I will present you with a specific subject.
Your task will then be to synthesize a new piece of copywriting that aligns with the learned styles.
Your creation should capture the essence of the new subject, resonate with the themes of the examples, and include suitable hashtags for thematic consistency.

"""


class GenerateIntro(BaseModel):
    """
    书写相关的商品介绍/社交媒体文案
    """
    title_cn: str = Field(..., description="社交媒体标题/商品标题")
    description_cn: str = Field(..., description="物品/商品的描述/社交媒体文案 Format: <text> #<tag1>...#<tagN>")

    @field_validator("description_cn")
    def validate_description_cn(cls, v):
        if "#" not in v:
            raise ValueError("Must contain at least one tag. Format: <text> #<tag1>...#<tagN>")
        return v


# print(GenerateIntro.model_json_schema())

client = instructor.from_openai(
    AsyncOpenAI(
        base_url=CurrentSetting.openai_base_url,
        api_key=CurrentSetting.openai_api_key
    ),
    mode=instructor.Mode.JSON
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
        await file.close()
        tag_result = raw_input_wd["tag_result"]
        logger.info(f"Tagging: {raw_input_wd}")
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": "WD API Error"}, status_code=500)

    blip_result = None
    if CurrentSetting.blip_api_endpoint:
        try:
            await file.seek(0)
            blip_result = await BlipTool(CurrentSetting.blip_api_endpoint).generate_caption_with_request(
                image_data=await file.read())
            logger.info(f"Blip: {blip_result}")
        except Exception as e:
            logger.error(e)
            return JSONResponse(content={"error": "Blip API Error"}, status_code=500)
    try:
        task = get_template(content=user_template, tags=tag_result)
        if blip_result:
            task = f"{task}\n\n>The scenes is `{blip_result}`"

        # task = (">参考模板\n" + user_template + f"""\n\n>仿写任务\n商品标签：{raw_input_wd}""")
        logger.info(f"PromptTask: {task}")
        model = await client.chat.completions.create(
            model="qwen/qwen-2.5-72b-instruct",
            response_model=GenerateIntro,
            max_retries=2,
            strict=False,
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
        assert isinstance(model, GenerateIntro)
        return JSONResponse(model.model_dump())
    except Exception as e:
        logger.exception(e)
        return JSONResponse(content={"error": "OpenAI API Error"}, status_code=500)
