from tkinter import Tk, END, StringVar, Menu, Toplevel, Listbox, Variable
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.ttk import Notebook, Frame, Button, OptionMenu, Label, Entry
from tkinter.scrolledtext import ScrolledText
from webbrowser import open_new as open_url


class Window:
    def __init__(self, application):
        self.top = True
        self.app = application
        self.window = Tk("  PY-IRC Client", "PY-IRC Client", "PY-IRC Client")
        self.window.geometry('800x700')
        self.window.minsize(800, 700)
        self.window.title("-- Not logged in --")

        self.chat_box = ScrolledText(self.window, background="#555555", font='Arial 12 bold', border=2, relief="solid",
                                     inactiveselectbackground="black")
        # TODO Sort out height based on font and pixel and yeah lot of messy stuff.
        self.chat_box.vbar.forget()

        self.input_var = StringVar()
        self.input_entry = Entry(self.window, textvariable=self.input_var, font='Arial 12 bold',
                                 background="white", foreground="black")
        self.input_entry.focus()
        self.input_entry.configure(state="readonly")
        # TEMP
        self.input_entry.configure(state="normal")
        self.input_entry.bind("<Return>",
                              lambda e: self.app.handle_input(self.input_var.get()) or self.input_var.set(""))

        self.log_box = ScrolledText(self.window, font='Arial 12 italic', background="#202020", border=2, relief="solid")
        self.log_box.vbar.forget()

        self._register_tags()

        self.chat_box.config(height="30", wrap="word")
        self.chat_box.pack(fill="x")
        self.input_entry.pack(fill="x")
        self.log_box.pack(expand=True, fill="both")
        self.window.grid_columnconfigure(0, weight=1)

        self.chat_box.configure(state='normal')
        self.chat_box.insert(END, "Server notices and channel chat will appear here.", 'app_notice')
        self.chat_box.configure(state='disabled')

        self.log_box.configure(state='normal')
        self.log_box.insert(END, "Server information and errors will appear here.", 'app_notice')
        self.log_box.configure(state='disabled')

        self._register_menubar()

    def _register_menubar(self, server_connected=False):
        def do_nothing():
            pass

        menubar = Menu(self.window)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences", command=lambda: self.open_preferences())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        servermenu = Menu(menubar, tearoff=0)
        servermenu.add_command(label="Connect", command=do_nothing,
                               state="normal" if not server_connected else "disabled")
        servermenu.add_command(label="Disconnect", command=do_nothing,
                               state="normal" if server_connected else "disabled")
        servermenu.add_separator()
        servermenu.add_command(label="Information", command=do_nothing,
                               state="normal" if server_connected else "disabled")
        servermenu.add_command(label="Users", command=do_nothing, state="normal" if server_connected else "disabled")
        servermenu.add_command(label="Channels", command=do_nothing, state="normal" if server_connected else "disabled")
        menubar.add_cascade(label="Server", menu=servermenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=do_nothing)
        helpmenu.add_command(label="GitHub Repository",
                             command=lambda: open_url("https://github.com/JaxkDev/pyirc-client"))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.window.config(menu=menubar)

    def _register_tags(self):
        self.chat_box.tag_config('app_notice', foreground='lightgreen')
        self.chat_box.tag_config('app_error', foreground='red')
        self.chat_box.tag_config('chat', foreground='aqua')
        self.chat_box.tag_config('error', foreground='red')

        self.log_box.tag_config('app_notice', foreground='lightgreen')
        self.log_box.tag_config('app_error', foreground='red')
        self.log_box.tag_config('log', foreground='aqua')
        self.log_box.tag_config('error', foreground='red')

    def open_preferences(self):
        if not self.top:
            return
        pref = Preferences(self.window, self.app)
        pref.grab_set()
        pref.focus_force()
        self.top = False
        self.window.wait_window(pref)
        self.top = True

    def insert_chat(self, text, tag="chat", prefix="\n", suffix=""):
        self.chat_box.configure(state='normal')
        self.chat_box.insert(END, prefix + text + suffix, tag)
        self.chat_box.yview(END)
        self.chat_box.configure(state='disabled')

    def insert_log(self, text, tag="log", prefix="\n", suffix=""):
        self.log_box.configure(state='normal')
        self.log_box.insert(END, prefix + text + suffix, tag)
        self.log_box.yview(END)
        self.log_box.configure(state='disabled')

    def main_loop(self):
        self.window.mainloop()


# noinspection PyTypeChecker
class Preferences(Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.geometry('400x500')
        self.minsize(400, 500)
        self.title("Preferences")
        self.build()

        # Keep on top.
        self.grab_set()
        self.wm_transient(parent)
        self.attributes('-topmost', 'true')

    def build(self):
        tab_control = Notebook(self)

        general_tab = Frame(tab_control, borderwidth=20)
        general_tab.grid_columnconfigure((0, 1), weight=1)
        user_tab = Frame(tab_control, borderwidth=20)
        user_tab.grid_columnconfigure((0, 1), weight=1)
        servers_tab = Frame(tab_control, borderwidth=20)
        servers_tab.grid_columnconfigure((0, 1), weight=1)

        tab_control.add(general_tab, text='General')
        tab_control.add(user_tab, text='User')
        tab_control.add(servers_tab, text='Servers')
        tab_control.pack(expand=1, fill="both")

        save_button = Button(self, text="Save", command=lambda: self.save(), width=4)
        save_button.pack(side="right", padx=(0, 15), pady=(0, 10))
        cancel_button = Button(self, text="Cancel", command=self.destroy, width=5)
        cancel_button.pack(side="right", padx=(0, 5), pady=(0, 10))
        import_button = Button(self, text="Import", command=lambda: self.load(), width=5)
        import_button.pack(side="left", padx=(15, 0), pady=(0, 10))
        export_button = Button(self, text="Export", command=lambda: self.export(), width=5)
        export_button.pack(side="left", padx=(5, 0), pady=(0, 10))

        # Load
        self.data = self.app.preferences
        if self.data is None:
            self.data = {"auto_connect": "None", "user": {"nickname": "", "real_name": "", "username": ""}, "servers":
                {0: {"name": "New Server", "ip": "0.0.0.0", "port": 6667, "password": ""}}}
        self.servers = self.data["servers"]
        self.server_names = []
        for server in self.servers.keys():
            self.server_names.append(self.servers[server]["name"])

        # General tab
        auto_connect_label = Label(general_tab, text="Auto connect:")
        Tooltip(auto_connect_label, "Choose the server to automatically connect to when the app next starts.\nChoose "
                                    "None to not automatically connect.")
        self.auto_connect_var = StringVar(general_tab)
        self.auto_connect_entry = OptionMenu(general_tab, self.auto_connect_var, self.data["auto_connect"],
                                             *self.server_names)
        self.auto_connect_entry.config(width=10)

        auto_connect_label.grid(row=1, column=0, sticky="e")
        self.auto_connect_entry.grid(row=1, column=1, sticky="w", padx=10)

        # User tab

        nickname_label = Label(user_tab, text="Nickname:")
        Tooltip(nickname_label, "The name you will be known as on the server.")
        username_label = Label(user_tab, text="Username:")
        Tooltip(username_label, "The name you will use to log in to the server.")
        realname_label = Label(user_tab, text="Real Name:")
        Tooltip(realname_label, "Your 'real name', or a pseudonym if you prefer.\nYou can use any name you like it is "
                                "not checked.")

        self.nickname_entry = Entry(user_tab)
        self.nickname_entry.insert(0, self.data["user"]["nickname"])
        self.username_entry = Entry(user_tab)
        self.username_entry.insert(0, self.data["user"]["username"])
        self.realname_entry = Entry(user_tab)
        self.realname_entry.insert(0, self.data["user"]["real_name"])

        nickname_label.grid(row=1, column=0, sticky="e")
        self.nickname_entry.grid(row=1, column=1, sticky="w", padx=10)
        username_label.grid(row=2, column=0, sticky="e")
        self.username_entry.grid(row=2, column=1, sticky="w", padx=10)
        realname_label.grid(row=3, column=0, sticky="e")
        self.realname_entry.grid(row=3, column=1, sticky="w", padx=10)

        # Servers tab

        server_names_var = Variable(value=self.server_names)
        server_list = Listbox(servers_tab, listvariable=server_names_var, selectmode="single", width=30, height=10,
                              borderwidth=2, relief="solid")

        self._prev_server = None

        def change_server():
            server_name_entry.config(state="normal")
            server_host_entry.config(state="normal")
            server_port_entry.config(state="normal")
            server_password_entry.config(state="normal")
            if self._prev_server is not None:
                data = {"name": server_name_entry.get(), "ip": server_host_entry.get(),
                        "port": int(server_port_entry.get()),
                        "password": server_password_entry.get()}
                self.servers[self._prev_server] = data

                # Update server names in case of change
                self.server_names = []
                for server in self.servers.keys():
                    self.server_names.append(self.servers[server]["name"])
                server_names_var.set(self.server_names)

                # Update other preferences that use server name/data.
                # self.auto_connect_entry.set_menu(self.auto_connect_entry.selection_get(), *self.server_names)

            selected = server_names_var.get()[server_list.curselection()[0]]
            _server = None
            for s in self.servers.keys():
                _server = self.servers[s]
                if _server["name"] == selected:
                    self._prev_server = s
                    break
            if self._prev_server is None or _server is None:
                raise ValueError("Server not found.")
            server_name_entry.delete(0, "end")
            server_host_entry.delete(0, "end")
            server_port_entry.delete(0, "end")
            server_password_entry.delete(0, "end")
            server_name_entry.insert(0, _server["name"])
            server_host_entry.insert(0, _server["ip"])
            server_port_entry.insert(0, _server["port"])
            server_password_entry.insert(0, _server["password"])

        server_name_label = Label(servers_tab, text="Server Name:")
        Tooltip(server_name_label, "A name to remember the server by.\nThis is not the server's IP/Specific name.")
        server_host_label = Label(servers_tab, text="Server Host:")
        Tooltip(server_host_label, "The IP or hostname of the server.")
        server_port_label = Label(servers_tab, text="Server Port:")
        Tooltip(server_port_label, "The port the server is running on.\nDefault is 6667.")
        server_password_label = Label(servers_tab, text="Server Password:", width=14)
        Tooltip(server_password_label, "The password to use when connecting to the server.\nLeave blank if no "
                                       "password is required.")

        server_name_entry = Entry(servers_tab, state="readonly")
        server_host_entry = Entry(servers_tab, state="readonly")
        server_port_entry = Entry(servers_tab, state="readonly")
        server_password_entry = Entry(servers_tab, state="readonly")

        server_list.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        server_name_label.grid(row=1, column=0, sticky="e")
        server_name_entry.grid(row=1, column=1, sticky="w", padx=10)
        server_host_label.grid(row=2, column=0, sticky="e")
        server_host_entry.grid(row=2, column=1, sticky="w", padx=10)
        server_port_label.grid(row=3, column=0, sticky="e")
        server_port_entry.grid(row=3, column=1, sticky="w", padx=10)
        server_password_label.grid(row=4, column=0, sticky="e")
        server_password_entry.grid(row=4, column=1, sticky="w", padx=10)

        server_list.bind('<<ListboxSelect>>', lambda e: change_server())

    def save(self, file=None):
        # TODO Save any temp changes in servers.

        # Validate
        auto = self.auto_connect_var.get()
        nickname = self.nickname_entry.get().strip()
        realname = self.realname_entry.get().strip()
        username = self.username_entry.get().strip()
        # servers = self.servers

        if nickname == "":
            print("Nickname is empty.")
            return
        if realname == "":
            print("Real Name is empty.")
            return
        if username == "":
            print("Username is empty.")
            return

        # Save
        self.app.preferences = {"auto_connect": auto,
                                "user": {"nickname": nickname, "real_name": realname, "username": username},
                                "servers": self.servers}
        self.app.save_preferences(file)

    def load(self):
        f = askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Import Preferences")
        if f is None or f == "":
            return
        #Todo
        #self.app.load_preferences(f)

    def export(self):
        f = asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Export Preferences")
        if f is None or f == "":
            return
        self.save(f)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", lambda e: self.show())
        self.widget.bind("<Leave>", lambda e: self.hide())

    def show(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text="  " + self.text.replace("\n", "\n  "), relief="solid", borderwidth=1)
        label.pack(ipady=4, ipadx=4)

    def hide(self):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None
