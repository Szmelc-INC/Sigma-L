import sys
import json
import os
import re
import webbrowser
from urllib.parse import urlparse, unquote
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QLineEdit, QPushButton, QMessageBox, QInputDialog, QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

from src.core import ChatThread
from src.commands import handle_command  # Import the modular commands


class Sigmal(QWidget):
    def __init__(self):
        super().__init__()

        # Load configurations
        self.config = self.load_config()

        self.setWindowTitle("Sigmal P2P Chat")
        self.setGeometry(
            300,
            300,
            self.config["window"]["width"],
            self.config["window"]["height"],
        )
        self.chat_thread = None
        self.chat_history = []
        self.is_host = False
        self.sound_enabled = self.config["sound"]["enabled"]

        # Initialize sounds
        self.init_sounds()

        # Main layout
        self.layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.anchorClicked.connect(self.handle_link_click)
        self.chat_display.setStyleSheet(
            f"background-color: {self.config['colors']['background']}; color: {self.config['colors']['text']};"
        )
        self.layout.addWidget(self.chat_display)

        # Message input field
        self.input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setStyleSheet(
            f"background-color: {self.config['colors']['input_background']}; color: {self.config['colors']['input_text']};"
        )
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)
        self.layout.addLayout(self.input_layout)

        # Set layout
        self.setLayout(self.layout)

        # Startup dialog
        self.show_startup_dialog()

    def load_config(self):
        """Load configuration from config.json or use defaults if not found or invalid."""
        default_config = {
            "window": {"width": 400, "height": 300},
            "colors": {
                "background": "#2b2b2b",
                "text": "#d3d3d3",
                "input_background": "#3c3c3c",
                "input_text": "#ffffff",
                "host_color": "red",
                "client_color": "cyan",
                "system_message_color": "lightgreen",
            },
            "nicknames": {"host": "[H] Host", "client": "[C] Client"},
            "sound": {
                "enabled": True,
                "volume": {"message": 0.5, "error": 0.8, "connection_lost": 0.8},
                "paths": {
                    "message": "sound/message_notification.wav",
                    "error": "sound/error_notification.wav",
                    "connection_lost": "sound/connection_lost.wav",
                },
            },
        }

        config_path = os.path.join(os.getcwd(), 'config.json')
        print(f"Looking for config file at: {config_path}")

        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                print("Config loaded successfully from config.json.")
                return config
        except FileNotFoundError:
            print("Config file not found. Using default settings.")
        except json.JSONDecodeError as e:
            print(f"Error decoding config.json: {e}. Using default settings.")
        
        return default_config

    def init_sounds(self):
        """Initialize sound effects."""
        self.message_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        self.connection_lost_sound = QSoundEffect()

        message_sound_path = self.config["sound"]["paths"]["message"]
        error_sound_path = self.config["sound"]["paths"]["error"]
        connection_lost_sound_path = self.config["sound"]["paths"]["connection_lost"]

        # Load sound files if they exist, otherwise print an error
        if os.path.exists(message_sound_path):
            self.message_sound.setSource(QUrl.fromLocalFile(message_sound_path))
        else:
            print(f"Sound file not found: {message_sound_path}")

        if os.path.exists(error_sound_path):
            self.error_sound.setSource(QUrl.fromLocalFile(error_sound_path))
        else:
            print(f"Sound file not found: {error_sound_path}")

        if os.path.exists(connection_lost_sound_path):
            self.connection_lost_sound.setSource(QUrl.fromLocalFile(connection_lost_sound_path))
        else:
            print(f"Sound file not found: {connection_lost_sound_path}")

        # Set volume from config if sound files are loaded
        if self.message_sound.source():
            self.message_sound.setVolume(self.config["sound"]["volume"]["message"])
        if self.error_sound.source():
            self.error_sound.setVolume(self.config["sound"]["volume"]["error"])
        if self.connection_lost_sound.source():
            self.connection_lost_sound.setVolume(self.config["sound"]["volume"]["connection_lost"])

    def show_startup_dialog(self):
        choice = QMessageBox.question(
            self,
            "Sigmal Startup",
            "Would you like to Host (Yes) or Join (No) a session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if choice == QMessageBox.StandardButton.Yes:
            self.is_host = True
            self.nickname = self.config["nicknames"]["host"]  # Set host nickname
            self.message_color = self.config["colors"]["host_color"]
            port, ok = QInputDialog.getInt(self, "Sigmal Host", "Enter port to host on:", 2137, 1024, 65535)
            if ok:
                self.chat_thread = ChatThread(host_mode=True, port=port)
                self.chat_thread.new_message.connect(self.display_message)
                self.chat_thread.connection_lost.connect(self.handle_connection_lost)
                self.chat_thread.file_received.connect(self.handle_file_received)
                self.chat_thread.start()
                self.display_message(f"Hosting chat on port {port}...", self.config['colors']['system_message_color'])
            else:
                self.close()
        elif choice == QMessageBox.StandardButton.No:
            self.is_host = False
            self.nickname = self.config["nicknames"]["client"]  # Set client nickname
            self.message_color = self.config["colors"]["client_color"]
            ip, ok = QInputDialog.getText(self, "Sigmal Join", "Enter host IP:")
            if ok:
                port, ok = QInputDialog.getInt(self, "Sigmal Join", "Enter host port:", 2137, 1024, 65535)
                if ok:
                    self.chat_thread = ChatThread(host_mode=False, ip=ip, port=port)
                    self.chat_thread.new_message.connect(self.display_message)
                    self.chat_thread.connection_lost.connect(self.handle_connection_lost)
                    self.chat_thread.file_received.connect(self.handle_file_received)
                    self.chat_thread.start()
                    self.display_message(f"Attempting to join chat at {ip}:{port}...", self.config['colors']['system_message_color'])
                else:
                    self.close()
            else:
                self.close()
        else:
            self.close()

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            if message.startswith('/'):
                handle_command(self, message)
            else:
                # Automatically detect URLs and format them
                formatted_message = self.make_urls_clickable(message)
                message_with_color = f"{self.nickname}: {formatted_message}|COLOR={self.message_color}"
                self.chat_thread.send_message(message_with_color)
                self.display_message(f"{self.nickname}: {formatted_message}", self.message_color, is_html=True)
                self.chat_history.append(f"{self.nickname}: {formatted_message}")
            self.message_input.clear()

    def save_chat_history(self):
        """Save the chat history to a log file."""
        try:
            # Ensure the 'logs' directory exists
            os.makedirs('logs', exist_ok=True)

            # Generate a unique log file name based on the current date and time
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            log_filename = f'logs/log-{timestamp}.txt'

            # Save chat history to the log file
            with open(log_filename, 'w') as log_file:
                log_file.write("\n".join(self.chat_history))

            self.display_message(f"Chat history saved to {log_filename}.", self.config['colors']['system_message_color'])
        except Exception as e:
            self.display_message(f"Error saving chat history: {e}", "red")

    def apply_config(self):
        """Apply the loaded configuration."""
        self.setGeometry(
            300,
            300,
            self.config["window"]["width"],
            self.config["window"]["height"],
        )
        self.sound_enabled = self.config["sound"]["enabled"]
        self.chat_display.setStyleSheet(
            f"background-color: {self.config['colors']['background']}; color: {self.config['colors']['text']};"
        )

    def display_message(self, message, color="white", is_html=False):
        if "|COLOR=" in message:
            parts = message.split("|COLOR=")
            message = parts[0]
            color = parts[1].strip() if len(parts) > 1 else color

        # Apply color and format for display
        colored_message = f'<span style="color:{color}">{message}</span>'
        self.chat_display.insertHtml(colored_message + "<br>")
        self.chat_history.append(message)

        # Play sound if a new message is received and sound is enabled
        if "Connected" not in message and self.sound_enabled:
            self.message_sound.play()

    def handle_file_received(self, file_path, filename):
        """Handle a received file and display a download link."""
        download_link = f'<a href="download://{filename}|{file_path}" download="{filename}">Download {filename}</a>'
        self.display_message(f"File received: {download_link}", self.config['colors']['system_message_color'])

    def handle_link_click(self, url):
        """Handle link clicks manually to prevent chat clearing."""
        if url.scheme() == "download":
            # Extract filename and size from URL
            parsed_url = urlparse(url.toString())
            filename, filesize = parsed_url.path.split('|')
            filename = unquote(filename)
            filesize = int(filesize)
            self.chat_thread.receive_file(filename, filesize)
        elif url.isValid():
            webbrowser.open(url.toString())
        return

    def make_urls_clickable(self, text):
        url_regex = r'(https?://\S+)'
        return re.sub(url_regex, r'<a href="\1" title="\1">\1</a>', text)

    def handle_connection_lost(self):
        self.display_message("Connection lost.", self.config['colors']['system_message_color'])
        if self.sound_enabled:
            self.connection_lost_sound.play()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode on and off."""
        if self.isFullScreen():
            self.showNormal()
            self.display_message("Exited fullscreen mode.", self.config['colors']['system_message_color'])
        else:
            self.showFullScreen()
            self.display_message("Entered fullscreen mode.", self.config['colors']['system_message_color'])


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = Sigmal()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
