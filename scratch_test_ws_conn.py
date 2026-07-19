import websocket
import threading
import time
import subprocess
import os

def start_server():
    print("[Server] Starting FastAPI server...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    return subprocess.Popen(
        [".venv/bin/python", "run.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

def test_client():
    # Wait for server to boot
    time.sleep(3)
    
    ws_url = "ws://127.0.0.1:8080/ws/test-task-id-999"
    print(f"[Client] Connecting to {ws_url}...")
    
    try:
        ws = websocket.create_connection(ws_url)
        print("[Client] Connection established!")
        
        # Read the first handshake message
        msg = ws.recv()
        print(f"[Client] Received: {msg}")
        
        ws.close()
        print("[Client] Connection closed successfully.")
    except Exception as e:
        print(f"[Client] Connection failed: {e}")

def main():
    server_proc = start_server()
    
    # Start server reader thread to print server logs
    def log_reader():
        for line in server_proc.stdout:
            print(f"[Server Log] {line.strip()}")
            
    t = threading.Thread(target=log_reader, daemon=True)
    t.start()
    
    try:
        test_client()
    finally:
        print("[Server] Shutting down FastAPI server...")
        server_proc.terminate()
        server_proc.wait()
        print("[Server] Terminated.")

if __name__ == "__main__":
    main()
