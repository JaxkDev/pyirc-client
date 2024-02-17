import os.path
import json
from threading import Thread
from time import gmtime, strftime

from App.Connection.Server import Message, Server
from App.Interface.Window import Window

VERSION = "0.0.1"


class Application:
    def __init__(self):
        self.inbound_queue = []
        self.outbound_queue = []
        self.server = None
        self.thread = None
        self.preferences = None
        self.preferences_file = "preferences.json"
        self.window = Window(self)
        self.window.window.after(1, self.start)
        self.window.main_loop()
        self.exit()

    def start(self):
        self.window.insert_log("Application version: " + VERSION, "app_notice")
        self.load_preferences()

    def connect(self, server_id) -> None:
        if self.server is not None:
            self.window.insert_log("Already connected to server.", "app_error")
            return
        if self.preferences is None:
            self.window.insert_log("No preferences loaded, cannot connect to server.", "app_error")
            return

        self.window.insert_log("Connecting to server...", "app_notice")
        self.server = Server(self.outbound_queue, self.inbound_queue, self.preferences["servers"][server_id]["ip"],
                             self.preferences["servers"][server_id]["port"], self.preferences["user"]["nickname"],
                             self.preferences["user"]["username"], self.preferences["user"]["real_name"],
                             self.preferences["servers"][server_id]["password"])
        self.server.connect()
        self.thread = Thread(target=self.server.loop, name="Server-Thread")
        self.thread.start()

        self.window.window.after(20, self.tick)

        self.window.insert_log("Connected to server.", "app_notice")

    def tick(self):
        self.window.window.after(20, self.tick)
        while len(self.inbound_queue) > 0:
            message = self.inbound_queue.pop(0)
            if message.command == "PING":
                self.server.send(Message().build("PONG", [message.parameters[0]]))
                continue
            # TODO ServerHandler here.
            # TODO Handle message from server.
            timestamp = strftime("%H:%M:%S", gmtime())
            params = (" ".join(message.parameters)) if len(message.parameters) > 0 else ""
            self.window.insert_chat(f"{timestamp} | {message.command} > {params}", "chat")

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
        if validate_preferences(self.preferences):
            self.window.insert_log("Preferences are valid.", "app_notice")
            self.window.window.title("IRC Client - " + self.preferences["user"]["nickname"] + "!" + self.preferences["user"]["username"] + "@localhost" + " - v" + VERSION)
            if self.preferences["auto_connect"] is not None or str(self.preferences["auto_connect"]).lower() != "none":
                server_id = None
                for server in self.preferences["servers"].keys():
                    if self.preferences["servers"][server]["name"] == self.preferences["auto_connect"]:
                        server_id = server
                        break
                if server_id is not None:
                    self.connect(server_id)
                else:
                    self.window.insert_log("Auto-connect server was not found.", "app_error")
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

    def exit(self):
        self.window.quit()
        if self.server is not None:
            self.server.disconnect()
            self.thread.join()


def validate_preferences(preferences) -> bool:
    if type(preferences) is not dict:
        return False

    if len(preferences) != 3:
        return False
    if "auto_connect" not in preferences.keys():
        return False
    if "servers" not in preferences.keys():
        return False
    if "user" not in preferences.keys():
        return False

    servers = preferences["servers"]
    user = preferences["user"]

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
