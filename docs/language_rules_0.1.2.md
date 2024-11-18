# Orca language rules V0.1.2

## 1. 变量标识符
- 变量以数字字母下划线组成并且不能以数字开头，要用“$variable”表示，如果变量后有其它数字、字母、下划线，需要在末尾加空格。

## 2. LLM调用语句
- 标识符：llm_call、xxxx、p:xxxx；
- 样例：
```
请根据以下内容生成一个json格式的内容：$variable ->result(json)

p: 请根据以下内容生成一个json格式的内容：$variable ->result(json)


@llm_call(
    query="请根据以下内容生成一个json格式的内容：$variable。使用chatglm3-130b模型。",
)->result
```

## 3. 函数调用语句
- 标识符：@；
- 样例：
```
@tool1(2)->result(int)
```

## 4. 循环语句
- 标识符：for、遍历；
- 样例：
```
FOR $item in $variable:
    根据$item写一首诗->>result(list)
    @func1(args1)->>result1(list)
    @func2(args2)->>result2(list)
END

遍历$variable:
    # do something
END
```

## 5. 程序退出语句
- 标识符：exit()；
- 样例：
```
@exit(msg="步骤 1运行结束,退出程序！")
```

## 6. 函数定义语句
```python
def add_one(a):
    return a+1
```
```workflow
def flow1():
    @tool1($a) -> result1
    @tool2($result1) -> result2
    return result2
```
- 定义函数要有明确的代码缩进，函数名以字母开头，后接字母数字下划线，函数参数以逗号分隔，函数体以冒号结尾，函数体以4个空格缩进。

## 7. agent定义语句(支持页面配置、语言内配置临时agent)
```
@agent_init(roles = {}, tools = {})->agent_name
```

## 8. agent调用语句
- 标识符：；
- 样例：
```
不指定agent运行：
p:写一首诗，再赏析

指定agent运行：
@agent_name(query=$query) -> result
```

## 9. 断点语句
- 标识符：(bp)；
- 样例：
```
# do something
(bp)
```

## 10.语义条件判断函数
- @condition_judge($variable, [">1", "<=1"])->result
- 返回当前$variable$属于列表中的类别索引

## 11. 条件语句
- 标识符：if、elif、else；
- 如果为非明确语义判断需要结合condition_judge函数，如：
```
@condition_judge($variable, [">1", "<1"，"=1"])->condition_flag
IF $condition_flag == 0:
    # do something
elif $condition_flag == 1:
    # do something
else:
    # do something
END
```
- 如果为明确判断则直接判断：
```
IF $variable > 1:
    # do something
elif $variable <= 1:
    # do something
else:
    # do something
END
```



- 说明：
- 1. 断点工具用于调试，只能写在step结束位置，在程序运行到指定位置时，程序会暂停运行，并返回当前步骤的output和所有变量的状态值breakpoint_infos；
- 2. 继续执行时，传入step_in则继续运行一个step后暂停，传入step_continue则会运行至所有step结束；在传入step_in或者step_continue时，需要传入breakpoint_infos;


## 保留关键字：
- if、elif、else、for、遍历、exit、llm_call、tool_call、def、function_call、agent_init、agent_call、step、goto、condition_judge、步骤、(bp)
- 每一条执行命令内容需要使用"@","->result"包裹起来，每个步骤最外层执行的prompt内容不需要包裹起来，里层嵌套的prompt需要使用"\np:"和"\n"包裹起来。

## 说明
- 大小写敏感；
- 使用@符号调用函数时，必须使用->或->>接收返回值，如果没有返回值则“->None”
