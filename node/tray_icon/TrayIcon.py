from pathlib import Path
from threading import Thread, Event
import os
import logging
from time import sleep
import traceback
import webbrowser

import win32api
import win32gui
import win32con
import winerror

from node.NodeConfig import NodeConfig
from node.tray_icon.TrayIconConstants import TrayIconCommandId


log = logging.getLogger()


class TrayIcon():
    def __init__(self, websocket_instance):        
        self.websocket_instance = websocket_instance       
        self.hwnd = None
        self.node_config = NodeConfig()
        self.already_destroyed = False

    def _message_loop_func(self):
        self._register_window()

        # Runs a message loop until a WM_QUIT message is received.
        win32gui.PumpMessages()

    
    def _register_window(self):
        if self.hwnd:
            return

        # Register the Window class.
        message_map = {
            win32gui.RegisterWindowMessage("Chia Manager Client Taskbar Created"): self._restart,
            win32con.WM_DESTROY: self.destroy,
            win32con.WM_COMMAND: self._command,
            win32con.WM_USER + 20: self._notify,
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "Chia Manager Client"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map  # could also specify a wndproc.

        # Don't blow up if class already registered to make testing easier
        try:
            _ = win32gui.RegisterClass(wc)
        except win32gui.error as err_info:
            if err_info.winerror != winerror.ERROR_CLASS_ALREADY_EXISTS:
                log.exception(traceback.format_exc())

        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName,
            "Chia Manager Client Taskbar",
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None,
        )
        win32gui.UpdateWindow(self.hwnd)

        # create tray icon
        self._create()

    def start(self):
        self._message_loop_thread = Thread(
            target=self._message_loop_func,
            name="Thread-TrayIcon",
            daemon=True,
            )
        self._message_loop_thread.start()

    def _create(self):
        log.info("Create tray icon")
        icon = Path('chia_manager.ico')

        if icon.exists():
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hinst = win32api.GetModuleHandle(None)
            hicon = win32gui.LoadImage(
                hinst, str(icon), win32con.IMAGE_ICON, 0, 0, icon_flags
            )
        else:
            log.error("Can't find chia_manager.ico - using default")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "Chia Manager Client")
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except win32gui.error:
            # This is common when windows is starting, and this code is hit
            # before the taskbar has been created.
            # but keep running anyway - when explorer starts, we get the
            # TaskbarCreated message.
            log.error("Failed to add the taskbar icon - is explorer running?")

    def _restart(self, hwnd, msg, wparam, lparam):
        self._create()

    def destroy(self, *args):
        """Destroy the tray icon"""
        if self.already_destroyed:
            log.debug("TrayIcon already destroyed!")
            return

        log.info("Destroy tray icon")

        nid = (self.hwnd, 0)
        try:
            win32gui.PostMessage(self.hwnd ,win32con.WM_CLOSE, 0, 0)
        except BaseException as exc:
            if exc.args[0] == -2147467259:
                # catch the 'Unknown Error'
                log.error(
                    "Unhandled exception: TrayIcon might not able to be created " \
                    "because the Chia Manager Client crashed or closed before."
                )
            log.exception(traceback.format_exc())

        self.already_destroyed = True
        log.info("Destroy tray icon.. Done!")
        

    def _notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_RBUTTONUP:
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, TrayIconCommandId.OPEN_WEB_UI, "Open ChiaManager")
            win32gui.AppendMenu(menu, win32con.MF_STRING, TrayIconCommandId.OPEN_CONFIG, "Open Config")
            win32gui.AppendMenu(menu, win32con.MF_STRING, TrayIconCommandId.EXIT, "Exit")
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(
                menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None
            )
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1


    def _command(self, hwnd, msg, wparam, lparam):
        id = win32api.LOWORD(wparam)
        # first is 10
        if id == TrayIconCommandId.OPEN_WEB_UI:
            webbrowser.open_new_tab(
                f"https://{self.node_config['Connection']['server']}:{self.node_config['Connection']['port']}"
            )
        elif id == TrayIconCommandId.OPEN_CONFIG:
            log.debug("Open node config")
            os.startfile(self.node_config.chia_config_file)
        elif id == TrayIconCommandId.EXIT:
            log.debug("Exit triggerd by tray icon.")
            self.websocket_instance.stop_websocket = True
        else:
            log.error(f"Unknown Tray command - {id}")
