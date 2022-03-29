import threading
import keyboard
import os, sys

# Add parent folder to path
sys.path.insert(1, os.path.join(sys.path[0], ".."))

# Import from parent directory
import util, sockets

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
    args = util.get_args()

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
