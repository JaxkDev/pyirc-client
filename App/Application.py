import os.path
import json

from App.Connection.Server import Message
from App.Interface.Window import Window

VERSION = "0.0.1"


class Application:
    def __init__(self):
        self.server = None
        self.preferences = None
        self.preferences_file = "preferences.json"
        self.window = Window(self)
        self.window.window.after(1, self.start)
        self.window.main_loop()

    def start(self):
        self.window.insert_log("Application version: " + VERSION, "app_notice")
        self.load_preferences()

    def connect(self, server) -> None:
        if self.server is not None:
            self.window.insert_log("Already connected to server.", "app_error")
            return
        if self.preferences is None:
            self.window.insert_log("No preferences loaded, cannot connect to server.", "app_error")
            return

        self.window.insert_log("Connecting to server...", "app_notice")
        #TODO: Connect to server.

    def handle_input(self, text):
        if self.server is None:
            self.window.insert_log("Not connected to server, cannot send messages", "app_error")
            return

        # todo channels
        self.server.send(Message().build("PRIVMSG", ["#ebooks", text]))
        self.window.insert_chat("> " + text)
        # TODO: Send to server/channel if connected.

    def load_preferences(self, file="preferences.json") -> None:
        self.window.insert_log("Loading preferences...", "app_notice")
        if not os.path.exists(file) and file == "preferences.json":
            file = open("preferences.json", "w")
            file.write("{}")
            file.close()
        elif not os.path.exists(file):
            self.window.insert_log("No preferences file found at '" + file + "'", "app_error")
            return
        file = open("preferences.json", "r")
        self.preferences_file = file
        self.preferences = json.load(file)
        file.close()
        self.window.insert_log("Preferences loaded.", "app_notice")
        if self.validate_preferences():
            self.window.insert_log("Preferences are valid.", "app_notice")
            self.window.window.title("IRC Client - " + self.preferences["user"]["nickname"] + "!" + self.preferences["user"]["username"] + "@localhost" + " - v" + VERSION)
            if self.preferences["auto_connect"] is not None or str(self.preferences["auto_connect"]).lower() != "none":
                self.connect(self.preferences["auto_connect"])
        else:
            self.window.insert_log("Preferences are invalid.", "app_error")
            # TODO Default.
            self.preferences = None
            self.window.open_preferences()

    def save_preferences(self, file=None) -> None:
        if self.preferences is None:
            self.window.insert_log("No preferences to save.", "app_error")
            return
        self.preferences_file = file if file is not None else self.preferences_file
        file = open(self.preferences_file, "w")
        json.dump(self.preferences, file, indent=4)
        file.close()
        self.window.insert_log(
            "Preferences saved to '" + self.preferences_file + "'",
            "app_notice")

    def validate_preferences(self) -> bool:
        if type(self.preferences) is not dict:
            return False

        if len(self.preferences) != 3:
            return False
        if "auto_connect" not in self.preferences.keys():
            return False
        if "servers" not in self.preferences.keys():
            return False
        if "user" not in self.preferences.keys():
            return False

        servers = self.preferences["servers"]
        user = self.preferences["user"]

        if len(user.keys()) != 3:
            return False
        if "nickname" not in user.keys():
            return False
        if "real_name" not in user.keys():
            return False
        if "username" not in user.keys():
            return False

        if type(user["nickname"]) is not str:
            return False
        if type(user["real_name"]) is not str:
            return False
        if type(user["username"]) is not str:
            return False

        if type(servers) is not dict:
            return False

        for server_id in servers.keys():
            server = servers[server_id]
            if type(server) is not dict:
                return False

            if len(server.keys()) != 4:
                return False

            if type(server["name"]) is not str:
                # Server Name
                return False
            if type(server["ip"]) is not str:
                # Server Host/IP
                return False
            if type(server["port"]) is not int:
                # Server Port
                return False
            if type(server["password"]) is not str and server["password"] is not None:
                # Server Password
                return False

        return True
