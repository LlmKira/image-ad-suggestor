# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 下午12:28
# @Author  : sudoskys
# @File    : demo.py
# @Software: PyCharm
import requests

template_id = 1
files = "test/01.png"
# Specify the URL of the endpoint
url = f"http://127.0.0.1:10011/generate_caption?template_id={template_id}"

# Open the image file in binary mode
with open(files, "rb") as img_file:
    # Define the multipart/form-data payload
    payload = {
        "file": (files, img_file, "image/png")
    }

    # Send the POST request
    response = requests.post(url, headers={"accept": "application/json"}, files=payload)

# Print the response
print(response.json())
