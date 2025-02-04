import socket
import threading
import json
import random
import time

CHUNK_SIZE = 1024  # Size of each chunk in bytes
MASTER_PORT=5000
HEARTBEAT_INTERVAL = 10  # in seconds

class MasterServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.chunk_servers = []  # List of connected chunk servers (host, port)
        self.lock = threading.Lock()
        self.chunk_mappings={}
        self.chunk_server_chunks = {}  # Map of chunk server to its chunks


    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Master Server running on {self.host}:{self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=self.handle_connection, args=(client_socket,)).start()

    def handle_connection(self, conn):
        try:
            data = conn.recv(1024).decode() 
            if data.startswith("REGISTER"):
                self.register_chunk_server(data.split()[1], conn)
            elif data.startswith("HEARTBEAT"):
                self.process_heartbeat(data.split(" ", 1)[1], conn)
            elif data.startswith("UPLOAD"):
                _, filename = data.split() # Upload example.html
                self.handle_upload(filename, conn)
            elif data.startswith("READ"):
                _,filename=data.split() 
                self.handle_read(filename,conn)
            elif data.startswith("APPEND"):
                _, filename = data.split()
                self.handle_append(filename, conn)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    def process_heartbeat(self, heartbeat_data, conn):
        try:
            heartbeat_info = json.loads(heartbeat_data)
            server_info = heartbeat_info['server']
            chunk_ids = heartbeat_info['chunks']

            with self.lock:
                # Update the mappings based on the heartbeat
                self.chunk_server_chunks[server_info] = chunk_ids
                for chunk_id in chunk_ids:
                    # Ensure the chunk is mapped to the correct server
                    for file, mapping in self.chunk_mappings.items():
                        for chunk_index, chunk_metadata in mapping.items():
                            if chunk_metadata["chunk_id"] == chunk_id:
                                chunk_metadata["server"] = tuple(server_info.split(":"))
            print(f"Processed heartbeat from {server_info}. Updated mappings.")
        except Exception as e:
            print(f"Failed to process heartbeat: {e}")

    def handle_append(self, filename, conn):
        conn.sendall(b"lol")
        chunk_mapping=self.chunk_mappings[filename]
        chunk_mapping_json = json.dumps(chunk_mapping).encode()  # Convert dict to JSON and encode
        conn.sendall(len(chunk_mapping_json).to_bytes(4, 'big'))  # Send the length of the data first
        conn.sendall(chunk_mapping_json)  # Send the actual data

        print(f"Sent chunk mapping to client: {chunk_mapping}")

    def handle_read(self,filename,conn):
        conn.sendall(b"lol")
        chunk_mapping=self.chunk_mappings[filename]
        chunk_mapping_json = json.dumps(chunk_mapping).encode()  # Convert dict to JSON and encode
        conn.sendall(len(chunk_mapping_json).to_bytes(4, 'big'))  # Send the length of the data first
        conn.sendall(chunk_mapping_json)  # Send the actual data

        print(f"Sent chunk mapping to client: {chunk_mapping}")

    def register_chunk_server(self, server_info, conn):
        with self.lock:
            self.chunk_servers.append(tuple(server_info.split(":")))
        print(f"Registered Chunk Server: {server_info}")
        conn.sendall(b"REGISTERED")

    def handle_upload(self, filename, conn):
        if not self.chunk_servers:
            conn.sendall(b"NO_CHUNK_SERVERS")
            print("No chunk servers available for upload.")
            return

        chunks = self.split_file(filename)
        chunk_mapping = {}
        conn.sendall(b"SENDING_MAPPINGS")

        for i, chunk in enumerate(chunks):
            # chunk_id
            chunk_id = f"{random.randint(1,1000000)}"
            assigned_server = self.chunk_servers[i % len(self.chunk_servers)]
            assigned_server1 = self.chunk_servers[(i+1) % len(self.chunk_servers)]
            assigned_server2 = self.chunk_servers[(i+2) % len(self.chunk_servers)]
            chunk_mapping[i] = {
                "chunk_id":chunk_id,
                "primary_server":assigned_server,
                "secondary_1":assigned_server1,
                "secondary_2":assigned_server2
            }
        self.chunk_mappings[filename]=chunk_mapping
        # conn.sendall(str(chunk_mapping).encode())

        # chunk_mapping_str = str(chunk_mapping).encode()
        
        chunk_mapping_json = json.dumps(chunk_mapping).encode()  # Convert dict to JSON and encode
        conn.sendall(len(chunk_mapping_json).to_bytes(4, 'big'))  # Send the length of the data first
        conn.sendall(chunk_mapping_json)  # Send the actual data

        print(f"Sent chunk mapping to client: {chunk_mapping}")

    def split_file(self, filename):
        with open(filename, "rb") as f:
            chunks = []
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:  # End of file
                    break
                chunks.append(chunk)
            return chunks

if __name__ == "__main__":
    master = MasterServer(host="0.0.0.0", port=MASTER_PORT)
    master.start()