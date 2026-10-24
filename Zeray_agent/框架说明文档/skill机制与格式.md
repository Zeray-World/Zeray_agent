# skill机制与格式.md

## 格式

1. skill下分别有两个目录 agent和user
2. 用户在user目录中创建一个文件夹名字就是自己的skill_name

### 3. skill_name文件夹中必须有两个文件

- 和skill_name一个名字的md文件充当skill住教程角色
- 一个说明.txt不能超过100字

## 机制

- 程序每轮注入来及时发现更改
- 以上任意一点不满足模型只能看到格式错误
- 模型会看到 skill_name,skill_path,skill_说明

## 特别说明

- skill每轮注入更符合skill的用法 : 新建/改了 skill，下一轮模型就能看到，不用重启
- 当然 如果你skill真的多到一个极端值 那么你也可以让你的agent改掉框架代码