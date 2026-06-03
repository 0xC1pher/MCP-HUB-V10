import subprocess
import json
import time

def send_message(process, message):
    json_msg = json.dumps(message)
    print(f"Sending: {json_msg}")
    process.stdin.write(json_msg + "\n")
    process.stdin.flush()

def read_response(process):
    line = process.stdout.readline()
    if line:
        print(f"Received: {line.strip()}")
        return json.loads(line)
    return None

def test_server():
    # Start the server
    process = subprocess.Popen(
        ["python", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 1. Initialize
        send_message(process, {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        })
        read_response(process)
        
        # 2. List Tools
        send_message(process, {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        })
        read_response(process)
        
        # 3. Call Tool: create_implementation_plan
        send_message(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "create_implementation_plan",
                "arguments": {
                    "feature_description": "Sistema de login con OAuth"
                }
            }
        })
        # This might take a bit longer
        response = read_response(process)
        
    finally:
        process.terminate()
        # Print stderr for debugging
        print("\nServer Log (stderr):")
        print(process.stderr.read())

if __name__ == "__main__":
    test_server()
