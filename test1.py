#!/usr/bin/env python3
"""
Q: Trouble making a custom title bar in Tkinter

https://stackoverflow.com/q/49621671/291641
"""

import tkinter as tk
import tkinter.ttk as ttk
from ctypes import windll

GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

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
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())

def create_button_element(root, name, id):
    """Create some custom button elements from the Windows theme.
    Due to a parsing bug in the python wrapper, call Tk directly."""
    root.eval('''ttk::style element create {0} vsapi WINDOW {1} {{
        {{pressed !selected}} 3
        {{active !selected}} 2
        {{pressed selected}} 6
        {{active selected}} 5
        {{selected}} 4
        {{}} 1
    }} -syssize {{SM_CXVSCROLL SM_CYVSCROLL}}'''.format(name,id))

class TitleFrame(ttk.Widget):
    """Frame based class that has button elements at one end to
    simulate a windowmanager provided title bar.
    The button click event is handled and generates virtual events
    if the click occurs over one of the button elements."""
    def __init__(self, master, **kw):
        self.point = None
        kw['style'] = 'Title.Frame'
        kw['class'] = 'TitleFrame'
        ttk.Widget.__init__(self, master, 'ttk::frame', kw)
    @staticmethod
    def register(root):
        """Register the custom window style for a titlebar frame.
        Must be called once at application startup."""
        style = ttk.Style()
        create_button_element(root, 'close', 18)
        create_button_element(root, 'minimize', 15)
        create_button_element(root, 'maximize', 17)
        create_button_element(root, 'restore', 21)
        style.layout('Title.Frame', [
            ('Title.Frame.border', {'sticky': 'nswe', 'children': [
                ('Title.Frame.padding', {'sticky': 'nswe', 'children': [
                    ('Title.Frame.close', {'side': 'right', 'sticky': ''}),
                    ('Title.Frame.maximize', {'side': 'right', 'sticky': ''}),
                    ('Title.Frame.minimize', {'side': 'right', 'sticky': ''})
                ]})
            ]})
        ])
        style.configure('Title.Frame', padding=(1,1,1,1), background='#090909')
        style.map('Title.Frame', **style.map('TEntry'))
        root.bind_class('TitleFrame', '<ButtonPress-1>', TitleFrame.on_press)
        root.bind_class('TitleFrame', '<B1-Motion>', TitleFrame.on_motion)
        root.bind_class('TitleFrame', '<ButtonRelease-1>', TitleFrame.on_release)
    @staticmethod
    def on_press(event):
        event.widget.point = (event.x_root,event.y_root)
        element = event.widget.identify(event.x,event.y)
        if element == 'close':
            event.widget.event_generate('<<TitleFrameClose>>')
        elif element == 'minimize':
            event.widget.event_generate('<<TitleFrameMinimize>>')
        elif element == 'restore':
            event.widget.event_generate('<<TitleFrameRestore>>')
    @staticmethod
    def on_motion(event):
        """Use the relative distance since the last motion or buttonpress event
        to move the application window (this widgets toplevel)"""
        if event.widget.point:
            app = event.widget.winfo_toplevel()
            dx = event.x_root - event.widget.point[0]
            dy = event.y_root - event.widget.point[1]
            x = app.winfo_rootx() + dx
            y = app.winfo_rooty() + dy
            app.wm_geometry('+{0}+{1}'.format(x,y))
            event.widget.point=(event.x_root,event.y_root)
    @staticmethod
    def on_release(event):
        event.widget.point = None


class SampleApp(tk.Tk):
    """Example basic application class"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_geometry('320x240')

def main():
    app = SampleApp()
    TitleFrame.register(app)
    app.overrideredirect(True)
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x_coordinate = (screen_width/2) - (1050/2)
    y_coordinate = (screen_height/2) - (620/2)
    app.geometry("{}x{}+{}+{}".format(1050, 650, int(x_coordinate), int(y_coordinate)))
    title_bar = TitleFrame(app, height=20, width=1050)
    title_bar.place(x=0, y=0)
    app.bind('<<TitleFrameClose>>', lambda ev: app.destroy())
    app.bind('<<TitleFrameMinimize>>', lambda ev: app.wm_iconify())
    app.bind('<Key-Escape>', lambda ev: app.destroy())
    app.after(10, lambda: set_appwindow(app))
    app.mainloop()

if __name__ == "__main__":
    main()