import threading
import keyboard
import os, sys

# Add sibling folder to path, import util modules
sys.path.append(os.path.abspath('./utils'))
import cli, sockets

# Stop/cleanup
def stop():
    if server is not None:
        server.close()


# Stop sever on key press
def listenForKey():
    print("Press 'Q' to STOP..!")
    shouldListen = True

    # Run until key press or server crashes
    while shouldListen and server.shouldPoll:
        try:
            # Stop server/thread on key q
            if keyboard.is_pressed("q"):
                shouldListen = False
                stop()
        except:
            continue

# Main()
if __name__ == "__main__":
    # Parse CLI args
    args = cli.get_args()

    # Init socket
    server = sockets.get(args.ip, args.port, args.tcp)
    server.bind()

    print("SERVER=", server.sock)

    # Verify server started
    if server.sock is None:
        # Failed to start server - stop
        stop()
    else:
        # Start keyboard listener on new daemon thread
        # https://docs.python.org/3/library/threading.html
        keyListener = threading.Thread(target=listenForKey)
        keyListener.setDaemon = True
        keyListener.start()

        print("started key listener")
        # Server started successfully! Poll...
        server.open()
