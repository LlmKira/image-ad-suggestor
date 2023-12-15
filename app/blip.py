# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 下午10:33
# @Author  : sudoskys
# @File    : blip.py
# @Software: PyCharm
from io import BytesIO
from typing import Optional

import aiohttp
from loguru import logger


class BlipTool:
    def __init__(self, api: str, timeout: int = 30, proxy: str = None):
        if not api.rstrip("/").endswith("upload"):
            api = api.rstrip("/") + "/upload/"
        self._url = api
        self.timeout = timeout
        self.proxy = proxy

    async def generate_caption_with_request(self, image_data: bytes) -> Optional[str]:
        try:
            headers = {'Accept': 'application/json'}
            async with aiohttp.ClientSession() as session:
                async with session.post(self._url, headers=headers, data={'file': image_data},
                                        timeout=self.timeout, proxy=self.proxy) as response:
                    response_data = await response.json()
                    if response.status != 200:
                        logger.warning(f"Blip API Outline:{response_data.get('detail')}")
                    _data = response_data["text"]
        except Exception as e:
            logger.exception(f"Blip:{e}")
            return
        else:
            return _data
