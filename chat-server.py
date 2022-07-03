import socket
import threading


def init_server(host_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(host_port)
    server.listen(100)
    print(f'Server running at {host_port[0]}, port {host_port[1]}')
    return server


def first_shake(client, user_names, user_clients):
    data = ""

    while not data.endswith("\n"):
        data += client.recv(2).decode('utf-8')

    if not data.startswith('HELLO-FROM '):
        client.sendall('BAD-RQST-HDR\n'.encode('utf-8'))
    elif data.startswith('HELLO-FROM '):
        if len(user_names) >= 100:
            client.sendall('BUSY\n'.encode('utf-8'))
        else:
            user_name = data.split()[1]
            if user_name in user_names:
                client.sendall('IN-USE\n'.encode('utf-8'))
                first_shake(client, user_names, user_clients)
            else:
                user_names.append(user_name)
                user_clients.append(client)
                response = 'HELLO'+' '+user_name+'\n'
                client.sendall(response.encode('utf-8'))
    
    return user_name, user_names, user_clients


def who(client, user_names):
    names = ','.join(user_names)
    response = f'WHO-OK {names}\n'
    client.sendall(response.encode('utf-8'))
    return


def send_message(data, client, user_clients, user_names):
    if len(data.split()) <= 2:
        client.sendall('BAD-RQST-BODY\n'.encode('utf-8'))
        return
    else:
        data_split = data.split(" ", 2)
        destinationUser = data_split[1]
        if destinationUser in user_names:
            senderIndex = user_clients.index(client)
            senderName = user_names[senderIndex]
            indexOfDestinationUser = user_names.index(destinationUser)
            destinationClient = user_clients[indexOfDestinationUser]
            response = 'DELIVERY'+' '+senderName+' '+data_split[2]+'\n'
            destinationClient.sendall(response.encode('utf-8'))
            client.sendall('SEND-OK\n'.encode('utf-8'))
        else:
            client.sendall('UNKNOWN\n'.encode('utf-8'))
        return


def intercommunication(client, user_name, user_names, user_clients):
    while True:
        try:
            data = ''
            while not data.endswith("\n"):
                data += client.recv(2).decode('utf-8')
                if data == '':
                    user_names.remove(user_name)
                    user_clients.remove(client)
                    return

            if data.startswith('WHO\n'):
                who(client, user_names)
            elif data.startswith('SEND '):
                send_message(data, client, user_clients, user_names)
            else:
                client.sendall('BAD-RQST-HDR\n'.encode('utf-8'))

        except:
            user_names.remove(user_name)
            user_clients.remove(client)
            break


def main():
    host_port = ("127.0.0.1", 4005)
    user_names = []
    user_clients = []

    server = init_server(host_port)

    while 1:
        client, address = server.accept()
        user_name, user_names, user_clients = first_shake(
            client, user_names, user_clients)
        thread = threading.Thread(
            target=intercommunication, args=(client, user_name, user_names, user_clients))
        thread.start()


if __name__ == "__main__":
    main()