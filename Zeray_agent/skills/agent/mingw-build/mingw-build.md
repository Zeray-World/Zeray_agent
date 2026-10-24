# mingw-build —— 把 C/C++ 编译成独立可分发 exe

## 什么时候用
- 用户要求把 .c / .cpp 编译成 exe
- 要交付给别的机器跑，不能依赖对方装运行库
- 需要加图标、版本信息、UAC 清单等 Windows 资源

## 0. 定位工具链（不要硬编码用户路径）
框架自带的 mingw64 就在**框架根目录**下。框架根 = 本 skill 目录向上三级：
`<框架根>/skills/agent/mingw-build/` → `<框架根>/`

确认方式（存在即用；不存在就如实告诉用户并停下，不要改用系统 gcc）：

    dir "<框架根>\mingw64\bin\gcc.exe"

工具清单：`gcc.exe` `g++.exe` `windres.exe` `objcopy.exe` `strip.exe` `make.exe`
自带版本：GCC 16.2.0，默认目标 x86_64-w64-mingw32（64 位）。

## 1. 源码规范
- 源文件一律存 **UTF-8 无 BOM**，不要依赖记事本默认的 GBK。
- 不写死绝对路径、盘符、用户名；路径用参数或相对路径。
- 控制台要输出中文时，在 main 开头加：

      #include <windows.h>
      SetConsoleOutputCP(CP_UTF8);   // 否则 cmd 按 GBK(936) 解析 UTF-8 会乱码

- 需要双击运行后停住看结果的，结尾加 `system("pause");` 或 `getchar();`。

## 2. 标准编译命令（推荐默认档）

C：

    gcc -O2 -static -s -Wall -o app.exe app.c

C++：

    g++ -O2 -static -s -Wall -o app.exe app.cpp

参数含义：
- `-O2` 优化
- `-static` **关键**：把 libgcc / libstdc++ / winpthread 全部静态链进去，换台没装 MinGW 的机器也能跑；不加的话常缺 `libgcc_s_seh-1.dll`、`libstdc++-6.dll`
- `-s` 去符号表，体积能砍掉一大半
- `-Wall` 开着，编译告警读一眼再交付

体积优先可再叠加：`-Os`（替代 -O2）、`strip app.exe` 二次瘦身、`-ffunction-sections -fdata-sections` 配合 `--gc-sections` 去死代码。
要崩溃栈信息就别 `-s`。

## 3. 加图标 / 版本信息 / UAC 清单（可选）
写 `app.rc`：

    #pragma code_page(65001)
    #include <windows.h>
    1 ICON "app.ico"
    1 VERSIONINFO
    FILEVERSION 1,0,0,0
    PRODUCTVERSION 1,0,0,0
    BEGIN
      BLOCK "StringFileInfo"
      BEGIN
        BLOCK "080404b0"
        BEGIN
          VALUE "FileDescription", "程序说明"
          VALUE "FileVersion", "1.0.0.0"
          VALUE "ProductName", "产品名"
          VALUE "LegalCopyright", "© 2026"
        END
      END
      BLOCK "VarFileInfo"
      BEGIN
        VALUE "Translation", 0x804, 1200
      END
    END

编译资源并链接：

    windres app.rc -O coff -o app_res.o
    gcc -O2 -static -s -o app.exe app.c app_res.o

需要管理员权限时，另建 `app.manifest` 写 `requestedExecutionLevel level="requireAdministrator"`，rc 里加 `1 24 "app.manifest"`。

## 4. 验证（交付前必做）
1. 运行一遍，确认真实输出：

       cd /d <输出目录> && app.exe

   会阻塞等输入的交互式程序别直接跑，用 `echo 输入 | app.exe` 喂数据，或者先问用户。
2. 查依赖，确认只剩系统 DLL：

       objdump -p app.exe | findstr /i "DLL Name"

   期望只见 `KERNEL32.dll` / `msvcrt.dll` / `USER32.dll` 这类系统库；出现 `libgcc*`、`libstdc++*`、`libwinpthread*` 说明 `-static` 没生效。
3. 看体积与架构：`dir app.exe`，`objdump -f app.exe | findstr architecture`。

## 5. 收尾清理
删掉本次产生的中间文件，只留源码和 exe（除非用户要中间产物）：
`*.o`、一次性生成的 `*.rc`、临时构建目录、构建残留。不要动用户源码和交付物。

## 常见报错对照
| 报错 | 原因 / 处理 |
| --- | --- |
| `'gcc' 不是内部或外部命令` | 没用绝对路径调，改用 `<框架根>\mingw64\bin\gcc.exe` |
| `undefined reference to ...` | 源文件没写进命令、漏了 `-l` 库、或忘了把多个 .c 一起编译 |
| `cannot find -lxxx` | 库不存在，确认框架 mingw64 内是否有该库，没有就告知用户 |
| 中文输出乱码 | 源码不是 UTF-8，或没调 `SetConsoleOutputCP(CP_UTF8)` |
| windres 报编码错 | rc 首行加 `#pragma code_page(65001)`，文件存 UTF-8 |
| 提示缺 `libstdc++-6.dll` | `-static` 漏了，C++ 必须带 |
| 程序一闪而过 | 结尾加 `system("pause")` 或 `getchar()` |

## 硬性纪律
- 只用框架 mingw64，禁止改用系统 gcc/clang。
- 一次只跑一条命令；编译失败先贴完整报错定位，不要瞎改源码。
- 交付时必须说明：exe 绝对路径、是否静态、实测输出、体积。
