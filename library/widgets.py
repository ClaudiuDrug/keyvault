# -*- coding: UTF-8 -*-

from abc import ABC
from json import dumps, loads
from tkinter import Tk, Event, TclError, Toplevel
from tkinter.ttk import (
    Frame, LabelFrame, Label, Entry, Button,
    Scrollbar, Treeview, Style, Widget
)
from typing import Tuple, Dict, List

from keyring import get_password, set_password, delete_password
from keyring.errors import PasswordDeleteError

from .constants import (
    ROOT, ALL, HIDDEN, NSEW, NEW, NE, SE, PADDING, PADX, PADY, UP, BOTTOM,
    LEFT, RIGHT, BROWSE, HORIZONTAL, VERTICAL, END, FLAT, STYLE, CACHE,
    KEYVAULT,
)
from .mapping import Icons, Variables
from .utils import check_folder_path, read_file, write_file

__all__ = [
    "ToolTip", "SharedState", "KeyVault", "TreeFrame", "AccountFrame",
    "ClearFrame", "ToolboxFrame", "NotificationFrame"
]


class ToolTip:
    def __init__(self, widget: Widget, text: str, delay: int = 1000):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds
        self.window = None
        self.id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.cancel)

    def schedule(self, event: Event):
        self.cancel(event)  # Cancel existing scheduled event if any
        self.id = self.widget.after(self.delay, self.enter)

    def enter(self):
        x, y, cx, cy = self.widget.bbox()
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Create a toplevel window
        self.window = self.new_window(x, y)
        self.id = None

    def new_window(self, x: int, y: int) -> Toplevel:
        window = Toplevel(self.widget)
        window.wm_overrideredirect(True)
        window.wm_geometry(f"+{x}+{y}")
        self.new_label(window)
        return window

    def new_label(self, master: Toplevel) -> Label:
        label = Label(
            master,
            text=self.text,
            background="lightyellow",
            borderwidth=1,
            relief="solid",
            padding=PADDING
        )
        label.pack()
        return label

    def cancel(self, event: Event):
        if self.id is not None:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.window:
            self.window.destroy()
            self.window = None


class SharedState(ABC):

    root: Tk
    variables: Variables
    icons: Icons
    style: Style
    tree: Treeview
    cache: Dict[str, List[str]]

    __shared__: dict = {}

    @staticmethod
    def get_service_id(tree: Treeview, value: str) -> str:
        """
        Check if service exists in `Treeview` and
        return its `iid` value else `None`.
        """
        services: Tuple[str, ...] = tree.get_children()

        for service in services:
            name: str = tree.item(service, "text")

            if value.lower() == name.lower():
                return service

    @staticmethod
    def get_username_id(tree, service_id: str, username: str) -> str:
        """Check if a username is present in the tree."""
        usernames: Tuple[str, ...] = tree.get_children(service_id)

        for username_id in usernames:
            item: str = tree.item(username_id, "text")

            if username.lower() == item.lower():
                return username_id

    @staticmethod
    def get_cache() -> Dict[str, List[str]]:
        """Read cached data and return it as a dictionary."""
        try:
            cache: str = read_file(CACHE)
        except FileNotFoundError:
            return dict()
        else:
            return loads(cache)

    @staticmethod
    def set_cache(cache: Dict[str, List[str]]):
        """Write `cache` data to user profile."""
        check_folder_path(KEYVAULT)
        cache: str = dumps(cache)
        write_file(cache, CACHE)

    def __init__(self):
        self.__shared__.update(self.__dict__)
        self.__dict__ = self.__shared__

    @property
    def service(self) -> str:
        return self.variables.service.get()

    @service.setter
    def service(self, value: str):
        self.variables.service.set(value)

    @service.deleter
    def service(self):
        self.variables.service.set("")

    @property
    def username(self) -> str:
        return self.variables.username.get()

    @username.setter
    def username(self, value: str):
        self.variables.username.set(value)

    @username.deleter
    def username(self):
        self.variables.username.set("")

    @property
    def password(self) -> str:
        return self.variables.password.get()

    @password.setter
    def password(self, value: str):
        self.variables.password.set(value)

    @password.deleter
    def password(self):
        self.variables.password.set("")

    @property
    def message(self) -> str:
        return self.variables.notification.get()

    @message.setter
    def message(self, value: str):
        self.variables.notification.set(value)

    @message.deleter
    def message(self):
        self.variables.notification.set("")

    @property
    def clipboard(self) -> str:
        return self.root.clipboard_get()

    @clipboard.setter
    def clipboard(self, value: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(value)

    @clipboard.deleter
    def clipboard(self):
        self.root.clipboard_clear()

    def show_info(self, msg: str):
        """Display an info `msg` in the notification section."""
        if (msg is not None) and (len(msg) > 0):
            self.message = f"[INFO]: {msg}"

    def show_warning(self, msg: str):
        """Display a warning `msg` in the notification section."""
        if (msg is not None) and (len(msg) > 0):
            self.message = f"[WARNING]: {msg}"

    def show_error(self, msg: str):
        """Display an error `msg` in the notification section."""
        if (msg is not None) and (len(msg) > 0):
            self.message = f"[ERROR]: {msg}"

    def add_username(self, service: str, username: str):
        """Add a username to the tree."""
        service_id: str = self.get_service_id(self.tree, service)

        if service_id is None:
            service_id = self.tree.insert(ROOT, END, text=service)

        if self.get_username_id(self.tree, service_id, username) is None:
            self.tree.insert(service_id, END, text=username)

    def del_username(self, service: str, username: str):
        """Delete a username from the tree."""
        service_id: str = self.get_service_id(self.tree, service)

        if service_id is not None:

            for account_id in self.tree.get_children(service_id):
                account: str = self.tree.item(account_id, "text")

                if account.lower() != username.lower():
                    continue

                self.tree.delete(account_id)

            if len(self.tree.get_children(service_id)) == 0:
                self.tree.delete(service_id)

    def get_tree(self) -> Dict[str, List[str]]:
        """Populate the widget with cached data."""
        tree: Dict[str, List[str]] = {}
        service_ids: Tuple[str, ...] = self.tree.get_children()

        for service_id in service_ids:
            service: str = self.tree.item(service_id, "text")
            account_ids: Tuple[str, ...] = self.tree.get_children(service_id)
            accounts: List[str] = [
                self.tree.item(account_id, "text")
                for account_id in account_ids
            ]

            tree.update({service: accounts})

        return tree

    def set_tree(self, cache: Dict[str, List[str]]):
        """Populate the widget with cached data."""
        for key, value in cache.items():
            for item in value:
                self.add_username(key, item)


class KeyVault(SharedState):
    """Main window."""

    def __init__(self, master: Tk):
        super(KeyVault, self).__init__()

        # shared:
        self.root = master
        self.variables = Variables(master)
        self.icons = Icons(master)
        self.style = Style(master)
        self.cache = self.get_cache()

        # layout:
        self.root.title("KeyVault")
        self.root.configure(background="white")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # style:
        for key, value in STYLE.items():
            self.style.configure(key, background=value)

        main_frame: Frame = Frame(master, padding=PADDING)
        main_frame.grid(column=0, row=0, sticky=NSEW, padx=PADX, pady=PADY)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)

        TreeFrame(main_frame)
        AccountFrame(main_frame)
        ClearFrame(main_frame)
        ToolboxFrame(main_frame)
        NotificationFrame(main_frame)

        self.set_tree(self.cache)


class TreeFrame(SharedState):

    def __init__(self, master: Frame):
        super(TreeFrame, self).__init__()

        # section:
        frame = LabelFrame(master, text="Vault", padding=PADDING)
        frame.grid(row=0, column=0, sticky=NSEW, padx=PADX, pady=PADY, rowspan=3)
        frame.rowconfigure(0, weight=1)

        # `ttk`.`TreeView` widgets:
        self.tree = Treeview(frame, show="tree", selectmode=BROWSE, padding=PADDING)
        self.tree.grid(row=0, column=0, sticky=NSEW, padx=LEFT, pady=UP)

        # # `ttk`.`Scrollbar` widgets:
        search_scrollbar_y = Scrollbar(frame, orient=VERTICAL)
        search_scrollbar_y.configure(command=self.tree.yview)
        search_scrollbar_y.grid(row=0, column=1, sticky=NSEW, padx=RIGHT, pady=UP)
        self.tree.configure(yscrollcommand=search_scrollbar_y.set)

        search_scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)
        search_scrollbar_x.configure(command=self.tree.xview)
        search_scrollbar_x.grid(row=1, column=0, sticky=NSEW, padx=LEFT, pady=BOTTOM)
        self.tree.configure(xscrollcommand=search_scrollbar_x.set)

        self.tree.bind('<<TreeviewSelect>>', self.select)

    def select(self, event: Event):
        tree: Treeview = event.widget
        selected: str = tree.focus()

        if len(selected) > 0:
            parent: str = tree.parent(selected)
            value: str = tree.item(selected, "text")

            del self.service, self.username, self.password

            if parent == ROOT:
                self.service = value
                self.show_info("Service selected.")

            else:
                self.service = tree.item(parent, "text")
                self.username = value
                self.show_info("Username selected.")


class AccountFrame(SharedState):

    @staticmethod
    def reveal(event: Event):
        event.widget.configure(show=ALL)

    @staticmethod
    def hide(event: Event):
        event.widget.configure(show=HIDDEN)

    def __init__(self, master: Frame):
        super(AccountFrame, self).__init__()

        frame = LabelFrame(master, text="Account", padding=PADDING)
        frame.grid(row=0, column=1, sticky=NEW, padx=PADX, pady=PADY)
        frame.columnconfigure(1, weight=1)

        # `ttk.Label` widgets:
        label_1 = Label(frame, text="Service:", relief=FLAT)
        label_1.grid(row=0, column=0, sticky=NSEW, padx=PADX, pady=PADY)

        label_2 = Label(frame, text="Username:", relief=FLAT)
        label_2.grid(row=1, column=0, sticky=NSEW, padx=PADX, pady=PADY)

        label_3 = Label(frame, text="Password:", relief=FLAT)
        label_3.grid(row=2, column=0, sticky=NSEW, padx=PADX, pady=PADY)

        # `ttk.Entry` widgets:
        entry_1 = Entry(frame, textvariable=self.variables.service)
        entry_1.grid(row=0, column=1, sticky=NSEW, padx=PADX, pady=PADY)

        entry_2 = Entry(frame, textvariable=self.variables.username)
        entry_2.grid(row=1, column=1, sticky=NSEW, padx=PADX, pady=PADY)

        entry_3 = Entry(frame, show=HIDDEN, textvariable=self.variables.password)
        entry_3.grid(row=2, column=1, sticky=NSEW, padx=PADX, pady=PADY)
        entry_3.bind("<Enter>", self.reveal)
        entry_3.bind("<Leave>", self.hide)

        # `ttk.Button` widgets:
        btn_1 = Button(frame, image=self.icons.copy, command=self.copy_service)
        btn_1.grid(row=0, column=2, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_1, "Copy")

        btn_2 = Button(frame, image=self.icons.paste, command=self.paste_service)
        btn_2.grid(row=0, column=3, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_2, "Paste")

        btn_3 = Button(frame, image=self.icons.copy, command=self.copy_username)
        btn_3.grid(row=1, column=2, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_3, "Copy")

        btn_4 = Button(frame, image=self.icons.paste, command=self.paste_username)
        btn_4.grid(row=1, column=3, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_4, "Paste")

        btn_5 = Button(frame, image=self.icons.copy, command=self.copy_password)
        btn_5.grid(row=2, column=2, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_5, "Copy")

        btn_6 = Button(frame, image=self.icons.paste, command=self.paste_password)
        btn_6.grid(row=2, column=3, sticky=NSEW, padx=PADX, pady=PADY)
        ToolTip(btn_6, "Paste")

    def copy_service(self):
        self.clipboard = self.service
        self.show_info("Service copied to clipboard.")

    def paste_service(self):
        del self.service
        try:
            self.service = self.clipboard
        except TclError:
            self.show_error("Clipboard empty!")
        else:
            self.show_info("Service pasted from clipboard.")

    def copy_username(self):
        self.clipboard = self.username
        self.show_info("Username copied to clipboard.")

    def paste_username(self):
        del self.username
        try:
            self.username = self.clipboard
        except TclError:
            self.show_error("Clipboard empty!")
        else:
            self.show_info("Username pasted from clipboard.")

    def copy_password(self):
        self.clipboard = self.password
        self.show_info("Password copied to clipboard.")

    def paste_password(self):
        del self.password
        try:
            self.password = self.clipboard
        except TclError:
            self.show_error("Clipboard empty!")
        else:
            self.show_info("Password pasted from clipboard.")


class ClearFrame(SharedState):

    def __init__(self, master: Frame):
        super(ClearFrame, self).__init__()

        # section:
        frame = Frame(master, padding=PADDING)
        frame.grid(row=1, column=1, sticky=NE, padx=PADX, pady=PADY)

        # `ttk`.`TreeView` widgets:
        btn_1 = Button(frame, text="Clear", command=self.clear_entries)
        btn_1.grid(row=0, column=0, sticky=NSEW, padx=PADX, pady=PADY)

    def clear_entries(self):
        """Clear all entries in the account section"""
        del self.service, self.username, self.password
        self.show_info("Cleared all entries!")


class ToolboxFrame(SharedState):

    def __init__(self, master: Frame):
        super(ToolboxFrame, self).__init__()

        frame: Frame = Frame(master, padding=PADDING)
        frame.grid(row=2, column=1, sticky=SE, padx=PADX, pady=PADY)

        # `ttk.Button` widgets:
        btn_1 = Button(frame, text="Fetch", command=self.get_password)
        btn_1.grid(row=0, column=0, sticky=NSEW, padx=PADX, pady=PADY)

        btn_2 = Button(frame, text="Save", command=self.set_password)
        btn_2.grid(row=0, column=1, sticky=NSEW, padx=PADX, pady=PADY)

        btn_3 = Button(frame, text="Delete", command=self.del_password)
        btn_3.grid(row=0, column=2, sticky=NSEW, padx=PADX, pady=PADY)

    def get_password(self):
        """Fetch a password from the keyring."""
        del self.password

        if (len(self.service) > 0) and (len(self.username) > 0):
            value: str = get_password(self.service, self.username)

            if value is not None:
                self.password = self.clipboard = value
                self.add_account(self.service, self.username)
                self.show_info("Password retrieved from keyring.")

            else:
                self.del_account(self.service, self.username)
                self.show_warning("Password not found!")

        else:
            self.show_warning("Service and username cannot be empty!")

    def set_password(self):
        """Save a password to the keyring."""
        if (
            len(self.service) > 0 and
            len(self.username) > 0 and
            len(self.password) > 0
        ):
            set_password(self.service, self.username, self.password)
            self.add_account(self.service, self.username)
            self.clipboard = self.password
            self.show_info("Password saved to keyring.")

        else:
            self.show_warning("Service, username and password cannot be empty!")

    def del_password(self):
        if len(self.service) > 0 and len(self.username) > 0:
            try:
                delete_password(self.service, self.username)
            except PasswordDeleteError:
                self.show_warning("Password not found in keyring!")
            else:
                self.show_info("Password deleted from keyring.")
            finally:
                self.del_account(self.service, self.username)
                del self.service, self.username, self.password

        else:
            self.show_warning("Service and username cannot be empty!")

    def add_account(self, service: str, username: str):
        """Add a new account to the vault and update cache."""
        self.add_username(service, username)
        data: Dict[str, List[str]] = self.get_tree()
        self.set_cache(data)

    def del_account(self, service: str, username: str):
        """Add a new account to the vault and update cache."""
        self.del_username(service, username)
        data: Dict[str, List[str]] = self.get_tree()
        self.set_cache(data)


class NotificationFrame(SharedState):

    def __init__(self, master: Frame):
        super(NotificationFrame, self).__init__()

        frame: Frame = Frame(master, padding=PADDING)
        frame.grid(row=3, column=0, sticky=NSEW, padx=PADX, pady=PADY, columnspan=2)

        label: Label = Label(frame, textvariable=self.variables.notification, relief=FLAT)
        label.grid(row=0, column=0, sticky=NSEW, padx=PADX, pady=PADY)
