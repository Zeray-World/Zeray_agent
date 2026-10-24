# 检查是否安装了那些库
# 这里直接把我上年写的一键安装项目模块照搬过来修剪了一下 非常节省时间

import os
import time
print(f"步骤一:导入模块列表")
module_list = [
    "openai",
    "tavily-python",
    "tokenizers"
]
import_name = [
    "openai",
    "tavily",
    "tokenizers"
]

print(f"""导入完成!

步骤二:更新新版pip和setuptools并清理缓存""")
try:
    pip_start_time=time.time()
    pip_update_result = os.system("pip install --upgrade pip setuptools wheel")
    if pip_update_result == 0:
        pip_end_time = time.time()
        print(f'pip更新成功用时{int(pip_end_time-pip_start_time)}秒')
    else:
        try:
            import sys
            print(f"""
            更新失败尝试-m方法""")
            os.system(f'"{sys.executable}" -m pip install --upgrade pip')
        except:
            print('pip更新失败，可能是网络或权限问题(主要看报错 ~ ~ ~)')
except Exception as e:
    print("更新pip时出错：", e)
try:
    a = os.system("pip cache purge")
    if a == 0 :
        print('pip缓存清理成功')
except:
     print('pip缓存清理失败，可能是网络或权限问题(主要看报错 ~ ~ ~)')
print(f"""
步骤三:预处理函数并开始下载模块""")
def jian_cha():
    for i in import_name:
        try:
            __import__(i)
            print(f"您已安装过模块：{i}")
        except ImportError:
            print(f"未安装模块{i}，稍后将为你开始安装-----")
def download():
    print(f"""==================
注意pyinstaller安装失败没事他主要是打包的只需要给全局安装就可以(基本,没有以偏概全)
1:清华源(最快)
2:阿里云源(较快)
3:官方源(最慢最新)
    """)
    choose = input(f"请选择一个下载源:")
    choose_yuan = {
        "1":"-i https://pypi.tuna.tsinghua.edu.cn/simple/",
        "2":"-i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com",
        "3":""
    }
    use_yuan = choose_yuan.get(choose)
    if use_yuan is None:
        print("输入无效，默认使用官方源")
        use_yuan = ""
    print(f"步骤四:开始安装模块(安装过的也会进行一遍不过通常不超过2秒)")
    for i in module_list:
        start_time = time.time()
        install_result = os.system(f"pip install {i} {use_yuan}")
        end_time = time.time()
        time_stamp = end_time - start_time
        if install_result == 0:
            print(f"安装{i}成功，用时：{time_stamp:.2f}秒")
        else:
            print(f"安装{i}失败，用时：{time_stamp:.2f}秒（可能模块名错误,PY和系统版本不同或网络问题）")
def version():
    import tkinter
    from tkinter import filedialog
    win_object = tkinter.Tk()
    win_object.withdraw()
    #获取Win版本
    import wmi
    win_ver = wmi.WMI().Win32_OperatingSystem()[0].Caption
    #获取并保存 Python 版本信息
    import sys
    ver_info = sys.version_info
    python_ver = f"{ver_info.major}.{ver_info.minor}.{ver_info.micro}"
    file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
    with open(file_path, "w", encoding="utf-8") as f: #W模式为清空写入
        f.write("使用python版本:" + python_ver + "\n")
        f.write("使用的操作系统:" + win_ver + "\n")
        f.write(f"保存时间:{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} \n")
    for i in module_list:
        os.system(f'echo {i}版本: >> "{file_path}" && pip show {i} | findstr Version >> "{file_path}"')
        print(f"已导入{i}的版本号")
    print(f"全部导入完成!")
def uninstall():
    for i in module_list:
        print(f"开始卸载模块{i}")
        os.system(f"pip uninstall {i} -y")
    print('卸载完成')
def total():
    jian_cha()
    download()
def single():
    _ = input("""请选择:
    1:卸载单个模块
    2:下载单个模块
    3：卸载并重装""")
    module = input("请输入模块名:")
    if _ == "1":
        a = os.system(f"pip uninstall {module} -y")
        if a != 0:
            print("请检查是否模块名写错或压根没安装该模块")
    elif _ == "2":
        a = os.system(f"pip install {module}")
        if a != 0:
            print("请检查是否模块名写错")
    elif _ == "3":
        a = os.system(f"pip uninstall {module} -y")
        if a != 0:
            print("请检查是否模块名写错或压根没安装该模块")
            exit()
        b = os.system(f"pip install {module}")
        if b != 0:
            print("请检查是否模块名写错")
            exit()
    print("操作已完成!")
def main():
    print(f"""1:仅检查模块安装
2:仅下载模块
3:检查并下载
4:卸载全部项目模块
5:把项目模块的版本号保存到txt中
(5:注意 : 文件内容将会被清空!)
6:下载或卸载单个模块
""")
    _ = input("请选择方式:")
    __ = {
        "1":jian_cha,
        "2":download,
        "3":total,
        "4":uninstall,
        "5":version,
        "6":single
    }
    l = __.get(_)#返回值如果是一个要执行的函数就可以在后面加()
    if l:          #比如a()返回a之后后面有()就被当作a()执行
        l()#这样做是因为字典直接对应函数会默认从上到下执行而不管后面的get
    else:
        print("无效输入")
main()