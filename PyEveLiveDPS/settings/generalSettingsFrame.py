import tkinter as tk
import tkinter.font as tkFont
from peld import settings

class GeneralSettingsFrame(tk.Frame):
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = mainWindow
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(4, weight=1)
        self.configure(pady=10)
        tk.Frame(self, height="0", width="1").grid(row="0", column="0")
        tk.Frame(self, height="0", width="1").grid(row="0", column="4")
        self.counter = 0
        
        checkboxValue = tk.BooleanVar()
        checkboxValue.set(settings.getGraphDisabled())
        self.graphDisabled = tk.Checkbutton(self, text="禁用统计图", variable=checkboxValue)
        self.graphDisabled.var = checkboxValue
        self.graphDisabled.grid(row=self.counter, column="1", columnspan="2")
        descriptor = tk.Label(self, text="标签仍然会显示")
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2")
        tk.Frame(self, height="20", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3
        
        self.secondsVar = tk.StringVar()
        self.secondsVar.set(settings.getSeconds())
        self.addSetting(self.secondsVar, "DPS计算周期(秒):", 
                        "建议将此条设置为比你武器循环时间高一点的整数")
        
        self.intervalVar = tk.StringVar()
        self.intervalVar.set(settings.getInterval())
        self.addSetting(self.intervalVar, "图形绘制周期(毫秒):", 
                        "数值越低CPU负担越大")
        
        self.transparencyVar = tk.StringVar()
        self.transparencyVar.set(settings.getCompactTransparency())
        self.addSetting(self.transparencyVar, "Compat模式的透明度:", 
                        "100为不透明，0为全透明")
        
        
    def addSetting(self, var, labelText, descriptorText):
        centerFrame = tk.Frame(self)
        centerFrame.grid(row=self.counter, column="1", columnspan="2")
        label = tk.Label(centerFrame, text=labelText)
        label.grid(row=self.counter, column="1", sticky="e")
        entry = tk.Entry(centerFrame, textvariable=var, width=10)
        entry.grid(row=self.counter, column="2", sticky="w")
        descriptor = tk.Label(self, text=descriptorText)
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2")
        tk.Frame(self, height="20", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3
        
    def doSettings(self):
        try:
            secondsSetting = int(self.secondsVar.get())
        except ValueError:
            tk.messagebox.showerror("错误", "请输入DPS计算周期数值(秒)")
            return
        if (secondsSetting < 2 or secondsSetting > 600):
            tk.messagebox.showerror("错误", "请输入2-600之间的DPS计算周期数值")
            return  
        
        try:
            intervalSetting = int(self.intervalVar.get())
        except ValueError:
            tk.messagebox.showerror("错误", "请输入图形绘制周期数值(毫秒)")
            return
        if (intervalSetting < 10 or intervalSetting > 1000):
            tk.messagebox.showerror("错误", "请输入10-1000之间的图形绘制周期数值")
            return
        
        if ((secondsSetting*1000)/intervalSetting <= 10):
            tk.messagebox.showerror("错误", "DPS计算周期/图形绘制周期必须> 10.\n" +
                                   "如果这个比例小于10，软件没有足够的数据来绘制图形!")
            return
        
        if ((secondsSetting*1000)/intervalSetting < 20):
            okCancel = tk.messagebox.askokcancel("你确定要继续吗?", "DPS计算周期/图形绘制周期\n  < 20\n" +
                                   "这样虽然没有什么大问题,但是我们推荐提高你的DPS计算周期或者降低你的图形绘制周期来获得更好的图形体验.\n"
                                   "你确定要保存这些设定吗?")
            if not okCancel:
                return
            
        if (intervalSetting < 50):
            okCancel = tk.messagebox.askokcancel("你确定要继续吗?", "将图形绘制周期设置为小于50的数值会给CPU极大的压力，我们不推荐这样做."
                                                 "你确定要保存这些设定吗?")
            if not okCancel:
                return
            
        if (secondsSetting/intervalSetting > 1):
            okCancel = tk.messagebox.askokcancel("你确定要继续吗?", "DPS计算周期/图形绘制周期\n 现在 > 1\n" +
                                   "这样虽然没有什么大问题,但是我们推荐降低你的图形绘制周期来获得更好的性能.\n"
                                   "在DPS计算周期较高的时候你不需要如此低的绘制周期\n"
                                   "你确定要保存这些设定吗?")
            if not okCancel:
                return
            
        try:
            compactTransparencySetting = int(self.transparencyVar.get())
        except ValueError:
            tk.messagebox.showerror("错误", "请输入透明度数值")
            return
        if (compactTransparencySetting < 1 or compactTransparencySetting > 100):
            tk.messagebox.showerror("错误", "请输入1-100之间的透明度数值")
            return  
        
        return {"seconds": secondsSetting, "interval": intervalSetting, 
                "compactTransparency": compactTransparencySetting, "graphDisabled": self.graphDisabled.var.get()}
