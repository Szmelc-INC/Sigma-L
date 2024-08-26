# src/commands.py

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QFileDialog  # Ensure QFileDialog is imported
from src.core import ChatThread  # Ensure QFileDialog is imported
# Other necessary imports if there are any

def handle_command(app, command):
    """Handle user commands."""
    if command == "/clear":
        app.chat_display.clear()
    elif command == "/exit":
        app.close()
    elif command == "/save":
        app.save_chat_history()
    elif command == "/help":
        help_message = (
            "Available commands:\n"
            "/clear - Clear the chat screen\n"
            "/exit - Exit the application\n"
            "/save - Save chat history to a log file\n"
            "/help - Display this help message\n"
            "/reload config - Reload configuration from config.json\n"
            "/reconnect - Reconnect to the current session\n"
            "/nick <new_nickname> - Change your nickname\n"
            "/color <#HEX> - Change your text color\n"
            "/toggle sound - Toggle sound on/off\n"
            "/transfer - Open file selection to send a file\n"
            "/fullscreen - Toggle fullscreen mode on/off\n"  # Added fullscreen command
        )
        app.display_message(help_message, app.config['colors']['system_message_color'])
    elif command == "/reload config":
        reload_config(app)
    elif command == "/reconnect":
        reconnect_session(app)
    elif command.startswith("/nick "):
        new_nick = command.split(" ", 1)[1].strip()
        change_nickname(app, new_nick)
    elif command.startswith("/color "):
        new_color = command.split(" ", 1)[1].strip()
        change_color(app, new_color)
    elif command.startswith("/toggle "):
        option = command.split(" ", 1)[1].strip()
        toggle_option(app, option)
    elif command == "/fullscreen":  # Handle fullscreen command
        app.toggle_fullscreen()
    elif command == "/transfer":
        open_file_dialog(app)
    else:
        app.display_message(f"Unknown command: {command}", "red")


def reload_config(app):
    """Reload configuration from config.json."""
    app.config = app.load_config()
    app.display_message("Configuration reloaded from config.json.", app.config['colors']['system_message_color'])
    app.apply_config()


def reconnect_session(app):
    """Reconnect to the current session."""
    app.display_message("Reconnecting...", app.config['colors']['system_message_color'])
    if app.chat_thread:
        app.chat_thread.stop()
    if app.is_host:
        port = app.chat_thread.port
        app.chat_thread = ChatThread(host_mode=True, port=port)
    else:
        ip = app.chat_thread.ip
        port = app.chat_thread.port
        app.chat_thread = ChatThread(host_mode=False, ip=ip, port=port)
    app.chat_thread.new_message.connect(app.display_message)
    app.chat_thread.connection_lost.connect(app.handle_connection_lost)
    app.chat_thread.file_received.connect(app.handle_file_received)
    app.chat_thread.start()


def change_nickname(app, new_nick):
    """Change the user's nickname."""
    app.nickname = new_nick
    app.display_message(f"Nickname changed to {new_nick}.", app.config['colors']['system_message_color'])


def change_color(app, new_color):
    """Change the user's message color."""
    app.message_color = new_color
    app.display_message(f"Message color changed to {new_color}.", app.config['colors']['system_message_color'])


def toggle_option(app, option):
    """Toggle a given option (e.g., sound)."""
    if option == "sound":
        app.sound_enabled = not app.sound_enabled
        state = "enabled" if app.sound_enabled else "disabled"
        app.display_message(f"Sound {state}.", app.config['colors']['system_message_color'])
    else:
        app.display_message(f"Unknown toggle option: {option}", "red")


def open_file_dialog(app):
    """Open a file dialog to select a file for transfer."""
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(app, "Select File to Transfer", "", "All Files (*);;Text Files (*.txt)", options=options)
    if file_path:
        app.chat_thread.send_file(file_path)
