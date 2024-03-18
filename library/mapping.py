# -*- coding: UTF-8 -*-

from dataclasses import dataclass, field
from os.path import join
from tkinter import Tk, PhotoImage, StringVar

from .constants import ICONS

__all__ = ["Icons", "Variables"]


@dataclass
class Icons:
    master: Tk = field(init=True)

    def __post_init__(self):
        self.cut: PhotoImage = self._get_image("cut")
        self.copy: PhotoImage = self._get_image("copy")
        self.paste: PhotoImage = self._get_image("paste")

    def _get_image(self, target: str) -> PhotoImage:
        path: str = self._get_path(target)
        return PhotoImage(target, master=self.master, file=path)

    @staticmethod
    def _get_path(target: str) -> str:
        return join(ICONS, f"{target}.png")


@dataclass
class Variables:
    master: Tk = field(init=True)

    def __post_init__(self):
        self.service: StringVar = StringVar(self.master)
        self.username: StringVar = StringVar(self.master)
        self.password: StringVar = StringVar(self.master)
        self.notification: StringVar = StringVar(self.master)
