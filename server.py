import http.server
import socketserver
import threading
import tkinter as tk
from tkinter import messagebox
import os
from urllib.parse import urlparse, parse_qs

PORT = 8080
SERVER_DIR = "catapult_server"
# ANSI colors
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"


banner_ascii = f""" {RED}                                              
                     @@@@@@@@@@@@                     
                @@@@@@@@@@@@@@@@@@@@@@                
             @@@@@@@@@@@@@@@@@@@@@@@@@@@@             
           @@@@@@@  @@@@@@@@@@@@@@  @@@@@@@           
          @@@          @@@@@@@@          @@@          
         @@@            @@@@@@            @@@         
        @@@@           @@@@@@@@           @@@@        
       @@@@@           @@@@@@@@           @@@@@       
       @@@@@@       @@@@@    @@@@@       @@@@@@       
      @@@@@@@@@@@@@@@@@@      @@@@@@@@@@@@@@@@@@      
   @@@@@@@@@@ @@@@@@@            @@@@@@@ @@@@@@@@@@   
  @@@@@@@@@@                              @@@@@@@@@@  
  @@@@@@@@@@        @@@@      @@@@        @@@@@@@@@@  
  @@@@@@@@@@       @@@@@      @@@@@       @@@@@@@@@@  
  @@@@@@@@@@       @@@@@      @@@@@       @@@@@@@@@@  
  @@@@@@@@@@       @@@@@      @@@@@       @@@@@@@@@@         {CYAN}{BOLD} Gh0stCourier  V. 1.0.0                                                                       
      @@@@@@@@@                        @@@@@@@@@              
          @@@@@@@@@@              @@@@@@@@@@          
              @@@@@@@@@@@@@@@@@@@@@@@@@@@             
                     @@@@@@@@@@@@@  

    {GREEN}[+]{RESET} {BOLD}[+] Gh0stCourier —: Situational Awareness Utility for file upload and download server 
        for red engagements and Adversary Emulation.
    {GREEN}[+]{RESET}[+] This tool prevents your exploits and Cyber Offensive Weapons from being detect and analysed 
    from threat intelligence and SOC tier analyst.

        developed by {YELLOW}David Boakye Kessie{RESET}    
    {BLUE}https://github.com/activex37b/Gh0stCourier{RESET} By activex37b     
                                                                                                                  """

# Store queued tasks per token: { token: [ "upload filename", ... ] }
tasks = {}

class UploadHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/request_token":
            token_list = qs.get("token", [])
            token = token_list[0] if token_list else None

            if not token:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing token parameter")
                return

            # If there is a queued task for this token, pop and handle it
            if token in tasks and tasks[token]:
                task = tasks[token].pop(0)  # FIFO
                # If the task requires operator approval, prompt now
                if task.startswith("upload "):
                    filename = task.split(" ", 1)[1]
                    # Ask operator
                    approved = self.ask_user(filename, token)
                    if approved:
                        # Send the task string to the client (client should then call /download)
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(task.encode())
                        print(f"[+] Approved task sent to {token}: {task}")
                    else:
                        # Denied -> inform client, log, and discard the task
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b"[!] Transfer denied by operator")
                        print(f"[-] Denied task for {token}: {task}")
                else:
                    # Other tasks (if any) are sent directly
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(task.encode())
                    print(f"[+] Task sent to {token}: {task}")
            else:
                # No task for this token
                self.send_response(204)
                self.end_headers()

        elif path == "/list":
            self.send_list()

        elif path == "/download":
            file_list = qs.get("file", [])
            filename = file_list[0] if file_list else None
            if not filename:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing file parameter")
                return
            self.send_file(filename)

        else:
            self.send_response(404)
            self.end_headers()

    def ask_user(self, filename, token):
        """Prompt operator with a Yes/No box before allowing transfer."""
        # Use a small Tk popup; ensure it doesn't create a persistent root window
        root = tk.Tk()
        root.withdraw()
        msg = f"Client token: {token}\nRequests file: {filename}\n\nAllow transfer?"
        answer = messagebox.askyesno("File Transfer Request", msg)
        root.destroy()
        return answer

    def log_message(self, format, *args):
        # silence default logging
        return

    def send_list(self):
        try:
            files = os.listdir(SERVER_DIR)
            file_list = "\n".join(files) if files else "[!] No files in directory."
            self.send_response(200)
            self.end_headers()
            self.wfile.write(file_list.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

    def send_file(self, filename):
        file_path = os.path.join(SERVER_DIR, filename)
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"[!] File not found")
            print(f"[-] File not found for download request: {filename}")
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(data)
                print(f"[+] Served file to client: {filename}")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
            print(f"[!] Error serving file {filename}: {e}")


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def server_thread(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass



def print_command_menu():
    menu = f"""
{CYAN}{BOLD}================= Command Menu ================={RESET}

  {YELLOW}list{RESET}      - List files in server directory
  {YELLOW}upload{RESET}    - Queue file upload to client
              usage: upload <filename> <token>
  {YELLOW}exit{RESET}      - Shut down the server

{CYAN}================================================{RESET}
"""
    print(menu)





def start_server():
    os.makedirs(SERVER_DIR, exist_ok=True)
    with ThreadingTCPServer(("", PORT), UploadHandler) as httpd:
        print(banner_ascii)
        print(f"[*] Gh0stCourier started on port {PORT}")
        print_command_menu()

        t = threading.Thread(target=server_thread, args=(httpd,), daemon=True)
        t.start()

        # Command loop
        while True:
            try:
                cmd = input("Gh0stC0urier> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "list":
                    files = os.listdir(SERVER_DIR)
                    if files:
                        for f in files:
                            print("  -", f)
                    else:
                        print("[!] No files in directory.")

                elif cmd[0] == "upload":
                    if len(cmd) < 3:
                        print("[!] Usage: upload <filename> <token>")
                        continue
                    filename, token = cmd[1], cmd[2]
                    if not os.path.exists(os.path.join(SERVER_DIR, filename)):
                        print("[!] File not found in server directory.")
                        continue
                    tasks.setdefault(token, []).append(f"upload {filename}")
                    print(f"[+] Task queued: send {filename} to {token}")

                elif cmd[0] == "exit":
                    print("[!] Shutting down server...")
                    httpd.shutdown()
                    break

                else:
                    print("[!] Unknown command.")

            except KeyboardInterrupt:
                print("\n[!] Shutting down server...")
                httpd.shutdown()
                break


if __name__ == "__main__":
    start_server() 