from tkinter import FLAT
from typing import Dict, Any, List

ACCENT_M1 = "#006f6f"
ACCENT = "#009f9f"
ACCENT_P1 = "#00cfcf"

theme: Dict[str, Dict[str, Dict]] = {
    "TEntry": {
        "configure": {"font": ("helvetica", 11), "relief": "flat", "selectborderwidth": 0, "padding": 2},
        "map": {
            "relief": [("active", FLAT),
                       ("focus", FLAT),
                       ("!disabled", FLAT),
                       ("disabled", FLAT)],
            "bordercolor": [("active", "#f7f7f7"),
                            ("focus", "#f7f7f7"),
                            ("!disabled", "#f0f0f0"),
                            ("disabled", "#ffffff")],
            "background": [("active", "#f7f7f7"),
                           ("focus", "#f7f7f7"),
                           ("!disabled", "#f0f0f0"),
                           ("disabled", "#ffffff")],
            "fieldbackground": [("active", "#f7f7f7"),
                                ("focus", "#f7f7f7"),
                                ("!disabled", "#f0f0f0"),
                                ("disabled", "#ffffff")],
            "foreground": [("active", "#0f0f0f"),
                           ("focus", "#0f0f0f"),
                           ("!disabled", "#0f0f0f"),
                           ("disabled", "#7f7f7f")],
            "selectbackground": [("active", ACCENT),
                                 ("focus", ACCENT),
                                 ("!disabled", ACCENT_P1),
                                 ("disabled", "#f7f7f7")],
            "selectforeground": [("active", "#ffffff"),
                                 ("focus", "#ffffff"),
                                 ("!disabled", "#ffffff"),
                                 ("disabled", "#7f7f7f")]
        }
    },
    "TButton": {
        "configure": {"font": ("helvetica", 10), "padding": 1},
        "map": {
            "relief": [("pressed", FLAT),
                       ("active", FLAT),
                       ("focus", FLAT),
                       ("!disabled", FLAT),
                       ("disabled", FLAT)],
            "background": [("pressed", ACCENT_M1),
                           ("active", ACCENT_P1),
                           ("focus", ACCENT_P1),
                           ("!disabled", "#f0f0f0"),
                           ("disabled", "#ffffff")],
            "bordercolor": [("pressed", ACCENT_M1),
                            ("active", ACCENT_P1),
                            ("focus", ACCENT_P1),
                            ("!disabled", "#f0f0f0"),
                            ("disabled", "#ffffff")],
            "foreground": [("pressed", "#ffffff"),
                           ("active", "#ffffff"),
                           ("focus", "#ffffff"),
                           ("!disabled", "#0f0f0f"),
                           ("disabled", "#7f7f7f")],
        }
    },
    "TLabel": {
        "configure": {"background": "#ffffff",
                      "foreground": "#404040",
                      "font": ("Helvetica", 10)}
    },
    "TProgressbar": {
        "configure": {"background": ACCENT,
                      "bordercolor": ACCENT,
                      "troughcolor": "#f7f7f7"}
    },
    "TFrame": {
        "configure": {"background": "#ffffff", "relief": FLAT}
    },
    "TCombobox": {
        "configure": {"padding": 2, "arrowsize": 15, "postoffset": 0},
        "map": {
            "arrowcolor": [("active", "#ffffff"),
                           ("focus", "#ffffff"),
                           ("pressed", "#ffffff"),
                           ("!disabled", "#ffffff"),
                           ("disabled", "#7f7f7f")],
            "bordercolor": [("active", ACCENT),
                            ("focus", ACCENT),
                            ("!disabled", "#f0f0f0"),
                            ("disabled", "#ffffff")],
            "background": [("active", ACCENT),
                           ("focus", ACCENT),
                           ("pressed", ACCENT_P1),
                           ("!disabled", ACCENT),
                           ("disabled", "#ffffff")],
            "fieldbackground": [("active", "#f7f7f7"),
                                ("focus", "#f7f7f7"),
                                ("!disabled", "#f0f0f0"),
                                ("disabled", "#ffffff")],
            "foreground": [("active", "#ffffff"),
                           ("focus", "#ffffff"),
                           ("!disabled", "#0f0f0f"),
                           ("disabled", "#7f7f7f")],
            "selectbackground": [("active", ACCENT_P1),
                                 ("focus", ACCENT_P1),
                                 ("!disabled", ACCENT),
                                 ("disabled", "#ffffff")],
            "selectforeground": [("active", "#ffffff"),
                                 ("focus", "#ffffff"),
                                 ("!disabled", "#0f0f0f"),
                                 ("disabled", "#7f7f7f")]
        }
    },
    "ComboboxPopdownFrame": {
        "configure": {"relief": FLAT,
                      "borderwidth": 0}
    },
    "TRadiobutton": {
        "configure": {"padding": 8, "indicatormargin": 2},
        "map": {
            "background": [("pressed", "#ffffff"),
                           ("active", "#ffffff"),
                           ("focus", "#ffffff"),
                           ("alternate", "#ffffff"),
                           ("readonly", "#ffffff"),
                           ("disabled", "#ffffff"),
                           ("selected", "#ffffff"),
                           ("!disabled", "#ffffff")],
            "foreground": [("pressed", "#000000"),
                           ("active", "#000000"),
                           ("focus", "#000000"),
                           ("alternate", "#000000"),
                           ("readonly", "#000000"),
                           ("disabled", "#000000"),
                           ("selected", "#000000"),
                           ("!disabled", "#000000")],
            "indicatorcolor": [("selected", ACCENT_P1),
                               ("!selected", ACCENT_M1),
                               ("pressed", ACCENT_M1),
                               ("alternate", ACCENT),
                               ("active", "#e0e0e0"),
                               ("focus", "#e0e0e0"),
                               ("readonly", "#ffffff"),
                               ("disabled", "#ffffff"),
                               ("!disabled", "#f0f0f0")],
            "indicatorbackground": [("pressed", "#ffffff"),
                                    ("active", "#000000"),
                                    ("focus", "#000000"),
                                    ("alternate", "#ffffff"),
                                    ("readonly", "#7f7f7f"),
                                    ("disabled", "#7f7f7f"),
                                    ("selected", "#ffffff"),
                                    ("!disabled", "#0f0f0f")],
            "indicatorrelief": [("pressed", FLAT),
                                ("active", FLAT),
                                ("focus", FLAT),
                                ("alternate", FLAT),
                                ("readonly", FLAT),
                                ("disabled", FLAT),
                                ("selected", FLAT),
                                ("!disabled", FLAT)]
        }
    },
    "TCheckbutton": {
        "configure": {"padding": 8, "indicatormargin": 2},
        "map": {
            "background": [("pressed", "#ffffff"),
                           ("active", "#ffffff"),
                           ("focus", "#ffffff"),
                           ("alternate", "#ffffff"),
                           ("readonly", "#ffffff"),
                           ("disabled", "#ffffff"),
                           ("selected", "#ffffff"),
                           ("!disabled", "#ffffff")],
            "foreground": [("pressed", "#000000"),
                           ("active", "#000000"),
                           ("focus", "#000000"),
                           ("alternate", "#000000"),
                           ("readonly", "#000000"),
                           ("disabled", "#000000"),
                           ("selected", "#000000"),
                           ("!disabled", "#000000")],
            "indicatorcolor": [("selected", ACCENT_P1),
                               ("!selected", ACCENT_M1),
                               ("pressed", ACCENT_M1),
                               ("alternate", ACCENT),
                               ("active", "#e0e0e0"),
                               ("focus", "#e0e0e0"),
                               ("readonly", "#ffffff"),
                               ("disabled", "#ffffff"),
                               ("!disabled", "#f0f0f0")],
            "indicatorbackground": [("pressed", "#ffffff"),
                                    ("active", "#000000"),
                                    ("focus", "#000000"),
                                    ("alternate", "#ffffff"),
                                    ("readonly", "#7f7f7f"),
                                    ("disabled", "#7f7f7f"),
                                    ("selected", "#ffffff"),
                                    ("!disabled", "#0f0f0f")],
            "indicatorrelief": [("pressed", FLAT),
                                ("active", FLAT),
                                ("focus", FLAT),
                                ("alternate", FLAT),
                                ("readonly", FLAT),
                                ("disabled", FLAT),
                                ("selected", FLAT),
                                ("!disabled", FLAT)]
        }
    },
    "Treeview": {
        "configure": {"padding": 0, "font": ("Helvetica", 10), "relief": "flat", "border": 0,
                      "rowheight": 24},
        "map": {
            "background": [("disabled", "#ffffff"),
                           ("active", ACCENT),
                           ("selected", ACCENT),
                           ("focus", ACCENT_P1),
                           ("!disabled", "#f7f7f7")],
            "fieldbackground": [("disabled", "#ffffff"),
                                ("active", "#f7f7f7"),
                                ("focus", "#f7f7f7"),
                                ("!disabled", "#f7f7f7"),
                                ("disabled", "#f0f0f0")],
            "foreground": [("disabled", "#afafaf"),
                           ("active", "#0f0f0f"),
                           ("selected", "#ffffff"),
                           ("focus", "#0f0f0f"),
                           ("!disabled", "#0f0f0f")],
            "relief": [("focus", "flat"),
                       ("active", "flat"),
                       ("!disabled", "flat")]
        }
    },
    "Treeview.Item": {
        "configure": {"padding": 0, "indicatorsize": 10},
        "map": {
            "foreground": [("disabled", "#7f7f7f"),
                           ("selected", ACCENT),
                           ("active", ACCENT),
                           ("focus", "#f7f7f7"),
                           ("!disabled", ACCENT)]
        }
    },
    "Treeview.Cell": {
        "configure": {"padding": 0},
        "map": {
            "background": [("disabled", "#f7f7f7"),
                           ("active", ACCENT),
                           ("selected", ACCENT),
                           ("!disabled", ACCENT),
                           ("!selected", ACCENT)],
            "fieldbackground": [("disabled", "#f7f7f7"),
                                ("selected", ACCENT),
                                ("active", ACCENT),
                                ("!disabled", ACCENT),
                                ("!selected", ACCENT)],
            "foreground": [("disabled", "#f7f7f7"),
                           ("focus", "#ffffff"),
                           ("selected", "#ffffff"),
                           ("!disabled", "#ffffff"),
                           ("!selected", "#ffffff")],
            "relief": [("disabled", "flat"),
                       ("selected", "flat"),
                       ("focus", "flat"),
                       ("active", "flat"),
                       ("!disabled", "flat"),
                       ("!selected", "flat")]
        }
    },
    "Treeview.Heading": {
        "configure": {"padding": 0, "font": ("helvetica", 10)},
        "map": {
            "background": [("disabled", "#f7f7f7"),
                           ("active", "#6f6f6f"),
                           ("selected", "#6f6f6f"),
                           ("!disabled", "#4f4f4f"),
                           ("!selected", "#4f4f4f")],
            "fieldbackground": [("disabled", "#f7f7f7"),
                                ("selected", ACCENT),
                                ("active", ACCENT),
                                ("!disabled", ACCENT),
                                ("!selected", ACCENT)],
            "foreground": [("disabled", "#f7f7f7"),
                           ("selected", "#ffffff"),
                           ("focus", "#f7f7f7"),
                           ("!disabled", "#ffffff"),
                           ("!selected", "#ffffff")],
            "relief": [("disabled", "flat"),
                       ("selected", "flat"),
                       ("focus", "flat"),
                       ("active", "flat"),
                       ("!disabled", "flat"),
                       ("!selected", "flat")]
        }
    }
}

layout = {
    'TEntry': [
        ('Entry.highlight', {
            "border": 0,
            'sticky': 'nswe',
            'children': [
                ('Entry.border', {
                    'border': 0,
                    'sticky': 'nswe',
                    'children': [
                        ('Entry.padding', {
                            'sticky': 'nswe',
                            'children': [
                                ('Entry.textarea', {
                                    'sticky': 'nswe',
                                    "border": 0
                                })
                            ]
                        })
                    ]
                }), ('Entry.bd', {
                    'sticky': 'nswe',
                    'children': [
                        ('Entry.padding', {
                            'sticky': 'nswe',
                            'children': [
                                ('Entry.textarea', {
                                    'sticky': 'nswe'
                                })
                            ]
                        })
                    ],
                    'border': 0
                })
            ]
        })
    ]
}

# layout: Dict[str, List] = {}

options: Dict[str, Any] = {"TCombobox.Listbox": {"background": "#f7f7f7", "foreground": "#0f0f0f", "selectBackground": ACCENT, "selectForeground": "#ffffff", "font": ("helvetica", 10)}}

config: Dict[str, Dict[str, Any]] = {"TProgressbar": {"troughrelief": "flat", "borderwidth": 0, "thickness": 10}}  # {"TEntry": {"relief": FLAT, "bd": 0, "borderwidth": 0}}
theme_name: str = "default"
