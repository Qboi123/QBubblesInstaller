import json
import os
import platform
import sys
import time
import tkinter
import tkinter.filedialog
from ctypes import windll, Structure, c_int, wintypes, c_bool, WINFUNCTYPE, POINTER, pythonapi
from ctypes.wintypes import DWORD, HRGN
from math import sqrt
from subprocess import Popen
from threading import Thread
from tkinter import Canvas, Tk
from tkinter.ttk import Button, Label, Radiobutton, Style, Frame, Combobox, Checkbutton, Treeview, Entry, \
    Widget, Progressbar
from typing import Optional, Dict, Any, Callable, Tuple, List
from zipfile import ZipFile

import win32api
import win32gui
from PIL import Image, ImageTk
# from win32con import WS_EX_APPWINDOW, GWL_EXSTYLE, WS_EX_TOOLWINDOW
from win32con import GWL_STYLE, WS_CAPTION, WS_THICKFRAME, WS_SYSMENU, GCL_STYLE
from wx.lib.agw.fmresources import CS_DROPSHADOW

from lib.exceptions import SceneNotFoundError

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def set_appwindow(root):
    """Change the window flags to allow an overrideredirect window to be
    shown on the taskbar.
    (See https://stackoverflow.com/a/30819099/291641)
    """
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)


    class Margins(Structure):
        _fields_ = [("cxLeftWidth", c_int),
                    ("cxRightWidth", c_int),
                    ("cyTopHeight", c_int),
                    ("cyBottomHeight", c_int)]

    class BlurBehind(Structure):
        _fields_ = [("dwFlags", wintypes.DWORD),  # 0x00000001),
                   ("fEnable", c_bool),  # True),
                   ("hRgnBlur", wintypes.HRGN)]  # None)]

    # windll.DwmApi.DwmEnableBlurBehindWIndow(hwnd,
    #                                         True)

    hwnd = win32gui.GetParent(root.winfo_id())
    l_style = win32gui.GetWindowLong(hwnd, GWL_STYLE)
    l_style &= ~(WS_CAPTION | WS_THICKFRAME | WS_SYSMENU)
    # l_style &= ~(WS_SYSMENU)
    # l_style &= WS_SYSMENU
    # l_style = WS_CAPTION | WS_BORDER | WS_SYSMENU | WS_MINIMIZEBOX
    win32gui.SetWindowLong(hwnd, GWL_STYLE, l_style)
    l_style = win32api.GetWindowLong(hwnd, GCL_STYLE)
    l_style |= CS_DROPSHADOW
    win32api.SetWindowLong(hwnd, GCL_STYLE, l_style)

    DWM_BB_ENABLE = 0x0001
    DWM_BB_BLURREGION = 0x0002
    DWM_BB_TRANSITIONMAXIMIZED = 0x0003
    WM_DWMCOMPOSITIONCHANGED = 0x031E

    class DWM_BLURBEHIND(Structure):
        """
        http://msdn.microsoft.com/en-us/library/windows/desktop/aa969500%28v=vs.85%29.aspx
        """
        _fields_ = [
            ('dwFlags', DWORD),
            ('fEnable', c_bool),
            ('hRgnBlur', HRGN),
            ('fTransitionOnMaximized', c_bool)
        ]

    def DWM_enable_blur_behind_window(hwnd, enable=True):
        """
        Enable or disable blur behind window on a window.
        """
        # if not has_dwm:
        #     return False

        bb = DWM_BLURBEHIND()
        bb.fEnable = c_bool(enable)
        bb.dwFlags = DWM_BB_ENABLE
        bb.hRgnBlur = None

        result = _DwmEnableBlurBehindWindow(hwnd, bb)

        return not result

    # prototype = WINFUNCTYPE(c_int, c_int, POINTER(DWM_BLURBEHIND))
    # params = (1, "hWnd", 0), (1, "pBlurBehind", 0)
    # _DwmEnableBlurBehindWindow = prototype(("DwmEnableBlurBehindWindow",
    # windll.dwmapi), params)
    #
    # print(DWM_enable_blur_behind_window(hwnd, True))

    # windll.DwmApi.DwmEnableBlurBehindWindow(hwnd, BlurBehind(0x00000001, True, None))
    # windll.DwmApi.DwmExtendFrameIntoClientArea(hwnd, Margins(-1))
    # re-assert the new window style
    root.wm_withdraw()
    root.wm_deiconify()


class Downloader(object):
    def __init__(self, url, fp):
        from threading import Thread
        self._url = url
        self._fp = fp
        self.fileSize = 1
        self.downloadedBytes = 0
        self._downloaded: bool = False

        # Thread(None, self.download).start()

    def is_downloading(self):
        return not self._downloaded

    def download(self):
        thread = Thread(target=self._download, name="DownloadThread")
        thread.start()
        return thread

    # noinspection PyUnboundLocalVariable
    def _download(self):
        import urllib.request
        import os

        self._downloaded = False

        dat = None

        while dat is None:
            # Get the total number of bytes of the file to download before downloading
            u = urllib.request.urlopen(str(self._url))
            if os.path.exists(self._fp):
                os.remove(self._fp)
            meta = u.info()
            dat = meta["Content-Length"]
        self.fileSize = int(dat)

        if os.path.split(self._fp)[0] != "":
            if not os.path.exists(os.path.split(self._fp)[0]):
                os.makedirs(os.path.split(self._fp)[0])

        with open(self._fp, "ab+") as f:
            while True:
                block = u.read(1024)
                self.downloadedBytes += len(block)
                _hash = ((60 * self.downloadedBytes) // self.fileSize)
                if not len(block):
                    active = False
                    break
                f.write(block)
            f.close()

        u.close()

        self._downloaded = True


SCENES: Dict[str, 'Scene'] = {}
CURRENT_SCENE: Optional['Scene'] = None


class SceneManager(object):
    def __init__(self):
        self.allowClose = True
        # self.currentScene: Optional[Scene] = None
        # self.currentSceneName: Optional[str] = None

    def add_scene(self, scene: 'Scene', name: str) -> None:
        SCENES[name] = scene

    def change_scene(self, name, *args, **kwargs):
        global CURRENT_SCENE
        global CURRENT_SCENE_NAME
        if name not in SCENES.keys():
            print(list(SCENES.keys()))
            raise SceneNotFoundError(f"scene '{name}' not existent")

        # Hide old scene first
        if CURRENT_SCENE is not None:
            CURRENT_SCENE.hide_scene()

        # Get new scene and show it
        new_scene = SCENES[name]
        CURRENT_SCENE_NAME = name
        CURRENT_SCENE = new_scene
        CURRENT_SCENE.show_scene(*args, **kwargs)


class Scene(object):
    scenemanager = SceneManager()

    def __init__(self, root):
        self._frame = tkinter.Frame(root, width=800, height=600, bg=ACCENT)

    def hide_scene(self):
        self._frame.pack_forget()

    def show_scene(self, *args, **kwargs):
        self._frame.pack(fill="both", expand=True)

    def start_scene(self):
        pass

    def update(self):
        pass

    def tick_update(self):
        pass

    def __repr__(self):
        return f"SceneObject<{self.__class__.__name__}>"


class CanvasScene(Scene):
    def __init__(self, root):
        super(CanvasScene, self).__init__(root)
        self.canvas = Canvas(self.frame, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def __repr__(self):
        return super(CanvasScene, self).__repr__()


class WizardPage(Scene):
    def __init__(self, root: 'Main', *, arrow_left: Tuple[bool, Callable[[], Any]],
                 arrow_right: Tuple[bool, Callable[[], Any]]):
        super(WizardPage, self).__init__(root)

        self.frame = Frame(self._frame)

        self._root = root

        self.arrowLeft = arrow_left[0]
        self.arrowRight = arrow_right[0]

        self.arrowLeftCanvas = None
        self.arrowRightCanvas = None

        self.hovered = {}
        self.pressed = {}
        self.commands = {}

        # if arrow_left[0]:
        self._create_arrow(side="left", command=arrow_left[1])
        # if arrow_right[0]:
        self._create_arrow(side="right", command=arrow_right[1])

        self.pageFrame = Frame(self.frame)
        self.pageFrame.pack(fill="both", expand=True, padx=25, pady=30)
        self.frame.pack(padx=1, pady=1, fill="both", expand=True)

    def _on_button_motion(self, canvas: Canvas, id_, x, evt):
        _, y = canvas.coords(id_)
        if distance(x, y, evt.x, evt.y) < 49:
            if not self.pressed[canvas]:
                canvas.itemconfig(id_, image=self._root.arrowImages["circle"][1])
            self.hovered[canvas] = True
        else:
            canvas.itemconfig(id_, image=self._root.arrowImages["circle"][0])
            self.hovered[canvas] = False

    def _on_button_leave(self, canvas: Canvas, id_, x, evt):
        _, y = canvas.coords(id_)
        if distance(x, y, evt.x, evt.y) >= 49:
            canvas.itemconfig(id_, image=self._root.arrowImages["circle"][0])
            self.hovered[canvas] = False

    def _on_button_press(self, canvas: Canvas, id_, x, evt):
        _, y = canvas.coords(id_)
        if distance(x, y, evt.x, evt.y) < 49:
            canvas.itemconfig(id_, image=self._root.arrowImages["circle"][-1])
            self.pressed[canvas] = True

    def _on_button_release(self, canvas: Canvas, id_, x, evt):
        _, y = canvas.coords(id_)
        if distance(x, y, evt.x, evt.y) < 49:
            canvas.itemconfig(id_, image=self._root.arrowImages["circle"][0])
            self.pressed[canvas] = False
            if canvas in self.commands.keys():
                self.commands[canvas]()

    def change_command(self, *, side, command: Callable[[], Any]):
        if side.lower() == "left":
            c = self.arrowLeftCanvas
            self.commands[c] = command
        elif side.lower() == "right":
            c = self.arrowRightCanvas
            self.commands[c] = command
        else:
            raise ValueError("Invalid side: %s, must be either left or right" % side)

    def create_arrow(self, *, side, command: Callable[[], Any]):
        if side.lower() in ["left", "right"]:
            circle_image = self._root.arrowImages["circle"][0]
            arrow_image = self._root.arrowImages[side]
        else:
            raise ValueError("Invalid side: %s, must be either left or right" % side)

        h = 480
        w = 50

        if side.lower() == "left":
            c = self.arrowLeftCanvas
            self.commands[c] = command
            x = -60 + 50
            self.arrowLeft = True
            if self.arrowLeft:
                id_circ = self.arrowLeftCanvas.create_image(-60, h / 2, image=circle_image, anchor="w", tags=("button",))
                id_arro = self.arrowLeftCanvas.create_image(24, h / 2, image=arrow_image, anchor="e", tags=("button",))
        else:
            c = self.arrowRightCanvas
            self.commands[c] = command
            x = w + 60 - 50
            self.arrowRight = True
            if self.arrowRight:
                id_circ = self.arrowRightCanvas.create_image(w + 60, h / 2, image=circle_image, anchor="e",
                                                             tags=("button",))
                id_arro = self.arrowRightCanvas.create_image(w - 24, h / 2, image=arrow_image, anchor="w", tags=("button",))
        c.tag_bind("button", "<Motion>", lambda evt: self._on_button_motion(c, id_circ, x, evt))
        c.tag_bind("button", "<Leave>", lambda evt: self._on_button_leave(c, id_circ, x, evt))
        c.tag_bind("button", "<ButtonPress>", lambda evt: self._on_button_press(c, id_circ, x, evt))
        c.tag_bind("button", "<ButtonRelease>", lambda evt: self._on_button_release(c, id_circ, x, evt))


    def _create_arrow(self, *, side, command: Callable[[], Any]):
        if side.lower() in ["left", "right"]:
            circle_image = self._root.arrowImages["circle"][0]
            arrow_image = self._root.arrowImages[side]
        else:
            raise ValueError("Invalid side: %s, must be either left or right" % side)

        h = 480
        w = 50

        bind = False

        if side.lower() == "left":
            c = self.arrowLeftCanvas = Canvas(self.frame, width=w, highlightthickness=0, bg="#ffffff")
            self.commands[c] = command
            self.hovered[c] = False
            self.pressed[c] = False
            self.arrowLeftCanvas.pack(side=side, fill="y")
            x = -60 + 50
            if self.arrowLeft:
                id_circ = self.arrowLeftCanvas.create_image(-60, h / 2, image=circle_image, anchor="w", tags=("button",))
                id_arro = self.arrowLeftCanvas.create_image(24, h / 2, image=arrow_image, anchor="e", tags=("button",))
                bind=True
        else:
            c = self.arrowRightCanvas = Canvas(self.frame, width=w, highlightthickness=0, bg="#ffffff")
            self.commands[c] = command
            self.hovered[c] = False
            self.pressed[c] = False
            self.arrowRightCanvas.pack(side=side, fill="y")
            x = w + 60 - 50
            if self.arrowRight:
                id_circ = self.arrowRightCanvas.create_image(w + 60, h / 2, image=circle_image, anchor="e",
                                                             tags=("button",))
                id_arro = self.arrowRightCanvas.create_image(w - 24, h / 2, image=arrow_image, anchor="w", tags=("button",))
                bind=True

        if bind:
            c.tag_bind("button", "<Motion>", lambda evt: self._on_button_motion(c, id_circ, x, evt))
            c.tag_bind("button", "<Leave>", lambda evt: self._on_button_leave(c, id_circ, x, evt))
            c.tag_bind("button", "<ButtonPress>", lambda evt: self._on_button_press(c, id_circ, x, evt))
            c.tag_bind("button", "<ButtonRelease>", lambda evt: self._on_button_release(c, id_circ, x, evt))

    def show_scene(self, *args, **kwargs):
        super(WizardPage, self).show_scene(*args, **kwargs)
        # print("Show Scene")

    def hide_scene(self):
        super(WizardPage, self).hide_scene()


class PythonInstaller(Downloader):
    def __init__(self, progressbar, root: 'Main', description: List[Label]):
        self.progressBar: Progressbar = progressbar
        self.root: Main = root
        self.description: List[Label] = description
        self.options = list()
        self.options.append("/quiet")
        self.options.append("InstallAllUsers=1")
        self.options.append("CompileAll=1")
        self.options.append("PrependPath=1")

    def download_url(self):
        """
        Returns 64-bit python installer url if system is 64-bit else the 32-bit version.
        Does not support 16-bit installation (The QBubbles Installer won't even open)

        :return:
        """

        url_x64 = "https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe"  # 64-bit / amd64 / x86-64 / x64
        url_x86 = "https://www.python.org/ftp/python/3.7.7/python-3.7.7.exe"  # 32-bit / i386 / x86

        if platform.architecture()[0] == "64bit":
            return url_x64
        else:
            return url_x86

    def download(self):
        url = self.download_url()

        downloader = Downloader(url, fp="python377-installer.exe")
        downloader.download()

        self.progressBar.config(maximum=downloader.fileSize)

        while downloader.is_downloading():
            self.progressBar.config(value=downloader.downloadedBytes, maximum=downloader.fileSize)
            self.description[0].config(text=f"Downloaded {downloader.downloadedBytes} Bytes of {downloader.fileSize} Bytes\n"
                                            f"{int(100 * downloader.downloadedBytes / downloader.fileSize)}% downloaded"
                                            f"\n\n")
            self.root.update()

    def install(self):
        t = Thread(target=lambda: os.system("python377-installer.exe" + " ".join(self.options)), name="PythonInstaller")
        t.start()

        while t.is_alive():
            self.root.update()

        self.progressBar.config(value=self.progressBar.cget("maximum"))


class PythonDownloadPage(WizardPage):
    def __init__(self, root):
        super(PythonDownloadPage, self).__init__(root, arrow_left=(False, lambda: None), arrow_right=(False, lambda: None))

        self.title = Label(self.pageFrame, text="Downloading Python 3.7.7...", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="...",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        self.progressBar = Progressbar(self.pageFrame, maximum=100, value=0)
        self.pyInstaller = PythonInstaller(progressbar=self.progressBar, root=self._root, description=[self.description])
        self.progressBar.pack(fill="x")

    def show_scene(self, *args, **kwargs):
        super(PythonDownloadPage, self).show_scene(*args, **kwargs)
        self._root.sceneManager.allowClose = False
        self._root.update()
        self.pyInstaller.download()
        self._root.sceneManager.allowClose = True
        self.create_arrow(side="right", command=lambda: self.scenemanager.change_scene("pythonInstallation"))


class InstallationOptionsPage(WizardPage):
    def __init__(self, root):
        super(InstallationOptionsPage, self).__init__(
            root, arrow_left=(False, lambda: None),
            arrow_right=(True, lambda: self.scenemanager.change_scene("pythonDownload")))

        self.title = Label(self.pageFrame, text="Choose your install options:", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        self.installDirFrame = Frame(self.pageFrame, height=24)
        # self.installDirLabel = Label(self.installDirFrame, text="Choose install directory:  ")
        self.installDirEntry = Entry(self.installDirFrame)
        self.installDirEntry.insert("end", f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Programs\\QBubbles")
        self.installDirButton = Button(self.installDirFrame, text="...", width=5, command=self.open_dir)
        self.installDirButton.pack(side="right")
        self.installDirEntry.pack(side="right", fill="both", expand=True)
        # self.installDirLabel.pack(side="right", fill="y")
        self.installDirFrame.pack(fill="x")

    def hide_scene(self):
        super(InstallationOptionsPage, self).hide_scene()

        self._root.installationDirectory = self.installDirEntry.get()

    def open_dir(self):
        initialdir = self.installDirEntry.get()
        if not os.path.exists(self.installDirEntry.get()):
            initialdir = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Programs\\"

        directory = tkinter.filedialog.askdirectory(parent=self.installDirFrame, initialdir=initialdir,
                                                 title="Select Installation Directory.", mustexist=False)
        directory: str
        if directory:
            directory = os.path.join(directory, "QBubbles").replace("/", os.sep)
            self.installDirEntry.delete("0", "end")
            self.installDirEntry.insert("end", directory)
        # print(dialog.directory)


class PythonInstallationPage(WizardPage):
    def __init__(self, root):
        super(PythonInstallationPage, self).__init__(root, arrow_left=(False, lambda: None), arrow_right=(False, lambda: None))

        self.title = Label(self.pageFrame, text="Installing Python 3.7.7...", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="There will be a prompt for installing.",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        self.progressBar = Progressbar(self.pageFrame, maximum=100, value=0)
        self.pyInstaller = PythonInstaller(progressbar=self.progressBar, root=self._root, description=[self.description])
        self.progressBar.pack(fill="x")

    def show_scene(self, *args, **kwargs):
        super(PythonInstallationPage, self).show_scene(*args, **kwargs)
        self._root.sceneManager.allowClose = False
        self._root.update()
        self.pyInstaller.install()
        self._root.sceneManager.allowClose = True
        self.create_arrow(side="right", command=lambda: self.scenemanager.change_scene("launcherDownloader"))


class LauncherInstaller(object):
    def __init__(self, progressbar, root: 'Main', description: List[Label]):
        self.progressBar: Progressbar = progressbar
        self.root: Main = root
        self.description: List[Label] = description
        self.options = list()
        self.options.append("/quiet")
        self.options.append("InstallAllUsers=1")
        self.options.append("CompileAll=1")
        self.options.append("PrependPath=1")

    def create_shortcuts(self):
        import os, winshell
        from win32com.client import Dispatch
        desktop = winshell.desktop()
        winshell.start_menu()
        path = os.path.join(desktop, "Media Player Classic.lnk")
        target = r""+os.path.join(self.root.installationDirectory, self.root.executable)
        wDir = r"P:\Media\Media Player Classic"
        icon = r"P:\Media\Media Player Classic\mplayerc.exe"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()

    def get_downloadurl(self):
        """
        Returns 64-bit python installer url if system is 64-bit else the 32-bit version.
        Does not support 16-bit installation (The QBubbles Installer won't even open)

        :return:
        """
        import urllib.request
        import urllib.error
        import http.client

        request: http.client.HTTPResponse = urllib.request.urlopen(
            "https://github.com/Qboi123/QBubblesInstaller/raw/master/launcherdata.json")

        raw_json = request.read()
        data = json.loads(raw_json)
        url = data["DownloadUrl"]

        self.root.executable = data["ExecutablePath"]

        return url

        # if platform.architecture()[0] == "64bit":
        #     return url_x64
        # else:
        #     return url_x86

    def download(self):
        url = self.get_downloadurl()

        downloader = Downloader(url, fp="qbubbleslauncher.zip")
        downloader.download()

        self.progressBar.config(maximum=downloader.fileSize)

        while downloader.is_downloading():
            self.progressBar.config(value=downloader.downloadedBytes, maximum=downloader.fileSize)
            self.description[0].config(text=f"Downloaded {downloader.downloadedBytes} Bytes of {downloader.fileSize} Bytes\n"
                                            f"{int(100 * downloader.downloadedBytes / downloader.fileSize)}% downloaded"
                                            f"\n\n")
            self.root.update()

    def extract(self):
        zipfile = ZipFile("qbubbleslauncher.zip", "r")

        members = zipfile.namelist()
        # print(members)

        path = self.root.installationDirectory
        # print(path)

        self.progressBar.config(maximum=len(members))

        for index in range(len(members)):
            self.progressBar.config(value=index+1)
            self.description[0].config(text=f"Extracting: qbubbleslauncher.zip/{members[index]}")
            zipfile._extract_member(members[index], path, None)

    def install(self):
        t = Thread(target=lambda: self.extract(), name="PythonInstaller")
        t.start()

        while t.is_alive():
            self.root.update()

        self.progressBar.config(value=self.progressBar.cget("maximum"))


class LauncherDownloaderPage(WizardPage):
    def __init__(self, root):
        super(LauncherDownloaderPage, self).__init__(root, arrow_left=(False, lambda: None),
                                                     arrow_right=(False, lambda: None))

        self.title = Label(self.pageFrame, text="Downloading the Launcher...", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="...",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        self.progressBar = Progressbar(self.pageFrame, maximum=100, value=0)
        self.launcherInstaller = LauncherInstaller(
            progressbar=self.progressBar, root=self._root, description=[self.description])
        self.progressBar.pack(fill="x")

    def show_scene(self, *args, **kwargs):
        super(LauncherDownloaderPage, self).show_scene(*args, **kwargs)
        self._root.sceneManager.allowClose = False
        self._root.update()
        self.launcherInstaller.download()
        self._root.sceneManager.allowClose = True
        self.create_arrow(side="right", command=lambda: self.scenemanager.change_scene("launcherInstallation"))


class LauncherInstallationPage(WizardPage):
    def __init__(self, root):
        super(LauncherInstallationPage, self).__init__(root, arrow_left=(False, lambda: None),
                                                     arrow_right=(False, lambda: None))

        self.title = Label(self.pageFrame, text="Downloading the Launcher...", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="...",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        self.progressBar = Progressbar(self.pageFrame, maximum=100, value=0)
        self.launcherInstaller = LauncherInstaller(
            progressbar=self.progressBar, root=self._root, description=[self.description])
        self.progressBar.pack(fill="x")

    def show_scene(self, *args, **kwargs):
        super(LauncherInstallationPage, self).show_scene(*args, **kwargs)
        self._root.sceneManager.allowClose = False
        self._root.update()
        self.launcherInstaller.install()
        self._root.sceneManager.allowClose = True
        self.create_arrow(side="right", command=lambda: print("Launcher Installed, no new page found!!")) # self.scenemanager.change_scene("launcherDownloader"))


class StartPage(WizardPage):
    def __init__(self, root):
        super(StartPage, self).__init__(root, arrow_left=(False, lambda: print("Previous Page")),
                                        arrow_right=(True, lambda: self.scenemanager.change_scene("installationOptions")))

        # self.create_arrow(side="left")

        self.title = Label(self.pageFrame, text="Welcome to QBubbles Installer!", font=("helvetica", 32))
        self.title.pack(fill="x", padx=2, pady=7)

        self.description = Label(self.pageFrame,
                                 text="Use the arrow buttons to navigate between pages\n"
                                      "You can't cancel the installation while installing Python or QBubbles.",
                                 font=("helvetica", 12))
        self.description.pack(fill="x", padx=2, pady=5)

        if platform.system() == "Windows":
            self.info = Label(self.pageFrame, text=f"Your operating system is: Windows {platform.win32_ver()[0]}.\n"
                                                   f"    NT Version: {platform.win32_ver()[1]}.\n",
                              font=("helvetica", 12))
            self.info.pack(fill="x", padx=2, pady=5)
        elif platform.system() == "Linux":
            self.info = Label(self.pageFrame, text=f"Your operating system is: {platform.system()}.\n"
                                                   f"   Distro: <Unknown>")
            self.info.pack(fill="x", padx=2, pady=5)

        # self.create_arrow(side="right")

    def show_scene(self, *args, **kwargs):
        super(StartPage, self).show_scene(*args, **kwargs)
        # print(self._frame.pack_info())


def create_button_element(root, name, id_):
    """Create some custom button elements from the Windows theme.
    Due to a parsing bug in the python wrapper, call Tk directly."""
    root.eval('''ttk::style element create {0} vsapi WINDOW {1} {{
        {{pressed !selected}} 3
        {{active !selected}} 2
        {{pressed selected}} 6
        {{active selected}} 5
        {{selected}} 4
        {{}} 1
    }} -syssize {{SM_CXVSCROLL SM_CYVSCROLL}}'''.format(name, id_))


# noinspection PyProtectedMember
class TitleFrame(Widget):
    """Frame based class that has button elements at one end to
    simulate a windowmanager provided title bar.
    The button click event is handled and generates virtual events
    if the click occurs over one of the button elements."""
    windows = {}
    cache = {}

    # noinspection PyPep8Naming,PyUnusedLocal
    def __init__(self, master, **kw):
        self.point = None
        kw['style'] = 'Title.Frame'
        kw['class'] = 'TitleFrame'

        Widget.__init__(self, master, 'ttk::frame', kw)

        if "closeImage" in TitleFrame.cache:
            closeImage = TitleFrame.cache["closeImage"]
        else:
            closeImage = ImageTk.PhotoImage(Image.open("img/closeButton.png"))
            TitleFrame.cache["closeImage"] = closeImage
        if "closeImageHover" in TitleFrame.cache:
            closeImageHover = TitleFrame.cache["closeImageHover"]
        else:
            closeImageHover = ImageTk.PhotoImage(Image.open("img/closeButtonPressed.png"))
            TitleFrame.cache["closeImageHover"] = closeImageHover
        if "closeImagePressed" in TitleFrame.cache:
            closeImagePressed = TitleFrame.cache["closeImagePressed"]
        else:
            closeImagePressed = ImageTk.PhotoImage(Image.open("img/closeButtonHover.png"))
            TitleFrame.cache["closeImagePressed"] = closeImagePressed

        self.closeBtn = Canvas(self, bg=ACCENT, width=33, height=33, highlightthickness=0)
        w, h = self.closeBtn.winfo_width(), self.closeBtn.winfo_height()
        self.closeBtn.create_rectangle(-1, 0, 32, 33, outline=ACCENT)
        self.closeBtn.create_image(3, 4, image=closeImage, anchor="nw", tags=("button",))
        TitleFrame.windows[master._root()] = {"closeBtn": self.closeBtn}
        self.closeBtn.bind("<ButtonPress-1>", self.on_press)
        self.closeBtn.bind('<B1-Motion>', self.on_motion)
        self.closeBtn.bind('<ButtonRelease-1>', self.on_release)
        self.closeBtn.bind("<Enter>", self.on_enter)
        self.closeBtn.bind('<Leave>', self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind('<B1-Motion>', self.on_motion)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.closeBtn.pack(side="right")

    # noinspection PyUnusedLocal
    @staticmethod
    def register(root):
        """Register the custom window style for a titlebar frame.
        Must be called once at application startup."""
        style = Style()
        # create_button_element(root, 'close', 18)
        # create_button_element(root, 'minimize', 15)
        # create_button_element(root, 'maximize', 17)
        # create_button_element(root, 'restore', 21)

        # label = Label(T, )

        style.layout('Title.Frame', [
            ('Title.Frame.border', {'sticky': 'nswe', 'children': [
                ('Title.Frame.padding', {'sticky': 'nswe'}  # 'children': [
                 # ('Title.Frame.close', {'side': 'right', 'sticky': ''}),
                 # ('Title.Frame.maximize', {'side': 'right', 'sticky': ''}),
                 # ('Title.Frame.minimize', {'side': 'right', 'sticky': ''})
                 )
            ]})
        ])
        style.configure('Title.Frame', padding=(12, 1, 12, 1), background=ACCENT)
        style.map('Title.Frame', **style.map('TEntry'))
        # root.bind_class('TitleFrame', '<ButtonPress-1>', TitleFrame.on_press)
        # root.bind_class('TitleFrame', '<B1-Motion>', TitleFrame.on_motion)
        # root.bind_class('TitleFrame', '<ButtonRelease-1>', TitleFrame.on_release)

    @staticmethod
    def on_press(event):
        if event.widget == TitleFrame.windows[event.widget._root()]["closeBtn"]:
            event.widget.master.point = None
        else:
            event.widget.master.point = (event.x_root, event.y_root)
        # element = event.widget.master.identify(event.x,event.y)
        # if element == 'close':
        #     event.widget.event_generate('<<TitleFrameClose>>')
        # elif element == 'minimize':
        #     event.widget.event_generate('<<TitleFrameMinimize>>')
        # elif element == 'restore':
        #     event.widget.event_generate('<<TitleFrameRestore>>')
        # else:
        #     print(element)

    @staticmethod
    def on_enter(event):
        # event.widget.point = (event.x_root,event.y_root)
        # element = event.widget.identify(event.x,event.y)
        if event.widget == TitleFrame.windows[event.widget._root()]["closeBtn"]:
            event.widget.itemconfig("button", image=TitleFrame.cache["closeImageHover"])
            event.widget.config(bg="#ffffff")
        # if element == 'close':
        #     event.widget.event_generate('<<TitleFrameClose>>')
        # elif element == 'minimize':
        #     event.widget.event_generate('<<TitleFrameMinimize>>')
        # elif element == 'restore':
        #     event.widget.event_generate('<<TitleFrameRestore>>')
        # else:
        #     print(element)

    @staticmethod
    def on_leave(event):
        # event.widget.point = (event.x_root,event.y_root)
        # element = event.widget.identify(event.x,event.y)
        if event.widget == TitleFrame.windows[event.widget._root()]["closeBtn"]:
            event.widget.itemconfig("button", image=TitleFrame.cache["closeImage"])
            event.widget.config(bg=ACCENT)
        # if element == 'close':
        #     event.widget.event_generate('<<TitleFrameClose>>')
        # elif element == 'minimize':
        #     event.widget.event_generate('<<TitleFrameMinimize>>')
        # elif element == 'restore':
        #     event.widget.event_generate('<<TitleFrameRestore>>')
        # else:
        #     print(element)

    @staticmethod
    def on_motion(event):
        """Use the relative distance since the last motion or buttonpress event
        to move the application window (this widgets toplevel)"""
        print(event.widget.master.point)
        if event.widget.master.point:
            app = event.widget.master.winfo_toplevel()
            dx = event.x_root - event.widget.master.point[0]
            dy = event.y_root - event.widget.master.point[1]
            x = app.winfo_rootx() + dx
            y = app.winfo_rooty() + dy
            # app.wm_geometry('+{0}+{1}'.format(x,y))
            if y > 1008:
                y = 1008
            win32gui.SetWindowPos(win32gui.GetParent(app.winfo_id()), -2, x, y, 800, 480, 0x0040)
            event.widget.master.point = (event.x_root, event.y_root)

    @staticmethod
    def on_release(event):
        event.widget.point = None
        if event.widget == TitleFrame.windows[event.widget._root()]["closeBtn"]:
            event.widget.event_generate('<<TitleFrameClose>>')


class Main(Tk):
    # noinspection PyProtectedMember,PyUnusedLocal
    def __init__(self, argv):
        super(Main, self).__init__()
        self.wm_attributes("-alpha", 0)

        self.installationDirectory: Optional[str] = None
        self.executable: Optional[str] = None

        TitleFrame.register(self)
        # self.overrideredirect(True)
        # self.wm_attributes('-toolwindow', 'splash')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (800 / 2)
        y_coordinate = (screen_height / 2) - (480 / 2)
        # self.update()
        self.geometry("{}x{}+{}+{}".format(800, 480, int(x_coordinate), int(y_coordinate)))
        title_bar = TitleFrame(self, height=32, width=800)
        title_bar.pack(side="top", fill="x")

        arrow_left = Image.open("img/arrowLeft.png")  # .resize((12, 12), Image.ANTIALIAS)
        arrow_right = Image.open("img/arrowRight.png")  # .resize((12, 12), Image.ANTIALIAS)
        arrow_circle_m1 = Image.open("img/navButtonMinus1.png")
        arrow_circle = Image.open("img/navButtonNormal.png")
        arrow_circle_p1 = Image.open("img/navButtonPlus1.png")
        self.arrowImages = {
            "left": ImageTk.PhotoImage(arrow_left),
            "right": ImageTk.PhotoImage(arrow_right),
            "circle": {
                -1: ImageTk.PhotoImage(arrow_circle_m1),
                0: ImageTk.PhotoImage(arrow_circle),
                +1: ImageTk.PhotoImage(arrow_circle_p1)
            }
        }

        # self.wm_geometry("800x480")

        style = Style()
        style.theme_settings(theme_name, theme)
        style.theme_use(theme_name)

        for key, value in config.items():
            style.configure(key, **value)

        for key, value in layout.items():
            style.layout(key, value)

        for key, value in options.items():
            if "*" in key:
                raise ValueError("Option key must not contain '*'")
            type_old = key.replace(".", "*")
            type_ = "*" + type_old + "*"
            # print("LOOP A:", type_, type_old, key, value)
            for key2, value2 in value.items():
                # print(f"LOOP B: root_.option_add({repr(type_ + key2)}, {repr(value2)})")
                self.option_add(type_ + key2, value2)

        if hasattr(sys, "_MEIPASS"):
            os.chdir(sys._MEIPASS)

        icon_pillow: Image.Image = Image.open("img/icon.png")
        icon_pillow = icon_pillow.convert("1")
        icon_tk = ImageTk.PhotoImage(icon_pillow)
        tkinter.BitmapImage()
        self.iconbitmap('img/icon.ico')

        self.update()

        # self.withdraw()

        self.iconify()

        time.sleep(2)

        self.deiconify()

        self.sceneManager = SceneManager()
        self.sceneManager.add_scene(StartPage(self), "startScene")
        self.sceneManager.add_scene(InstallationOptionsPage(self), "installationOptions")
        self.sceneManager.add_scene(PythonDownloadPage(self), "pythonDownload")
        self.sceneManager.add_scene(PythonInstallationPage(self), "pythonInstallation")
        self.sceneManager.add_scene(LauncherDownloaderPage(self), "launcherDownloader")
        self.sceneManager.add_scene(LauncherInstallationPage(self), "launcherInstallation")
        # print(scene_manager._scenes)
        self.sceneManager.change_scene("startScene")

        self.bind('<<TitleFrameClose>>', lambda ev: self.destroy() if self.sceneManager.allowClose else None)
        self.bind('<<TitleFrameMinimize>>', lambda ev: self.wm_iconify())
        # self.bind('<Key-Escape>', lambda ev: self.destroy())
        self.after(10, lambda: set_appwindow(self))

        win32gui.SetWindowPos(self.winfo_id(), -2, int(x_coordinate), int(y_coordinate), 800, 480, 0x0040)

        self.wm_attributes("-alpha", 1)
        # self.mainloop()

        # PythonInstallationPage(self)


# noinspection PyGlobalUndefined
def main():
    if platform.system() == 'Windows':
        print(f"Platform used is: Windows {platform.win32_ver()[0]} {platform.architecture()[0]}")
    else:
        print(f"Platform used is: {platform.system()}")

    global ACCENT
    global theme_name
    global theme
    global config
    global layout
    global options
    from lib.theme import theme, theme_name, config, layout, ACCENT, options

    def test():
        root_ = Tk()
        root_.wm_geometry("800x600")

        style = Style()
        style.theme_settings(theme_name, theme)
        style.theme_use(theme_name)

        for key, value in config.items():
            style.configure(key, **value)

        for key, value in layout.items():
            style.layout(key, value)

        for key, value in options.items():
            if "*" in key:
                raise ValueError("Option key must not contain '*'")
            type_old = key.replace(".", "*")
            type_ = "*" + type_old + "*"
            # print("LOOP A:", type_, type_old, key, value)
            for key2, value2 in value.items():
                # print(f"LOOP B: root_.option_add({repr(type_ + key2)}, {repr(value2)})")
                root_.option_add(type_ + key2, value2)

        style = Style()
        # create_button_element(root, 'close', 18)
        # create_button_element(root, 'minimize', 15)
        # create_button_element(root, 'maximize', 17)
        # create_button_element(root, 'restore', 21)

        # label = Label(T, )

        style.layout('Title.Frame', [
            ('Title.Frame.border', {'sticky': 'nswe', 'children': [
                ('Title.Frame.padding', {'sticky': 'nswe'}  # 'children': [
                 # ('Title.Frame.close', {'side': 'right', 'sticky': ''}),
                 # ('Title.Frame.maximize', {'side': 'right', 'sticky': ''}),
                 # ('Title.Frame.minimize', {'side': 'right', 'sticky': ''})
                 )
            ]})
        ])
        style.configure('Title.Frame', padding=(12, 1, 12, 1), background=ACCENT)
        style.map('Title.Frame', **style.map('TFrame'))
        # root.bind_class('TitleFrame', '<ButtonPress-1>', TitleFrame.on_press)
        # root.bind_class('TitleFrame', '<B1-Motion>', TitleFrame.on_motion)
        # root.bind_class('TitleFrame', '<ButtonRelease-1>', TitleFrame.on_release)

        frame_ = Frame(root_)
        radio1_ = Radiobutton(frame_, text="Hallo")
        radio1_.grid(row=0, column=0)
        radio2_ = Radiobutton(frame_, text="Hallo")
        radio2_.grid(row=0, column=1)
        check1_ = Checkbutton(frame_, text="Hallo")
        check1_.grid(row=1, column=0)
        check2_ = Checkbutton(frame_, text="Hallo")
        check2_.grid(row=1, column=1)

        entry = Entry(frame_, text="Test001")
        entry.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        combobox = Combobox(frame_, values=("0", "1", "2", "3", "4", "5", "6"))
        combobox.grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        treeview = Treeview(frame_, columns=("Col1",), height=5)
        a = treeview.insert("", "end", text="Number 1")
        treeview.heading("#0", text="Column 1")
        treeview.heading("#1", text="Column 2")
        treeview.insert(a, "end", text="Letter A")
        treeview.insert(a, "end", text="Letter B")
        # treeview.item()
        treeview.grid(row=3, column=0, padx=2, pady=2)

        treeview2 = Treeview(frame_, columns="Col1", height=5)
        a = treeview2.insert("", "end", text="Number 1")
        treeview2.heading("#0", text="Column 1")
        treeview2.heading("#1", text="Column 2")
        treeview2.insert(a, "end", text="Letter A")
        treeview2.insert(a, "end", text="Letter B")
        treeview2.state(["disabled"])
        # treeview.item()
        treeview2.grid(row=3, column=1, padx=2, pady=2)

        button1 = Button(frame_, text="TButton 1")
        button1.grid(row=4, column=0, padx=2, pady=2, sticky="ew")
        button2 = Button(frame_, text="TButton 2")
        button2.state(["disabled"])
        button2.grid(row=4, column=1, padx=2, pady=2, sticky="ew")

        frame_.pack(fill="both", expand=True)

        # Root Mainloop
        root_.mainloop()

    # exit()

    Main(sys.argv[1:]).mainloop()


if __name__ == '__main__':
    main()
