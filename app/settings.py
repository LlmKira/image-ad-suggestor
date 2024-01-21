# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午8:14
# @Author  : sudoskys
# @File    : settings.py
# @Software: PyCharm
from typing import Optional

import requests
from dotenv import load_dotenv
from loguru import logger
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ServerSettings(BaseSettings):
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    wd_api_endpoint: str = "http://127.0.0.1:10011/upload"
    blip_api_endpoint: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def check_env(self):
        if not self.openai_api_key or len(self.openai_api_key) < 4:
            raise ValueError("openai_api_key is not set or is too short")
        if not self.wd_api_endpoint:
            raise ValueError("wd_api_endpoint is not set")
        if self.wd_api_endpoint.endswith("/"):
            self.wd_api_endpoint = self.wd_api_endpoint[:-1]

        if not self.wd_api_endpoint.endswith("upload"):
            logger.warning(
                "wd_api_endpoint should end with /upload, but it does not. "
                "Please Use Certain Server At https://github.com/LlmKira/wd14-tagger-server"
            )
            raise ValueError("wd_api_endpoint should end with /upload")

        if self.blip_api_endpoint:
            if self.blip_api_endpoint.endswith("/"):
                self.blip_api_endpoint = self.blip_api_endpoint[:-1]
            if not self.blip_api_endpoint.endswith("upload"):
                logger.warning(
                    "blip_api_endpoint should end with /upload, but it does not. "
                    "Please Use Certain Server At https://github.com/LlmKira/blipserver"
                )

        # 检查链接
        try:
            resp = requests.head(self.wd_api_endpoint)
            if resp.headers.get("server") != "uvicorn":
                logger.warning(
                    f"wd_api_endpoint {self.wd_api_endpoint} request success, but server is not uvicorn"
                )
            else:
                logger.success(f"wd_api_endpoint {self.wd_api_endpoint} is available")
        except Exception as e:
            logger.warning(
                f"wd_api_endpoint {self.wd_api_endpoint} is not available, please check the server is running {e}"
            )

        if self.blip_api_endpoint:
            try:
                resp = requests.head(self.blip_api_endpoint)
                if resp.headers.get("server") != "uvicorn":
                    logger.warning(
                        f"blip_api_endpoint {self.blip_api_endpoint} request success, but server is not uvicorn"
                    )
                else:
                    logger.success(f"blip_api_endpoint {self.blip_api_endpoint} is available")
            except Exception as e:
                logger.warning(
                    f"blip_api_endpoint {self.blip_api_endpoint} is not available, please check the server is running {e}"
                )
                self.blip_api_endpoint = None
        return self


CurrentSetting = ServerSettings()
