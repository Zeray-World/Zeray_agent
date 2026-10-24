from pathlib import Path
from tavily import TavilyClient
import subprocess
import config

#扫描skills目录 检查格式并输出
def skill():
    根 = Path(config.项目根) / "skills"
    list = []
    errors_list = []

    #检查来源
    for 来源 in ("user", "agent"):
        目录 = 根 / 来源

        if not 目录.is_dir(): #没有目录
            continue
        for 文件夹 in 目录.iterdir():
            if not 文件夹.is_dir():
                continue

            名字 = 文件夹.name #skill_id
            教程 = 文件夹 / f"{名字}.md" #skill_md
            说明 = 文件夹 / "说明.txt" #skill_说明

            if not 教程.is_file(): #存在=True
                errors_list.append(f"格式错误 : 缺少{名字}.md")
                continue

            if not 说明.is_file():
                errors_list.append(f"格式错误 : 缺少说明.txt")
                continue

            txt = " ".join(read_text(说明).splitlines()).strip()
            if len(txt) > 100:
                errors_list.append(f"格式错误 : 说明.txt超过100字 - {len(txt)}字")
                continue

            内容 = read_text(教程).strip()
            if not 内容:
                errors_list.append(f"{名字}.md是空的")
                continue

            #所有检查都通过了 .relative_to计算相对路径 给路径前缀返回后续路径
            list.append(f"skill: {名字}\n路径: {教程}\n描述: {txt}")

    if not list and not errors_list:
        return "skills目录里还没有skill"

    输出 = ""

    if list: #\n\n分割每一个skill 中间空一行
        输出 = "可用skill:\n" + "\n\n".join(list)
    if errors_list:
        输出 += "\n\n格式错误的skill:\n" + "\n".join(errors_list)

    return 输出

def 检查权限(工具名):
    p = config.权限.get(工具名, True)

    if p is False:
        return "该工具已被禁用"
    if p == "ask":
        if input(f"允许调用 {工具名} 吗？(y/n) ") != "y":
            return "用户拒绝了这次调用"
    return None #没被拦，继续执行

#文件读写 路径 开始行 结束行
def file_read(path,start_line = False,end_line = False):
    r = 检查权限("file_read")
    if r:
        return r

    if Path(path).is_dir():
        return f"这是目录，不是文件 : {path}，可以用 cmd 的 dir 查看"

    if config.权限.get("workspace"):
        目标 = Path(path).resolve() #返回绝对路径
        #直接+会报错 要么str() 要么/ 可以想成“文件夹 / 子文件夹
        根 = (config.项目根 / "workspace").resolve()
        if 根 not in 目标.parents and 目标 != 根: #parents - 这个路径的所有上级目录
            return "只能读工作区里的文件"

    #检查是否仅填写start/end
    try: #容错
        if start_line is not False and end_line is not False:
            if start_line < 1:
                start_line = 1
            _ = read_text(fr"{path}").splitlines() #读出完整内容后切片
            return "\n".join(_[start_line-1 : end_line]) #把列表用"\n"拼成一个字符串

        else:
            return read_text(fr"{path}")
    except FileNotFoundError:
        return f"文件不存在 : {path}"

#读文本
def read_text(path,encoding = None):
    path = Path(rf"{path}")  #实例化对象
    if encoding: #模型填了encoding 用模型的读
        return path.read_text(encoding=encoding)

    if Path(path).is_dir():
        return f"这是目录，不是文件 : {path}，可以用 cmd 的 dir 查看"

    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        编码 = "utf-8"

        if text.startswith("\ufeff"):
            text = text[1:]
            编码 = "utf-8-sig"

    except UnicodeDecodeError:
        with open(path, "r", encoding="gbk", newline="") as f:
            text = f.read()
        编码 = "gbk"

    except FileNotFoundError:
        return f"文件不存在 : {path}"

    #兜底 全编码失败就直接替换吧
    if text is None:
        text = path.read_text(encoding="utf-8", errors="replace")

    if text == "":
        return "空文件"

    return text

#文件编辑 路径 旧文本 新文本
def file_edit(path, old, new):
    r = 检查权限("file_edit")
    if r:
        return r

    if config.权限.get("workspace"):

        目标 = Path(path).resolve()
        根 = (config.项目根 / "workspace").resolve()

        if 根 not in 目标.parents and 目标 != 根:
            return "只能写工作区里的文件"

    try:

        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        编码 = "utf-8"
        if text.startswith("\ufeff"):
            text = text[1:]
            编码 = "utf-8-sig"

    except UnicodeDecodeError:
        with open(path, "r", encoding="gbk", newline="") as f:
            text = f.read()
        编码 = "gbk"

    except FileNotFoundError:
        return f"文件不存在 : {path}"


    n = text.count(old)
    if n == 0:
        return "没找到这段内容，可能已经被改过了"
    if n > 1:
        return f"这段内容出现了 {n} 次，请写长一点再试"

    #先把新内容按原编码试一遍 编不出来就不碰文件避免写回失败把原文件清空
    text = text.replace(old, new)
    try:
        text.encode(编码)
    except UnicodeEncodeError:
        return f"写回失败：原文件是 {编码} 编码 新内容里有它不支持的字符 请换成普通字符 或把文件转成 UTF-8 再改。"
    Path(path).write_text(text, encoding=编码, newline="")
    return "修改成功"

#文件写入 路径 文本
def file_write(path, text):
    r = 检查权限("file_write")
    if r:
        return r

    if config.权限.get("workspace"):
        目标 = Path(path).resolve()
        根 = (config.项目根 / "workspace").resolve()
        if 根 not in 目标.parents and 目标 != 根:
            return "只能写工作区里的文件"

    try:
        #write_text默认newline=None Windows文本模式写入时会把\n转成\r\n 原文件是Unix换行的 编辑一次就变成Windows换行。
        Path(path).write_text(text, encoding="utf-8", newline="")
    except FileNotFoundError:
        return f"目录不存在 : {Path(path).parent}"

    return "写入成功"

#解析cmd工具
def cmd(command):

    if "\n" in command or "\r" in command:
        return "命令里有换行会被 cmd 截断 请把多行代码用 file_write 写成.py文件 再执行 : python 文件名.py"

    r = 检查权限("cmd")
    if r:
        return r

    try:
        #shell是要不要cmd程序跑当前命令（False就用第一个参数当程序）
        #capture_output = 要不要把cmd输出记录下来
        tmp = subprocess.run(command, shell=True, capture_output=True)
    except Exception as e:
        return f"命令执行出错: {e}"

        #stdout正常输出内容        stderr错误输出内容
        # b"" = 空字节(和""区别是一个字节类型一个字符串类型)
        #没看text=True返回的是字节数据所以必须b""
        #不用text=True 原因 = 只能一个编码 不能自动切换
    原始 = (tmp.stdout or b"") + (tmp.stderr or b"")
    try:
        #最后得到的是一个正常+报错的值 尝试用不同编码读他
        out = 原始.decode("utf-8")
    except UnicodeDecodeError:
        #保底 所以用替换不报错
        out = 原始.decode("gbk", errors="replace")

    if not out.strip():
        return f"执行完毕，无输出 : return_code = {tmp.returncode}"

    return out

#联网
def curl(query,max_results):
    r = 检查权限("curl")
    if r:
        return r

    if not config.TavilyKey:
        return "TavilyKey未填写 - 调用失败"

    tavily_client = TavilyClient(api_key=config.TavilyKey)
    response = tavily_client.search(query, max_results=max_results)
    # print("results =", response.get("results", []))
    # print("len =", len(response.get("results", [])))

    out = []
    out.append(f"query : {response.get('query', '')}") #只取一遍
    _ = 0
    # #格式 :一个列表里面多个字典
    for i, r in enumerate(response.get("results", [])):
        out.append(
            f"title : {r.get('title', ' ')}\n"
            f"url : {r.get('url', ' ')}\n"
            f"content : {r.get('content', '')}\n"
        )
        # "content": r.get("content", ""),  # 摘要片段
        # "url": r.get("url", ""),         # 需要来源就加上
        # "raw_content": (r.get("raw_content") or "")[:1000],  # 需要全文就加上，记得截断

    return f"{out}"
