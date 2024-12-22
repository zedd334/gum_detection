import platform
import subprocess
from shutil import disk_usage


def get_cpu_id():
    """获取 CPU 的唯一标识符"""
    try:
        # Linux 获取 CPU ID
        with open("/proc/cpuinfo", "r") as f:
            cpu_info = f.read()
            for line in cpu_info.split("\n"):
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
        raise Exception("无法获取 CPU ID: 'Serial' 字段不存在")
    except Exception as e:
        raise Exception(f"获取 CPU ID 时发生错误: {e}")




def generate_hardware_id():
    """生成硬件ID"""
    cpu_id = get_cpu_id()
    disk_serial='1034'
    if not cpu_id :
        raise Exception("无法获取 CPU ID 或硬盘序列号。")

    # 将 CPU ID 和硬盘序列号组合成一个唯一的硬件ID
    hardware_id = f"{cpu_id}-{disk_serial}"

    # 生成一个基于 CPU ID 和硬盘序列号的 UUID
    return hardware_id

def check_license():
    hardware_id=generate_hardware_id()
    if hardware_id=="ARMv8 Processor rev 1 (v8l)-1034":
        print('start')
        return True
    else:
        print("False")
        return False

