import platform

"""
This script demonstrates how to use the `platform` module to get the Python version and system information.
"""
def show_python_version():
    version = platform.python_version()
    print(f"Python version: {version}")

if __name__ == "__main__":
    show_python_version()
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Platform: {platform.platform()}")
