from openai import OpenAI
import config

#定义模型请求 请求模型 思考程度
def model_reply(model,思考,tools_list,messages):
    client = OpenAI(
        api_key=config.key,
        base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=model,
        messages = messages,
        stream=False,
        reasoning_effort=思考,
        extra_body={"thinking": {"type": "enabled"}}, # 开启思考模式
        tools = tools_list,
        tool_choice = "auto",  # 让模型自动决定是否调用工具
    )
    # 完整回复
    return response.choices[0].message
