"""Simple server launcher"""
import socket

def find_port():
    for p in range(8000, 9000):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', p))
            s.close()
            return p
        except:
            pass
    return 8000

if __name__ == "__main__":
    port = find_port()
    print(f"\nStarting server on http://127.0.0.1:{port}\n")
    
    import uvicorn
    from app_working import app
    uvicorn.run(app, host="127.0.0.1", port=port)

