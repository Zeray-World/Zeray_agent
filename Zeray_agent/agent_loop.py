
import json
import tools
import 调试and工具

def model_user(messages, model_all_reply, model_reply_content, model_reasoning_content,
               tool_use, Max_tool_use, start_time, end_time):

    if model_all_reply.tool_calls:

        #额度已用尽：工具不执行，但必须让模型"知道"发生了什么
        if tool_use >= Max_tool_use:
            messages.append({"role": "assistant",
                             "content": model_reply_content or "",
                             "reasoning_content": model_reasoning_content or "",}, )

            messages.append({"role": "system",
                             "content": f"工具调用上限（{tool_use}/{Max_tool_use}）—— 你刚才请求的工具没有执行，不要再请求工具，请直接用已有信息回答/请求用户放宽或交付。"}, )

            print(f"用时 : {str(end_time - start_time)[0:3]}s\n")

            return tool_use, False

        tool_use += 1

        if tool_use == Max_tool_use:
            messages.append({"role": "system",
                             "content": "这是最后一次工具调用，执行后无法再调用工具，建议直接交付或请用户放宽"}, )

        print("模型请求调用工具 agent循环继续")
        messages.append({"role": "assistant",
                         "content": model_reply_content or "","reasoning_content": model_reasoning_content or "",
                         "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in model_all_reply.tool_calls
            ], }, )

        for tool_call in model_all_reply.tool_calls:
            print(f"调用工具: {tool_call.function.name}")

            try:
                arguments = json.loads(tool_call.function.arguments)
                print(f"参数: {arguments}")

                #根据工具名和参数执行本地函数

                if tool_call.function.name == "cmd":
                    result = tools.cmd(**arguments)  #字典解包 XX=XX

                elif tool_call.function.name == "curl":
                    result = tools.curl(**arguments)

                elif tool_call.function.name == "all_info":
                    result = 调试and工具.all_info(**arguments)

                elif tool_call.function.name == "file_read":
                    result = tools.file_read(**arguments)

                elif tool_call.function.name == "file_edit":
                    result = tools.file_edit(**arguments)

                elif tool_call.function.name == "file_write":
                    result = tools.file_write(**arguments)

                elif tool_call.function.name == "subagent":
                    import sub_agent
                    result = sub_agent.运行子代理(**arguments)

                else:
                    result = f"未知工具: {tool_call.function.name}"

            except KeyboardInterrupt:
                result = "用户打断了本次工具调用"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        return tool_use, True

    else:

        messages.append({"role": "assistant",
                         "content": model_reply_content,
                         "reasoning_content": model_reasoning_content or ""})

        return tool_use, False
