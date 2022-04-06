import argparse

def get_args():
    # Check for CLI args / Set defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="Target address to bind", default="127.0.0.1")
    parser.add_argument("--port", help="Target port to bind", default=80)
    parser.add_argument("--tcp", help="Set server to use TCP", default=False)
    
    parser.add_argument("--threads", help="Set # of threads for scanner", default=8)
    parser.add_argument("--start", help="Set start port for scanner", default=1)
    parser.add_argument("--end", help="Set end port for scanner", default=1023)
    return parser.parse_args()