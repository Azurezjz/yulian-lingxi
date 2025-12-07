"""
检查 .env 文件配置
"""
import os
from pathlib import Path

def check_env_file():
    """检查 .env 文件是否存在并显示内容（隐藏敏感信息）"""
    env_path = Path(__file__).parent / ".env"
    
    print("=" * 60)
    print("环境变量配置检查")
    print("=" * 60)
    
    if env_path.exists():
        print(f"✓ .env 文件存在: {env_path}")
        print("\n文件内容（隐藏敏感信息）:")
        print("-" * 60)
        
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    print(f"{line_num:3d}: {line}")
                elif '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 隐藏敏感信息
                    if 'KEY' in key.upper() or 'SECRET' in key.upper() or 'PASSWORD' in key.upper():
                        if value:
                            masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
                            print(f"{line_num:3d}: {key}={masked_value}")
                        else:
                            print(f"{line_num:3d}: {key}=")
                    else:
                        print(f"{line_num:3d}: {line}")
        
        print("-" * 60)
        
        # 检查关键配置
        print("\n关键配置检查:")
        print("-" * 60)
        
        # 读取环境变量
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        weather_key = os.getenv("WEATHER_API_KEY")
        if weather_key:
            print(f"✓ WEATHER_API_KEY: 已配置 ({weather_key[:10]}...)")
        else:
            print("✗ WEATHER_API_KEY: 未配置")
            print("  请在 .env 文件中添加: WEATHER_API_KEY=06408ee685b86982dacc54a7e92a1787")
        
        llm_key = os.getenv("LLM_API_KEY")
        if llm_key:
            print(f"✓ LLM_API_KEY: 已配置")
        else:
            print("○ LLM_API_KEY: 未配置（可选，将使用规则识别）")
        
    else:
        print(f"✗ .env 文件不存在: {env_path}")
        print("\n请创建 .env 文件，内容如下:")
        print("-" * 60)
        print("WEATHER_API_KEY=06408ee685b86982dacc54a7e92a1787")
        print("-" * 60)
        print("\n创建步骤:")
        print("1. 在 backend/ 目录下创建 .env 文件")
        print("2. 添加上述内容")
        print("3. 保存文件")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        check_env_file()
    except ImportError:
        print("警告: python-dotenv 未安装，无法读取 .env 文件")
        print("请运行: pip install python-dotenv")
        # 直接检查文件
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            print(f"\n✓ .env 文件存在: {env_path}")
        else:
            print(f"\n✗ .env 文件不存在: {env_path}")





