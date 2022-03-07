from shared import *
from datetime import datetime
import socket, sys, _thread

active_clients = dict()

def disconnect_client(kick_reason, info):
	if (kick_reason != 0):
		for k in active_clients:
			if (active_clients[k]['client'] != info['client']):
				try:
					active_clients[k]['client'].send(
						'[KICK] {}: client {} ({}) has been kicked from the server: {}'.format(
							datetime.now().strftime('%H:%M'),
							info['name'],
							info['index'],
							kick_reason
						).encode()
					)
				except Exception as e:
					print('Unable to send data to {}: {}'.format(k, e))
	else:
		for k in active_clients:
			if (active_clients[k]['client'] != info['client']):
				try:
					active_clients[k]['client'].send(
						'[LEAVE] {}: client {} ({}) has left the server'.format(
							datetime.now().strftime('%H:%M'),
							info['name'],
							info['index']
						).encode()
					)
				except Exception as e:
					print('Unable to send data to {}: {}'.format(k, e))

	active_clients.pop(info['index'])
	info['client'].close()
	_thread.exit()

def listen_client(info):
	while (1):
		data = info['client'].recv(1026).decode()
		if (data == 'e'):
			return disconnect_client(0, info)
		if (not data or len(data) <= 3): disconnect_client(0 if len(data) > 3 else 'illegal message', info)

		identifier, message = data[:2], data[2:]
		if (len(message) <= 0 or not identifier in remotes.values()):
			disconnect_client('illegal message', info)

		if (identifier == remotes['message']):
			for k in active_clients:
				if (active_clients[k]['client'] != info['client']):
					try:
						active_clients[k]['client'].send(
							'{} ({}) {}: {}'.format(info['index'], datetime.now().strftime('%H:%M'), info['name'], message).encode()
						)
					except Exception as e:
						print('Unable to send data to {}: {}'.format(k, e))

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	sock.bind((addr, port))
	sock.listen(10)

	try:
		while (1):
			client, client_addr = sock.accept()
			client_ip = client_addr[0]
			client_if = {
				'client': client,
				'name': socket.getfqdn(client_ip) + ':' + str(client_addr[1]),
				'ipv4': client_ip,
				'addr': client_addr,
				'index': ':'.join([client_addr[0], str(client_addr[1])])
			}

			for k in active_clients:
				if (active_clients[k]['client'] != client):
					active_clients[k]['client'].send(
						'[JOIN] {}:({}:{}) has joined the server.'.format(client_if['name'], client_if['ipv4'], client_addr[1]).encode()
					)

			active_clients[client_if['index']] = client_if

			_thread.start_new_thread(listen_client, (client_if,))
		
	except KeyboardInterrupt:
		return sys.exit(0)

if (__name__ == '__main__'): main()