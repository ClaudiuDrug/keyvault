# -*- coding: UTF-8 -*-

from os import environ
from os.path import dirname, realpath, join
from typing import Literal, Tuple, Dict

__all__ = [
    "FLAT", "HORIZONTAL", "VERTICAL", "BROWSE", "END", "ROOT", "ALL",
    "HIDDEN", "NSEW", "NEW", "NE", "SE", "PADDING", "ZERO", "PADX", "RIGHT",
    "LEFT", "PADY", "UP", "BOTTOM", "STYLE", "LIBRARY", "ICONS",
    "USERPROFILE", "KEYVAULT", "CACHE",
]

# relief:
FLAT: Literal["flat"] = "flat"

# orient:
HORIZONTAL: Literal["horizontal"] = "horizontal"
VERTICAL: Literal["vertical"] = "vertical"

# selection mode:
BROWSE: Literal["browse"] = "browse"

# insert positions:
END: Literal["end"] = "end"

# root index:
ROOT: Literal[""] = ""

# show password:
ALL: Literal[""] = ""
HIDDEN: Literal["*"] = "*"

# grid:
NSEW: Literal["NSEW"] = "NSEW"
NEW: Literal["NEW"] = "NEW"
NE: Literal["NE"] = "NE"
SE: Literal["SE"] = "SE"

# padding:
PADDING: float = 2.5
ZERO: float = 0

# padx:
PADX: float = PADDING
RIGHT: Tuple[float, float] = (ZERO, PADDING)
LEFT: Tuple[float, float] = (PADDING, ZERO)

# pady:
PADY: float = PADDING
UP: Tuple[float, float] = (PADDING, ZERO)
BOTTOM: Tuple[float, float] = (ZERO, PADDING)

# style:
STYLE: Dict[str, str] = {
    "TFrame": "white",
    "TButton": "white",
    "TLabelframe": "white",
    "TLabelframe.Label": "white",
    "TLabel": "white",
    "Horizontal.TScrollbar": "white",
    "Vertical.TScrollbar": "white",
    "Treeview": "white",
}

# library:
LIBRARY: str = dirname(realpath(__file__))

# icons:
ICONS: str = join(LIBRARY, "icons")

# user profile path:
USERPROFILE: str = environ.get("USERPROFILE")

# home folder:
KEYVAULT: str = join(USERPROFILE, ".keyvault")

# cached accounts:
CACHE: str = join(KEYVAULT, "keyvault.json")
