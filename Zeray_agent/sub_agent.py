import time
import config
import llm
import agent_loop
import tools

子代理工具 = [
    {
        "type": "function",
        "function": {
            "name": "file_read",
            "description": "读文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "可选，从第几行开始（1 表示第一行）"
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "可选，到第几行结束（包含这一行）"
                    },
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "curl",
            "description": "联网搜索",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜索的关键字"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "要搜索的数量"
                    }
                },
                "required": ["query", "max_results"]
            }
        }
    },
]


def 运行子代理(task, max_rounds=5, max_tool_use=5):
    r = tools.检查权限("subagent")
    if r:
        return r

    max_rounds = min(int(max_rounds), 30)
    if max_rounds < 1:
        max_rounds = 1

    max_tool_use = min(int(max_tool_use), 50)
    if max_tool_use < 1:
        max_tool_use = 1

    sub_messages = [
        {"role": "system", "content": "你是一个子代理,只能读文件和联网搜索,不能执行命令不能写文件 完成用户给的任务后直接给出结果。"},
        {"role": "user", "content": task},
    ]

    工具次数 = 0
    print(f"\n[子代理] 开始任务 ---")

    for 轮 in range(1, max_rounds + 1):
        print(f"[子代理] 第 {轮}/{max_rounds} 轮")

        开始 = time.time()
        reply = llm.model_reply(
            model=config.model,
            思考=config.思考,
            tools_list=子代理工具,
            messages=sub_messages,
        )
        工具次数, 继续 = agent_loop.model_user(
            sub_messages,
            reply,
            reply.content,
            reply.reasoning_content,
            工具次数,
            max_tool_use,
            开始,
            time.time(),
        )

        if not 继续:
            print(f"[子代理] 完成，共 {轮} 轮")
            return reply.content or ""

    print("[子代理] 达到轮数上限，未完成")
    return "子代理达到轮数上限，未完成"
