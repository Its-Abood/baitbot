import argparse
from ssh_honeypot import honeypot
from web_honeypot import app
import threading

def run_ssh_honeypot(address, port, username, password):
    print(f"[-] Running SSH Honeypot on {address}:{port}...")
    honeypot(address, port, username, password)

def run_http_honeypot():
    print("[-] Running HTTP Honeypot (Flask)...")
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Honeypot Simulation - Choose SSH or HTTP")
    
    # SSH Honeypot Arguments
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1', help="IP address to bind the honeypot")
    parser.add_argument('-p', '--port', type=int, default=2222, help="Port to bind the honeypot")
    parser.add_argument('-u', '--username', type=str, help="Optional: Username for SSH honeypot")
    parser.add_argument('-pw', '--password', type=str, help="Optional: Password for SSH honeypot")
    
    # Honeypot Type Flags
    parser.add_argument('-s', '--ssh', action="store_true", help="Run the SSH Honeypot")
    parser.add_argument('-w', '--http', action="store_true", help="Run the HTTP Honeypot")
    
    args = parser.parse_args()

    try:
        if args.ssh:
            username = args.username if args.username else 'admin'
            password = args.password if args.password else 'admin123'

            run_ssh_honeypot(args.address, args.port, username, password)

        elif args.http:
            http_thread = threading.Thread(target=run_http_honeypot)
            http_thread.start()

        else:
            print("[!] Choose a honeypot type (SSH --ssh) or (HTTP --http).")
    
    except Exception as e:
        print(f"\n[!] Error: {str(e)}\nExiting HONEYPOT...\n")
