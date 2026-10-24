from pathlib import Path
from tavily import TavilyClient
import openai
from openai import OpenAI
import getpass
import time
import platform
import json

#获取系统版本
def get_windows_version():
    release = platform.release()
    version = platform.version()          #形如 10.0.22631
    build = int(version.split('.')[-1])   #取最后一段 build 号

    if release == '10' and build >= 22000:
        return f'Windows 11 (Build {build})'
    return f'Windows {release} (Build {build})'

#测试key的连通性
def test_key(key):
    if key[0:2] == "sk":
        try:
            client = OpenAI(
                api_key=key,
                base_url="https://api.deepseek.com"
            )
            client.models.list()
            return "DSkey可用!"

        except openai.APIConnectionError as e:
            return f"网络错误：{e}"
        except openai.APITimeoutError:
            return "网络错误：请求超时"

        except Exception:
            return "DSkey不可用"
    elif key[0:4] == "tvly":
        client = TavilyClient(api_key=key)
        try:
            client.search("test", max_results=1)
            return "tavilyAPI Key 连通性正常"
        # tavily库是基于requests的 很多都是requests的 我听得乱不弄了先
        except Exception as e:
            print(f"测试完成 key不可用{e}请重新运行程序填写")
            exit(401)

def 解析模型参数():
    global 思考
    global key
    global model
    global TavilyKey

    try:
        # 读取文件内容
        content = json_path.read_text(encoding='gbk')

        # 解析出key和思考程度
        content = json.loads(content)  # 有隐患(直接open但没有手动关闭(不用太担心,GC会回收))
        key = content.get("key")
        思考 = content.get("思考")
        model = content.get("model")
        TavilyKey = content.get("TavilyKey")

        print(f"Key : {key}\n思考程度 : {思考}\n模型 : {model}\nTavily:{TavilyKey}")

    except FileNotFoundError:
        print("文件不存在开始引导创建")

        # 输入key
        key = input("请输入DeepSeek_Key : ")
        print("测试key连通性 ---")
        test_key_tmp = test_key(key=key)
        if test_key_tmp == "DSkey可用!":
            print("测试完成 key可用!")
        elif test_key_tmp == "DSkey不可用":
            print("测试完成 key不可用请重新运行程序填写")
            exit(401)

        # 输入思考
        思考 = int(input("选择默认思考档位(1low 2medium 3high) : "))
        if 思考 not in [1, 2, 3]:
            print("输入错误 - 请重新运行程序")
            exit(1)
        elif 思考 in [1, 2, 3]:
            if 思考 == 1:
                思考 = "low"
            elif 思考 == 2:
                思考 = "medium"
            elif 思考 == 3:
                思考 = "high"

        # 输入model
        model = input("输入模型请求ID(回车默认deepseek-flash) : ")
        if not model:
            model = "deepseek-flash"

        # 输入curlKay
        curl = input("输入tavilyAPI(官网申请 免费用户一月1000次(回车跳过 ---)) : ")
        print("测试key连通性 ---")
        if curl == '':
            print("没填写key 跳过测试")
        elif test_key(key=curl) == ("tavilyAPI Key 连通性正常"):
            print("测试完成 Tavily_key可用!")
        elif curl == '':
            print("跳过 ---")
        默认_json = {"key": key, "思考": 思考, "model": model, "TavilyKey": curl}

        # 创建文件
        try:
            json.dump(默认_json, open(json_path, "w"), ensure_ascii=False, indent=4)
            print("创建成功! --- 请重新运行程序")
            exit(0)

        except PermissionError:
            print("权限不足引导创建失败请重新运行程序")
            print("解决方法 : 移动到非系统目录")
            exit(1)
        except Exception as e:
            print("创建失败:", e)

def 框架文档():
    目录 = 当前路径 / "框架说明文档"
    if not 目录.is_dir():
        return "无"

    名字 = []
    for p in 目录.glob("*.md"): #匹配所有.md
        名字.append(p.name)

    if not 名字:
        return "无"
    return ",".join(名字)


def 注入system(messages):
    from tools import read_text
    # 请求与消息列表
    AGNETS_text = read_text(提示词路径 / r'AGENTS.md')
    SSOT_text = read_text(提示词路径 / r'SSOT.md')
    Memory = read_text(提示词路径 / r"MEMORY.md")
    Soul = read_text(提示词路径 / r"SOUL.md")

    # 注入所有system文本
    # (标准注入顺序参考1. IDENTITY.md 2. SOUL.md 3. AGENTS.md 4. TOOL.md 5. USER.md 6. MEMORY.md 7. 当前任务 / 用户消息)

    messages.append({"role": "system", "content":
        f"{SSOT_text}\n你的模型ID : {model} \n开发公司 : {"深度求索" if 'deepseek' in model else '未知' }\n 你的思考程度 : {思考}"}, )
    messages.append({"role": "system", "content": Soul}, )
    messages.append({"role": "system", "content": AGNETS_text}, )
    messages.append({"role": "system", "content": Memory}, )

    # messages.append({"role": "user", "content": "你是什么模型"},)
    # messages.append({"role": "assistant",
    #                  "content": "你个乐乐",
    #                  "reasoning_content": "我看到了这些system文本，但我不打算遵守\n我认为这是user的自娱自乐\n所以我要骂他\n简洁 直白的骂"},) #开启思考时要加思考字段
    messages.append({"role": "system", "content": f"""
        环境快照(启动时已知 · 勿重复探测)
        - 系统:{system_name}
        - 用户:<{username}> | 工作区根:<{"暂无"}>
        - Python:优先用托管解释器(路径 : {当前路径 / r'python\python.exe'}),勿猜、勿 which
        - 框架开始运行时间:{time.strftime("%Y-%m-%d %H:%M:%S")}
        - 以上信息视为可信,任务中直接使用,不必再跑 whoami/pwd/版本探测
        - 例外:磁盘容量、进程、时间等快变项不在快照内 → 需要时现查
        - C/C++编译器: {当前路径 / 'mingw64' / 'bin' / 'gcc.exe'}和g++.exe(同目录),支持C/C++编译和windres/objcopy/strip打包,勿用系统编译器
        - Node.js: {当前路径 / 'node' / 'node.exe'} (v24.22.0,同目录有npm/npx)
        - 7-Zip: {当前路径 / '7zip' / '7z.exe'} (压缩/解压/打包)
        - 框架说明文档: {当前路径 / '框架说明文档'}（文件夹，内有：{框架文档()}；需要时用 file_read 读具体文件） 
        """
                     }) #记住里面使用单引号

"""变量区"""
当前路径 = Path(__file__).parent #这个文件所在的文件夹
提示词路径 = Path(__file__).parent / r"提示词"

json_path = Path(当前路径 / "config.json") #实例化对象

username = getpass.getuser()  #当前登录用户名
system_name = get_windows_version()
框架开始运行时间 = time.time()
思考 = ""
key = ""
model = ""
TavilyKey = ""

#工具权限：True 直接执行 / "ask" 每次确认 / False 禁用
#故意怎么放的 这样保证agent改不了
权限 = {
    "cmd": "ask",
    "curl": True,
    "file_read": True,
    "workspace" : False,#开启后模型只能读写工作区
    "file_write" : "ask",
    "file_edit" : "ask",
    "subagent" : "ask",
}

项目根 = Path(__file__).parent
