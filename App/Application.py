import os.path
import json

from App.Connection.Server import Message
from App.Interface.Window import Window

VERSION = "0.0.1"


class Application:
    def __init__(self):
        self.server = None
        self.preferences = None
        self.window = Window(self)
        self.window.window.after(1, self.start)
        self.window.main_loop()

    def start(self):
        self.window.insert_log("Application version: " + VERSION, "app_notice")
        self.load_preferences()

    def connect(self):
        if self.server is not None:
            self.window.insert_log("Already connected to server.", "app_error")
            return
        if self.preferences is None:
            self.window.insert_log("No preferences loaded, cannot connect to server.", "app_error")
            return

    def handle_input(self, text):
        if self.server is None:
            self.window.insert_log("Not connected to server, cannot send messages", "app_error")
            return

        # todo channels
        self.server.send(Message().build("PRIVMSG", ["#ebooks", text]))
        self.window.insert_chat("> " + text)
        # TODO: Send to server/channel if connected.

    def handle_preferences(self, preferences):
        self.preferences = preferences
        self.save_preferences()

    def load_preferences(self):
        self.window.insert_log("Loading preferences...", "app_notice")
        if not os.path.exists("preferences.json"):
            file = open("preferences.json", "w")
            file.write("{}")
            file.close()
        file = open("preferences.json", "r")
        self.preferences = json.load(file)
        file.close()
        self.window.insert_log("Preferences loaded.", "app_notice")
        if self.validate_preferences():
            self.window.insert_log("Preferences are valid.", "app_notice")
        else:
            self.window.insert_log("Preferences are invalid.", "app_error")
            self.preferences = None
            self.window.open_preferences()

    def save_preferences(self):
        if self.preferences is None:
            self.window.insert_log("No preferences to save.", "app_error")
            return
        file = open("preferences.json", "w")
        json.dump(self.preferences, file)
        file.close()
        self.window.insert_log("Preferences saved to preferences.json", "app_notice")

    def validate_preferences(self):
        if self.preferences is not dict:
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

        if len(user) != 3:
            return False
        if "nickname" not in user.keys():
            return False
        if "real_name" not in user.keys():
            return False
        if "username" not in user.keys():
            return False

        if user["nickname"] is not str:
            return False
        if user["real_name"] is not str:
            return False
        if user["username"] is not str:
            return False

        if servers is not list:
            return False

        for server in servers:
            if len(server) != 4:
                return False

            if server[0] is not str:
                # Server Name
                return False
            if server[1] is not str:
                # Server Host/IP
                return False
            if server[2] is not int:
                # Server Port
                return False
            if server[3] is not str and server[3] is not None:
                # Server Password
                return False
