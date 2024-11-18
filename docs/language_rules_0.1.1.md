# Orca language rules V0.1.1

## 1. 步骤标识符
- 步骤标识符结构：“步骤 name：” 或者 “step name:”
- 说明：步骤标识符以“步骤”、"step"开头，冒号结尾（中英文），中间的name是步骤代号，如“1”、“a”、“a1”、“1a”等以数字字母组成的字符串；中文“步骤”与name之间空格可以删除，英文step与name之间空格必须保留；
- 示例：“步骤1：”、“步骤a：”、“step a：”等

## 2. 变量标识符
- 变量以数字字母下划线组成并且不能以数字开头，要用“{variable}”表示
- 如果表示json或者dict类型内容，则使用“{{}}”表示

## 3. 跳转标识符
- “goto step a” 或者 “goto 步骤 a” 或者 “goto a”；

## 4.语义条件判断函数
- condition_judge({variable}, [">1", "<=1"])，返回当前{variable}属于列表中的类别索引

## 5. 条件语句
- 标识符：if、elif、else；
- 如果为非明确语义判断需要结合condition_judge函数，如：
```
condition_flag = condition_judge({variable}, [">1", "<1"，"=1"])
if condition_flag == 0:
    # do something
elif condition_flag == 1:
    # do something
else:
    # do something
```
- 如果为明确判断则直接判断：
```
if {variable} > 1:
    # do something
elif {variable} <= 1:
    # do something
else:
    # do something
```

## 6. 循环语句
- 标识符：for、遍历；
- 样例：
```
for item in {variable}:
    # do something

遍历{variable}:
    # do something
```

## 7. 程序退出标识符
- 标识符：exit()；
- 样例：
```
step 1:
# do something
exit(msg="步骤 1运行结束,退出程序！")
```
- 说明：exit()只能写在单个步骤的末尾，不能写在step的中间逻辑中。返回内容包括固定的msg字段和当前step的output；

## 8. LLM调用
- 标识符：llm_call；
- 样例：
```
step 1:
llm_call(
    prompt="请根据以下内容生成一个json格式的内容：{variable}",
    model="chatglm3-130b",
)
```

## 9. 工具调用
- 标识符：tool_call；
- 样例：
```
step 1:
tool_call(
    tool_name="get_time",
    args={
        "time_zone": "Asia/Shanghai",
    },
)
```

## 10. 断点工具
- 标识符：(bp)；
- 样例：
```
step 1:
# do something
(bp)
```
- 说明：
- 1. 断点工具用于调试，只能写在step结束位置，在程序运行到指定位置时，程序会暂停运行，并返回当前步骤的output和所有变量的状态值breakpoint_infos；
- 2. 继续执行时，传入step_in则继续运行一个step后暂停，传入step_continue则会运行至所有step结束；在传入step_in或者step_continue时，需要传入breakpoint_infos;



## 保留关键字：
- if、elif、else、for、遍历、exit、llm_call、tool_call、step、goto、condition_judge、步骤、breakpoint

## 说明
- 大小写敏感；
