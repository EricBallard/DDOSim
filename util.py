import argparse

def get_args():
    # Check for CLI args / Set defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="Target address to bind", default="127.0.0.1")
    parser.add_argument("--port", help="Target port to bind", default="25565")
    parser.add_argument("--tcp", help="Set server to use TCP", default=False)
    return parser.parse_args()