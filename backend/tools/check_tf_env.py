"""Utility to print interpreter info and TensorFlow availability.

Run this with a specific Python executable to verify which environment
contains TensorFlow and its version.

Outputs (to stdout):
 - exe: full path to Python executable
 - version: Python version
 - tensorflow: version if available, or an error message
"""
import sys
import platform

def main():
    print("exe:", sys.executable)
    print("version:", platform.python_version())
    try:
        import tensorflow as tf  # type: ignore
        print("tensorflow:", tf.__version__)
    except Exception as e:
        print("tensorflow_error:", type(e).__name__, str(e))

if __name__ == "__main__":
    main()
