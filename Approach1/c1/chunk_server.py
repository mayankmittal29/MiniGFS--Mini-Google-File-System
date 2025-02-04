import socket
import threading
import random
import time
import json 
import os

MASTER_PORT=5000
HEARTBEAT_INTERVAL=10

class ChunkServer:
    def __init__(self, host, port, master_host, master_port):
        self.host = host
        self.port = port
        self.master_host = master_host
        self.master_port = master_port
        self.storage = {}  # Map of chunk_id to data

    def register_with_master(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.master_host, self.master_port))
            sock.sendall(f"REGISTER {self.host}:{self.port}".encode())

            response = sock.recv(1024).decode()
            if response == "REGISTERED":
                print(f"Chunk Server registered with Master Server at {self.master_host}:{self.master_port}")

    def send_heartbeat(self):
        while True:
            try:
                self.storage = {}  # Clear existing storage
                for file in os.listdir('.'):  # List files in the current directory
                    if file.startswith("chunk_") and file.endswith(".txt"):
                        # Extract the chunk ID from the filename
                        chunk_id = file.split("_")[1].split(".")[0]
                        self.storage[chunk_id] = file  # Map chunk ID to filename

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.master_host, self.master_port))

                    # Prepare the heartbeat message
                    heartbeat_data = {
                        "server": f"{self.host}:{self.port}",
                        "chunks": list(self.storage.keys())
                    }
                    message = f"HEARTBEAT {json.dumps(heartbeat_data)}".encode()

                    sock.sendall(message)
                    print(f"Heartbeat sent to master: {heartbeat_data}")
            except Exception as e:
                print(f"Failed to send heartbeat: {e}")
            time.sleep(HEARTBEAT_INTERVAL)


    def start(self):
        self.register_with_master()
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Chunk Server running on {self.host}:{self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"Client connected from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, conn):
        try:
            req_length = int.from_bytes(conn.recv(4), 'big')
            req = conn.recv(req_length)    
            print(req.decode())
            print("we are here")
            if req.decode()=="UPLOAD":
                chunk_id_length = int.from_bytes(conn.recv(4), 'big')
                chunk_id = conn.recv(chunk_id_length).decode()

                # Receive chunk data
                chunk_data_length = int.from_bytes(conn.recv(4), 'big')
                chunk_data = conn.recv(chunk_data_length)
                file_name = f"chunk_{chunk_id}.txt"
                with open(file_name, "w") as file:
                    file.write(chunk_data.decode())

                print(f"Stored {chunk_id}")
            
            if req.decode()=="READ":
                chunk_id_length = int.from_bytes(conn.recv(4), 'big')
                chunk_id = conn.recv(chunk_id_length).decode()
                file_name=f"chunk_{chunk_id}.txt"
                with open(file_name, "rb") as f:
                    chunk_data = f.read(1024)
                conn.sendall(chunk_data)
            
            if req.decode()=="APPEND":
                chunk_id_length = int.from_bytes(conn.recv(4), 'big')
                chunk_id = conn.recv(chunk_id_length).decode()
                file_name=f"chunk_{chunk_id}.txt"
                with open(file_name, "rb") as f:
                    chunk_data = f.read(1024)
                conn.sendall(chunk_data)
                prepare_chunk_data_length = int.from_bytes(conn.recv(4), 'big')
                prepare_chunk_data = conn.recv(prepare_chunk_data_length)
                
                cancommit = int.from_bytes(conn.recv(4), 'big')
                cancommitmsg = conn.recv(cancommit)
                print(cancommitmsg.decode())
                if cancommitmsg.decode()=="canCommit?":
                    conn.sendall(b"yes")
                    print("Sending yes......")
                    AbortOrCommit=int.from_bytes(conn.recv(4), 'big')
                    AbortOrCommitmsg=conn.recv(AbortOrCommit)
                    print(AbortOrCommit.decode())
                    if AbortOrCommitmsg.decode()=="doCommit":
                        file_name = f"chunk_{chunk_id}.txt"
                        with open(file_name, "w") as file:
                            file.write(prepare_chunk_data.decode())
                        print("Data Successfully committed")

        finally:
            conn.close()

if __name__ == "__main__":
    chunk_server = ChunkServer(host="0.0.0.0", port=random.randint(1,65554), master_host="127.0.0.1", master_port=MASTER_PORT)
    chunk_server.start()