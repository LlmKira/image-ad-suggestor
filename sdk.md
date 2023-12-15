## API Documentation

### POST /generate_caption

#### Description

这个端点用于生成标题。它接收一个文件作为输入，然后返回一个标题。

#### Parameters

- `file`: 一个文件，必须提供。

#### Responses

- `200 OK`: 成功的响应将返回一个`ProductsIntro`对象，包含产品的标题和描述。
- `500 Internal Server Error`: 如果在处理请求时发生错误，将返回一个包含错误信息的JSON对象。

#### Example

##### Request

```bash
curl -X POST "http://localhost:8000/generate_caption" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@file.txt"
```

##### Response

```json
{
  "title_cn": "产品标题",
  "description_cn": "产品描述"
}
```
