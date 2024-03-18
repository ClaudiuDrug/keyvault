# -*- coding: UTF-8 -*-

from tkinter import Tk

from library import KeyVault


def draw():
    root = Tk()
    KeyVault(root)
    root.mainloop()


if __name__ == '__main__':
    draw()
