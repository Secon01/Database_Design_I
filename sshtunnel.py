import paramiko
import socket
import select
import threading
from multiprocessing import Process, Event

class SSHTunnel:
	"""SSH Tunnel manager with start/stop interface"""

	def __init__(self, ssh_username, ssh_password, host, port):
		self.ssh_username = ssh_username
		self.ssh_password = ssh_password
		self.host = host
		self.port = port

		self.local_port = None
		self.local_host = None

		self.tunnel_opened = Event()
		self.close_tunnel = Event()
		self.client = None
		self.forward_thread = None

	def _pipe(self, src, dst):
		"""Copy data both ways between sockets"""
		try:
			while True:
				r, w, x = select.select([src, dst], [], [])
				if src in r:
					data = src.recv(1024)
					if len(data) == 0:
						break
					dst.sendall(data)
				if dst in r:
					data = dst.recv(1024)
					if len(data) == 0:
						break
					src.sendall(data)
		finally:
			try:
				src.close()
			except EOFError:
				pass
			try:
				dst.close()
			except EOFError:
				pass

	def _forward_tunnel(self, local_host, local_port, remote_host, remote_port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((local_host, local_port))
		self.local_host, self.local_port = sock.getsockname()
		sock.settimeout(1.0)
		sock.listen(2)

		self.tunnel_opened.set()

		while not self.close_tunnel.is_set():
			try:
				client, addr = sock.accept()
				chan = self.client.get_transport().open_channel(
					"direct-tcpip",
					(remote_host, remote_port),
					client.getsockname()
				)
				threading.Thread(target=self._pipe, args=(client, chan), daemon=True).start()
			except socket.timeout:
				continue

		sock.close()

	def _run_tunnel(self, local_host, local_port, remote_host, remote_port):
		# Connect SSH
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(
			hostname=self.host,
			port=self.port,
			username=self.ssh_username,
			password=self.ssh_password
		)

		# Start forwarding
		self._forward_tunnel(local_host, local_port, remote_host, remote_port)

		# Clean up
		self.client.close()

	def start(self, local_host, local_port, remote_host, remote_port):
		"""Start the SSH tunnel in a separate process"""
		self.process = Process(target=self._run_tunnel,
							   args=(local_host, local_port, remote_host, remote_port))
		self.process.start()
		self.tunnel_opened.wait()  # Wait until tunnel is ready

	def stop(self):
		"""Stop the tunnel"""
		self.close_tunnel.set()
		self.process.join()
