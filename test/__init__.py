# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午1:27
# @Author  : sudoskys
# @File    : __init__.py.py
# @Software: PyCharm
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from rich.pretty import pprint

import setting

aclient = instructor.apatch(AsyncOpenAI(
    base_url=setting.openai_base_url,
    api_key=setting.openai_api_key)
)


class ProductsIntro(BaseModel):
    """
    Extracts the title and description of a product from a list of bullet points.
    """
    title_cn: str = Field(..., description="The title of the product. 中文")
    description_cn: str = Field(..., description="The description of the product. 中文")


async def main(file_path: str = "01.png"):
    raw_input_wd = "1girl, solo, tail, animal ears, cat tail, bag, white background, sailor collar, cat ears, simple background, black hair, blush, yellow eyes, holding, open clothes, ribbon, holding bag, long hair, long sleeves, yellow ribbon, cat girl, looking at viewer, school uniform, bangs, neck ribbon, cardigan, jacket, shirt, parted lips, serafuku, :o"
    pprint(f"Tagging: {raw_input_wd}")
    _blip_input_ = "a shoe"
    pprint(f"Input: {_blip_input_}")
    model = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=ProductsIntro,
        messages=[
            {
                "role": "system",
                "content": """你现在是一个电商平台的运营，需要从相关信息和模板中创作出一个商品的标题和介绍"""
                           """Study the provided copywriting templates to understand the style and emotional expression each one conveys. """
                           """Once you have grasped the stylistic elements, I will present you with a specific subject. """
                           """Your task will then be to synthesize a new piece of copywriting that aligns with the learned styles. """
                           """Your creation should capture the essence of the new subject, resonate with the themes of the examples, and include suitable hashtags for thematic consistency."""
            },
            {
                "role": "user",
                "content": f"""
# Template 
“峰回路转，雾凇乍现，一缕阳光斜射，刹那间晶莹剔透，宛若仙境，美极了！ #风景 #旅行”
“秋是慢入的,但冷却是突然的,晴不知夏去,一雨方觉秋深！有些情绪不言而喻…… #最美风景 #秋天 #心动的旅行”
“愿新年胜旧年，愿将来胜过往，愿你与旧事归于尽，来年依旧迎花开。#向烟花许个愿 #除夕 #大年三十 #跨年夜”

# 仿写任务
Desc：{_blip_input_} , Tags：{raw_input_wd}

"""
                # f"Desc：{_blip_input_} , Tags：{raw_input_wd}"
            },
        ],
    )
    pprint(model.model_dump())
    assert isinstance(model, ProductsIntro)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            file_path="01.png"
        )
    )
