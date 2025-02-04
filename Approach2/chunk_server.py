
# import os
# import socket

# CHUNK_STORAGE_DIR = "chunk_storage"
# CHUNK_SERVERS = {
#     8001: "chunk_server_1",
#     8002: "chunk_server_2",
#     8003: "chunk_server_3",
#     8004: "chunk_server_4",
#     8005: "chunk_server_5"
# }

# def setup_storage():
#     if not os.path.exists(CHUNK_STORAGE_DIR):
#         os.mkdir(CHUNK_STORAGE_DIR)
#     for server_dir in CHUNK_SERVERS.values():
#         server_path = os.path.join(CHUNK_STORAGE_DIR, server_dir)
#         if not os.path.exists(server_path):
#             os.mkdir(server_path)

# def chunk_server(port):
#     server_dir = CHUNK_SERVERS[port]
#     server_path = os.path.join(CHUNK_STORAGE_DIR, server_dir)
    
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind(("localhost", port))
#         s.listen(5)
#         print(f"Chunk server running on port {port}.")

#         while True:
#             conn, addr = s.accept()
#             with conn:
#                 data = conn.recv(1024).decode()
#                 if not data:
#                     continue

#                 print(f"[Chunk Server {port}] Received message {data}")

#                 command, *args = data.split(" ", 1)
#                 if command == "WRITE":
#                     print("Response from master server...")
#                     chunk_id, chunk_data = args[0].split(" ", 1)
#                     chunk_path = os.path.join(server_path, chunk_id)
                    
#                     with open(chunk_path, "w") as f:
#                         f.write(chunk_data)
                    
#                     print(f"[Chunk Server {port}] Stored chunk '{chunk_id}' with data: {chunk_data}")
#                     conn.sendall("ACK".encode())
#                     print(f"[Chunk Server {port}] Sent acknowledgment to master.")
                
#                 elif command == "READ":
#                     print("Request is from client...")
#                     chunk_id = args[0]
#                     chunk_path = os.path.join(server_path, chunk_id)
                    
#                     if os.path.exists(chunk_path):
#                         with open(chunk_path, "r") as f:
#                             data = f.read()
                        
#                         print(f"[Chunk Server {port}] Read chunk '{chunk_id}': {data}")
#                         conn.sendall(data.encode())
#                         print(f"[Chunk Server {port}] Sent chunk data to client.")
#                     else:
#                         error_message = "Chunk not found."
#                         print(f"[Chunk Server {port}] {error_message} for chunk '{chunk_id}'")
#                         conn.sendall(error_message.encode())
                
#                 # elif command == "METADATA":
#                 #     metadata = args[0]
#                 #     print(f"[Chunk Server {port}] Received metadata: {metadata}")
#                 #     conn.sendall("ACK".encode())
#                 #     print(f"[Chunk Server {port}] Sent acknowledgment for metadata.")
                
#                 else:
#                     error_message = "Unknown command."
#                     print(f"[Chunk Server {port}] {error_message}")
#                     conn.sendall(error_message.encode())

# if __name__ == "__main__":
#     setup_storage()
#     import sys
#     port = int(sys.argv[1])
#     chunk_server(port)
import os
import socket

CHUNK_STORAGE_DIR = "chunk_storage"
CHUNK_SERVERS = {
    8001: "chunk_server_1",
    8002: "chunk_server_2",
    8003: "chunk_server_3",
    8004: "chunk_server_4",
    8005: "chunk_server_5"
}

def setup_storage():
    if not os.path.exists(CHUNK_STORAGE_DIR):
        os.mkdir(CHUNK_STORAGE_DIR)
    for server_dir in CHUNK_SERVERS.values():
        server_path = os.path.join(CHUNK_STORAGE_DIR, server_dir)
        if not os.path.exists(server_path):
            os.mkdir(server_path)

def chunk_server(port):
    server_dir = CHUNK_SERVERS[port]
    server_path = os.path.join(CHUNK_STORAGE_DIR, server_dir)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", port))
        s.listen(5)
        print(f"Chunk server running on port {port}.")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue

                print(f"[Chunk Server {port}] Received message {data}")

                command, *args = data.split(" ", 1)
                if command == "WRITE":
                    print("Response from master server...")
                    chunk_id, chunk_data = args[0].split(" ", 1)
                    chunk_path = os.path.join(server_path, chunk_id)
                    
                    with open(chunk_path, "w") as f:
                        f.write(chunk_data)
                    
                    print(f"[Chunk Server {port}] Stored chunk '{chunk_id}' with data: {chunk_data}")
                    conn.sendall("ACK".encode())
                    print(f"[Chunk Server {port}] Sent acknowledgment to master.")
                
                elif command == "READ":
                    print("Request is from client...")
                    chunk_id = args[0]
                    chunk_path = os.path.join(server_path, chunk_id)
                    
                    if os.path.exists(chunk_path):
                        with open(chunk_path, "r") as f:
                            data = f.read()
                        
                        print(f"[Chunk Server {port}] Read chunk '{chunk_id}': {data}")
                        conn.sendall(data.encode())
                        print(f"[Chunk Server {port}] Sent chunk data to client.")
                    else:
                        error_message = "Chunk not found."
                        print(f"[Chunk Server {port}] {error_message} for chunk '{chunk_id}'")
                        conn.sendall(error_message.encode())
                
                else:
                    error_message = "Unknown command."
                    print(f"[Chunk Server {port}] {error_message}")
                    conn.sendall(error_message.encode())

if __name__ == "__main__":
    setup_storage()
    import sys
    port = int(sys.argv[1])
    chunk_server(port)
