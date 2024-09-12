import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading
from cryptography.fernet import Fernet
import time
from collections import defaultdict

# login formate, paramiko key, and generates a symmetric encryption key
logging_format = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"
host_key = paramiko.RSAKey(filename='server.key')

key = Fernet.generate_key()
cipher = Fernet(key)

# Logging setup
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

commands_logger = logging.getLogger('CommandsLogger')
commands_logger.setLevel(logging.INFO)
commands_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
commands_handler.setFormatter(logging_format)
commands_logger.addHandler(commands_handler)

fake_filesystem = {
    '/': ['bin', 'etc', 'home', 'var', 'root'],
    '/home': ['user1', 'user2'],
    '/home/user1': ['file1.txt', 'file2.txt'],
    '/home/user2': ['file3.txt', 'secret.txt'],
    '/etc': ['passwd', 'shadow'],
    '/var': ['log', 'tmp'],
    '/root': ['.bashrc', 'README.md'],
    '/bin': ['ls', 'cat', 'pwd', 'rm', 'echo']
}

def list_files(path):
    if path in fake_filesystem:
        return "  ".join(fake_filesystem[path]) + "\n"
    else:
        return "No such directory\n"


MAX_FAILED_ATTEMPTS = 5
BLOCK_DURATION = 60
failed_attempts = defaultdict(int)
blocked_ips = {}

# Emulated shell
def emulated_shell(channel, client_ip):
    channel.send(b'kali@kali$ ')
    command = b""
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()
            break

        command += char

        if char == b'\r':
            cmd = command.strip().decode('utf-8')
            response = b''

            if cmd == 'exit':
                response = b'\nbye\n'
                channel.send(response)
                channel.close()
                break
            elif cmd == 'pwd':
                response = b'/usr/local/\r\n'
            elif cmd == 'whoami':
                response = (client_ip + '\r\n').encode()
            elif cmd.startswith('ls'):
                if cmd == 'ls':
                    path = '/'
                else:
                    path = cmd.split(' ')[1]

                response = list_files(path).encode() + b'\r\n'
            elif cmd.startswith('cat '):
                file_to_cat = cmd.split(' ')[1]
                if file_to_cat in ['/etc/passwd']:
                    response = b'\nroot:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\r\n'
                else:
                    response = b'No such file or directory\r\n'
            elif cmd == 'ps':
                response = b'  PID TTY          TIME CMD\n 1234 pts/0    00:00:01 bash\n'
            else:
                response = f'\n{cmd}: command not found\n'.encode()

            commands_logger.info(f'Command "{cmd}" executed by {client_ip}')
            
            channel.send(response)
            channel.send(b'kali@kali$ ')
            command = b""

# SSH server
class Server(paramiko.ServerInterface):
    users = {
        'admin': 'admin123',
        'user1': 'password1',
        'user2': 'password2'
    }

    def __init__(self, client_ip):
        self.event = threading.Event()
        self.client_ip = client_ip

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    # Check authentication and handle brute force protection
    def check_auth_password(self, username, password):
        if self.client_ip in blocked_ips:
            blocked_until = blocked_ips[self.client_ip]
            if time.time() < blocked_until:
                funnel_logger.warning(f"{self.client_ip} is blocked due to repeated failed attempts")
                return paramiko.AUTH_FAILED
            else:
                del blocked_ips[self.client_ip]

        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')

        if username in self.users and self.users[username] == password:
            funnel_logger.info(f"Successful login attempt by {self.client_ip} with username: {username}")
            return paramiko.AUTH_SUCCESSFUL
        else:
            failed_attempts[self.client_ip] += 1
            if failed_attempts[self.client_ip] >= MAX_FAILED_ATTEMPTS:
                blocked_ips[self.client_ip] = time.time() + BLOCK_DURATION
                funnel_logger.warning(f"{self.client_ip} is now blocked after {MAX_FAILED_ATTEMPTS} failed attempts")
            return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

# Client handler
def client_handle(client, addr):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")

    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER

        server = Server(client_ip=client_ip)
        transport.add_server_key(host_key)
        transport.start_server(server=server)

        channel = transport.accept(5000)
        if channel is None:
            print("No Channel was opened.")
        else:
            standard_banner = "Welcome to Kali Linux (Debian GNU/Linux 11)\n"
            channel.send(standard_banner.encode())
            emulated_shell(channel, client_ip)

    except Exception as error:
        print(f"Error: {error}")

    finally:
        try:
            transport.close()
        except Exception as error:
            print(f"Error closing transport: {error}")
        client.close()

def honeypot(address, port):
    try:
        socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socks.bind((address, port))
        socks.listen(100)
        print(f"SSH server is listening on port {port}.")

        while True:
            try:
                client, addr = socks.accept()
                ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr))
                ssh_honeypot_thread.start()
            except Exception as error:
                print(f"Error handling client: {error}")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
    except Exception as error:
        print(f"Error in honeypot: {error}")
    finally:
        try:
            socks.close()
            print("Socket closed.")
        except Exception as error:
            print(f"Error closing socket: {error}")


honeypot('127.0.0.1', 2223)
