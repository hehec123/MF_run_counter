from init import *
from utils import tk_dynamic as tkd
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import screeninfo


def build_time_str(elap):
    hours = int(elap / 3600)
    minutes = int(elap / 60 - hours * 60.0)
    seconds = int(elap - hours * 3600.0 - minutes * 60.0)
    hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
    return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)


def get_monitor_from_coord(x, y):
    monitors = screeninfo.get_monitors()

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]


def get_displaced_coords(root, app_x, app_y, pos_x=None, pos_y=None):
    if pos_x is None:
        pos_x = root.winfo_rootx()
    if pos_y is None:
        pos_y = root.winfo_rooty()
    mon = get_monitor_from_coord(root.winfo_rootx(), root.winfo_rooty())
    min_x = mon.x
    min_y = mon.y
    max_x = mon.width + min_x
    max_y = mon.height + min_y

    displaced_x = max(min(pos_x, max_x - app_x - 10), min_x - 5)
    displaced_y = max(min(pos_y, max_y - app_y), min_y)

    return '%sx%s+%s+%s' % (app_x, app_y, displaced_x, displaced_y)


class RegistrationForm:
    def __init__(self, root, coords, first_profile):
        self.new_win = tk.Tk()
        self.new_win.title('Profile registration')
        self.new_win.wm_attributes('-topmost', 1)
        self.new_win.resizable(False, False)

        geom = get_displaced_coords(root, 290, 185, coords[0], coords[1])
        self.new_win.geometry(geom)
        # self.new_win.eval('tk::PlaceWindow . center')
        self.new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        self.allowed_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

        if first_profile:
            la = tk.Label(self.new_win, text='Please create your first profile.', font='Helvetica 14')
        else:
            la = tk.Label(self.new_win, text='Profile registration', font='Helvetica 14')
        la.pack()

        self.a1 = self.make_entry_row('Profile name')
        self.a2 = self.make_entry_row('Character name')
        self.a3 = self.make_entry_row('Run type')
        self.a4 = self.make_combobox_row('Game mode', ['Single Player', 'Multiplayer'])

        # Restrict input to profile name, only allowing characters that can appear in a windows file name
        vcmd = (self.new_win.register(self.validate_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.a1.config(validate='key', validatecommand=vcmd)

        tk.Button(self.new_win, text='Submit', font='helvetica 12 bold', command=self.b1_action, bd=2).pack(fill=tk.X, expand=tk.YES)
        self.new_win.bind('<KeyPress-Return>', func=self.b1_action)
        self.new_win.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        self.new_win.protocol("WM_DELETE_WINDOW", self.close_mod)
        self.a1.focus_set()

    def b1_action(self, event=None):
        try:
            a1 = self.a1.get()
            a2 = self.a2.get()
            a3 = self.a3.get()
            a4 = self.a4.get()

            x = {'Profile name': a1, 'Character name': a2, 'Run type': a3, 'Game mode': a4}
        except AttributeError:
            self.returning = None
            self.new_win.quit()
        else:
            self.returning = x
            self.new_win.quit()

    def make_entry_row(self, text):
        frame = tk.Frame(self.new_win)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(frame, width=22, text=text + ': ', anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar()
        out = tk.Entry(frame, textvariable=var)
        out.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return out

    def make_combobox_row(self, text, values):
        frame = tk.Frame(self.new_win)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(frame, width=22, text=text + ': ', anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar()
        out = ttk.Combobox(frame, textvariable=var, state='readonly', values=values)
        out.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        out.set(values[0])
        return out

    def validate_input(self, *args):
        if args[0] == '1':
            return args[4] in self.allowed_chars
        else:
            return True

    def close_mod(self):
        self.returning = None
        self.new_win.quit()


def registration_form(root, coords=None, first_profile=False):
    reg_form = RegistrationForm(root, coords, first_profile)
    reg_form.new_win.focus_force()
    reg_form.new_win.mainloop()

    reg_form.new_win.destroy()
    return reg_form.returning


class MultiEntryBox(object):
    def __init__(self, entries, coords, title):
        self.enum = len(entries)
        root = self.root = tk.Tk()
        self.root.focus_set()
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        root.title(title)
        self.root.wm_attributes("-topmost", True)

        frm_1 = tk.Frame(root)
        frm_1.pack(ipadx=4, ipady=2)

        for i, e in enumerate(entries):
            ff = tk.Frame(frm_1)
            ff.pack()
            tk.Label(ff, font='arial 11', text=e, width=8).pack(side=tk.LEFT, expand=True, fill=tk.X, pady=3)
            setattr(self, 'e' + str(i), tk.Entry(ff, font=('arial', 11), justify='center'))
            getattr(self, 'e' + str(i)).pack(side=tk.LEFT, expand=True, fill=tk.X)
            if i == 0:
                getattr(self, 'e' + str(i)).focus_set()

        # button frame
        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        btn_1 = tk.Button(frm_2, width=8, text='OK')
        btn_1['command'] = self.b1_action
        btn_1.pack(side='left')

        btn_2 = tk.Button(frm_2, width=8, text='Cancel')
        btn_2['command'] = self.close_mod
        btn_2.pack(side='left')

        # The enter button will trigger button 1, while escape will close the window
        root.bind('<KeyPress-Return>', func=self.b1_action)
        root.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        root.update_idletasks()
        if coords:
            xp = coords[0]
            yp = coords[1]
        else:
            xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
            yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        root.deiconify()

    def b1_action(self, event=None):
        self.returning = [getattr(self, 'e' + str(i)).get() for i in range(self.enum)]
        self.root.quit()

    def close_mod(self):
        self.returning = None
        self.root.quit()

def mebox(entries, coords=False, title='Message'):
    msgbox = MultiEntryBox(entries, coords, title)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


class MessageBox(object):
    def __init__(self, msg, b1, b2, entry, coords, title, hyperlink):
        root = self.root = tk.Tk()
        self.root.focus_set()
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        root.title(title)
        # self.root.attributes("-toolwindow", True)
        self.root.wm_attributes("-topmost", True)
        self.msg = str(msg)

        # ctrl+c to copy self.msg
        root.bind('<Control-c>', func=self.to_clip)

        # default values for the buttons to return
        self.b1_return = True
        self.b2_return = False

        # if b1 or b2 is a tuple unpack into the button text & return value
        if isinstance(b1, tuple):
            b1, self.b1_return = b1
        if isinstance(b2, tuple):
            b2, self.b2_return = b2

        # main frame
        frm_1 = tk.Frame(root)
        frm_1.pack(ipadx=4, ipady=2)

        # the message
        message = tk.Label(frm_1, text=self.msg, font=('arial', 11))
        message.pack(padx=8, pady=8)

        # if entry or hyperlink is True create and set focus
        if hyperlink:
            self.button = tk.Label(frm_1, text=release_repo, fg="blue", cursor="hand2", font=('arial', 11))
            self.button.pack()
            self.button.bind("<Button-1>", lambda e: webbrowser.open_new(hyperlink))
        if entry:
            self.entry = tk.Entry(frm_1, font=('arial', 11), justify='center')
            self.entry.pack()
            self.entry.focus_set()

        # button frame
        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        btn_1 = tk.Button(frm_2, width=8, text=b1)
        btn_1['command'] = self.b1_action
        btn_1.pack(side='left')
        if not entry:
            btn_1.focus_set()
        if b2 != '':
            btn_2 = tk.Button(frm_2, width=8, text=b2)
            btn_2['command'] = self.b2_action
            btn_2.pack(side='left')

        # The enter button will trigger button 1, while escape will close the window
        root.bind('<KeyPress-Return>', func=self.b1_action)
        root.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        # Roughly center the box on screen. For accuracy see: https://stackoverflow.com/a/10018670/1217270
        root.update_idletasks()
        if coords:
            xp = coords[0]
            yp = coords[1]
        else:
            xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
            yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        root.deiconify()

    def b1_action(self, event=None):
        try:
            x = self.entry.get()
        except AttributeError:
            self.returning = self.b1_return
            self.root.quit()
        else:
            if x:
                self.returning = x
                self.root.quit()

    def b2_action(self, event=None):
        self.returning = self.b2_return
        self.root.quit()

    def close_mod(self):
        self.returning = None
        self.root.quit()

    def to_clip(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.msg)


def mbox(msg, b1='OK', b2='Cancel', entry=False, coords=False, title='Message', hyperlink=''):
    msgbox = MessageBox(msg, b1, b2, entry, coords, title, hyperlink)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


def add_circle(parent, pixels, color):
    canvas = tkd.Canvas(parent, width=pixels + 2, height=pixels + 2, borderwidth=0, highlightthickness=0)

    cpix = pixels // 2
    circ_id = canvas.create_circle(cpix, cpix, cpix, fill=color, width=0.5)  # outline = 'black'
    canvas.create_circle_arc(cpix, cpix, pixels // 2.2, style="arc", outline="white", width=pixels // 12.5,
                             start=270 - 25, end=270 + 25)
    return canvas, circ_id


def test_mapfile_path(game_path, char_name):
    if not os.path.exists(game_path) or game_path in ['', '.']:
        messagebox.showerror('Game path error', """Game path not found, please update the path in options (for PoD, it's ending with "/Path of Diablo/Save/Path of Diablo") \n\n"""
                                                'This session will continue in manual mode.')
        return False
    elif char_name == '':
        messagebox.showerror('Character name missing', 'Chosen profile has no character name specified. Create a new profile with a character name to use automode\n\n'
                                                       'This session will continue in manual mode.')
        return False
    elif not os.path.exists(os.path.join(game_path, char_name)):
        messagebox.showerror('Character file not found', 'Map file for specified character not found. Make sure the character name in chosen profile is identical to your in-game character name. If not, create a new profile with the correct character name\n\n'
                                                         'This session will continue in manual mode')
        return False
    return True


class Tooltip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        self.tipwindow.wm_attributes('-topmost', True)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    tooltip = Tooltip(widget)
    widget.bind('<Enter>', lambda event: tooltip.showtip(text))
    widget.bind('<Leave>', lambda event: tooltip.hidetip())


if __name__ == '__main__':
    r = tk.Tk()
    print(registration_form(r))
