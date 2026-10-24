# Zeray Agent

首次运行会自动创建 config.json，按提示填写后重新运行即可。

一个运行在命令行里的轻量 AI Agent：能读写文件、执行命令、联网搜索、派子代理、积累 skill，自带便携运行环境，换电脑解压后双击即可运行。

## 1. 环境要求

- Windows 10 / 11 64 位
- 依赖库（缺失时用 `check.py` 安装）：
  - openai 2.37.0
  - tavily-python 0.8.4
  - tokenizers 0.22.2

### 便携环境（完整版自带，GitHub 版未上传）

| 组件 | 版本 | 用途 |
|---|---|---|
| Python | 3.12.9 | 运行主程序 |
| GCC | 16.2.0 | C/C++ 编译（mingw64） |
| Node.js | 24.22.0 | 运行 JavaScript |
| 7-Zip | 25.00 | 压缩 / 解压 |

如果下载的是 GitHub 版，把完整版的 `python/`、`mingw64/`、`node/`、`7zip/` 放进项目根目录即可；没有便携环境时，也可以用系统已安装的 Python 3.12 运行。

## 2. 目录结构

```
Zeray_agent/
├─ run.bat                 一键启动
├─ check.py                依赖检查与安装
├─ main.py                 入口 / 主循环
├─ agent_loop.py           一轮工具调用循环
├─ config.py               配置、提示词注入、权限表
├─ llm.py                  DeepSeek 请求
├─ tools.py                工具实现
├─ sub_agent.py            子代理
├─ 调试and工具.py          斜杠命令、all_info
├─ deepseek_tokenizer.py   token 统计
├─ config.json             API Key、模型、思考档位
├─ tokenizer.json          tokenizer 数据
├─ 提示词/                  SSOT、AGENTS、SOUL、MEMORY、CHANGELOG
├─ 框架说明文档/            框架机制、依赖、开发说明
├─ skills/                 skill 目录（user / agent）
├─ python/                 便携 Python 3.12.9（GitHub 版未上传）
├─ mingw64/                便携 C/C++ 编译器（GCC 16.2.0，GitHub 版未上传）
├─ node/                   便携 Node.js（v24.22.0，GitHub 版未上传）
└─ 7zip/                   便携 7-Zip（25.00，GitHub 版未上传）
```

## 3. 安装依赖

### 方式一：run.bat（推荐）

1. 双击 `run.bat`；
2. 提示“是否检查并安装新版 pip 和项目依赖”时输入 `1`；
3. `check.py` 会列出菜单，选 `1` 仅检查、`3` 检查并安装；
4. 下载源建议选 `1`（清华源）。

### 方式二：命令行

```
python\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 4. 启动

### 便携 Python（推荐）

1. 双击 `run.bat`；
2. 输入 `2` 跳过依赖检查（已经装好时）；
3. 进入 `你 :` 提示符即可对话。

### 系统 Python

1. 确保已安装 Python 3.12；
2. 安装依赖：`pip install -r requirements.txt`；
3. 在项目根目录执行：`python main.py`。

## 5. 配置

`config.json`：

```json
{
    "key": "DeepSeek API Key",
    "思考": "medium",
    "model": "deepseek-flash",
    "TavilyKey": "Tavily API Key"
}
```

- `key`：DeepSeek API Key；
- `思考`：`low` / `medium` / `high`；
- `model`：模型 ID，默认 `deepseek-flash`；
- `TavilyKey`：Tavily 搜索 Key，没有可留空。

## 6. 常用命令

| 命令 | 作用 |
|---|---|
| `/help` | 查看全部命令 |
| `/思考 low/medium/high` | 临时切换思考档位 |
| `/思考行数 N` | 调整思考内容显示行数 |
| `/权限` | 查看当前权限 |
| `/权限 工具 true/ask/false` | 单独调整某个工具权限 |
| `/权限档位 0/1/2/3` | 一键切换权限档位 |
| `/system 文本` | 临时追加 system 提示 |
| `/导出会话` | 导出当前会话 |
| `/加载会话` | 加载会话 |
| `/Max_tool_use N` | 调整工具调用上限 |
| `/全轮 N` | 调整当前轮数 |
| `/全局最大轮数 N` | 调整全局轮数上限 |

## 7. 权限档位

| 档位 | 含义 | cmd | curl | file_read | file_write | file_edit | subagent | workspace |
|---|---|---|---|---|---|---|---|---|
| 0 | 完全权限 | True | True | True | True | True | True | False |
| 1 | 工作区权限 | ask | True | True | False | False | False | True |
| 2 | 读写权限 | ask | True | True | True | True | False | False |
| 3 | 仅对话 | False | False | False | False | False | False | False |

## 8. 便携环境

| 目录 | 内容 |
|---|---|
| `python/` | Python 3.12.9、pip |
| `mingw64/` | GCC 16.2.0、g++、windres、objcopy、strip、make |
| `node/` | Node.js v24.22.0、npm、npx |
| `7zip/` | 7-Zip 25.00 |

## 9. 常见问题

**Q：启动时提示找不到模块？**

A：先跑 `run.bat` 选 `1`，用 `check.py` 安装依赖；或手动执行第 3 节的 pip 命令。

**Q：中文显示乱码？**

A：项目对文件读取和 `cmd` 输出做了 UTF-8 / GBK 自动识别；如果启动脚本的中文提示乱码，把控制台代码页切回 936 再运行。

**Q：pip 下载很慢或超时？**

A：`check.py` 里下载源选 `1`（清华源），或手动加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。

**Q：模型要执行危险命令？**

A：把权限档位切到 `1` 或 `3`，或在 `/权限` 里把 `cmd` 设为 `false`。

## 10. 开源依赖

- [openai](https://github.com/openai/openai-python)（Apache-2.0）
- [tavily-python](https://github.com/tavily-ai/tavily-python)
- [tokenizers](https://github.com/huggingface/tokenizers)（Apache-2.0）
- DeepSeek API（模型服务）
- Tavily API (联网服务)

## 11. 许可证

仅用于参赛与学习，未经允许请勿用于商业用途。
