import socket
import os
from PyQt5.QtCore import QThread, pyqtSignal


class ChatThread(QThread):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()
    file_received = pyqtSignal(str, str)  # Signal for file reception with file path and name

    def __init__(self, host_mode=False, ip=None, port=2137):
        super().__init__()
        self.host_mode = host_mode
        self.ip = ip
        self.port = port
        self.sock = None
        self.conn = None
        self.running = True
        self.private_key = None
        self.public_key = None
        self.remote_public_key = None
        self.generate_keys()

    def generate_keys(self):
        """Generate RSA key pair."""
        from src.cipher import generate_key_pair

        self.private_key, self.public_key = generate_key_pair()

    def run(self):
        from src.cipher import serialize_key, deserialize_key

        if self.host_mode:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind(("", self.port))
                self.sock.listen(1)
                self.new_message.emit(f"Listening on port {self.port}...")
                self.conn, addr = self.sock.accept()
                self.new_message.emit(f"Connected by {addr}")

                # Exchange keys
                self.conn.sendall(serialize_key(self.public_key))
                remote_key_data = self.conn.recv(1024)
                self.remote_public_key = deserialize_key(remote_key_data)

                while self.running:
                    if self.conn is None:
                        self.connection_lost.emit()
                        break
                    data = self.conn.recv(4096)
                    if not data:
                        self.connection_lost.emit()
                        break
                    self.process_received_data(data)
            except OSError as e:
                if e.errno == 98:
                    self.new_message.emit(f"Port {self.port} already in use. Please restart and try a different port.")
                else:
                    self.new_message.emit(f"Error: {e}")
            except Exception as e:
                self.new_message.emit(f"Error: {e}")
                self.connection_lost.emit()
        else:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.ip, self.port))
                self.new_message.emit(f"Connected to {self.ip}:{self.port}")

                # Exchange keys
                remote_key_data = self.sock.recv(1024)
                self.remote_public_key = deserialize_key(remote_key_data)
                self.sock.sendall(serialize_key(self.public_key))

                while self.running:
                    if self.sock is None:
                        self.connection_lost.emit()
                        break
                    data = self.sock.recv(4096)
                    if not data:
                        self.connection_lost.emit()
                        break
                    self.process_received_data(data)
            except ConnectionRefusedError:
                self.new_message.emit("Failed to connect. Server might be down.")
            except Exception as e:
                self.new_message.emit(f"Error: {e}")
                self.connection_lost.emit()

    def process_received_data(self, data):
        """Process incoming data for message or file."""
        from src.cipher import decrypt_message

        try:
            if data.startswith(b"<File>"):
                # Handle file reception
                metadata, file_size = data.decode("utf-8").split()[1:3]
                self.receive_file(metadata, int(file_size))
            else:
                # Decode the JSON structure
                decrypted_message = decrypt_message(data.decode('utf-8'), self.private_key)
                self.new_message.emit(decrypted_message)
        except ValueError as ve:
            self.new_message.emit(f"Decryption error: Incorrect padding or corrupted data. {ve}")
        except Exception as e:
            self.new_message.emit(f"Error processing data: {e}")

    def receive_file(self, filename, filesize):
        """Receive a file from the socket and save it to the transfer folder."""
        transfer_folder = "transfer"
        os.makedirs(transfer_folder, exist_ok=True)  # Ensure the transfer folder exists
        file_path = os.path.join(transfer_folder, filename)

        with open(file_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                if self.conn:
                    chunk = self.conn.recv(min(remaining, 4096))
                else:
                    chunk = self.sock.recv(min(remaining, 4096))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        self.file_received.emit(file_path, filename)  # Signal that the file has been received
        self.new_message.emit(f"Downloaded {filename} ({filesize} bytes) to {transfer_folder}")

    def send_message(self, message):
        from src.cipher import encrypt_message

        try:
            full_message = encrypt_message(message, self.remote_public_key).encode('utf-8')
            
            if self.host_mode and self.conn:
                self.conn.sendall(full_message)
            elif self.sock:
                self.sock.sendall(full_message)
        except BrokenPipeError:
            self.new_message.emit("Connection lost. Unable to send message.")
        except Exception as e:
            self.new_message.emit(f"Error sending message: {e}")

    def send_file(self, filepath):
        """Send a file over the socket without encryption."""
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        file_header = f"<File> {filename} {filesize}".encode("utf-8")
        try:
            if self.host_mode and self.conn:
                self.conn.sendall(file_header)
                with open(filepath, "rb") as f:
                    while chunk := f.read(4096):
                        self.conn.sendall(chunk)
            elif self.sock:
                self.sock.sendall(file_header)
                with open(filepath, "rb") as f:
                    while chunk := f.read(4096):
                        self.sock.sendall(chunk)
        except Exception as e:
            self.new_message.emit(f"Error sending file: {e}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        if self.conn:
            self.conn.close()
        self.quit()
