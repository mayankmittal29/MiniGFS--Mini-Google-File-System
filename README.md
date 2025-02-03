# 🚀 MiniGFS - A Simple Mini Google File System Implementation

## 📌 Project Overview
MiniGFS is a simplified **Google File System (GFS) replica**, implemented in Python. It simulates a distributed file storage system using **one master server, five chunk servers, and a client**. The system handles **file uploads and reads**, distributing data into 64-byte chunks and managing metadata.

## 🎯 Features
✅ **File Upload & Storage** - Splits files into 64-byte chunks and distributes them across chunk servers.  
✅ **Metadata Management** - Tracks file-to-chunk and chunk-to-server mappings in `metadata.json`.  
✅ **File Retrieval** - Reads file chunks by retrieving data from the chunk servers.  
✅ **Fault Tolerance** - Handles errors, acknowledgments, and missing chunk servers.  
✅ **TCP Socket Communication** - Secure data transfer between client, master, and chunk servers.  

---

## 📁 Project Structure
```
MiniGFS/
│── client.py          # Client for file operations (upload & read)
│── master.py          # Master server managing metadata and chunk mapping
│── chunk_server.py    # Handles chunk storage and retrieval
│── metadata.json      # Stores file-to-chunk and chunk-to-server mappings
│── servers/           # Directory containing 5 chunk server folders
│   ├── chunk1/
│   ├── chunk2/
│   ├── chunk3/
│   ├── chunk4/
│   ├── chunk5/
│── README.md          # Documentation
```

---

## 🛠️ Setup & Installation
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/ShardHive.git
cd ShardHive
```

### 2️⃣ Install Dependencies
Ensure Python 3 is installed, then install required libraries (if needed):
```bash
pip install -r requirements.txt  # If any dependencies are required
```

### 3️⃣ Run the Master Server 🏗️
```bash
python master.py
```

### 4️⃣ Start the Chunk Servers 📦 (Run each in separate terminals)
```bash
python chunk_server.py --id=1
python chunk_server.py --id=2
python chunk_server.py --id=3
python chunk_server.py --id=4
python chunk_server.py --id=5
```

### 5️⃣ Start the Client 🎮
```bash
python client.py
```

---

## 📜 Usage Guide
### Upload a File 📤
1️⃣ Run `client.py`
2️⃣ Select **Option 1** (Upload a file) and provide the file path.
3️⃣ The file is split into 64-byte chunks and distributed among chunk servers.
4️⃣ Metadata is updated in `metadata.json`.
5️⃣ A confirmation message is displayed upon success.

### Read a Chunk from a File 📥
1️⃣ Run `client.py`
2️⃣ Select **Option 2** (Read a chunk from a file).
3️⃣ Provide the file name.
4️⃣ The master server returns the chunk locations.
5️⃣ The client fetches data from the corresponding chunk server.
6️⃣ The chunk content is displayed.

---

## 🛡️ Error Handling & Acknowledgments
- If a chunk server is down, the system will **retry fetching the data**.
- The master ensures **uniform chunk distribution** across servers.
- If a file is not found, an appropriate **error message** is displayed.

---

## 🏆 Future Enhancements
🚀 **Chunk Replication** - Improve reliability with redundant copies.  
🚀 **Dynamic Scaling** - Add or remove chunk servers dynamically.  
🚀 **Load Balancing** - Optimize chunk distribution based on server load.  
🚀 **Web UI** - Create a dashboard for file uploads & retrievals.

---

## 👨‍💻 Author
**Mayank Mittal**  
---

## ⭐ Contribute & Support
If you find this project helpful, please consider giving a **⭐ Star** to the repository!  
Feel free to **fork, open issues, or submit PRs** to improve the project.  

Happy coding! 🚀

