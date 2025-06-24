import requests

# 定义目标URL
url = "https://api.binjie.fun/api/generateStream?refer__1360=n4%2BhDKD57KiK0IygxBMioGkDcC8mp5D8Yo2eD"  # 替换为实际的API地址

# 定义请求头（如果需要）
headers = {
    "Content-Type": "application/json",  # 如果发送JSON数据
}

# 定义POST请求的参数或数据
data = {
    "key1": "你好",
}

# 发送POST请求
response = requests.post(url, json=data, headers=headers)


# 检查响应状态码
if response.status_code == 200:
    print("请求成功！")
    print("响应内容：", response.json())  # 如果响应是JSON格式
else:
    print(f"请求失败，状态码：{response.status_code}")
    print("错误信息：", response.text)
