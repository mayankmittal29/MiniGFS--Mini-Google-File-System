import json
import os
import socket

CHUNK_SIZE = 64
NUM_CHUNK_SERVERS = 5
METADATA_FILE = "metadata.json"
CHUNK_SERVER_PORTS = [8001, 8002, 8003, 8004, 8005]

if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        json.dump({}, f)

def load_metadata():
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

def handle_create_file(filename):
    metadata = load_metadata()
    if filename in metadata:
        return "File already exists."
    metadata[filename] = {"total_chunks": 0}
    save_metadata(metadata)
    print(f"File {filename} created successfully.")
    return f"File {filename} created successfully."

# def handle_write_file(filename, content, append=False):
#     metadata = load_metadata()
#     if filename not in metadata:
#         return "File does not exist. Create it first."
#     existing_chunks = metadata[filename]
#     existing_content = ""
#     if append:
#         for chunk_id, server in existing_chunks.items():
#             if "replica" not in chunk_id:
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                     s.connect(("localhost", server))
#                     s.sendall(f"READ {chunk_id}".encode())
#                     existing_content += s.recv(1024).decode()

#     content = existing_content + content

#     chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
#     chunk_servers = CHUNK_SERVER_PORTS[:]
#     file_chunks = {}

#     for i, chunk in enumerate(chunks):
#         chunk_id = f"chunk{i}_{filename}"
#         primary_server = chunk_servers[i % NUM_CHUNK_SERVERS]
#         file_chunks[chunk_id] = primary_server
#         replicas = []
#         for j in range(1, 4):
#             replica_server = chunk_servers[(i + j) % NUM_CHUNK_SERVERS]
#             replicas.append(replica_server)

#         file_chunks[f"{chunk_id}_replica1"] = replicas[0]
#         file_chunks[f"{chunk_id}_replica2"] = replicas[1]
#         file_chunks[f"{chunk_id}_replica3"] = replicas[2]

#         for server in [primary_server] + replicas:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect(("localhost", server))
#                 s.sendall(f"WRITE {chunk_id} {chunk}".encode())
#                 ack = s.recv(1024).decode()
#                 if ack != "ACK":
#                     return f"Error storing chunk {chunk_id} on server {server}."

#         for server in [primary_server] + replicas:
#             metadata_details = {
#                 "chunk_id": chunk_id,
#                 "primary_server": primary_server,
#                 "replicas": replicas
#             }
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect(("localhost", server))
#                 s.sendall(f"METADATA {json.dumps(metadata_details)}".encode())
#                 ack = s.recv(1024).decode()
#                 if ack != "ACK":
#                     return f"Error sending metadata for {chunk_id} to server {server}."

#     metadata[filename] = file_chunks
#     save_metadata(metadata)
#     print(f"File {filename} {'appended' if append else 'written'} successfully.")
#     return f"File {filename} {'appended' if append else 'written'} successfully."
# def handle_write_file(filename, content, append=False):
#     metadata = load_metadata()
#     if filename not in metadata:
#         return "File does not exist. Create it first."
#     existing_chunks = metadata[filename]
#     existing_content = ""
    
#     if append:
#         for chunk_id, server in existing_chunks.items():
#             if "replica" not in chunk_id:
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                     s.connect(("localhost", server))
#                     s.sendall(f"READ {chunk_id}".encode())
#                     existing_content += s.recv(1024).decode()

#     content = existing_content + content

#     chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
#     file_chunks = {}

#     for i, chunk in enumerate(chunks):
#         chunk_id = f"chunk{i}_{filename}"
#         # Assign chunk to servers in a round-robin fashion
#         chunk_servers = CHUNK_SERVER_PORTS[:]
#         replicas = [chunk_servers[(i + j) % NUM_CHUNK_SERVERS] for j in range(1, 4)]

#         # Add chunk data and replicas to the file's chunk metadata
#         # file_chunks[chunk_id] = { "replicas": replicas }
#         primary_server = chunk_servers[i % NUM_CHUNK_SERVERS]
#         file_chunks[chunk_id] = primary_server
#         file_chunks[f"{chunk_id}_replica1"] = replicas[0]
#         file_chunks[f"{chunk_id}_replica2"] = replicas[1]
#         file_chunks[f"{chunk_id}_replica3"] = replicas[2]
#         # Write the chunk to each server (primary and replicas)
#         for server in [chunk_servers[i % NUM_CHUNK_SERVERS]] + replicas:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect(("localhost", server))
#                 s.sendall(f"WRITE {chunk_id} {chunk}".encode())
#                 ack = s.recv(1024).decode()
#                 if ack != "ACK":
#                     return f"Error storing chunk {chunk_id} on server {server}."

#         # # Send metadata for the chunk to all involved servers
#         # for server in [chunk_servers[i % NUM_CHUNK_SERVERS]] + replicas:
#         #     metadata_details = {
#         #         "chunk_id": chunk_id,
#         #         "replicas": replicas
#         #     }
#         #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         #         s.connect(("localhost", server))
#         #         s.sendall(f"METADATA {json.dumps(metadata_details)}".encode())
#         #         ack = s.recv(1024).decode()
#         #         if ack != "ACK":
#         #             return f"Error sending metadata for {chunk_id} to server {server}."

#     metadata[filename] = file_chunks
#     save_metadata(metadata)
#     print(f"File {filename} {'appended' if append else 'written'} successfully.")
#     return f"File {filename} {'appended' if append else 'written'} successfully."
def handle_write_file(filename, content, append=False):
    metadata = load_metadata()
    if filename not in metadata:
        return "File does not exist. Create it first."
    
    existing_chunks = metadata[filename]
    existing_content = ""
    total_chunks = existing_chunks["total_chunks"]
    
    if append:
        # Get the last chunk and its server
        last_chunk_index = total_chunks - 1
        last_chunk_id = f"chunk{last_chunk_index}_{filename}"
        last_server = existing_chunks[last_chunk_id]
        
        # Read the last chunk to check available space
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", last_server))
            s.sendall(f"READ {last_chunk_id}".encode())
            existing_content = s.recv(1024).decode()

        # Check if the last chunk has enough space
        if len(existing_content) + len(content) <= CHUNK_SIZE:
            new_content = existing_content + content
            # Write the updated content to the last chunk and its replicas
            for server in [last_server] + [existing_chunks[f"{last_chunk_id}_replica{i}"] for i in range(1, 4)]:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", server))
                    s.sendall(f"WRITE {last_chunk_id} {new_content}".encode())
                    ack = s.recv(1024).decode()
                    if ack != "ACK":
                        return f"Error appending to chunk {last_chunk_id} on server {server}."
            
            print(f"File {filename} appended successfully.")
            return f"File {filename} appended successfully."
    
    # If we reach here, either not appending or chunk is full, create new chunks
    content = existing_content + content if append else content
    chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
    file_chunks = existing_chunks.copy()

    for i in range(len(existing_chunks), len(existing_chunks) + len(chunks)):
        chunk_id = f"chunk{i}_{filename}"
        primary_server = CHUNK_SERVER_PORTS[i % NUM_CHUNK_SERVERS]
        replicas = [CHUNK_SERVER_PORTS[(i + j) % NUM_CHUNK_SERVERS] for j in range(1, 4)]
        total_chunks=total_chunks+1
        file_chunks[chunk_id] = primary_server
        file_chunks[f"{chunk_id}_replica1"] = replicas[0]
        file_chunks[f"{chunk_id}_replica2"] = replicas[1]
        file_chunks[f"{chunk_id}_replica3"] = replicas[2]
        
        for server in [primary_server] + replicas:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", server))
                s.sendall(f"WRITE {chunk_id} {chunks[i-len(existing_chunks)]}".encode())
                ack = s.recv(1024).decode()
                if ack != "ACK":
                    return f"Error storing chunk {chunk_id} on server {server}."
    file_chunks["total_chunks"]=total_chunks
    metadata[filename] = file_chunks
    save_metadata(metadata)
    print(f"File {filename} {'appended' if append else 'written'} successfully.")
    return f"File {filename} {'appended' if append else 'written'} successfully."


def handle_upload_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    filename = os.path.basename(file_path)
    response = handle_create_file(filename)
    if "already exists" not in response:
        response += f"\n{handle_write_file(filename, content)}"
    else:
        response = handle_write_file(filename, content)
    return response

def handle_read_file(filename, byte_range):
    metadata = load_metadata()
    if filename not in metadata:
        return json.dumps({"error": "File does not exist."})
    
    file_chunks = metadata[filename]
    chunk_details = {}

    for chunk, server in file_chunks.items():
        if "_replica" not in chunk: 
            replica_key_prefix = f"{chunk}_replica"
            replicas = [server]
            for replica_key, replica_server in file_chunks.items():
                if replica_key.startswith(replica_key_prefix):
                    replicas.append(replica_server)
            chunk_details[chunk] = replicas

    return json.dumps(chunk_details, indent=4)

def master_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 8000))
        s.listen(5)
        print("Master server running on port 8000.")
        
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue
                
                command, *args = data.split(" ", 1)
                if command == "CREATE":
                    filename = args[0]
                    response = handle_create_file(filename)
                elif command == "WRITE":
                    filename, content = args[0].split(" ", 1)
                    response = handle_write_file(filename, content)
                elif command == "APPEND":
                    filename, content = args[0].split(" ", 1)
                    response = handle_write_file(filename, content, append=True)
                elif command == "UPLOAD":
                    file_path = args[0]
                    response = handle_upload_file(file_path)
                elif command == "READ":
                    filename, byte_range = args[0].split(" ", 1)
                    response = handle_read_file(filename, byte_range)
                else:
                    response = "Unknown command."
                
                conn.sendall(response.encode())

if __name__ == "__main__":
    master_server()

