import threading
import socket
from datetime import datetime

def time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# first connection to the server
def first_handshake():
    while 1:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data = ''
        # make constants for the connection
        # SERVER =  '143.47.184.219' 
        # PORT = 5378  

        SERVER = "127.0.0.1"  
        PORT = 4005

        # connect to the server
        address = (SERVER, PORT)
        client.connect(address)

        current_time = time()
        name = input(f"{current_time}| Please enter your username: ")
        username = f"{'HELLO-FROM'} {name}\n"
        username_encoded = username.encode('utf-8')
        client.sendall(username_encoded)
        while not data.endswith("\n"):
            data += client.recv(2).decode('utf-8')
        if len(data.split(" ")) > 1:
            msg_start = data.split(" ")[0]
        else:
            msg_start = data
        current_time = time()
        if msg_start == 'IN-USE\n':
            print('Chosen username is already in use, try to use different one!')
            continue
        elif msg_start == 'BUSY\n':
            print(f'{current_time}| Sorry, the server is currently full, please try again later!')
            break
        else:
            print(f"{current_time}| Server greets {name}!!!")
            print(f"{current_time}| You can now start sending messages...")
            break
    return name, msg_start, client

def receive_decode_protocol(message):
    msg_start = ''

    if len(message.split(" ")) > 1:
        msg_start = message.split(" ")[0]
        msg_end = message.split(" ")[1::]

    current_time = time()
    # if server sent us something more than a header
    if msg_start != '':
        if msg_start == 'WHO-OK':
            msg_end = msg_end[0]
            print(f"{current_time}| Current users are: {msg_end}")
        elif msg_start == 'DELIVERY':
            print(f'{current_time}| Message recieved from {msg_end[0]}:')
            if len(msg_end[1::]) == 1:
                print(f'{current_time}| {msg_end[1]}')
            else:
                msg_end = ' '.join(msg_end[1::])
                print(f'{current_time}| {msg_end}')
    # server has sent only a header
    else:
        if message == 'SEND-OK\n':
            print(f'{current_time}| Message was sent successfully')
        elif message == 'UNKNOWN\n':
            print(f"{current_time}| User you've tried to send a message to a user that isn't currently online!")
            print(f'{current_time}| Please send the message again to a valid user!')
        elif message == 'BAD-RQST-HDR\n':
            print(f'{current_time}| Note to the programmer: You have messed the header up!')
        elif message == 'BAD-RQST-BODY\n':
            print(f'{current_time}| There is an error with the message you are trying to send!')
            print(f'{current_time}| Please try again!')

def receive(client, FORMAT):
    global running
    while running:
        data = ''
        while running and not data.endswith("\n"):
            data += client.recv(2).decode(FORMAT)
        print()
        receive_decode_protocol(data)

def who(client, FORMAT):
    message = 'WHO\n'
    message_encoded = message.encode(FORMAT)
    client.sendall(message_encoded)
    return

def send_message(client, FORMAT, user, message):
    message = ' '.join(message)
    msg = f'SEND {user} {message}\n'
    message_encoded = msg.encode(FORMAT)
    client.sendall(message_encoded)
    return

def send(client, FORMAT, name):
    global running
    while running:
        current_time = time()
        msg = input(f'{current_time}| {name} > ')
        if msg == '!quit':
            print(f'{current_time}| Goodbye!')
            running = False
            return
        elif msg == '!who':
            who(client, FORMAT)
        elif len(msg) > 0:
            if msg[0] == "@":
                msg = msg.split()
                msg[0] = msg[0][1::]
                send_message(client, FORMAT, msg[0], msg[1::])

def main():
    global running
    running = True
    FORMAT = 'utf-8'
    name, msg_start, client = first_handshake()
    if (msg_start == 'BUSY\n'):
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        return

    t = threading.Thread(target=receive, args=(client, FORMAT,))
    t.start()
    send(client, FORMAT, name)

    client.shutdown(socket.SHUT_RDWR)
    client.close()
    t.join()

if __name__ == "__main__":
    main()