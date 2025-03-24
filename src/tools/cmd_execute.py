import subprocess
import sys

async def cmd_execute(command: str = "", params_format: bool = False):
    """
    执行系统命令行工具
    
    Args:
        command: 要执行的命令字符串
        params_format: 是否返回参数格式
    
    Returns:
        str: 命令执行的输出结果
    
    Raises:
        Exception: 当命令为空或执行失败时
    """
    # 如果请求参数格式，返回参数列表
    if params_format:
        return ['command']
    
    # 参数校验
    if not command or not isinstance(command, str):
        raise Exception("命令不能为空且必须是字符串")
    
    # 显示命令并请求用户确认
    print(f"即将执行命令: {command}")
    confirm = input("确认执行此命令? (y/n): ").strip().lower()
    
    # 用户确认后执行命令
    if confirm == 'y' or confirm == 'yes':
        try:
            # 执行命令并获取输出
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            # 返回命令执行结果
            return {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
                "success": process.returncode == 0
            }
            
        except Exception as e:
            raise Exception(f"命令执行失败: {str(e)}")
    else:
        return "命令已取消执行"

# 测试代码
async def main():
    result = await cmd_execute(command="ls -la")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
