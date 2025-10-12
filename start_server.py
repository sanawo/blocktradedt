"""
Start Block Trade Information Retrieval Platform
"""
import socket
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def find_free_port(start_port=8000, max_port=9000):
    """Find available port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

if __name__ == "__main__":
    port = find_free_port()
    if port is None:
        print("Error: No available port found!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("  Block Trade Information Retrieval Platform")
    print("  大宗交易信息检索平台")
    print("="*60)
    print(f"\n  Server URL: http://127.0.0.1:{port}")
    print(f"  Please open the URL in your browser")
    print("\n" + "="*60 + "\n")
    
    import uvicorn
    from app_working import app
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
