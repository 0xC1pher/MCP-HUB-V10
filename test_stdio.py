import subprocess
import json
import time

process = subprocess.Popen(
    ["C:/Python314/python.exe", "C:/Users/Admin/Desktop/workspace/HUB/core/mcp_stdio.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

print("Process started. Waiting...")
time.sleep(2)

init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

print("Sending initialize...")
try:
    import select
    # read stderr line by line without blocking if possible
    process.stdin.write(json.dumps(init_request) + '\n')
    process.stdin.flush()
    
    import time
    for _ in range(50):
        if process.poll() is not None:
            break
        time.sleep(0.1)
    
    if process.poll() is not None:
        print("Process exited with code:", process.poll())
        print("STDERR:", process.stderr.read())
    else:
        print("Process still running but hanging...")
        # attempt to read stderr if any
        # (this might block, so we'll just terminate)
        pass
except Exception as e:
    print("Error:", e)

process.terminate()
