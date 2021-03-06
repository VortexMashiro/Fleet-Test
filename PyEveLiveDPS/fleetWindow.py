
import tkinter as tk
import tkinter.font as tkFont
from peld import settings
import logging
import socketManager
import sys
import multiprocessing
import threading

class FleetWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        
        self.mainWindow = mainWindow
        self.counter = 0
        self.sockMgr = None
        
        characterEntries = mainWindow.characterDetector.menuEntries
        if len(characterEntries) == 0:
            self.destroy()
            tk.messagebox.showerror("错误", "请在进入舰队模式前选择一个人物")
            return
        characterIndex = mainWindow.characterDetector.selectedIndex.get()
        self.characterName = characterEntries[characterIndex]
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(9, weight=1)
        self.configure(pady=10)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("舰队模式")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("375x310")
        self.update_idletasks()
        
        characterFrame = tk.Frame(self)
        tk.Label(characterFrame, text="当前选择的人物 ").grid(row="0", column="1", sticky="w")
        nameLabel = tk.Label(characterFrame, text=self.characterName)
        font = tkFont.Font(font=nameLabel['font'])
        font.config(weight='bold')
        nameLabel['font'] = font
        nameLabel.grid(row="0", column="2", sticky="w")
        nameDescription = tk.Label(self, text="如果要使用其他人物进入舰队模式\n" +
                            " 请在主菜单的人物选项中选择")
        font = tkFont.Font(font=nameDescription['font'])
        font.config(slant='italic')
        nameDescription['font'] = font
        characterFrame.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        nameDescription.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="15", width="10").grid(row=self.counter+2, column="1", columnspan="2")
        self.counter += 3
        
        self.serverVar = tk.StringVar()
        self.serverVar.set(settings.fleetServer)
        self.addEntrySetting(self.serverVar, "选择服务器 ", 
                        "请按FC要求你更改的地址更改")
        
        self.modeVar = tk.IntVar()
        self.modeVar.set(1)
        tk.Radiobutton(self, text="我是舰队成员", variable=self.modeVar, value=1).grid(row=self.counter, column="1", sticky="w")
        self.counter += 1
        tk.Radiobutton(self, text="我是舰队Boss", variable=self.modeVar, value=2).grid(row=self.counter, column="1", sticky="w")
        self.counter += 1
        tk.Frame(self, height="10", width="10").grid(row=self.counter, column="1", columnspan="5")
        self.counter += 1
        
        self.lowCPUVar = tk.BooleanVar()
        self.lowCPUVar.set(False)
        lowCPUCheckbutton = tk.Checkbutton(self, text="使用性能模式(电脑很卡的话)", variable=self.lowCPUVar)
        lowCPUCheckbutton.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        descriptor = tk.Label(self, text="性能模式中大部分功能将被禁用，只保留网络传输功能")
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="10", width="10").grid(row=self.counter+2, column="1", columnspan="2")
        self.counter += 3
        
        tk.Frame(self, height="10", width="1").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="10")
        self.loginButton = tk.Button(buttonFrame, text="  登录  ", command=self.login)
        self.loginButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  取消  ", command=self.logout)
        cancelButton.grid(row="0", column="2")

        self.mainWindow.mainMenu.menu.delete(3)
        self.mainWindow.mainMenu.menu.insert_command(3, label="退出舰队模式", command=self.logout)
        self.mainWindow.mainMenu.menu.entryconfig(5, state=tk.DISABLED)
        self.mainWindow.mainMenu.menu.entryconfig(6, state=tk.DISABLED)
        self.mainWindow.characterMenu.configure(state=tk.DISABLED)
        
    def login(self):
        self.loginNotificationQueue = multiprocessing.Queue()
        #settings.fleetServer = self.serverVar.get()
        requestArgs = "/sso/login?read_fleet=esi-fleets.read_fleet.v1"
        if self.modeVar.get() == 1:
            requestArgs += "&login_type=member"
        else:
            requestArgs += "&write_fleet=esi-fleets.write_fleet.v1"
            requestArgs += "&login_type=fc"
        self.sockMgr = socketManager.SocketManager(self.serverVar.get(), self.characterName, requestArgs, self.loginNotificationQueue)
        self.sockMgr.start()
        self.loginButton.configure(state=tk.DISABLED)
        self.loginWindowThread = threading.Thread(target=self.waitForLogin, daemon=True)
        self.loginWindowThread.start()

    def waitForLogin(self):
        loginWindow = SocketNotificationWindow(self.loginNotificationQueue)
        if loginWindow.loginStatus:
            if self.lowCPUVar.get():
                settings.lowCPUMode = True
                self.mainWindow.animator.changeSettings()
            self.mainWindow.topLabel.configure(text="舰队模式 (" + self.characterName + ")")
            self.mainWindow.topLabel.grid()
            self.mainWindow.animator.queue = self.sockMgr.dataQueue
            self.destroy()
        
    def logout(self):
        if hasattr(self, 'loginWindowThread') and self.loginWindowThread.is_alive():
            self.sockMgr.terminate()
            self.sockMgr = None
            logging.info('Websocket process terminated')
            self.loginNotificationQueue.put(False)
        elif self.sockMgr:
            self.sockMgr.terminate()
            self.sockMgr = None
            logging.info('Websocket process terminated')
            if settings.lowCPUMode:
                settings.lowCPUMode = False
                self.mainWindow.animator.changeSettings()
            self.mainWindow.animator.queue = None
            self.mainWindow.topLabel.grid_remove()
        self.mainWindow.mainMenu.menu.delete(3)
        self.mainWindow.mainMenu.menu.insert_command(3, label="舰队模式", command=lambda: FleetWindow(self.mainWindow))
        self.mainWindow.mainMenu.menu.entryconfig(5, state="normal")
        self.mainWindow.mainMenu.menu.entryconfig(6, state="normal")
        self.mainWindow.characterMenu.configure(state="normal")
        self.destroy()
        
    def addEntrySetting(self, var, labelText, descriptorText):
        centerFrame = tk.Frame(self)
        centerFrame.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        label = tk.Label(centerFrame, text=labelText)
        label.grid(row=self.counter, column="1", sticky="w")
        entry = tk.Entry(centerFrame, textvariable=var, width=25)
        entry.grid(row=self.counter, column="2", sticky="w")
        descriptor = tk.Label(self, text=descriptorText)
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="10", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3

class SocketNotificationWindow(tk.Toplevel):
    def __init__(self, loginQueue):
        tk.Toplevel.__init__(self)
        
        self.configure(pady=10, padx=20)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("等待登录")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("200x50")
        self.update_idletasks()
            
        tk.Label(self, text='正在等待登录授权...').grid(row=1, column=1)

        self.loginStatus = loginQueue.get()

        self.destroy()
