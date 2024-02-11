from tkinter import Tk, END, StringVar, Entry, Menu, Toplevel
from tkinter.scrolledtext import ScrolledText
from webbrowser import open_new as open_url


class Window:
    def __init__(self, application):
        self.top = True
        self.app = application
        self.window = Tk("IRC Client", "IRC Client", "IRC Client")
        self.window.geometry('1000x700')
        self.window.resizable(False, False)
        self.window.title("IRC Client - Not logged in")

        self.chat_box = ScrolledText(self.window, height=40, background="#555555", foreground="aqua",
                                     font='Arial 12 bold', border=2)
        self.chat_box.vbar.forget()

        self.input_var = StringVar()
        self.input_entry = Entry(self.window, textvariable=self.input_var, border=2, font='Arial 12 bold',
                                 background="white", foreground="black")
        self.input_entry.focus()
        self.input_entry.configure(state="readonly")
        self.input_entry.bind("<Return>", lambda e: self.app.handle_input(self.input_var.get()) or self.input_var.set(""))

        self.log_box = ScrolledText(self.window, height=10, font='Arial 12 italic', background="#202020")
        self.log_box.vbar.forget()

        self._register_tags()

        self.chat_box.pack(expand=True, fill='x')
        self.input_entry.pack(expand=True, fill='x')
        self.log_box.pack(expand=True, fill='x')

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
        filemenu.add_command(label="Preferences", command=pref)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        servermenu = Menu(menubar, tearoff=0)
        servermenu.add_command(label="Connect", command=donothing, state="normal" if server_connect else "disabled")
        servermenu.add_command(label="Disconnect", command=donothing, state="normal" if server_disconnect else "disabled")
        menubar.add_cascade(label="Server", menu=servermenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=donothing)
        helpmenu.add_command(label="GitHub Repository",
                             command=lambda: open_url("https://github.com/JaxkDev/irc-ebooks"))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.window.config(menu=menubar)

    def _register_tags(self):
        self.chat_box.tag_config('app_notice', foreground='lightgreen')
        self.log_box.tag_config('app_error', foreground='red')
        self.chat_box.tag_config('chat', foreground='aqua')
        self.chat_box.tag_config('error', foreground='red')

        self.log_box.tag_config('app_notice', foreground='lightgreen')
        self.log_box.tag_config('app_error', foreground='red')
        self.log_box.tag_config('log', foreground='aqua')
        self.log_box.tag_config('error', foreground='red')

    def open_preferences(self):
        pref = Preferences(self.window)
        pref.grab_set()
        pref.focus_force()

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

        # Keep on top.
        self.grab_set()
        self.wm_transient(parent)
        self.attributes('-topmost', 'true')
