# 🕶️ Gh0stCourier

# 🚀 Overview

Gh0stCourier is a situational awareness utility for Red Team file uploads & controlled downloads.
It provides a stealthy operator-controlled server to deliver or exfiltrate payloads without automated detection.

# 🔹 Key Features

📡 Multithreaded Python HTTP server

🔑 Token-based tasking system (per-client)

👨‍💻 Operator-in-the-loop approval popups (Tkinter)

📁 File upload/download control

🎨 Colorized ASCII banner & command menu

🛡️ Useful for Red Team ops, adversary emulation, and training


# ⚙️ Installation
    git clone https://github.com/activex37b/Gh0stCourier.git
    cd Gh0stCourier
    python3 server.py


# 🛠️ Usage
    Start the server:
    python3 server.py
    ================= Command Menu =================

    list      - List files in server directory
    upload    - Queue file upload to client
              usage: upload <filename> <token>
    exit      - Shut down the server

    ================================================

 # 📸 Screenshots
 Gh0stCourier server interface


File transfer Prompt with token


# 📡 Endpoints

    GET /request_token?token=<id>
    → Clients request queued tasks.

    GET /list
    → Returns the server’s available files.

    GET /download?file=<name>
    → Downloads a file from the server directory.


# ⚠️ Disclaimer

This project is created for educational and authorized Red Team purposes only.
Do NOT use it on unauthorized networks or systems.
The author is not responsible for misuse or any damage caused.


# 👤 Author

    Developed by activex37b

  


