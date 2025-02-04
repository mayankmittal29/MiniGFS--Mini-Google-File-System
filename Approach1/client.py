import socket
import json

MASTER_PORT=5000

class Client:
    def __init__(self, master_host, master_port):
        self.master_host = master_host
        self.master_port = master_port

    def upload_file(self, filename):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
            master_socket.connect((self.master_host, self.master_port))
            master_socket.sendall(f"UPLOAD {filename}".encode())
            response = master_socket.recv(1024).decode()

            if response == "NO_CHUNK_SERVERS":
                print("No chunk servers available. Upload failed.")
                return
            
            # Receive the length of the chunk mapping data
            data_length = int.from_bytes(master_socket.recv(4), 'big')
            response = b""

            # Receive the complete data
            while len(response) < data_length:
                response += master_socket.recv(1024)

            # chunk_mapping = eval(response.decode())
            chunk_mapping = json.loads(response.decode())  # Decode and parse JSON

            # chunk_mapping = eval(response)
            print(f"Received chunk mapping: {chunk_mapping}")
            self.send_chunks(filename, chunk_mapping)

    def send_chunks(self, filename, chunk_mapping):
        with open(filename, "rb") as f:
            for chunk_id, server in chunk_mapping.items():
                chunk_data = f.read(1024)
                # self.send_chunk(chunk_data, chunk_id, server)
                server_host, server_port = server["primary_server"]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((server_host, int(server_port)))
                    print(server["chunk_id"])
                    
                    req=b"UPLOAD"
                    sock.sendall(len(req).to_bytes(4, 'big'))
                    sock.sendall(req)

                    chunk_id_bytes = server["chunk_id"].encode()
                    sock.sendall(len(chunk_id_bytes).to_bytes(4, 'big'))
                    sock.sendall(chunk_id_bytes)

                    # Send chunk data
                    sock.sendall(len(chunk_data).to_bytes(4, 'big'))
                    sock.sendall(chunk_data)    
        
    def readfile(self,filename):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
            master_socket.connect((self.master_host, self.master_port))
            master_socket.sendall(f"READ {filename}".encode())
            response = master_socket.recv(1024).decode()
            print(response)
            if response == "NO_CHUNK_SERVERS":
                print("No chunk servers available. Upload failed.")
                return
            data_length = int.from_bytes(master_socket.recv(4), 'big')
            response = b""

            # Receive the complete data
            while len(response) < data_length:
                response += master_socket.recv(1024)

            # chunk_mapping = eval(response.decode())
            chunk_mapping = json.loads(response.decode())  # Decode and parse JSON

            # chunk_mapping = eval(response)
            print(f"Received chunk mapping: {chunk_mapping}")
            ans=""
            for chunk_id, server in chunk_mapping.items():
                server_host, server_port = server["primary_server"]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((server_host, int(server_port)))
                    print(server["chunk_id"])
                    req=b"READ"
                    sock.sendall(len(req).to_bytes(4, 'big'))
                    sock.sendall(req)

                    chunk_id_bytes = server["chunk_id"].encode()
                    sock.sendall(len(chunk_id_bytes).to_bytes(4, 'big'))
                    sock.sendall(chunk_id_bytes)

                    chunk_data=sock.recv(1024).decode()
                    ans+=chunk_data
            print(ans)
            
    def append(self, filename, new_content):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
            master_socket.connect((self.master_host, self.master_port))
            master_socket.sendall(f"READ {filename}".encode())
            response = master_socket.recv(1024).decode()
            print(response)
            if response == "NO_CHUNK_SERVERS":
                print("No chunk servers available. Upload failed.")
                return
            data_length = int.from_bytes(master_socket.recv(4), 'big')
            response = b""

            # Receive the complete data
            while len(response) < data_length:
                response += master_socket.recv(1024)

            # chunk_mapping = eval(response.decode())
            chunk_mapping = json.loads(response.decode())  # Decode and parse JSON

            # chunk_mapping = eval(response)
            print(f"Received chunk mapping: {chunk_mapping}")
            # print(chunk_mapping.keys())
            last_chunk_index = max(chunk_mapping.keys())
            metadata=chunk_mapping[last_chunk_index]
            server_host, server_port = metadata["server"]
            chunk_id = metadata["chunk_id"]
            print(chunk_id)
            print(server_port)
            
            # Send new content to the appropriate chunk server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as chunk_socket:
                chunk_socket.connect((server_host, int(server_port)))
                req = b"APPEND"
                chunk_socket.sendall(len(req).to_bytes(4, 'big'))
                chunk_socket.sendall(req)

                # Send chunk_id
                chunk_id_bytes = chunk_id.encode()
                chunk_socket.sendall(len(chunk_id_bytes).to_bytes(4, 'big'))
                chunk_socket.sendall(chunk_id_bytes)

                chunk_data=chunk_socket.recv(1024).decode()
                rem=1024-len(chunk_data)
                toadd=new_content[:rem]
                chunk_data=chunk_data+toadd                    
                chunk_socket.sendall(len(chunk_data).to_bytes(4, 'big'))
                chunk_socket.sendall(chunk_data.encode())    

                cancommit=b"canCommit?"
                chunk_socket.sendall(len(cancommit).to_bytes(4,'big'))
                chunk_socket.sendall(cancommit)

                resp=chunk_socket.recv(1024)
                if resp.decode()=="yes":
                    docommit=b"doCommit"
                    chunk_socket.sendall(len(docommit).to_bytes(4,'big'))
                    chunk_socket.sendall(docommit)

            print(f"Appended content to chunk {chunk_id}.")

if __name__ == "__main__":
    client = Client(master_host="127.0.0.1", master_port=MASTER_PORT)
    while True:
        print("Enter 1 to upload file")
        print("Enter 2 to read a file")
        print("Enter 3 to append to a file")
        
        req=input()
        print("Enter the filename")
        filename=input()
        if req=="1":
            print(filename)
            client.upload_file(filename=filename)
        if req=="2":
            client.readfile(filename=filename)
        if req=="3":
            new_content=input("Enter new content")
            client.append(filename=filename,new_content=new_content)