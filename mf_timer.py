import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import time
import os
import configparser
from system_hotkey import SystemHotkey
from messagebox import mbox
import winsound
import webbrowser
import queue
import threading
__version__ = '0.7'
__release_repo__ = 'https://github.com/oskros/MF_counter_releases/releases'
# ===== Block 0 =====


class ThreadedSound(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        winsound.PlaySound(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'run_sound.wav'), winsound.SND_FILENAME)
        self.queue.put("Task finished")


class Config:
    # ===== Block 1 =====
    def default_config(self):
        config = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        # ===== Block 2 =====
        config['DEFAULT']['logging_path'] = ''
        config['DEFAULT']['single_player_mode'] = 'NOT_IMPLEMENTED'
        config['DEFAULT']['window_start_position'] = str((100, 100))
        config['DEFAULT']['tab_keys_global'] = '1'
        config['DEFAULT']['run_timer_delay_seconds'] = '0'
        config['DEFAULT']['always_on_top'] = '1'
        config['DEFAULT']['check_for_new_version'] = '1'
        config['DEFAULT']['enable_sound_effects'] = '0'

        config.add_section('VERSION')
        config['VERSION']['version'] = __version__

        config.add_section('KEYBINDS')
        config.set('KEYBINDS', '# Please only edit keybinds from within the app')
        config['KEYBINDS']['start_key'] = str(['alt', 'q'])
        config['KEYBINDS']['end_key'] = str(['alt', 'w'])
        config['KEYBINDS']['stopstart_key'] = str(['alt', 'e'])
        config['KEYBINDS']['drop_key'] = str(['alt', 'a'])
        config['KEYBINDS']['reset_key'] = str(['alt', 'r'])
        config['KEYBINDS']['quit_key'] = str(['alt', 'escape'])

        return config

    @staticmethod
    def delete_config_file():
        if os.path.isfile('mf_config.ini'):
            os.remove('mf_config.ini')

    @staticmethod
    def build_config_file(config):
        with open('mf_config.ini', 'w') as fo:
            config.write(fo)

    def load_config_file(self):
        if not os.path.isfile('mf_config.ini'):
            self.build_config_file(self.default_config())
        parser = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        with open('mf_config.ini') as fi:
            parser.read_file(fi)

        # ===== Block 3 =====

        try:
            ver = parser.get('VERSION', 'version')
        except:
            ver = 0
        if ver != __version__:
            self.delete_config_file()
            self.build_config_file(self.default_config())
            parser = self.load_config_file()
            messagebox.showinfo('Config file recreated', 'You downloaded a new version. Config file has been recreated.')
        return parser


class MFRunTimer(tk.Frame):
    def __init__(self, config, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.cfg = config
        self._start = 0.0
        self._session_start = time.time()
        self._sessiontime = 0.0
        self._laptime = 0.0
        self._running = False
        self.sessionstr = tk.StringVar()
        self.timestr = tk.StringVar()
        self.no_of_laps = tk.StringVar()
        self.min_lap = tk.StringVar()
        self.avg_lap = tk.StringVar()
        self.laps = []
        self._make_widgets()

        # ===== Block 4 =====

        self._update_session_time()

    def _make_widgets(self):
        # Make the time label.
        l0 = tk.Label(self, textvariable=self.sessionstr)
        self._set_time(self._sessiontime, for_session=True)
        l0.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l0.config(font=('arial', 10))

        l1 = tk.Label(self, textvariable=self.timestr)
        self._set_time(0, for_session=False)
        l1.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l1.config(font=('arial', 20))

        l2 = tk.Label(self, textvariable=self.no_of_laps)
        self._set_laps(is_running=False)
        l2.pack(fill=tk.X, expand=tk.NO, pady=4, padx=2)
        l2.config(font=('arial', 12))

        l3 = tk.Label(self, textvariable=self.min_lap)
        self._set_fastest()
        l3.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l3.config(font=('arial', 11))

        l4 = tk.Label(self, textvariable=self.avg_lap)
        self._set_average()
        l4.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l4.config(font=('arial', 11))

        lf0 = tk.LabelFrame(self)
        lf0.pack()
        lf0.config(borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(lf0, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf0, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set)
        self.m.bindtags((self.m, self, "all"))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5, padx=2)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_lap_time(self):
        self._laptime = time.time() - self._start
        self._set_time(self._laptime, for_session=False)
        self._timer = self.after(50, self._update_lap_time)

    def _update_session_time(self):
        self._sessiontime = time.time() - self._session_start
        self._set_time(self._sessiontime, for_session=True)
        self.after(50, self._update_session_time)

    # ===== Block 5 =====

    def _set_time(self, elap, for_session):
        time_str = self._build_time_str(elap)
        if for_session:
            self.session_time_str = time_str
            self.sessionstr.set('Session time: ' + self.session_time_str)
        else:
            self.timestr.set(time_str)

    def _set_laps(self, is_running):
        run_count = len(self.laps)
        if is_running:
            run_count += 1
        self.no_of_laps.set('---- Run count: %s ----' % str(run_count))

    def _set_fastest(self):
        if self.laps:
            self.min_lap.set('Fastest time: %s' % self._build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % self._build_time_str(sum(self.laps)/len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    @staticmethod
    def _build_time_str(elap):
        hours = int(elap / 3600)
        minutes = int(elap / 60)
        seconds = int(elap - minutes * 60.0)
        hseconds = int((elap - minutes * 60.0 - seconds) * 10)
        return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)

    def queue_sound(self):
        self.queue = queue.Queue(maxsize=2)
        ThreadedSound(self.queue).start()
        self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            self.queue.get(False)
        except queue.Empty:
            self.master.after(50, self.process_queue)

    def Start(self, play_sound=True):
        def update_start():
            self._start = time.time() - self._laptime
            self._update_lap_time()
            self._set_laps(is_running=True)
            self._running = True

        if not self._running:
            delay = eval(self.cfg.get('DEFAULT', 'run_timer_delay_seconds'))
            if delay > 0:
                self.after(int(delay*1000), update_start)
            else:
                update_start()
            if play_sound and eval(self.cfg['DEFAULT']['enable_sound_effects']):
                self.queue_sound()

    def Stop(self, play_sound=True):
        if self._running:
            self.Lap()
            self._laptime = 0.0
            self._running = False
            self._set_time(0, for_session=False)
            self.after_cancel(self._timer)
            if play_sound and eval(self.cfg['DEFAULT']['enable_sound_effects']):
                self.queue_sound()

    def StopStart(self):
        self.Stop(play_sound=False)
        self.Start(play_sound=False)
        if eval(self.cfg['DEFAULT']['enable_sound_effects']):
            self.queue_sound()

    def Lap(self):
        if self._running:
            self.laps.append(self._laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + self._build_time_str(self.laps[-1]))
            self.m.yview_moveto(1)
            self._set_laps(is_running=False)
            self._set_fastest()
            self._set_average()


class Hotkeys(tk.Frame):
    def __init__(self, tab0, tab1, tab2, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.modifier_options = ['control', 'alt', 'shift', '']
        self.character_options = ['escape', 'space', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'NO_BIND']
        self.hk = SystemHotkey()

        lf0 = tk.LabelFrame(self)
        lf0.pack()
        lf0.config(borderwidth=0, highlightthickness=0, height=18)

        lf = tk.LabelFrame(self)
        lf.pack()

        lb = tk.Label(lf, text='Action/Modifier/Key                    ')
        lb.pack()

        self._start_run = eval(tab0.cfg['KEYBINDS']['start_key'])
        self._end_run = eval(tab0.cfg['KEYBINDS']['end_key'])
        self._stop_start = eval(tab0.cfg['KEYBINDS']['stopstart_key'])
        self._add_drop = eval(tab0.cfg['KEYBINDS']['drop_key'])
        self._reset = eval(tab0.cfg['KEYBINDS']['reset_key'])
        self._quit = eval(tab0.cfg['KEYBINDS']['quit_key'])

        self.add_hotkey('Start_run', self._start_run, tab1.Start)
        self.add_hotkey('End_run', self._end_run, tab1.Stop)
        self.add_hotkey('Stop_start', self._stop_start, tab1.StopStart)
        self.add_hotkey('Add_drop', self._add_drop, tab2.AddDrop)
        self.add_hotkey('Reset', self._reset, tab0.Reset)
        self.add_hotkey('Quit', self._quit, tab0.SaveQuit)

        if (any(x not in self.character_options for x in [self._start_run[1], self._end_run[1], self._add_drop[1], self._reset[1], self._quit[1]])
            or any(x not in self.modifier_options for x in [self._start_run[0], self._end_run[0], self._add_drop[0], self._reset[0], self._quit[0]])):
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()

    def add_hotkey(self, action, keys, func):
        default_modifier, default_key = keys
        action = action.lower()
        lf = tk.LabelFrame(self)
        lf.pack()

        lab = tk.Label(lf, text=action)
        lab.pack(side=tk.LEFT)
        lab.config(width=7)

        setattr(self, action + '_m', tk.StringVar())
        mod = getattr(self, action + '_m')
        mod.set(default_modifier)
        drop1 = tk.OptionMenu(lf, mod, *self.modifier_options)
        drop1.config(width=7, indicatoron=0)
        drop1.pack(side=tk.LEFT)

        setattr(self, action + '_e', tk.StringVar())
        key = getattr(self, action + '_e')
        key.set(default_key)
        drop2 = tk.OptionMenu(lf, key, *self.character_options)
        drop2.config(width=7, indicatoron=0)
        drop2.pack(side=tk.LEFT, fill=tk.X)

        mod.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        key.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        if default_key != 'NO_BIND':
            reg_key = [keys[1]] if keys[0] == '' else keys
            self.hk.register(reg_key, callback=lambda event: func())

    def re_register(self, event, old_hotkey, func):
        new_hotkey = [getattr(self, event + '_m').get(), getattr(self, event + '_e').get()]
        if new_hotkey in [list(x) for x in list(self.hk.keybinds.keys())]:
            messagebox.showerror('Reserved bind', 'This keybind is already in use.')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        elif new_hotkey == ['control', 'escape']:
            messagebox.showerror('Reserved bind', 'Control+escape is reserved for windows. This setting is not allowed')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        else:
            if old_hotkey[1] != 'NO_BIND':
                unreg = [old_hotkey[1]] if old_hotkey[0] == '' else old_hotkey
                self.hk.unregister(unreg)
            if new_hotkey[1] != 'NO_BIND':
                reg = [new_hotkey[1]] if new_hotkey[0] == '' else new_hotkey
                self.hk.register(reg, callback=lambda event: func(), overwrite=True)
            setattr(self, '_' + event, new_hotkey)


class Drops(tk.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.tab1 = tab1
        lf = tk.LabelFrame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(lf, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set)
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5, padx=2)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(self, text='Delete selection', command=self.delete).pack(side=tk.BOTTOM)

    def AddDrop(self):
        drop = mbox('Input your drop', entry=True)
        if drop is False:
            return
        run_no = len(self.tab1.laps)
        if self.tab1._running:
            run_no += 1
        self.m.insert(tk.END, 'Run %s: %s' % (run_no, drop))
        self.m.yview_moveto(1)

    def delete(self):
        selection = self.m.curselection()
        if selection:
            self.m.delete(selection[0])


class Help(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label = tk.Label(self, text="""
        Widget can be dragged on the banner.
        Please check your "mf_config.ini" file
        located in the running directory.
        
        Ctrl+Shift+PgUp/PgDn switches tabs. global 
        or only when focused is chosen in config. 
        All other hotkeys are always global and 
        should work while you are in-game.
        
        Widget position and hotkeys changed within 
        the app are saved to config. Please do not 
        change hotkeys directly in the config file.

        Single player mode has not yet been added,
        but when implemented it can monitor local
        save files to automatically start/end your
        runs.""", justify=tk.LEFT)
        label.pack(fill='both', anchor=tk.NW)
        label.place(x=-23, y=-14)


class About(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label = tk.Label(self, text="""
        Run counter for Diablo 2 developed in July 
        2019 by *oskros on Path of Diablo.
        
        Current version: %s
        
        Visit the page below for new releases""" % __version__, justify=tk.LEFT)
        label.pack()
        label.place(x=-23, y=-15)

        link1 = tk.Label(self, text="Release Hyperlink", fg="blue", cursor="hand2")
        link1.pack(side=tk.BOTTOM)
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(__release_repo__))


class Main(Config):
    def __init__(self):
        # Create root
        self.root = tk.Tk()

        # Build/load config file
        self.cfg = self.load_config_file()

        # Check for version
        if eval(self.cfg['DEFAULT']['check_for_new_version']):
            self.check_newest_version()

        # Modify root window
        self.root.resizable(False, False)
        # self.root.attributes('-type', 'dock')
        # self.root.overrideredirect(True)
        self.root.config(borderwidth=3, relief='raised')
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.wm_attributes("-topmost", eval(self.cfg['DEFAULT']['always_on_top']))
        self.root.title('MF run counter')
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.SaveQuit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico'))

        # Build banner image
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        img_panel = tk.Label(self.root, image=img)
        img_panel.pack()

        # Build tabs
        self.tabcontrol = ttk.Notebook(self.root)
        self.tab1 = MFRunTimer(self.cfg, self.tabcontrol)
        self.tab2 = Drops(self.tab1, parent=self.tabcontrol)
        self.tab3 = Hotkeys(self, self.tab1, self.tab2, parent=self.tabcontrol)
        self.tab4 = Help(self.tabcontrol)
        self.tab5 = About(self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Timer')
        self.tabcontrol.add(self.tab2, text='Drops')
        self.tabcontrol.add(self.tab3, text='Hotkeys')
        self.tabcontrol.add(self.tab4, text='Help')
        self.tabcontrol.add(self.tab5, text='About')
        self.tabcontrol.pack(expand=1, fill='both')

        # Add buttons to main widget
        lf = tk.LabelFrame(self.root)
        lf.pack()
        tk.Button(lf, text='Start run', command=self.tab1.Start).pack(side=tk.LEFT)
        tk.Button(lf, text='End run', command=self.tab1.Stop).pack(side=tk.LEFT)
        tk.Button(lf, text='Add drop', command=self.tab2.AddDrop).pack(side=tk.LEFT)
        tk.Button(lf, text='Reset', command=self.Reset).pack(side=tk.LEFT)
        tk.Button(lf, text='Quit', command=self.SaveQuit).pack(side=tk.LEFT)

        # Make window drag on the banner image
        img_panel.bind("<ButtonPress-1>", self._start_move)
        img_panel.bind("<ButtonRelease-1>", self._stop_move)
        img_panel.bind("<B1-Motion>", self._on_motion)

        # Register some hidden keybinds
        self.root.bind("<Delete>", lambda event: self.tab2.delete())
        self.root.bind("<Escape>", lambda event: self.SaveQuit())
        if eval(self.cfg['DEFAULT']['tab_keys_global']):
            self.tab3.hk.register(['control', 'shift', 'next'], callback=lambda event: self._next_tab())
            self.tab3.hk.register(['control', 'shift', 'prior'], callback=lambda event: self._prev_tab())
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self._next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self._prev_tab())

        # Open the widget
        self.root.mainloop()

    def _next_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        nxt_idx = tabs.index(cur_tab) + 1
        if nxt_idx >= len(tabs):
            nxt_idx = 0
        self.tabcontrol.select(tabs[nxt_idx])

    def _prev_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        prev_idx = tabs.index(cur_tab) - 1
        if prev_idx < 0:
            prev_idx = len(tabs) - 1
        self.tabcontrol.select(tabs[prev_idx])

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))

    def Reset(self):
        yesno = messagebox.askyesno('Reset', 'Would you like to reset data?')
        if yesno:
            self.tab1._start = time.time()
            self.tab1._laptime = 0.0
            self.tab1._session_start = time.time()
            self.tab1.laps = []
            self.tab1.m.delete(0, tk.END)
            self.tab1._set_time(self.tab1._laptime, for_session=False)
            self.tab1._set_time(self.tab1._sessiontime, for_session=True)
            self.tab1._set_laps(is_running=self.tab1._running)
            self.tab1._set_fastest()
            self.tab1._set_average()

            self.tab2.m.delete(0, tk.END)

    def Save(self):
        today = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        cfg_save_path = os.path.normpath(self.cfg.get('DEFAULT', 'logging_path'))
        if cfg_save_path in ['DEFAULT', '']:
            save_path = today
        else:
            save_path = os.path.join(cfg_save_path, today)
        with open(save_path + '.txt', 'wb') as savefile:
            to_write = [
                'Total session time: ' + str(self.tab1.session_time_str) + '\r\n',
                'Average run time:   ' + self.tab1._build_time_str(sum(self.tab1.laps) / len(self.tab1.laps)) + '\r\n',
                'Fastest run time:   ' + self.tab1._build_time_str(min(self.tab1.laps)) + '\r\n',
                'Percentage spent in runs: ' + str(
                    round(sum(self.tab1.laps) * 100 / self.tab1._sessiontime, 2)) + '%\r\n',
                '\r\n'
            ]
            for s in to_write:
                savefile.write(bytes(s, 'utf-8'))

            droplist = self.tab2.m.get(0, tk.END)
            if droplist:
                savefile.write(bytes('Drops collected: \r\n', 'utf-8'))
                for drop in droplist:
                    savefile.write(bytes(drop + '\r\n', 'utf-8'))
                savefile.write(bytes('\r\n', 'utf-8'))

            savefile.write(bytes('Individual run times: \r\n', 'utf-8'))
            for n, lap in enumerate(self.tab1.laps, 1):
                str_n = ' ' * max(len(str(len(self.tab1.laps))) - len(str(n)), 0) + str(n)
                savefile.write(bytes('Run ' + str_n + ': ' + self.tab1._build_time_str(lap) + '\r\n', 'utf-8'))

    def WriteToConfig(self):
        cfg = self.cfg

        # Update position
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        cfg['DEFAULT']['window_start_position'] = str((x, y))

        # Update hotkeys
        cfg.remove_section('KEYBINDS')
        cfg.add_section('KEYBINDS')
        cfg.set('KEYBINDS', '# Please only edit keybinds from within the app')
        cfg['KEYBINDS']['start_key'] = str(self.tab3._start_run)
        cfg['KEYBINDS']['end_key'] = str(self.tab3._end_run)
        cfg['KEYBINDS']['stopstart_key'] = str(self.tab3._stop_start)
        cfg['KEYBINDS']['drop_key'] = str(self.tab3._add_drop)
        cfg['KEYBINDS']['reset_key'] = str(self.tab3._reset)
        cfg['KEYBINDS']['quit_key'] = str(self.tab3._quit)

        self.build_config_file(cfg)

    def SaveQuit(self):
        if self.tab1._running:
            self.tab1.Stop()
        if self.tab1.laps and messagebox.askyesno('Reset', 'Would you like to save results?'):
            self.Save()
        self.WriteToConfig()
        self.root.quit()

    @staticmethod
    def check_newest_version():
        try:
            import github_releases
            from packaging import version as pk_version
            latest = github_releases.get_releases('oskros/MF_counter_releases')[0]
            latest_ver = latest['tag_name']
            # webbrowser.open_new("https://github.com/oskros/MF_counter_releases/releases")
            if pk_version.parse(__version__) < pk_version.parse(latest_ver):
                tk.messagebox.showinfo('New version',
                                       'Your version is not up to date. Get the newest release from:'
                                       '\n%s' % __release_repo__)
        except:
            pass


Main()