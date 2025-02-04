import socket
import os

MASTER_SERVER_PORT = 8000

def send_request(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", MASTER_SERVER_PORT))
        s.sendall(command.encode())
        print("Request by client sent to master server successfully")
        response = s.recv(4096).decode()
    return response

def fetch_chunk_data(chunk_id, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", server_port))
        s.sendall(f"READ {chunk_id}".encode())
        data = s.recv(4096).decode()
    return data

def client():
    print("Google File System Client")
    print("Available operations: CREATE, WRITE, READ, APPEND, UPLOAD")
    print("Examples:")
    print("  CREATE <filename>")
    print("  WRITE <filename> <content>")
    print("  APPEND <filename> <content>")
    print("  READ <filename> <byte-range>")
    print("  UPLOAD <file_path>")
    
    while True:
        user_input = input("\nEnter operation: ").strip()
        if user_input.lower() == "exit":
            print("Exiting client.")
            break
        operation = user_input.split(" ", 1)[0].upper()
        if operation == "UPLOAD":
            file_path = user_input.split(" ", 1)[1]
            if not os.path.exists(file_path):
                print("File not found. Please check the path.")
                continue
            response = send_request(user_input)
        elif operation == "READ":
            filename, byte_range = user_input.split(" ", 1)[1].split(" ", 1)
            response = send_request(f"READ {filename} {byte_range}")
            print("Master server response:", response)
            chunk_details = eval(response)
            final_data = []
            for chunk_id, server_ports in chunk_details.items():
                for port in server_ports:
                    try:
                        data = fetch_chunk_data(chunk_id, port)
                        print(f"{chunk_id} data from server {port}: {data}")
                        final_data.append(data)
                        break 
                    except Exception as e:
                        print(f"Failed to read chunk {chunk_id} from server {port}: {e}")
            print("Final Data:", "".join(final_data))
        else:
            response = send_request(user_input)
            print(f"Response: {response}")

if __name__ == "__main__":
    client()