from tkinter import Tk, END, StringVar, Menu, Toplevel
from tkinter.ttk import Notebook, Frame, Button, OptionMenu, Label, Entry
from tkinter.scrolledtext import ScrolledText
from webbrowser import open_new as open_url


class Window:
    def __init__(self, application):
        self.top = True
        self.app = application
        self.window = Tk("  PY-IRC Client", "PY-IRC Client", "PY-IRC Client")
        self.window.geometry('1000x800')
        self.window.resizable(False, False)
        self.window.title("-- Not logged in --")

        self.chat_box = ScrolledText(self.window, background="#555555", font='Arial 10 bold', border=2, relief="solid")  # TODO Sort out height based on font and pixel and yeah
        self.chat_box.vbar.forget()

        self.input_var = StringVar()
        self.input_entry = Entry(self.window, textvariable=self.input_var, font='Arial 10 bold',
                                 background="white", foreground="black")
        self.input_entry.focus()
        self.input_entry.configure(state="readonly")
        self.input_entry.bind("<Return>",
                              lambda e: self.app.handle_input(self.input_var.get()) or self.input_var.set(""))

        self.log_box = ScrolledText(self.window, font='Arial 10 italic', background="#202020", border=2, relief="solid")
        self.log_box.frame.config(width="100", height="100")
        self.log_box.vbar.forget()

        self._register_tags()

        self.chat_box.grid(row=0, column=0, sticky="nsew")
        self.input_entry.grid(row=1, column=0, sticky="nsew")
        self.log_box.grid(row=2, column=0, sticky="nsew")
        self.window.grid_columnconfigure(0, weight=1)

        self.chat_box.configure(state='normal')
        self.chat_box.insert(END, "Server notices and channel chat will appear here.", 'app_notice')
        self.chat_box.configure(state='disabled')

        self.log_box.configure(state='normal')
        self.log_box.insert(END, "Server information and errors will appear here.", 'app_notice')
        self.log_box.configure(state='disabled')

        self._register_menubar()

    def _register_menubar(self, server_connect=True, server_disconnect=False):
        def donothing():
            pass

        def pref():
            if self.top:
                self.open_preferences()

        menubar = Menu(self.window)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences", command=lambda: self.open_preferences())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        servermenu = Menu(menubar, tearoff=0)
        servermenu.add_command(label="Connect", command=donothing,
                               state="normal" if server_connect else "disabled")
        servermenu.add_command(label="Disconnect", command=donothing,
                               state="normal" if server_disconnect else "disabled")
        menubar.add_cascade(label="Server", menu=servermenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=donothing)
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
        pref = Preferences(self.window)
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


class Preferences(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('400x500')
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

        def save():
            print("Saved")

        save_button = Button(self, text="Save", command=save)
        save_button.pack(side="right", padx=(0, 20), pady=(0, 10))
        cancel_button = Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack(side="right", padx=(0, 5), pady=(0, 10))

        auto_connect_label = Label(general_tab, text="Auto connect:")
        Tooltip(auto_connect_label, "Choose the server to automatically connect to when the app next starts.\nChoose "
                                    "None to not automatically connect.")
        auto_connect_var = StringVar(general_tab)
        vars = ["1", "2", "3", "4"]
        auto_connect_entry = OptionMenu(general_tab, auto_connect_var, "None", "None", *vars)
        auto_connect_entry.config(width=10)

        auto_connect_label.grid(row=1, column=0, sticky="e")
        auto_connect_entry.grid(row=1, column=1, sticky="w", padx=10)

        nickname_label = Label(user_tab, text="Nickname:")
        username_label = Label(user_tab, text="Username:")
        realname_label = Label(user_tab, text="Real Name:")

        nickname_entry = Entry(user_tab)
        username_entry = Entry(user_tab)
        realname_entry = Entry(user_tab)

        nickname_label.grid(row=1, column=0, sticky="e")
        nickname_entry.grid(row=1, column=1, sticky="w", padx=10)
        username_label.grid(row=2, column=0, sticky="e")
        username_entry.grid(row=2, column=1, sticky="w", padx=10)
        realname_label.grid(row=3, column=0, sticky="e")
        realname_entry.grid(row=3, column=1, sticky="w", padx=10)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text=self.text, foreground="black", background="#ffffe0", relief="solid",
                      borderwidth=1)
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
