import os
from QCompiler.qcompiler import QCompilerPYZ, QCompilerPYC, QCompilerEXE


os.chdir("QBubblesInstaller")

# pre_compiler = QCompilerPYC([], "QBubblesInstaller")
# compiler = QCompilerPYZ("QBubblesInstaller", "QBubblesInstaller.pyz", "__init__:main", False, pre_compiler, True)
compiler = QCompilerEXE(
        exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
                 "obj", "icon.png", ".git", "compiler.py", "dll", "game", "downloads", "out.png", "account.json",
                 "launcherdata.json", "args.txt", "src", "icons", "requirements.txt"],
        icon=None, main_folder=os.getcwd(), main_file="__init__.py",
        hidden_imports=["os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
                        "pkg_resources.py2_warn", "PIL.Image", "PIL.ImageTk", "PIL", "ctypes", "ctypes.windll",
                        "win32com", "win32con", "win32net", "win32api", "win32gui"],
        log_level="INFO", app_name="QBubblesInstaller", clean=True, hide_console=True, one_file=True, uac_admin=True)
compiler.reindex()
compiler.compile(compiler.get_command(compiler.get_args()))
