
import time
import 调试and工具
import config
import llm
import tools
import agent_loop
from deepseek_tokenizer import token_compute
import ast
import sys
print("当前解释器:", sys.executable)

#定义cmd工具
tools_list = [
    {
        "type": "function",          # 固定写法：表示这是一个"函数型工具"
        "function": {
            "name": "cmd",         # 工具名字。模型就是靠这个名字点名要用哪个工具
            "description": "调用系统cmd工具执行任务",
            "parameters": {       # 这个工具要什么参数
                "type": "object",
                "properties": {   # 每个参数叫什么、什么类型、干什么用
                    "command": {
                        "type": "string",
                        "description": "必须输入，要执行的命令"
                    }
                },
                "required": ["command"]   # 哪些参数是必须给的
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "curl",
            "description": "调用TavilyAPI进行联网操作",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "必须输入且大于两个字，要搜索的关键字"
                    },
                    "max_results": {
                        "type": "integer", #整数
                        "description": "必须输入，要搜索的数量"
                    }
                },
                "required": ["query","max_results"]

            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "all_info",
            "description": "获取当前所有运行状态 ---模型，思考程度，轮数，工具调用等",
            "parameters": {
                "type": "object",
                "properties": {
                    "all": {
                        "type": "string",
                        "description": "必须输入，输入True,获得所有运行状态包括部分框架提醒例如:框架调试代码"
                    },
                    "CHANGELOG": {
                        "type": "string",
                        "description": "可选输入，输入True,获得框架所有更新历史"
                    }
                },
                "required": ["all"]
            }
        }
    },
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
                        "description": "必须输入，文件路径(只填写路径时返回所有文件内容)"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "(必须和end_line一起写)可选输入，从第几行开始（1 表示第一行，0 也当第一行）"
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "(必须和start_line一起写)可选输入，到第几行结束（包含这一行）"
                    },
                },
                "required": ["path"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "file_edit",
            "description": "编辑文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "必须输入，文件路径"
                    },
                    "old": {
                        "type": "string",
                        "description": "必须输入，要替换的旧文本"
                    },
                    "new": {
                        "type": "string",
                        "description": "必须输入，要替换的新文本"
                    },
                },
                "required": ["path","old","new"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "file_write",
            "description": "写入文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "必须输入，文件路径"
                    },
                    "text": {
                        "type": "string",
                        "description": "必须输入，要写入的文本"
                    },
                },
                "required": ["path","text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subagent",
            "description": "派一个子代理去完成独立任务 子代理只能读文件和联网 返回结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "交给子代理的任务"
                    },
                    "max_rounds": {
                        "type": "integer",
                        "description": "最多几轮,默认5,最多30"
                    },
                    "max_tool_use": {
                        "type": "integer",
                        "description": "最多调用几次工具,默认5,最多50"
                    }
                },
                "required": ["task"]
            }
        }
    },
]

#导出会话:
def save(mess, path, name):
    try:
        with open(f"{path}\\{name}.txt", "w", encoding="utf-8") as f:
            f.write(str(mess))
            print(f"导出成功! 路径 : {path}")
    except FileNotFoundError:
        print(f"文件创建失败 程序未退出 会话还在你可以检查是否为路径写错来重新尝试创建{path}")
        return 1

    return f"导出成功! 路径 : {path}"


#加载会话
def load(path, name):
    global messages

    #里面就是完整messages 直接拿
    text = tools.read_text(path + fr"\{name}" + ".txt")
    messages = ast.literal_eval(text)


def 帮助导出或加载():
    choose = int(input("请输入1导出/2加载 : "))
    if choose == 1:
        path = input("输入完整路径 : ")
        name = input("文件名(如看到输入错误/无效无需理会) : ")
        save(messages, path, name)
    elif choose == 2:
        path = input("输入完整路径(下一步才输入文件名) : ")
        name = input("文件名-不用写.txt(如看到输入错误/无效无需理会) : ")
        load(path, name)
    return f"辅助完成!"

messages=[

        ]

全局最大轮数 = 9999 #全部的模型回复 不是会话数量 例如第一次3句话 第二次7句话就满了
全轮 = 1 #前面发过一次消息 所以初始就是1
Max_tool_use = 9999
tool_use = 0
展示思考行数 = 5
user_input = ""

def start_user_message():
    global user_input

    while True:

        try:
            user_input = input("你 : ")
            break

        except UnicodeDecodeError:
            print("\n输入流异常，请重新输入")
            continue

        except KeyboardInterrupt: #捕捉一下 显得好看(不会一大堆报错)
            print("\n已取消输入，退出")
            exit(0)

    messages.append({"role" : "user","content" : user_input})

print(r""" _____                     
/ _  / ___ _ __ __ _ _   _ 
\// / / _ \ '__/ _` | | | |
 / //\  __/ | | (_| | |_| |
/____/\___|_|  \__,_|\__, |
                     |___/ """)

print("开始检查与初始化配置 ---")

config.解析模型参数()

config.注入system(messages=messages)
start_user_message()
all_token = 0

while True:

    #判断 user是否使用指令
    if user_input[0:1] == "/":

        #用户使用调试命令 所以不丢给模型 直接删了重新加
        messages.remove({"role": "user", "content": user_input})

        #检查返回值
        if 调试and工具.调试命令(user_input) != "命令执行完毕":
             print("输入错误/无效")
             start_user_message()
             continue

        start_user_message()

        continue
    #判断轮数
    if 全轮 > 全局最大轮数:
        print("轮数限制 程序结束")
        messages.append({"role": "system", "content": "轮数限制 程序结束"}, )
        exit(1)

    elif 全轮 == 全局最大轮数:
        messages.append({"role": "system", "content": "当前全局最大轮数剩余 0 建议:即刻交付/请求用户放宽"}, )

    #添加一下系统时间喵！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！(精确到秒)
    messages.append({"role": "system", "content":
        f"系统时间:{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{tools.skill()}"}) #每轮重复注入skills

    start_time = time.time()
    try:
        model_all_reply = llm.model_reply(model=config.model,思考=config.思考,tools_list=tools_list,messages=messages)
    except KeyboardInterrupt:
        print("\n已取消本次模型请求")
        messages.pop() #删除末尾元素 (连续两遍删除系统时间和user字段(这里是一位大佬给我提的 原本我就写了一个 - 在这里感谢大佬))
        messages.pop()
        start_user_message()
        continue

    model_reply_content = model_all_reply.content
    model_reasoning_content = model_all_reply.reasoning_content
    end_time = time.time()

    # 注意字符串切片到了结束点不会截取而是丢弃 所以要多设一位
    all_token += token_compute(user_input) + token_compute(model_reply_content+model_reasoning_content)

    print(f"轮数 : {全轮}/{全局最大轮数}\n工具调用 : {tool_use}/{Max_tool_use}\n"
          f"</think>\n{调试and工具.处理模型思考行数(model_reasoning_content)}\n<think/>\n模型 : {model_reply_content}\n用时 : {str(end_time - start_time)[0:3]}\n"
          f"上下文总token : {all_token} 输入token : {token_compute(user_input)} 输出token : {token_compute(model_reply_content+model_reasoning_content)} -- {str(token_compute(model_reply_content+model_reasoning_content)/(end_time - start_time))[0:6]} tok/s \n")

    #返回工具使用次数和是否调用了工具
    tool_use, 继续 = agent_loop.model_user(messages, model_all_reply, model_reply_content,
                                           model_reasoning_content, tool_use, Max_tool_use,
                                           start_time, end_time)
    if not 继续:
        start_user_message()

    全轮 += 1
