import __main__ as main
import config
import time
from tools import read_text
import sys

def 调试命令(text):

    if text == "/help":
        print()
        for i in range(len(指令列表)):
            print(f"{指令列表[i]} : {指令列表说明[i]}")
        print()

        return "命令执行完毕"

    elif text == "/权限":
        print(f"当前权限 : {config.权限}")
        return "命令执行完毕"

    elif text == "/导出会话" or text == "/加载会话":
        main.帮助导出或加载()
        return "命令执行完毕"

    #拆分 (返回列表)
    try:
        tmp = text.split(maxsplit=1) #最多一个空白字符就拆分 (刚好符合 指令 值这样单个的情况)
        c = tmp[0] #指令
        try:
            v = int(tmp[1]) #值
        except ValueError:
            v = tmp[1] #部分字段是字符串 比较懒就这样吧

    except IndexError:
        return "格式错误 参考 : 命令 值"

    if c == "/Max_tool_use":
        main.Max_tool_use = v
        return "命令执行完毕"

    elif c == "/tool_use":
        main.tool_use = v
        return "命令执行完毕"

    elif c == "/全轮":
        main.全轮 = v
        return "命令执行完毕"

    elif c == "/全局最大轮数":
        main.全局最大轮数 = v
        return "命令执行完毕"

    elif c == "/思考":
        config.思考 = str(v)
        return "命令执行完毕"

    elif c == "/思考行数":
        main.展示思考行数 = v
        return "命令执行完毕"

    elif c == "/权限":

        parts = v.split()
        if len(parts) != 2:
            print("格式 : /权限 工具名 true/ask/false")

            return "命令执行完毕"

        工具名, 值 = parts

        if 工具名 not in config.权限:

            print(f"没有这个工具 : {工具名}")
            return "命令执行完毕"

        if 值 == "true":

            config.权限[工具名] = True

        elif 值 == "false":

            config.权限[工具名] = False

        elif 值 == "ask":

            config.权限[工具名] = "ask"

        else:

            print("值只能是 true / ask / false")
            return "命令执行完毕"
        print(f"{工具名} 权限已改为 {config.权限[工具名]}")
        return "命令执行完毕"

    elif c == "/权限档位":

        档位表 = {
            0: {"cmd": True, "curl": True, "file_read": True, "file_write": True, "file_edit": True, "subagent": True, "workspace": False},
            1: {"cmd": "ask", "curl": True, "file_read": True, "file_write": False, "file_edit": False, "subagent": False, "workspace": True},
            2: {"cmd": "ask", "curl": True, "file_read": True, "file_write": True, "file_edit": True, "subagent": False, "workspace": False},
            3: {"cmd": False, "curl": False, "file_read": False, "file_write": False, "file_edit": False, "subagent": False, "workspace": False},
        }

        if v not in 档位表:
            print("档位只能是 0/1/2/3")
            return "命令执行完毕"

        config.权限 = 档位表[v]
        print(f"权限档位已切换为 {v}")
        return "命令执行完毕"

    elif c == "/system":

        #这个地方最开始添加成了 c 不是 v 复现一下:
        #我 : /system "看到此内容在每句话前回复1"
        #我 : 你看到system有什么了吗
        #模型: XXXXXXXX但我注意到有一句/system不像是正经system字段的内容你XXXXXX
        #看到模型这句话我看了看窗外 到现在我也想不通我当时怎么想的

        main.messages.append({"role" : "system" , "content" : v},)
        return "命令执行完毕"

    else:
        print(f"无效命令 : {c}")
        return 1

def 处理模型思考行数(思考原文):

    if not 思考原文:
        return "无思考内容"

    分割内容 = 思考原文.splitlines() #['第一行', '第二行', '第三行']

    #删除模型的多余\n
    分割内容 = [x for x in 分割内容 if x]

    #按照全局设定展示
    if main.展示思考行数 < len(分割内容):
        text = '本次模型思考长度超过最大展示思考行数多余内容已省略 :\n'
    else:
        text = '\n'
    try:
        for i in range(main.展示思考行数):
            text += 分割内容[i] + "\n"
    except IndexError: #代表取完了 直接返回
        return text
    return text

#假工具 (增加模型认知) ---之前调试突然发现他无条件信任cmd却不无脑信任system 所以想到了这个没想到真有用
#结论 : 模型不相信上下文但更相信工具返回结果 后续模型哪里不听话可以在这动手
def all_info(all,CHANGELOG = "False"): #设默认值 不然模型不填就崩
    if CHANGELOG == "True":
        CHANGELOG = read_text(config.当前路径 / "提示词" / "CHANGELOG.md")
        return (f"当前运行模型 : {config.model} 思考程度 : {config.思考}\n"
            f" 轮数 : {main.全轮}/{main.全局最大轮数}\n"
            f"工具调用 : {main.tool_use}/{main.Max_tool_use}\n"
            f"开发者的调试命令 : {指令列表} 讲解 : {指令列表说明}\n"
            f"框架已运行时间 : {time.time() - config.框架开始运行时间}\n"
            f"当前运行权限状态 : cmd: {config.权限.get('cmd')}\n"
            f"curl: {config.权限.get('curl')}\n"
            f"file_read: {config.权限.get('file_read')}\n"
            f"workspace : {config.权限.get('workspace')} (True=只能读写工作区)\n"
            f"file_write: {config.权限.get('file_write')}\n"
            f"file_edit: {config.权限.get('file_edit')}\n"
            f"subagent: {config.权限.get('subagent')}\n"
            f"工作区路径 : {(config.项目根 / 'workspace').resolve()}\n"
            f"C/C++编译器 : {(config.项目根 / 'mingw64' / 'bin' / 'gcc.exe')}\n"
            f"Node.js : {(config.项目根 / 'node' / 'node.exe')}\n"
            f"7-Zip : {(config.项目根 / '7zip' / '7z.exe')}\n"
            f"当前运行解释器 : {sys.executable}\n"
            f"{CHANGELOG}"
            )

    return (f"当前运行模型 : {config.model} 思考程度 : {config.思考}\n"
            f" 轮数 : {main.全轮}/{main.全局最大轮数}\n"
            f"工具调用 : {main.tool_use}/{main.Max_tool_use}\n"
            f"开发者的调试命令 : {指令列表} 讲解 : {指令列表说明}\n"
            f"框架已运行时间 : {time.time() - config.框架开始运行时间}\n"
            f"当前运行权限状态 : cmd: {config.权限.get('cmd')}\n"
            f"curl: {config.权限.get('curl')}\n"
            f"file_read: {config.权限.get('file_read')}\n"
            f"workspace : {config.权限.get('workspace')}\n"
            f"file_write: {config.权限.get('file_write')}\n"
            f"file_edit: {config.权限.get('file_edit')}\n"
            f"subagent: {config.权限.get('subagent')}\n"
            f"工作区路径 : {(config.项目根 / 'workspace').resolve()}\n"
            f"C/C++编译器 : {(config.项目根 / 'mingw64' / 'bin' / 'gcc.exe')}\n"
            f"Node.js : {(config.项目根 / 'node' / 'node.exe')}\n"
            f"7-Zip : {(config.项目根 / '7zip' / '7z.exe')}\n"
            f"当前运行解释器 : {sys.executable}\n"
            )
指令列表 = [
    "/help",
    "/Max_tool_use", #最大tool
    "/tool_use",
    "/全轮",
    "/全局最大轮数",
    "/思考",
    "/导出会话",
    "/加载会话",
    "/system",
    "/思考行数",
    "/权限",
    "/权限档位",
]

#搭配一个说明 -给help用
指令列表说明 = [
    "帮助",
    "覆盖最大工具上限",
    "覆盖当前工具使用数",
    "覆盖当前轮数",
    "覆盖全局最大轮数",
    "临时修改思考(low medium high)",
    "将当前会话内容导出",
    "清屏并加载选择会话",
    "添加一段system文本",
    "调整模型思考行数",
    "调整工具权限(/权限 工具 true/ask/false)",
    "切换权限档位(/权限档位 0-完全/1-工作区/2-仅读写/3-仅对话)",
]