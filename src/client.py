from shared import *
import socket, sys, time, _thread

sock = None
def send(msg):
	global sock;
	success, attempts = False, 0
	while (not success and attempts < 16):
		try:
			if (sock.send(msg) != -1):
				success = True
			
			break
		except:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((addr, port))

			success = False
			attempts += 1

			print("[BAD] Error while sending to server.")
			time.sleep(.5 * attempts)
	
	if (attempts >= 16):
		print("[FATAL] Unable to send to server.")
		sys.exit(-1)

def listen():
	while (1):
		data = sock.recv(1024)
		if (not data): return print("INVALID MESSAGE RECIEVED. IGNORED")
		print(data.decode())

def close():
	send(b'e')
	sock.close()

def main():
	global sock;
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((addr, port))

	try:
		_thread.start_new_thread(listen, ())
		while (1):
			message = input('> ')
			if (message == ''):
				continue
			data = '{}{}'.format(remotes['message'], message).encode()
			send(data)

	except KeyboardInterrupt:
		close()
		return sys.exit(0)
	except Exception as e:
		close()
		return print(e)

	close()
	

if (__name__ == '__main__'): main()