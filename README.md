# image-ad-suggestor

根据图像内容推荐广告的后端服务

搭配部署 https://github.com/LlmKira/wd14-tagger-server

## Config

```shell
cp .env.exp .env
nano .env

```

## Run

在终端中运行

```shell
pip install pdm
pdm install
pdm run python main.py

```

## PM2

启动 pm2 托管，自动重启

```shell
apt install npm
npm install pm2 -g
pip install pdm
pdm install
pm2 start pm2.json
pm2 stop pm2.json
pm2 restart pm2.json

```

## Docs

访问 `/docs` 页面查看接口文档并调试

## Acknowledgement

- [FastAPI](https://fastapi.tiangolo.com/)