import socket
import time

class Socket:
    def __init__(self):
        self.ip_address = '127.0.0.1'
        self.port = 8080
        self.buffer_size = 1024
        self.timeout = 3
    
    def send_solver(self, scrambled_state):
        data = []
        data.extend(scrambled_state[0])
        data.extend(scrambled_state[1])
        data.extend(scrambled_state[2])
        data.extend(scrambled_state[3])
        send_data = ' '.join([f'{num}' for num in data])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            start = time.time()
            s.send(send_data.encode('utf-8'))
            s.settimeout(self.timeout) # 返信待ちのタイムアウト
            try:
                recv_data = s.recv(self.buffer_size)
                solve_time = time.time() - start
            except socket.timeout:
                return None, None
        return recv_data.decode('utf-8'), solve_time
    