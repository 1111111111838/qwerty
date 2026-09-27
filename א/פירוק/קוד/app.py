# Source Generated with Decompyle++
# File: app.pyc (Python 3.14)

'''
app.py - QLYX Q8 Wallpaper Studio GUI Application
High-performance Canvas-based Wallpaper Manager with HD Preview & Live WOT Sync
'''
import os
import sys
import threading
import queue
import math
import colorsys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageFilter
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if not os.path.exists(os.path.join(BASE_DIR, 'assets')):
        _internal = os.path.join(os.path.dirname(sys.executable), '_internal')
        if os.path.exists(os.path.join(_internal, 'assets')):
            BASE_DIR = _internal
        else:
            BASE_DIR = os.path.dirname(sys.executable)
else:
    # NOTE(recovery): this else belongs to `if frozen` (decompiler mis-nested it);
    # without it BASE_DIR was undefined when run as a plain .py.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import spd_sjpg
import mmi_builder
import dll_generator
import theme_engine
import text_engine
ORIG_WP_DIR = os.path.join(BASE_DIR, 'assets', 'orig_wp')
CUSTOM_WP_DIR = os.path.join(BASE_DIR, 'assets', 'custom_user_wp')
os.makedirs(CUSTOM_WP_DIR, exist_ok = True)
TOTAL_WALLPAPERS = 70
THUMB_W = 144
THUMB_H = 192
CARD_W = 166
CARD_H = 276
GAP_X = 14
GAP_Y = 14
START_X = 16
START_Y = 16

def make_sharp_thumbnail(pil_image, size = (THUMB_W, THUMB_H)):
    '''
Downsamples image with high-quality Lanczos and subtle sharpening for crystal-clear clarity.
'''
    thumb = pil_image.resize(size, Image.Resampling.LANCZOS)
    return thumb.filter(ImageFilter.UnsharpMask(radius = 0.6, percent = 100, threshold = 2))


class ZoomDialog(tk.Toplevel):
    '''
Full 2x HD Zoom preview modal (480x640) for inspecting fine wallpaper details.
'''
    
    def __init__(self, parent, image, slot_num):
        '''תצוגת HD מוגדלת פי 2 (480x640) - טפט #'''
        super().__init__(parent)
        self.title(f'''תצוגת HD מוגדלת פי 2 (480x640) - טפט #{slot_num}''')
        self.geometry('520x750')
        self.resizable(False, False)
        self.configure(bg = '#181a1f')
        self.transient(parent)
        self.grab_set()
        lbl_title = tk.Label(self, text = f'''🔍 טפט #{slot_num} - רזולוציה מוכפלת פי 2 (480 × 640)''', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#181a1f')
        lbl_title.pack(pady = (14, 6))
        canvas = tk.Canvas(self, width = 480, height = 640, bg = '#111215', highlightthickness = 2, highlightbackground = '#06d6a0')
        canvas.pack(pady = 6)
        zoom_im = image.resize((480, 640), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(zoom_im)
        canvas.create_image(240, 320, image = self.tk_img)
        btn_close = tk.Button(self, text = 'סגור חלון', font = ('Segoe UI', 10, 'bold'), bg = '#3d405b', fg = '#ffffff', activebackground = '#2b2d42', activeforeground = '#ffffff', relief = 'flat', padx = 20, pady = 6, cursor = 'hand2', command = self.destroy)
        btn_close.pack(pady = (8, 12))
        return None



class ImageCropDialog(tk.Toplevel):
    '''
Dialog for previewing and choosing fit mode (Crop, Fit, Stretch) before applying.
Displays 1:1 native 240x320 preview for maximum clarity.
'''
    
    def __init__(self, parent, image_path, slot_num):
        '''התאמת תמונה - טפט #'''
        super().__init__(parent)
        self.title(f'''התאמת תמונה - טפט #{slot_num}''')
        self.geometry('460x650')
        self.resizable(False, False)
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        self.slot_num = slot_num
        self.raw_image = Image.open(image_path).convert('RGB')
        self.selected_mode = tk.StringVar(value = 'crop')
        self.result_image = None
        self._build_ui()
        self._update_preview()
        return None

    
    def _build_ui(self):
        '''הגדרת תמונה עבור טפט #'''
        lbl_title = tk.Label(self, text = f'''הגדרת תמונה עבור טפט #{self.slot_num}''', font = ('Segoe UI', 12, 'bold'), fg = '#f8f9fa', bg = '#22252a')
        lbl_title.pack(pady = (12, 4))
        lbl_sub = tk.Label(self, text = 'תצוגה מקדימה בגודל מסך מלא (240x320 פיקסלים)', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a')
        lbl_sub.pack(pady = (0, 6))
        self.preview_canvas = tk.Canvas(self, width = 240, height = 320, bg = '#111215', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.preview_canvas.pack(pady = 6)
        opts_frame = tk.LabelFrame(self, text = ' אופן התאמת התמונה למסך (240x320) ', font = ('Segoe UI', 10), fg = '#06d6a0', bg = '#22252a', padx = 12, pady = 6)
        opts_frame.pack(fill = 'x', padx = 24, pady = 6)
        modes = [
            ('crop', 'חיתוך ומרכוז למסך (מומלץ - שומר על איכות ללא עיוות)'),
            ('fit', 'התאמה מלאה עם שוליים שחורים (ללא חיתוך)'),
            ('stretch', 'מתיחה לגודל מסך מלא')]
        for val, txt in modes:
            rb = tk.Radiobutton(opts_frame, text = txt, value = val, variable = self.selected_mode, command = self._update_preview, font = ('Segoe UI', 9), fg = '#f8f9fa', bg = '#22252a', selectcolor = '#111215', activebackground = '#22252a', activeforeground = '#06d6a0')
            rb.pack(anchor = 'e', pady = 2)
        btn_frame = tk.Frame(self, bg = '#22252a')
        btn_frame.pack(fill = 'x', padx = 24, pady = (10, 14))
        btn_ok = tk.Button(btn_frame, text = '✔ שמור והחלף', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 16, pady = 6, cursor = 'hand2', command = self._on_ok)
        btn_ok.pack(side = 'right', padx = 6)
        btn_cancel = tk.Button(btn_frame, text = 'ביטול', font = ('Segoe UI', 10), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self.destroy)
        btn_cancel.pack(side = 'left', padx = 6)

    
    def _update_preview(self):
        mode = self.selected_mode.get()
        fitted = spd_sjpg.fit_image(self.raw_image, 240, 320, mode = mode)
        self.result_image = fitted
        self.tk_thumb = ImageTk.PhotoImage(fitted)
        self.preview_canvas.delete('all')
        self.preview_canvas.create_image(120, 160, image = self.tk_thumb)

    
    def _on_ok(self):
        '''wp_'''
        dest_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{self.slot_num}.png''')
        self.result_image.save(dest_path)
        sjpg_dest = os.path.join(CUSTOM_WP_DIR, f'''wp_{self.slot_num}.sjpg''')
        if os.path.exists(sjpg_dest):
            os.remove(sjpg_dest)
            return None



class WallpaperSwapDialog(tk.Toplevel):
    '''
Dialog for swapping / reordering wallpaper positions between two slots.
Shows side-by-side previews of Slot A and Slot B with real-time live updates.
'''
    
    def __init__(self, parent, initial_slot_a = 1, initial_slot_b = None):
        '''⇄ החלפת מיקומים בין טפטים'''
        super().__init__(parent)
        self.parent = parent
        self.title('⇄ החלפת מיקומים בין טפטים')
        self.geometry('540x510')
        self.resizable(False, False)
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        init_a = max(1, min(TOTAL_WALLPAPERS, initial_slot_a))
        if initial_slot_b is None:
            init_b = 1 if init_a != 1 else 2
        else:
            init_b = max(1, min(TOTAL_WALLPAPERS, initial_slot_b))
        self.slot_a_var = tk.IntVar(value = init_a)
        self.slot_b_var = tk.IntVar(value = init_b)
        self._thumb_a = None
        self._thumb_b = None
        self._build_ui()
        self._update_views()
        return None

    
    def _build_ui(self):
        '''⇄ החלפת מיקומים הדדית בין שני טפטים'''
        lbl_title = tk.Label(self, text = '⇄ החלפת מיקומים הדדית בין שני טפטים', font = ('Segoe UI', 13, 'bold'), fg = '#06d6a0', bg = '#22252a')
        lbl_title.pack(pady = (14, 2))
        lbl_desc = tk.Label(self, text = 'בחר שני טפטים כדי להחליף את התמונות שלהם אחד במקום השני:', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a')
        lbl_desc.pack(pady = (0, 10))
        cards_frame = tk.Frame(self, bg = '#22252a')
        cards_frame.pack(fill = 'x', padx = 20, pady = 4)
        col_a = tk.Frame(cards_frame, bg = '#1a1c23', padx = 12, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        col_a.pack(side = 'right', expand = True, fill = 'both', padx = (6, 0))
        row_sel_a = tk.Frame(col_a, bg = '#1a1c23')
        row_sel_a.pack(fill = 'x', pady = (0, 4))
        lbl_a = tk.Label(row_sel_a, text = 'טפט מקור:', font = ('Segoe UI', 9, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        lbl_a.pack(side = 'right', padx = (4, 0))
        self.spn_a = tk.Spinbox(row_sel_a, from_ = 1, to = TOTAL_WALLPAPERS, textvariable = self.slot_a_var, width = 5, font = ('Segoe UI', 10, 'bold'), justify = 'center', bg = '#111215', fg = '#06d6a0', insertbackground = '#06d6a0', command = self._update_views)
        self.spn_a.pack(side = 'right')
        self.spn_a.bind('<KeyRelease>', (lambda e: self._update_views()))
        self.canvas_a = tk.Canvas(col_a, width = 120, height = 160, bg = '#111215', highlightthickness = 1, highlightbackground = '#06d6a0')
        self.canvas_a.pack(pady = 6)
        self.lbl_tag_a = tk.Label(col_a, text = '', font = ('Segoe UI', 8), bg = '#1a1c23', fg = '#adb5bd')
        self.lbl_tag_a.pack()
        col_mid = tk.Frame(cards_frame, bg = '#22252a')
        col_mid.pack(side = 'right', padx = 6)
        btn_flip = tk.Button(col_mid, text = '⇄', font = ('Segoe UI', 16, 'bold'), bg = '#2b2d42', fg = '#06d6a0', activebackground = '#1e202e', activeforeground = '#00f5d4', relief = 'flat', padx = 10, pady = 4, cursor = 'hand2', command = self._flip_slots)
        btn_flip.pack(pady = 40)
        col_b = tk.Frame(cards_frame, bg = '#1a1c23', padx = 12, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        col_b.pack(side = 'right', expand = True, fill = 'both', padx = (0, 6))
        row_sel_b = tk.Frame(col_b, bg = '#1a1c23')
        row_sel_b.pack(fill = 'x', pady = (0, 4))
        lbl_b = tk.Label(row_sel_b, text = 'טפט יעד:', font = ('Segoe UI', 9, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        lbl_b.pack(side = 'right', padx = (4, 0))
        self.spn_b = tk.Spinbox(row_sel_b, from_ = 1, to = TOTAL_WALLPAPERS, textvariable = self.slot_b_var, width = 5, font = ('Segoe UI', 10, 'bold'), justify = 'center', bg = '#111215', fg = '#06d6a0', insertbackground = '#06d6a0', command = self._update_views)
        self.spn_b.pack(side = 'right')
        self.spn_b.bind('<KeyRelease>', (lambda e: self._update_views()))
        self.canvas_b = tk.Canvas(col_b, width = 120, height = 160, bg = '#111215', highlightthickness = 1, highlightbackground = '#06d6a0')
        self.canvas_b.pack(pady = 6)
        self.lbl_tag_b = tk.Label(col_b, text = '', font = ('Segoe UI', 8), bg = '#1a1c23', fg = '#adb5bd')
        self.lbl_tag_b.pack()
        self.lbl_summary = tk.Label(self, text = '', font = ('Segoe UI', 9), fg = '#06d6a0', bg = '#22252a', wraplength = 480, justify = 'center')
        self.lbl_summary.pack(pady = (10, 8))
        btn_row = tk.Frame(self, bg = '#22252a')
        btn_row.pack(fill = 'x', padx = 20, pady = (8, 14))
        self.btn_confirm = tk.Button(btn_row, text = '✔ בצע החלפה הדדית', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 18, pady = 7, cursor = 'hand2', command = self._on_confirm)
        self.btn_confirm.pack(side = 'right', padx = 6)
        btn_cancel = tk.Button(btn_row, text = 'ביטול', font = ('Segoe UI', 10), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 14, pady = 7, cursor = 'hand2', command = self.destroy)
        btn_cancel.pack(side = 'left', padx = 6)

    
    def _flip_slots(self):
        a = self.slot_a_var.get()
        b = self.slot_b_var.get()
        self.slot_a_var.set(b)
        self.slot_b_var.set(a)
        self._update_views()

    
    def _update_views(self):
        
        try:
            a = int(self.slot_a_var.get())
            b = int(self.slot_b_var.get())
        except Exception:
            return None

        a = max(1, min(TOTAL_WALLPAPERS, a))
        b = max(1, min(TOTAL_WALLPAPERS, b))
        item_a = self.parent.slot_state.get(a)
        if item_a and item_a.get('image'):
            im_a = item_a['image'].resize((120, 160), Image.Resampling.LANCZOS)
            self._thumb_a = ImageTk.PhotoImage(im_a)
            self.canvas_a.delete('all')
            self.canvas_a.create_image(60, 80, image = self._thumb_a)
            is_c_a = item_a.get('is_custom', False)
            self.lbl_tag_a.config(text = f'''טפט #{a}: ★ מותאם אישית''' if is_c_a else f'''טפט #{a}: מקורי''', fg = '#06d6a0' if is_c_a else '#adb5bd')
        item_b = self.parent.slot_state.get(b)
        if item_b and item_b.get('image'):
            im_b = item_b['image'].resize((120, 160), Image.Resampling.LANCZOS)
            self._thumb_b = ImageTk.PhotoImage(im_b)
            self.canvas_b.delete('all')
            self.canvas_b.create_image(60, 80, image = self._thumb_b)
            is_c_b = item_b.get('is_custom', False)
            self.lbl_tag_b.config(text = f'''טפט #{b}: ★ מותאם אישית''' if is_c_b else f'''טפט #{b}: מקורי''', fg = '#06d6a0' if is_c_b else '#adb5bd')
        if a == b:
            self.lbl_summary.config(text = '⚠️ בחר שני טפטים שונים כדי לבצע החלפה ביניהם.', fg = '#ff6b6b')
            self.btn_confirm.config(state = 'disabled', bg = '#2a2e38', fg = '#6c757d')
            return None
        self.lbl_summary.config(text = f'''‏טפט #{a} יקבל את התמונה של טפט #{b}, וטפט #{b} יקבל את התמונה של טפט #{a}.''', fg = '#06d6a0')
        self.btn_confirm.config(state = 'normal', bg = '#06d6a0', fg = '#111215', text = f'''✔ החלף בין טפט #{a} לטפט #{b}''')

    
    def _on_confirm(self):
        
        try:
            a = int(self.slot_a_var.get())
            b = int(self.slot_b_var.get())
        except Exception:
            return None

        if a != b:
            self.parent.swap_wallpapers(a, b)
        self.destroy()



class SplashScreen(tk.Toplevel):
    '''
Sleek, modern splash screen displayed on startup with application branding
and copyright credit to @מה-זה-משנה-אה.
'''
    
    def __init__(self, parent, duration_ms = 2800):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg = '#06d6a0')
        splash_w = 600
        splash_h = 370
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - splash_w) // 2)
        y = max(0, (screen_h - splash_h) // 2)
        self.geometry(f'''{splash_w}x{splash_h}+{x}+{y}''')
        self.attributes('-topmost', True)
        inner = tk.Frame(self, bg = '#16181d', padx = 20, pady = 18)
        inner.pack(fill = 'both', expand = True, padx = 2, pady = 2)
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_png):
            
            try:
                self._splash_logo = ImageTk.PhotoImage(Image.open(icon_png).resize((70, 70), Image.Resampling.LANCZOS))
                lbl_logo = tk.Label(inner, image = self._splash_logo, bg = '#16181d')
                lbl_logo.pack(pady = (6, 4))
            except Exception:
                pass

        lbl_title = tk.Label(inner, text = 'סטודיו ל-Q8', font = ('Segoe UI', 22, 'bold'), fg = '#06d6a0', bg = '#16181d')
        lbl_title.pack(pady = (2, 2))
        lbl_sub = tk.Label(inner, text = 'מערכת התאמה אישית מתקדמת: 70 טפטים, צבעי ממשק ומסך אודות', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#16181d')
        lbl_sub.pack(pady = (0, 14))
        credit_box = tk.Frame(inner, bg = '#232018', highlightthickness = 1, highlightbackground = '#ffd166', padx = 16, pady = 10)
        credit_box.pack(fill = 'x', padx = 10, pady = (0, 12))
        lbl_credit_tag = tk.Label(credit_box, text = '🌟 זכויות יוצרים ופיתוח 🌟', font = ('Segoe UI', 9, 'bold'), fg = '#ffd166', bg = '#232018')
        lbl_credit_tag.pack(pady = (0, 2))
        lbl_credit_user = tk.Label(credit_box, text = 'כל הזכויות שמורות ל- @מה-זה-משנה-אה מפורום מתמחים טופ', font = ('Segoe UI', 12, 'bold'), fg = '#ffffff', bg = '#232018')
        lbl_credit_user.pack()
        self.lbl_loading = tk.Label(inner, text = '...טוען נתונים ומתחבר למערכת', font = ('Segoe UI', 9), fg = '#6c757d', bg = '#16181d')
        self.lbl_loading.pack(side = 'bottom', pady = (4, 0))
        self.bind('<Button-1>', (lambda e: self._dismiss()))
        inner.bind('<Button-1>', (lambda e: self._dismiss()))
        self.bind('<Key>', (lambda e: self._dismiss()))
        self.after(duration_ms, self._dismiss)
        return None

    
    def _dismiss(self):
        
        try:
            self.destroy()
        except Exception:
            return None




class Q8WallpaperStudio(tk.Tk):
    
    def __init__(self):
        '''סטודיו לQ8'''
        super().__init__()
        self.title('סטודיו לQ8')
        self.geometry('1280x860')
        self.minsize(980, 680)
        self.configure(bg = '#181a1f')
        
        try:
            self.state('zoomed')
        except Exception:
            pass

        icon_ico = os.path.join(BASE_DIR, 'assets', 'app_icon.ico')
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_ico):
            
            try:
                self.iconbitmap(icon_ico)
            except Exception:
                pass

        if os.path.exists(icon_png):
            
            try:
                self._app_icon_img = ImageTk.PhotoImage(Image.open(icon_png).resize((32, 32), Image.Resampling.LANCZOS))
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass

        self.slot_state = { }
        self.thumb_images = { }
        self.selected_slot = 1
        self.current_cols = 4
        self.is_deploying = False
        self._hovered_btn = None
        self._hovered_card = None
        self.theme_config = theme_engine.load_theme_config()
        self.confirmed_theme_hex = self.theme_config.get('active_hex', '#0284C7')
        self.confirmed_theme_name = self.theme_config.get('name', 'כחול מפעל מקורי')
        self.current_theme_hex = self.confirmed_theme_hex
        self.current_theme_name = self.confirmed_theme_name
        self.active_tab = 'wallpapers'
        self.current_h = 0
        self.current_s = 1
        self.current_v = 1
        self._syncing_wheel = False
        self._mockup_update_job = None
        self._pending_theme_hex = None
        self._cached_wheel_img = None
        
        try:
            (r, g, b) = theme_engine.hex_to_rgb(self.current_theme_hex)
            (self.current_h, self.current_s, self.current_v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        except Exception:
            pass

        self.text_config = text_engine.load_text_config()
        self.about_title_var = tk.StringVar(value = self.text_config.get('about_title', text_engine.DEFAULT_ABOUT_TITLE))
        self.about_body_str = self.text_config.get('about_body', text_engine.DEFAULT_ABOUT_BODY)
        self.custom_replacements = dict(self.text_config.get('replacements', { }))
        self._about_mockup_job = None
        self.ui_queue = queue.Queue()
        self._check_ui_queue()
        self._build_header()
        self._build_tabs()
        self._build_content_containers()
        self._build_footer()
        self.bind('<Left>', (lambda e: self._navigate_slot(-1)))
        self.bind('<Right>', (lambda e: self._navigate_slot(1)))
        self.bind('<Up>', (lambda e: self._navigate_slot(-(self.current_cols))))
        self.bind('<Down>', (lambda e: self._navigate_slot(self.current_cols)))
        self.load_and_refresh_from_wot()
        
        try:
            self.splash = SplashScreen(self, duration_ms = 2800)
        except Exception:
            return None

        return None

    
    def post_ui(self, func):
        self.ui_queue.put(func)

    
    def _check_ui_queue(self):
        
        try:
            func = self.ui_queue.get_nowait()
            func()
        except queue.Empty:
            pass

        self.after(50, self._check_ui_queue)

    
    def _build_header(self):
        '''#21242b'''
        header = tk.Frame(self, bg = '#21242b', padx = 20, pady = 12)
        header.pack(fill = 'x', side = 'top')
        title_frame = tk.Frame(header, bg = '#21242b')
        title_frame.pack(side = 'right', fill = 'y')
        title_top_row = tk.Frame(title_frame, bg = '#21242b')
        title_top_row.pack(anchor = 'e')
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_png):
            
            try:
                self._header_logo_img = ImageTk.PhotoImage(Image.open(icon_png).resize((38, 38), Image.Resampling.LANCZOS))
                lbl_logo = tk.Label(title_top_row, image = self._header_logo_img, bg = '#21242b')
                lbl_logo.pack(side = 'right', padx = (10, 0))
            except Exception:
                pass

        lbl_title_heb = tk.Label(title_top_row, text = 'סטודיו ל-', font = ('Segoe UI', 18, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_title_heb.pack(side = 'right')
        lbl_title_q8 = tk.Label(title_top_row, text = 'Q8', font = ('Segoe UI', 18, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_title_q8.pack(side = 'right')
        lbl_sub = tk.Label(title_frame, text = '‏התאמה מלאה: 70 טפטים, ערכת נושא, מסך אודות ותפריטים', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#21242b')
        lbl_sub.pack(anchor = 'e', pady = (2, 0))
        actions_frame = tk.Frame(header, bg = '#21242b')
        actions_frame.pack(side = 'left', fill = 'y')
        self.btn_deploy = tk.Button(actions_frame, text = '‏🚀 החל לצריבה ב-WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self.deploy_to_wot)
        self.btn_deploy.pack(side = 'left', padx = 4)
        btn_refresh_wot = tk.Button(actions_frame, text = '‏🔄 רענן מ-WOT', font = ('Segoe UI', 9, 'bold'), bg = '#2a475e', fg = '#f8f9fa', activebackground = '#1b2838', activeforeground = '#66c0f4', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.load_and_refresh_from_wot)
        btn_refresh_wot.pack(side = 'left', padx = 4)
        btn_reset_all = tk.Button(actions_frame, text = '‏↺ איפוס הכל למקור', font = ('Segoe UI', 9), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.reset_all_wallpapers)
        btn_reset_all.pack(side = 'left', padx = 4)

    
    def _build_tabs(self):
        '''#1a1c23'''
        self.tabs_bar = tk.Frame(self, bg = '#1a1c23', padx = 20, pady = 6)
        self.tabs_bar.pack(fill = 'x', side = 'top')
        tabs_inner = tk.Frame(self.tabs_bar, bg = '#1a1c23')
        tabs_inner.pack(side = 'right')
        self.btn_tab_wp = tk.Button(tabs_inner, text = '🖼️ כרטיסיית טפטים (70 טפטים)', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('wallpapers')))
        self.btn_tab_wp.pack(side = 'right', padx = (6, 0))
        self.btn_tab_theme = tk.Button(tabs_inner, text = '🎨 כרטיסיית צבעי ערכת נושא', font = ('Segoe UI', 11), bg = '#252830', fg = '#adb5bd', activebackground = '#2d323c', activeforeground = '#f8f9fa', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('theme')))
        self.btn_tab_theme.pack(side = 'right', padx = (6, 0))
        self.btn_tab_text = tk.Button(tabs_inner, text = '📝 כרטיסיית טקסטים ומיתוג', font = ('Segoe UI', 11), bg = '#252830', fg = '#adb5bd', activebackground = '#2d323c', activeforeground = '#f8f9fa', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('texts')))
        self.btn_tab_text.pack(side = 'right', padx = (0, 6))

    
    def _switch_tab(self, tab_name):
        if tab_name == self.active_tab:
            return None
        if self.active_tab == 'theme' and hasattr(self, 'confirmed_theme_hex') and self.current_theme_hex.upper() != self.confirmed_theme_hex.upper():
            self.revert_to_confirmed_theme()
        self.wallpaper_frame.pack_forget()
        self.theme_frame.pack_forget()
        if hasattr(self, 'text_frame'):
            self.text_frame.pack_forget()
        for btn in (getattr(self, 'btn_tab_wp', None), getattr(self, 'btn_tab_theme', None), getattr(self, 'btn_tab_text', None)):
            if not btn:
                continue
            btn.config(bg = '#252830', fg = '#adb5bd', font = ('Segoe UI', 11))
        if tab_name == 'wallpapers':
            self.wallpaper_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            self.btn_tab_wp.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
        elif tab_name == 'theme':
            self.theme_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            self.btn_tab_theme.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
            self._update_theme_mockup()
        elif tab_name == 'texts':
            if hasattr(self, 'text_frame'):
                self.text_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            if hasattr(self, 'btn_tab_text'):
                self.btn_tab_text.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
            self._update_about_mockup()
        self.active_tab = tab_name

    
    def _build_content_containers(self):
        '''#181a1f'''
        self.content_container = tk.Frame(self, bg = '#181a1f')
        self.content_container.pack(fill = 'both', expand = True)
        self.wallpaper_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_wallpaper_tab_content()
        self.wallpaper_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
        self.theme_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_theme_tab_content()
        self.text_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_text_tab_content()
        self._update_theme_info_card()
        self._update_theme_mockup()
        self._update_preset_card_highlights()
        self._update_about_mockup()

    
    def _build_wallpaper_tab_content(self):
        '''#21242b'''
        self.preview_panel = tk.Frame(self.wallpaper_frame, bg = '#21242b', width = 320, padx = 16, pady = 8, highlightthickness = 1, highlightbackground = '#343a40')
        self.preview_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.preview_panel.pack_propagate(False)
        lbl_hd_title = tk.Label(self.preview_panel, text = '🔍 תצוגה מקדימה מלאה (HD)', font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_hd_title.pack(anchor = 'e')
        lbl_hd_sub = tk.Label(self.preview_panel, text = 'רזולוציה מקורית 240x320 (פיקסל לפיקסל)', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_hd_sub.pack(anchor = 'e', pady = (1, 4))
        self.hd_canvas = tk.Canvas(self.preview_panel, width = 240, height = 320, bg = '#0e1013', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.hd_canvas.pack(pady = 2)
        info_frame = tk.Frame(self.preview_panel, bg = '#1a1c23', padx = 10, pady = 5)
        info_frame.pack(fill = 'x', pady = 4)
        self.lbl_slot_title = tk.Label(info_frame, text = 'טפט #1', font = ('Segoe UI', 12, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        self.lbl_slot_title.pack(anchor = 'e')
        self.lbl_slot_badge = tk.Label(info_frame, text = 'מקורי (ברירת מחדל)', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23')
        self.lbl_slot_badge.pack(anchor = 'e', pady = (1, 0))
        lbl_dim = tk.Label(info_frame, text = 'גודל מסך: 240 × 320 פיקסלים | פורמט SJPG', font = ('Segoe UI', 8), fg = '#6c757d', bg = '#1a1c23')
        lbl_dim.pack(anchor = 'e', pady = (1, 0))
        self.btn_hd_replace = tk.Button(self.preview_panel, text = '✏️ החלף טפט זה...', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.replace_wallpaper(self.selected_slot)))
        self.btn_hd_replace.pack(fill = 'x', pady = (2, 2))
        self.btn_hd_swap = tk.Button(self.preview_panel, text = '⇄ החלף מיקום עם טפט אחר...', font = ('Segoe UI', 9, 'bold'), bg = '#2563eb', fg = '#ffffff', activebackground = '#1d4ed8', activeforeground = '#ffffff', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.open_swap_dialog(self.selected_slot)))
        self.btn_hd_swap.pack(fill = 'x', pady = 2)
        row_secondary = tk.Frame(self.preview_panel, bg = '#21242b')
        row_secondary.pack(fill = 'x', pady = 2)
        self.btn_hd_reset = tk.Button(row_secondary, text = '↺ אפס למקור', font = ('Segoe UI', 8), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.reset_wallpaper(self.selected_slot)))
        self.btn_hd_reset.pack(side = 'right', expand = True, fill = 'x', padx = (2, 0))
        self.btn_hd_zoom = tk.Button(row_secondary, text = '🔍 הגדל פי 2', font = ('Segoe UI', 8), bg = '#2b2d42', fg = '#adb5bd', activebackground = '#1e202e', activeforeground = '#f8f9fa', relief = 'flat', pady = 4, cursor = 'hand2', command = self._open_zoom_modal)
        self.btn_hd_zoom.pack(side = 'left', expand = True, fill = 'x', padx = (0, 2))
        btn_hd_export = tk.Button(self.preview_panel, text = '💾 שמור תמונה למחשב...', font = ('Segoe UI', 8), bg = '#262930', fg = '#adb5bd', activebackground = '#181a1f', activeforeground = '#f8f9fa', relief = 'flat', pady = 3, cursor = 'hand2', command = self._export_current_image)
        btn_hd_export.pack(fill = 'x', pady = (2, 2))
        self.gallery_frame = tk.Frame(self.wallpaper_frame, bg = '#181a1f')
        self.gallery_frame.pack(side = 'left', fill = 'both', expand = True)
        self.canvas = tk.Canvas(self.gallery_frame, bg = '#181a1f', highlightthickness = 0, yscrollincrement = 16)
        self.scrollbar = ttk.Scrollbar(self.gallery_frame, orient = 'vertical', command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.canvas.pack(side = 'left', fill = 'both', expand = True)
        self.scrollbar.pack(side = 'right', fill = 'y')
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    
    def _build_theme_tab_content(self):
        '''#21242b'''
        self.theme_right_panel = tk.Frame(self.theme_frame, bg = '#21242b', width = 320, padx = 16, pady = 14, highlightthickness = 1, highlightbackground = '#343a40')
        self.theme_right_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.theme_right_panel.pack_propagate(False)
        lbl_sim_title = tk.Label(self.theme_right_panel, text = '📱 תצוגה חיה של מסך הטלפון', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_sim_title.pack(anchor = 'e')
        lbl_sim_sub = tk.Label(self.theme_right_panel, text = 'הדמיית מראה התפריטים, הפסים והבאנר בצבע הנבחר', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_sim_sub.pack(anchor = 'e', pady = (1, 6))
        self.mockup_mode = 'menu'
        mode_frame = tk.Frame(self.theme_right_panel, bg = '#21242b')
        mode_frame.pack(fill = 'x', pady = (0, 6))
        self.btn_mode_menu = tk.Button(mode_frame, text = '📱 תפריט ראשי', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', relief = 'flat', cursor = 'hand2', command = (lambda : self._set_mockup_mode('menu')))
        self.btn_mode_menu.pack(side = 'right', expand = True, fill = 'x', padx = (2, 0))
        self.btn_mode_call = tk.Button(mode_frame, text = '📞 שיחה נכנסת', font = ('Segoe UI', 9), bg = '#2a2e38', fg = '#adb5bd', relief = 'flat', cursor = 'hand2', command = (lambda : self._set_mockup_mode('call')))
        self.btn_mode_call.pack(side = 'left', expand = True, fill = 'x', padx = (0, 2))
        self.mockup_canvas = tk.Canvas(self.theme_right_panel, width = 240, height = 320, bg = '#FFFFFF', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.mockup_canvas.pack(pady = 4)
        theme_card = tk.Frame(self.theme_right_panel, bg = '#1a1c23', padx = 12, pady = 10)
        theme_card.pack(fill = 'x', pady = (10, 8))
        swatch_row = tk.Frame(theme_card, bg = '#1a1c23')
        swatch_row.pack(fill = 'x')
        self.swatch_canvas = tk.Canvas(swatch_row, width = 28, height = 28, bg = self.current_theme_hex, highlightthickness = 1, highlightbackground = '#ffffff')
        self.swatch_canvas.pack(side = 'right', padx = (8, 0))
        self.lbl_active_theme_name = tk.Label(swatch_row, text = self.current_theme_name, font = ('Segoe UI', 13, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        self.lbl_active_theme_name.pack(side = 'right')
        self.lbl_theme_badge = tk.Label(theme_card, text = '✔ צבע פעיל שמור (נצרב למכשיר)', font = ('Segoe UI', 8, 'bold'), fg = '#06d6a0', bg = '#1a1c23')
        self.lbl_theme_badge.pack(anchor = 'e', pady = (4, 1))
        self.lbl_active_theme_codes = tk.Label(theme_card, text = '', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23')
        self.lbl_active_theme_codes.pack(anchor = 'e', pady = (2, 2))
        self.lbl_contrast_guard = tk.Label(theme_card, text = '', font = ('Segoe UI', 8, 'bold'), fg = '#06d6a0', bg = '#1a1c23', wraplength = 270, justify = 'right')
        self.lbl_contrast_guard.pack(anchor = 'e', pady = (2, 4))
        action_row = tk.Frame(theme_card, bg = '#1a1c23')
        action_row.pack(fill = 'x', pady = (4, 0))
        self.btn_confirm_theme = tk.Button(action_row, text = '✔ שמור וקבע צבע זה', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 10, pady = 4, cursor = 'hand2', command = self.confirm_active_theme)
        self.btn_confirm_theme.pack(side = 'right')
        self.btn_revert_theme = tk.Button(action_row, text = '↩ בטל תצוגה', font = ('Segoe UI', 8), bg = '#2a2e38', fg = '#adb5bd', activebackground = '#3a3e48', activeforeground = '#ffffff', relief = 'flat', padx = 8, pady = 4, cursor = 'hand2', command = self.revert_to_confirmed_theme)
        self.btn_apply_theme_tab = tk.Button(self.theme_right_panel, text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', pady = 10, cursor = 'hand2', command = self._apply_theme_tab_and_deploy)
        self.btn_apply_theme_tab.pack(fill = 'x', pady = (8, 4))
        self.theme_left_panel = tk.Frame(self.theme_frame, bg = '#181a1f')
        self.theme_left_panel.pack(side = 'left', fill = 'both', expand = True)
        presets_header = tk.Frame(self.theme_left_panel, bg = '#181a1f')
        presets_header.pack(fill = 'x', pady = (0, 8))
        lbl_presets_title = tk.Label(presets_header, text = '🎨 בחירת צבע מתוך פלטות מומלצות ומאומתות', font = ('Segoe UI', 13, 'bold'), fg = '#f8f9fa', bg = '#181a1f')
        lbl_presets_title.pack(anchor = 'e')
        lbl_presets_desc = tk.Label(presets_header, text = 'גוונים אלו נבדקו קלינית על מסך ה-Q8, שומרים על קריאות מיטבית ואינם מייצרים שום תופעות לוואי', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#181a1f')
        lbl_presets_desc.pack(anchor = 'e', pady = (2, 0))
        self.preset_cards = { }
        presets_grid_frame = tk.Frame(self.theme_left_panel, bg = '#181a1f')
        presets_grid_frame.pack(fill = 'both', expand = True)
        for c in range(3):
            presets_grid_frame.columnconfigure(c, weight = 1, uniform = 'preset_col')
        for r in range(3):
            presets_grid_frame.rowconfigure(r, weight = 1, uniform = 'preset_row')
        for i, p in enumerate(theme_engine.PRESETS):
            row = i // 3
            col = 2 - i % 3
            card = self._create_preset_card(presets_grid_frame, p)
            card.grid(row = row, column = col, padx = 5, pady = 5, sticky = 'nsew')
            self.preset_cards[p['id']] = card
        custom_frame = tk.Frame(self.theme_left_panel, bg = '#21242b', padx = 14, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        custom_frame.pack(fill = 'x', pady = (10, 6))
        lbl_custom_title = tk.Label(custom_frame, text = '✨ רוצה צבע אחר? בחר כל גוון שמתחשק לך מגלגל הצבעים', font = ('Segoe UI', 10, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_custom_title.pack(anchor = 'e')
        lbl_custom_sub = tk.Label(custom_frame, text = 'גרור על הגלגל או הזז את סרגל הבהירות – מסך הטלפון מתעדכן בחי בזמן אמת ללא צורך באישור!', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_custom_sub.pack(anchor = 'e', pady = (2, 6))
        wheel_container = tk.Frame(custom_frame, bg = '#21242b')
        wheel_container.pack(fill = 'x')
        wheel_subframe = tk.Frame(wheel_container, bg = '#21242b')
        wheel_subframe.pack(side = 'right', padx = (0, 10))
        wheel_size = 140
        self.wheel_canvas = tk.Canvas(wheel_subframe, width = wheel_size, height = wheel_size, bg = '#21242b', highlightthickness = 0, cursor = 'crosshair')
        self.wheel_canvas.pack()
        wheel_pil = self._generate_color_wheel_image(wheel_size)
        self.wheel_photo = ImageTk.PhotoImage(wheel_pil)
        self.wheel_canvas.create_image(wheel_size // 2, wheel_size // 2, image = self.wheel_photo)
        self._wheel_handle_shadow = self.wheel_canvas.create_oval(0, 0, 0, 0, outline = '#000000', width = 2)
        self._wheel_handle_ring = self.wheel_canvas.create_oval(0, 0, 0, 0, outline = '#FFFFFF', width = 2)
        self._wheel_handle_dot = self.wheel_canvas.create_oval(0, 0, 0, 0, fill = self.current_theme_hex, outline = '')
        self.wheel_canvas.bind('<Button-1>', self._on_wheel_click)
        self.wheel_canvas.bind('<B1-Motion>', self._on_wheel_drag)
        self.wheel_canvas.bind('<ButtonRelease-1>', self._on_wheel_release)
        slider_frame = tk.Frame(wheel_container, bg = '#21242b')
        slider_frame.pack(side = 'right', padx = (0, 14))
        lbl_slider_title = tk.Label(slider_frame, text = 'בהירות', font = ('Segoe UI', 8, 'bold'), fg = '#adb5bd', bg = '#21242b')
        lbl_slider_title.pack(anchor = 'center')
        # NOTE(recovery): decompiler mangled this widget construction into
        # `(slider_frame,)(*{...})`; reconstructed as a tk.Scale call.
        self.slider_brightness = tk.Scale(slider_frame,
            from_ = 100,
            to = 25,
            orient = 'vertical',
            resolution = 1,
            showvalue = 0,
            length = 100,
            width = 14,
            sliderlength = 18,
            bg = '#21242b',
            fg = '#ffffff',
            troughcolor = '#181a1f',
            activebackground = '#06d6a0',
            highlightthickness = 0,
            bd = 0,
            cursor = 'hand2',
            command = self._on_slider_change)
        self.slider_brightness.set(int(round(self.current_v * 100)))
        self.slider_brightness.pack(pady = 4)
        self.slider_brightness.bind('<ButtonRelease-1>', (lambda e: self.preview_theme(self._pending_theme_hex or self.current_theme_hex, 'מותאם אישית')))
        self.lbl_bri_val = tk.Label(slider_frame, text = f'''{int(round(self.current_v * 100))}%''', font = ('Consolas', 8), fg = '#06d6a0', bg = '#21242b')
        self.lbl_bri_val.pack(anchor = 'center')
        info_frame = tk.Frame(wheel_container, bg = '#21242b')
        info_frame.pack(side = 'right', fill = 'both', expand = True)
        swatch_line = tk.Frame(info_frame, bg = '#21242b')
        swatch_line.pack(fill = 'x', pady = (2, 4))
        self.custom_swatch = tk.Canvas(swatch_line, width = 38, height = 38, bg = self.current_theme_hex, highlightthickness = 2, highlightbackground = '#ffffff')
        self.custom_swatch.pack(side = 'right', padx = (0, 8))
        hex_sub = tk.Frame(swatch_line, bg = '#21242b')
        hex_sub.pack(side = 'right', fill = 'x')
        lbl_hex_title = tk.Label(hex_sub, text = 'קוד צבע (Hex):', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_hex_title.pack(anchor = 'e')
        hex_entry_row = tk.Frame(hex_sub, bg = '#21242b')
        hex_entry_row.pack(anchor = 'e', pady = (2, 0))
        self.entry_hex = tk.Entry(hex_entry_row, font = ('Consolas', 10, 'bold'), width = 9, bg = '#181a1f', fg = '#06d6a0', insertbackground = '#06d6a0', justify = 'center')
        self.entry_hex.insert(0, self.current_theme_hex)
        self.entry_hex.pack(side = 'right', padx = (0, 6))
        self.entry_hex.bind('<Return>', (lambda e: self._apply_custom_hex()))
        btn_apply_hex = tk.Button(hex_entry_row, text = 'החל קוד', font = ('Segoe UI', 8, 'bold'), bg = '#262930', fg = '#f8f9fa', relief = 'flat', padx = 8, pady = 3, cursor = 'hand2', command = self._apply_custom_hex)
        btn_apply_hex.pack(side = 'right')
        self.lbl_custom_contrast = tk.Label(info_frame, text = '✔ ניגודיות מצוינת', font = ('Segoe UI', 8), fg = '#06d6a0', bg = '#21242b')
        self.lbl_custom_contrast.pack(anchor = 'e', pady = (2, 2))
        btn_win_picker = tk.Button(info_frame, text = '🎨 לוח צבעים ישן של Windows...', font = ('Segoe UI', 8), bg = '#21242b', fg = '#64748b', activebackground = '#262930', activeforeground = '#94a3b8', relief = 'flat', cursor = 'hand2', command = self._open_color_picker)
        btn_win_picker.pack(anchor = 'e', pady = (2, 0))
        self._sync_wheel_to_color(self.current_theme_hex)

    
    def _create_preset_card(self, parent, preset):
        '''id'''
        p_id = preset['id']
        p_hex = preset['hex']
        p_name = preset['name']
        p_desc = preset['desc']
        card = tk.Frame(parent, bg = '#21242b', padx = 10, pady = 8, highlightthickness = 2, highlightbackground = '#06d6a0' if p_hex.upper() == self.current_theme_hex.upper() else '#343a40', cursor = 'hand2')
        top_row = tk.Frame(card, bg = '#21242b')
        top_row.pack(fill = 'x')
        swatch = tk.Canvas(top_row, width = 20, height = 20, bg = p_hex, highlightthickness = 1, highlightbackground = '#ffffff')
        swatch.pack(side = 'right', padx = (6, 0))
        lbl_name = tk.Label(top_row, text = p_name, font = ('Segoe UI', 10, 'bold'), fg = '#ffffff', bg = '#21242b')
        lbl_name.pack(side = 'right')
        lbl_desc = tk.Label(card, text = p_desc, font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b', wraplength = 200, justify = 'right')
        lbl_desc.pack(anchor = 'e', pady = (4, 0))
        
        def _on_click(event = None):
            self.select_theme(p_hex, p_name)

        card.bind('<Button-1>', _on_click)
        top_row.bind('<Button-1>', _on_click)
        swatch.bind('<Button-1>', _on_click)
        lbl_name.bind('<Button-1>', _on_click)
        lbl_desc.bind('<Button-1>', _on_click)
        
        def _on_enter(event = None):
            '''hex'''
            if preset['hex'].upper() != self.current_theme_hex.upper():
                card.config(highlightbackground = '#64748b', bg = '#262933')
                top_row.config(bg = '#262933')
                lbl_name.config(bg = '#262933')
                lbl_desc.config(bg = '#262933')
                return None

        
        def _on_leave(event = None):
            '''hex'''
            is_active = preset['hex'].upper() == self.current_theme_hex.upper()
            card.config(highlightbackground = '#06d6a0' if is_active else '#343a40', bg = '#21242b')
            top_row.config(bg = '#21242b')
            lbl_name.config(bg = '#21242b')
            lbl_desc.config(bg = '#21242b')

        card.bind('<Enter>', _on_enter)
        card.bind('<Leave>', _on_leave)
        return card

    
    def _update_preset_card_highlights(self):
        '''id'''
        for p in theme_engine.PRESETS:
            card = self.preset_cards.get(p['id'])
            if not card:
                continue
            is_active = p['hex'].upper() == self.current_theme_hex.upper()
            card.config(highlightbackground = '#06d6a0' if is_active else '#343a40', highlightthickness = 2 if is_active else 1)

    
    def _generate_color_wheel_image(self, size = 140):
        '''_cached_wheel_img'''
        if hasattr(self, '_cached_wheel_img') and self._cached_wheel_img is not None:
            return self._cached_wheel_img
        radius = (size - 1) / 2
        cy = radius
        cx = radius
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = img.load()
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = math.hypot(dx, dy)
                if not dist <= radius:
                    continue
                angle = math.atan2(-dy, dx)
                if angle < 0:
                    angle += 2 * math.pi
                h = angle / (2 * math.pi)
                s = min(1, dist / radius)
                (r, g, b) = colorsys.hsv_to_rgb(h, s, 1)
                alpha = int(255 * min(1, (radius - dist) + 1)) if dist > radius - 1 else 255
                pixels[(x, y)] = (int(r * 255), int(g * 255), int(b * 255), alpha)
        self._cached_wheel_img = img
        return img

    
    def _update_wheel_handle(self, x, y, hex_color):
        '''wheel_canvas'''
        if not hasattr(self, 'wheel_canvas'):
            return None
        self.wheel_canvas.coords(self._wheel_handle_shadow, x - 7, y - 7, x + 7, y + 7)
        self.wheel_canvas.coords(self._wheel_handle_ring, x - 6, y - 6, x + 6, y + 6)
        self.wheel_canvas.coords(self._wheel_handle_dot, x - 4, y - 4, x + 4, y + 4)
        self.wheel_canvas.itemconfig(self._wheel_handle_dot, fill = hex_color)

    
    def _sync_wheel_to_color(self, hex_val):
        
        try:
            (r, g, b) = theme_engine.hex_to_rgb(hex_val)
            (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            self.current_h = h
            self.current_s = s
            self.current_v = v
            if hasattr(self, 'slider_brightness'):
                self._syncing_wheel = True
                self.slider_brightness.set(int(round(v * 100)))
                if hasattr(self, 'lbl_bri_val'):
                    self.lbl_bri_val.config(text = f'''{int(round(v * 100))}%''')
                self._syncing_wheel = False
            radius = 69.5
            cy = radius
            cx = radius
            angle = h * 2 * math.pi
            dist = s * radius
            x = cx + dist * math.cos(angle)
            y = cy - dist * math.sin(angle)
            self._update_wheel_handle(x, y, hex_val)
            if hasattr(self, 'custom_swatch'):
                self.custom_swatch.config(bg = hex_val)
            if hasattr(self, 'lbl_custom_contrast'):
                (ok, msg) = theme_engine.check_contrast_guard(hex_val)
                self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
                return None
        except Exception:
            return None


    
    def _handle_wheel_coords(self, x, y, finalize = False):
        size = 140
        radius = (size - 1) / 2
        cy = radius
        cx = radius
        dx = x - cx
        dy = y - cy
        dist = math.hypot(dx, dy)
        if dist > radius:
            x = cx + (dx / dist) * radius
            y = cy + (dy / dist) * radius
            dist = radius
        angle = math.atan2(-dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        self.current_h = angle / (2 * math.pi)
        self.current_s = min(1, dist / radius)
        v = self.slider_brightness.get() / 100 if hasattr(self, 'slider_brightness') else self.current_v
        self.current_v = v
        (r, g, b) = colorsys.hsv_to_rgb(self.current_h, self.current_s, v)
        hex_color = f'''#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}'''
        self._update_wheel_handle(x, y, hex_color)
        if hasattr(self, 'custom_swatch'):
            self.custom_swatch.config(bg = hex_color)
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, hex_color)
        if hasattr(self, 'lbl_custom_contrast'):
            (ok, msg) = theme_engine.check_contrast_guard(hex_color)
            self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        if finalize:
            if self._mockup_update_job is not None:
                self.after_cancel(self._mockup_update_job)
                self._mockup_update_job = None
            self.preview_theme(hex_color, 'מותאם אישית')
            return None
        self._schedule_live_mockup_update(hex_color)

    
    def _on_wheel_click(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = False)

    
    def _on_wheel_drag(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = False)

    
    def _on_wheel_release(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = True)

    
    def _on_slider_change(self, val_str):
        '''_syncing_wheel'''
        if getattr(self, '_syncing_wheel', False):
            return None
        v = float(val_str) / 100
        self.current_v = v
        if hasattr(self, 'lbl_bri_val'):
            self.lbl_bri_val.config(text = f'''{int(round(v * 100))}%''')
        (r, g, b) = colorsys.hsv_to_rgb(self.current_h, self.current_s, v)
        hex_color = f'''#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}'''
        radius = 69.5
        cy = radius
        cx = radius
        angle = self.current_h * 2 * math.pi
        dist = self.current_s * radius
        x = cx + dist * math.cos(angle)
        y = cy - dist * math.sin(angle)
        self._update_wheel_handle(x, y, hex_color)
        if hasattr(self, 'custom_swatch'):
            self.custom_swatch.config(bg = hex_color)
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, hex_color)
        if hasattr(self, 'lbl_custom_contrast'):
            ok, msg = theme_engine.check_contrast_guard(hex_color)
            self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        self._schedule_live_mockup_update(hex_color)

    
    def _schedule_live_mockup_update(self, hex_color):
        self._pending_theme_hex = hex_color
        if self._mockup_update_job is None:
            self._mockup_update_job = self.after(30, self._do_live_mockup_update)
            return None

    
    def _do_live_mockup_update(self):
        self._mockup_update_job = None
        if hasattr(self, '_pending_theme_hex'):
            if self._pending_theme_hex:
                target_hex = self._pending_theme_hex
                self.current_theme_hex = target_hex
                self._update_theme_mockup()
                if hasattr(self, 'swatch_canvas'):
                    self.swatch_canvas.config(bg = target_hex)
                if hasattr(self, 'lbl_active_theme_codes'):
                    (r, g, b) = theme_engine.hex_to_rgb(target_hex)
                    c565 = theme_engine.rgb_to_rgb565(r, g, b)
                    self.lbl_active_theme_codes.config(text = f'''קוד Hex: {target_hex} | RGB565: 0x{c565:04X}''')
                if hasattr(self, 'lbl_contrast_guard'):
                    ok, msg = theme_engine.check_contrast_guard(target_hex)
                    self.lbl_contrast_guard.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
                if hasattr(self, 'lbl_active_theme_name'):
                    self.lbl_active_theme_name.config(text = 'מותאם אישית (חי)')
                    return None
                return None
            return None

    
    def _open_color_picker(self):
        '''בחר צבע עבור ערכת הנושא של ה-Q8'''
        chosen = colorchooser.askcolor(color = self.current_theme_hex, title = 'בחר צבע עבור ערכת הנושא של ה-Q8')
        if chosen:
            if chosen[1]:
                hex_val = chosen[1].upper()
                self.preview_theme(hex_val, 'מותאם אישית')
                return None
            return None

    
    def _apply_custom_hex(self):
        '''#'''
        val = self.entry_hex.get().strip()
        if not val.startswith('#'):
            val = '#' + val
        if len(val) in (4, 7):
            
            try:
                theme_engine.hex_to_rgb(val)
                self.preview_theme(val.upper(), 'מותאם אישית')
            except Exception:
                messagebox.showerror('קוד צבע שגוי', 'אנא הזן קוד צבע הקסדצימלי תקין (למשל: #1D4ED8)')
                return None

            return None
        messagebox.showerror('קוד צבע שגוי', 'אנא הזן קוד צבע הקסדצימלי תקין (למשל: #1D4ED8)')

    
    def preview_theme(self, hex_val, name):
        '''Previews a theme visually without saving or committing it to active config.'''
        self.current_theme_hex = hex_val.upper()
        self.current_theme_name = name
        self._update_theme_info_card()
        self._update_theme_mockup()
        self._update_preset_card_highlights()
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, self.current_theme_hex)
        self._sync_wheel_to_color(self.current_theme_hex)
        is_confirmed = self.current_theme_hex.upper() == self.confirmed_theme_hex.upper()
        if is_confirmed:
            self.lbl_status.config(text = f'''‏צבע ערכת הנושא הפעיל: {name} ({self.current_theme_hex}).''')
            return None
        self.lbl_status.config(text = f'''‏👁️ תצוגה מקדימה: {name} ({self.current_theme_hex}). לחץ \'שמור וקבע צבע זה\' כדי לקבוע אותו כצבע הפעיל.''')

    
    def select_theme(self, hex_val, name):
        '''Backwards-compatible alias for preview_theme.'''
        self.preview_theme(hex_val, name)

    
    def confirm_active_theme(self):
        '''Explicitly saves and commits current preview theme as active burning theme.'''
        self.confirmed_theme_hex = self.current_theme_hex
        self.confirmed_theme_name = self.current_theme_name
        theme_engine.save_theme_config(self.confirmed_theme_hex, self.confirmed_theme_name)
        self._update_theme_info_card()
        self._update_preset_card_highlights()
        self.lbl_status.config(text = f'''‏✔ צבע ערכת הנושא נשמר ואושר בהצלחה: {self.confirmed_theme_name} ({self.confirmed_theme_hex}).''')
        messagebox.showinfo('הצבע אושר בהצלחה', f'''הצבע {self.confirmed_theme_name} ({self.confirmed_theme_hex}) נשמר בהצלחה כצבע הפעיל של המכשיר!\n\nכעת כל צריבה של טפטים או ערכת נושא תשתמש בצבע זה.''')

    
    def revert_to_confirmed_theme(self):
        '''Reverts preview back to saved confirmed theme.'''
        self.preview_theme(self.confirmed_theme_hex, self.confirmed_theme_name)
        self.lbl_status.config(text = f'''‏התצוגה בוטלה. הוחזר לצבע הפעיל: {self.confirmed_theme_name} ({self.confirmed_theme_hex}).''')

    
    def _apply_theme_tab_and_deploy(self):
        '''Confirms current preview color, then starts deploy to WOT.'''
        self.confirmed_theme_hex = self.current_theme_hex
        self.confirmed_theme_name = self.current_theme_name
        theme_engine.save_theme_config(self.confirmed_theme_hex, self.confirmed_theme_name)
        self._update_theme_info_card()
        self.deploy_to_wot()

    
    def _update_theme_info_card(self):
        '''lbl_active_theme_name'''
        if not hasattr(self, 'lbl_active_theme_name'):
            return None
        is_confirmed = self.current_theme_hex.upper() == self.confirmed_theme_hex.upper()
        self.lbl_active_theme_name.config(text = self.current_theme_name)
        self.swatch_canvas.config(bg = self.current_theme_hex)
        (r, g, b) = theme_engine.hex_to_rgb(self.current_theme_hex)
        c565 = theme_engine.rgb_to_rgb565(r, g, b)
        self.lbl_active_theme_codes.config(text = f'''קוד Hex: {self.current_theme_hex} | RGB565: 0x{c565:04X}''')
        ok, msg = theme_engine.check_contrast_guard(self.current_theme_hex)
        self.lbl_contrast_guard.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        if hasattr(self, 'lbl_theme_badge'):
            if is_confirmed:
                self.lbl_theme_badge.config(text = '✔ צבע פעיל שמור (נצרב למכשיר)', fg = '#06d6a0')
            else:
                self.lbl_theme_badge.config(text = '👁️ תצוגה מקדימה בלבד (טרם נשמר!)', fg = '#ffd166')
        if hasattr(self, 'btn_confirm_theme'):
            if is_confirmed:
                self.btn_confirm_theme.config(text = '✔ צבע זה מאושר', state = 'disabled', bg = '#1e3a2b', fg = '#6ee7b7')
                if hasattr(self, 'btn_revert_theme'):
                    self.btn_revert_theme.pack_forget()
                    return None
                return None
            self.btn_confirm_theme.config(text = '✔ שמור וקבע צבע זה', state = 'normal', bg = '#06d6a0', fg = '#111215')
            if hasattr(self, 'btn_revert_theme'):
                self.btn_revert_theme.pack(side = 'left', padx = 4)
                return None
            return None

    
    def _set_mockup_mode(self, mode):
        '''menu'''
        self.mockup_mode = mode
        if mode == 'menu':
            self.btn_mode_menu.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 9, 'bold'))
            self.btn_mode_call.config(bg = '#2a2e38', fg = '#adb5bd', font = ('Segoe UI', 9))
            self.mockup_canvas.config(bg = '#FFFFFF')
        else:
            self.btn_mode_call.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 9, 'bold'))
            self.btn_mode_menu.config(bg = '#2a2e38', fg = '#adb5bd', font = ('Segoe UI', 9))
            self.mockup_canvas.config(bg = '#111215')
        self._update_theme_mockup()

    
    def _update_theme_mockup(self):
        '''mockup_canvas'''
        if not hasattr(self, 'mockup_canvas'):
            return None
        c = self.mockup_canvas
        c.delete('all')
        self._mockup_photos = { }
        th = self.current_theme_hex
        if getattr(self, 'mockup_mode', 'menu') == 'menu':
            c.create_rectangle(0, 0, 240, 320, fill = '#FFFFFF', outline = '')
            for i in range(4):
                bx = 10 + i * 4
                bh = 3 + i * 2.5
                c.create_rectangle(bx, 17 - bh, bx + 2, 17, fill = '#1e293b', outline = '')
            c.create_text(28, 12, text = 'VoLTE 4G1', anchor = 'w', font = ('Segoe UI', 7, 'bold'), fill = '#1e293b')
            c.create_rectangle(176, 7, 192, 17, outline = '#1e293b', width = 1)
            c.create_rectangle(178, 9, 189, 15, fill = '#1e293b', outline = '')
            c.create_rectangle(192, 10, 194, 14, fill = '#1e293b', outline = '')
            c.create_text(198, 12, text = '18:55', anchor = 'w', font = ('Segoe UI', 8, 'bold'), fill = '#1e293b')
            
            try:
                icons_dict = theme_engine.get_menu_icon_images(th)
            except Exception:
                icons_dict = { }

            grid_items = [
                (0, 2, 231, 'פרופילים'),
                (0, 1, 229, 'אנשי קשר'),
                (0, 0, 227, 'יומן שיחות'),
                (1, 2, 237, 'שעון'),
                (1, 1, 235, 'בלוטות'),
                (1, 0, 233, 'הגדרות'),
                (2, 2, 243, 'רשמקול'),
                (2, 1, 241, 'לוח שנה'),
                (2, 0, 251, 'כלים')]
            col_x = [
                42,
                120,
                198]
            row_y = [
                58,
                142,
                226]
            for row, col, item_id, label in grid_items:
                cx = col_x[col]
                cy = row_y[row]
                if item_id == 233:
                    c.create_rectangle(cx - 26, cy - 24, cx + 26, cy + 24, fill = '#F1F5F9', outline = th, width = 2)
                    c.create_oval(cx + 14, cy - 24, cx + 26, cy - 12, fill = th, outline = '#FFFFFF')
                    c.create_text(cx + 20, cy - 18, text = '✓', font = ('Segoe UI', 7, 'bold'), fill = '#FFFFFF')
                im = icons_dict.get(item_id)
                if im:
                    photo = ImageTk.PhotoImage(im)
                    self._mockup_photos[item_id] = photo
                    c.create_image(cx, cy, image = photo)
                c.create_text(cx, cy + 28, text = label, font = ('Segoe UI', 9), fill = '#1E293B')
            c.create_line(0, 296, 240, 296, fill = '#E2E8F0')
            c.create_text(205, 308, text = 'אחורה', font = ('Segoe UI', 9, 'bold'), fill = '#1E293B')
            c.create_text(35, 308, text = 'אישור', font = ('Segoe UI', 9, 'bold'), fill = '#1E293B')
            return None
        c.create_rectangle(0, 0, 240, 320, fill = '#121316', outline = '')
        c.create_rectangle(0, 0, 240, 24, fill = th, outline = '')
        c.create_text(120, 12, text = '18:55', fill = '#ffffff', font = ('Segoe UI', 9, 'bold'))
        c.create_rectangle(8, 70, 232, 220, fill = th, outline = '#ffffff', width = 1)
        c.create_text(120, 105, text = '📞 שיחה נכנסת...', fill = '#ffffff', font = ('Segoe UI', 12, 'bold'))
        c.create_text(120, 140, text = '050-1234567', fill = '#ffffff', font = ('Segoe UI', 12))
        c.create_text(120, 180, text = 'מענה [ירוק] | דחייה [אדום]', fill = '#e0e0e0', font = ('Segoe UI', 9))
        c.create_rectangle(0, 290, 240, 320, fill = '#0a0b0d', outline = '')
        c.create_text(205, 305, text = 'דחייה', font = ('Segoe UI', 9, 'bold'), fill = '#ff4d4d')
        c.create_text(35, 305, text = 'מענה', font = ('Segoe UI', 9, 'bold'), fill = '#06d6a0')

    
    def _build_text_tab_content(self):
        '''#21242b'''
        self.text_right_panel = tk.Frame(self.text_frame, bg = '#21242b', width = 320, padx = 16, pady = 14, highlightthickness = 1, highlightbackground = '#343a40')
        self.text_right_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.text_right_panel.pack_propagate(False)
        lbl_mockup_title = tk.Label(self.text_right_panel, text = '📱 תצוגה מקדימה: מסך אודות', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_mockup_title.pack(anchor = 'e', pady = (0, 4))
        lbl_mockup_sub = tk.Label(self.text_right_panel, text = 'הדמיה בזמן אמת של המסך במכשיר', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#21242b')
        lbl_mockup_sub.pack(anchor = 'e', pady = (0, 8))
        self.about_mockup_canvas = tk.Canvas(self.text_right_panel, width = 240, height = 320, bg = '#CAD8EE', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.about_mockup_canvas.pack(pady = 4)
        info_card = tk.Frame(self.text_right_panel, bg = '#1a1c23', padx = 12, pady = 10)
        info_card.pack(fill = 'x', pady = (10, 8))
        lbl_info_title = tk.Label(info_card, text = 'ℹ️ נתיב מסך זה במכשיר:', font = ('Segoe UI', 9, 'bold'), fg = '#06d6a0', bg = '#1a1c23')
        lbl_info_title.pack(anchor = 'e')
        lbl_info_desc = tk.Label(info_card, text = 'תפריט ➔ הגדרות ➔ אודות\nמסך זה מציג את שם הגרסה, הקדשה אישית ופרטי יוצר הגרסה.', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23', justify = 'right')
        lbl_info_desc.pack(anchor = 'e', pady = (2, 0))
        self.text_left_panel = tk.Frame(self.text_frame, bg = '#181a1f')
        self.text_left_panel.pack(side = 'left', fill = 'both', expand = True)
        card_about = tk.LabelFrame(self.text_left_panel, text = " 📱 עריכת מסך 'אודות' (About Screen) ", font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 14, pady = 10)
        card_about.pack(fill = 'x', pady = (0, 10))
        row_title = tk.Frame(card_about, bg = '#21242b')
        row_title.pack(fill = 'x', pady = (0, 6))
        lbl_title = tk.Label(row_title, text = 'כותרת גרסה (מופיע לפני מספר הגרסה):', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_title.pack(side = 'right', padx = (8, 0))
        self.entry_about_title = tk.Entry(row_title, textvariable = self.about_title_var, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 24, justify = 'right')
        self.entry_about_title.pack(side = 'right')
        self.entry_about_title.bind('<KeyRelease>', (lambda e: self._on_about_text_changed()))
        row_body_lbl = tk.Frame(card_about, bg = '#21242b')
        row_body_lbl.pack(fill = 'x', pady = (4, 2))
        lbl_body = tk.Label(row_body_lbl, text = 'טקסט האודות, מיתוג וקרדיטים (עד 96 תווים):', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_body.pack(side = 'right')
        self.lbl_char_count = tk.Label(row_body_lbl, text = '0 / 96 תווים', font = ('Segoe UI', 9), fg = '#06d6a0', bg = '#21242b')
        self.lbl_char_count.pack(side = 'left')
        self.txt_about_body = tk.Text(card_about, height = 4, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', padx = 8, pady = 6, wrap = 'word')
        self.txt_about_body.pack(fill = 'x', pady = (0, 8))
        self.txt_about_body.insert('1.0', self.about_body_str)
        self.txt_about_body.bind('<KeyRelease>', (lambda e: self._on_about_text_changed()))
        row_about_btns = tk.Frame(card_about, bg = '#21242b')
        row_about_btns.pack(fill = 'x')
        btn_save_about = tk.Button(row_about_btns, text = '✔ שמור מסך אודות', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 14, pady = 5, cursor = 'hand2', command = self._save_about_text)
        btn_save_about.pack(side = 'right', padx = (6, 0))
        btn_reset_about = tk.Button(row_about_btns, text = '↺ שחזר טקסט מקורי', font = ('Segoe UI', 9), bg = '#3d405b', fg = '#f8f9fa', activebackground = '#2b2d42', relief = 'flat', padx = 12, pady = 5, cursor = 'hand2', command = self._reset_about_text)
        btn_reset_about.pack(side = 'right')
        card_strings = tk.LabelFrame(self.text_left_panel, text = ' 🔍 חיפוש ושינוי שמות תפריטים במכשיר ', font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 14, pady = 8)
        card_strings.pack(fill = 'both', expand = True, pady = (0, 10))
        row_search = tk.Frame(card_strings, bg = '#21242b')
        row_search.pack(fill = 'x', pady = (0, 6))
        lbl_search = tk.Label(row_search, text = 'חפש מילה במכשיר:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_search.pack(side = 'right', padx = (8, 0))
        self.entry_str_search = tk.Entry(row_search, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 20, justify = 'right')
        self.entry_str_search.pack(side = 'right', padx = (0, 6))
        self.entry_str_search.bind('<Return>', (lambda e: self._do_search_strings()))
        btn_search = tk.Button(row_search, text = '🔍 חפש', font = ('Segoe UI', 9, 'bold'), bg = '#3a3f4d', fg = '#f8f9fa', activebackground = '#4a5163', relief = 'flat', padx = 12, pady = 3, cursor = 'hand2', command = self._do_search_strings)
        btn_search.pack(side = 'right')
        split_frame = tk.Frame(card_strings, bg = '#21242b')
        split_frame.pack(fill = 'both', expand = True, pady = (0, 6))
        active_box = tk.LabelFrame(split_frame, text = ' החלפות פעילות ', font = ('Segoe UI', 9, 'bold'), fg = '#adb5bd', bg = '#21242b', padx = 6, pady = 4)
        active_box.pack(side = 'left', fill = 'both', expand = True, padx = (0, 6))
        self.list_replacements = tk.Listbox(active_box, font = ('Segoe UI', 9), bg = '#111215', fg = '#ffffff', selectbackground = '#06d6a0', selectforeground = '#111215', relief = 'flat', height = 3)
        self.list_replacements.pack(fill = 'both', expand = True, pady = (0, 4))
        self._refresh_active_replacements_list()
        btn_del_rep = tk.Button(active_box, text = '🗑️ מחק החלפה נבחרת', font = ('Segoe UI', 8), bg = '#5c2429', fg = '#ff6b6b', relief = 'flat', cursor = 'hand2', command = self._delete_replacement)
        btn_del_rep.pack(fill = 'x')
        results_box = tk.LabelFrame(split_frame, text = ' תוצאות חיפוש (לחץ לבחירה) ', font = ('Segoe UI', 9, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 6, pady = 4)
        results_box.pack(side = 'right', fill = 'both', expand = True)
        tree_frame = tk.Frame(results_box, bg = '#21242b')
        tree_frame.pack(fill = 'both', expand = True)
        self.tree_strings = ttk.Treeview(tree_frame, columns = ('text', 'len'), show = 'headings', height = 3)
        self.tree_strings.heading('text', text = 'טקסט שנמצא במכשיר')
        self.tree_strings.heading('len', text = 'אורך')
        self.tree_strings.column('text', width = 160, anchor = 'e')
        self.tree_strings.column('len', width = 60, anchor = 'center')
        tree_scroll = ttk.Scrollbar(tree_frame, orient = 'vertical', command = self.tree_strings.yview)
        self.tree_strings.configure(yscrollcommand = tree_scroll.set)
        self.tree_strings.pack(side = 'left', fill = 'both', expand = True)
        tree_scroll.pack(side = 'right', fill = 'y')
        self.tree_strings.bind('<<TreeviewSelect>>', self._on_tree_select)
        row_replace = tk.Frame(card_strings, bg = '#21242b')
        row_replace.pack(fill = 'x', pady = (4, 4))
        lbl_rep_to = tk.Label(row_replace, text = 'טקסט חלופי חדש:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_rep_to.pack(side = 'right', padx = (8, 0))
        self.entry_str_replace = tk.Entry(row_replace, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 20, justify = 'right')
        self.entry_str_replace.pack(side = 'right', padx = (0, 6))
        btn_add_rep = tk.Button(row_replace, text = '✔ החלף מילה זו', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 10, pady = 3, cursor = 'hand2', command = self._apply_replacement)
        btn_add_rep.pack(side = 'right')
        self.btn_apply_text_tab = tk.Button(self.text_left_panel, text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 20, pady = 8, cursor = 'hand2', command = self._apply_text_tab_and_deploy)
        self.btn_apply_text_tab.pack(fill = 'x')

    
    def _update_about_mockup(self):
        '''about_mockup_canvas'''
        if not hasattr(self, 'about_mockup_canvas'):
            return None
        c = self.about_mockup_canvas
        c.delete('all')
        c.create_rectangle(0, 0, 240, 320, fill = '#CAD8EE', outline = '')
        c.create_rectangle(0, 0, 240, 24, fill = '#1B2C6E', outline = '')
        c.create_text(8, 6, text = 'Vo', fill = '#FFFFFF', font = ('Segoe UI', 6, 'bold'), anchor = 'nw')
        c.create_text(8, 13, text = 'LTE', fill = '#FFFFFF', font = ('Segoe UI', 6, 'bold'), anchor = 'nw')
        c.create_text(26, 12, text = '4G', fill = '#FFFFFF', font = ('Segoe UI', 8, 'bold'), anchor = 'w')
        for i in range(4):
            bx = 42 + i * 4
            bh = 3 + i * 2.5
            c.create_rectangle(bx, 17 - bh, bx + 2, 17, fill = '#FFFFFF', outline = '')
        c.create_rectangle(176, 7, 192, 17, outline = '#FFFFFF', width = 1)
        c.create_rectangle(178, 9, 190, 15, fill = '#FFFFFF', outline = '')
        c.create_rectangle(174, 9, 176, 15, fill = '#FFFFFF', outline = '')
        c.create_text(234, 12, text = '12:53', fill = '#FFFFFF', font = ('Segoe UI', 9, 'bold'), anchor = 'e')
        c.create_text(224, 46, text = 'אודות', fill = '#2D5FB2', font = ('Segoe UI', 13, 'bold'), anchor = 'e')
        title_text = self.about_title_var.get().strip() if hasattr(self, 'about_title_var') else 'מספר גרסה:'
        if not title_text:
            title_text = 'מספר גרסה:'
        id_title = c.create_text(224, 74, text = title_text, fill = '#25355E', font = ('Segoe UI', 10), anchor = 'e')
        bbox = c.bbox(id_title)
        left_x = bbox[0] if bbox else 150
        c.create_text(left_x - 4, 74, text = 'V4.5', fill = '#25355E', font = ('Segoe UI', 10), anchor = 'e')
        body = ''
        if hasattr(self, 'txt_about_body'):
            body = self.txt_about_body.get('1.0', 'end-1c')
        else:
            body = getattr(self, 'about_body_str', '')
        lines = []
        for paragraph in body.split('\n'):
            p = paragraph.strip()
            if not p:
                continue
            p_norm = p.replace('לשכפל ו/או', 'לשכפל ו /או')
            words = p_norm.split(' ')
            cur = ''
            for w in words:
                if not w:
                    continue
                # NOTE(recovery): decompiler rendered the next branch as `while`;
                # restored to `if` (long hyphenated email word split across lines).
                if '@' in w and '-' in w and len(w) > 14:
                    if cur:
                        lines.append(cur)
                        cur = ''
                    parts = w.split('-')
                    lines.append(parts[0] + '-')
                    lines.append('-'.join(parts[slice(1, None, None)]))
                    continue
                test = (cur + ' ' + w).strip() if cur else w
                if len(test) <= 23:
                    cur = test
                    continue
                if cur:
                    lines.append(cur)
                cur = w
            if not cur:
                continue
            lines.append(cur)
        y = 98
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            is_email = '@' in line_clean or 'tech.com' in line_clean
            if is_email:
                color = '#2D5FB2'
            else:
                color = '#25355E'
            if is_email and y < 190:
                y += 6
            c.create_text(224, y, text = line_clean, fill = color, font = ('Segoe UI', 10), anchor = 'e')
            y += 22
            if not y > 270:
                continue
            lines
        c.create_text(18, 302, text = 'אישור', fill = '#2D5FB2', font = ('Segoe UI', 11, 'bold'), anchor = 'w')
        c.create_text(224, 302, text = 'אחורה', fill = '#2D5FB2', font = ('Segoe UI', 11, 'bold'), anchor = 'e')

    
    def _on_about_text_changed(self):
        '''txt_about_body'''
        if not hasattr(self, 'txt_about_body') or not hasattr(self, 'lbl_char_count'):
            return None
        body = self.txt_about_body.get('1.0', 'end-1c')
        char_count = len(body)
        if char_count <= 96:
            self.lbl_char_count.config(text = f'''{char_count} / 96 תווים (תקין)''', fg = '#06d6a0')
        else:
            self.lbl_char_count.config(text = f'''⚠️ {char_count} / 96 תווים (חריגה מ-96!)''', fg = '#ff6b6b')
        if self._about_mockup_job:
            self.after_cancel(self._about_mockup_job)
        self._about_mockup_job = self.after(50, self._update_about_mockup)

    
    def _save_about_text(self):
        '''1.0'''
        title = self.entry_about_title.get().strip()
        body = self.txt_about_body.get('1.0', 'end-1c')
        if len(body) > 96:
            messagebox.showwarning('חריגה באורך', 'טקסט האודות חורג מ-96 תווים. אנא קצר אותו מעט כדי שיתאים במדויק לגודל המסך.')
            return None
        self.text_config['about_title'] = title
        self.text_config['about_body'] = body
        text_engine.save_text_config(self.text_config)
        self.lbl_status.config(text = "✔ מסך 'אודות' נשמר בהצלחה! לחץ 'החל' לצריבה למכשיר.")
        messagebox.showinfo('נשמר בהצלחה', "שינויי מסך 'אודות' נשמרו בהצלחה!\nלחץ על 'החל שינויי טקסט והכן לצריבה' כדי לפרוס ל-WOT.")

    
    def _reset_about_text(self):
        '''שחזור למקור'''
        if not messagebox.askyesno('שחזור למקור', "האם לשחזר את מסך 'אודות' לטקסט היצרן המקורי?"):
            return None
        self.about_title_var.set(text_engine.DEFAULT_ABOUT_TITLE)
        self.txt_about_body.delete('1.0', 'end')
        self.txt_about_body.insert('1.0', text_engine.DEFAULT_ABOUT_BODY)
        self._on_about_text_changed()
        self.text_config['about_title'] = text_engine.DEFAULT_ABOUT_TITLE
        self.text_config['about_body'] = text_engine.DEFAULT_ABOUT_BODY
        text_engine.save_text_config(self.text_config)
        self.lbl_status.config(text = "מסך 'אודות' אופס לטקסט המקורי של היצרן.")

    
    def _do_search_strings(self):
        query = self.entry_str_search.get().strip()
        if not query:
            return None
        self.lbl_status.config(text = f'''מחפש \'{query}\' במכשיר...''')
        # NOTE(recovery): decompiler left `get_children()()`; restored to clearing the tree.
        self.tree_strings.delete(*self.tree_strings.get_children())
        results = text_engine.search_hebrew_strings(query)
        if not results:
            self.lbl_status.config(text = f'''לא נמצאו מילים תואמות ל-\'{query}\'.''')
            return None
        for r in results:
            self.tree_strings.insert('', 'end', values = (r['text'], f'''עד {r['max_chars']} תווים''', f'''0x{r['offset']:X}'''))
        self.lbl_status.config(text = f'''נמצאו {len(results)} תוצאות עבור \'{query}\'.''')

    
    def _on_tree_select(self, event):
        sel = self.tree_strings.selection()
        if not sel:
            return None
        vals = self.tree_strings.item(sel[0], 'values')
        if vals:
            orig_txt = vals[0]
            self.entry_str_replace.delete(0, 'end')
            self.entry_str_replace.insert(0, orig_txt)
            return None

    
    def _refresh_active_replacements_list(self):
        '''list_replacements'''
        if not hasattr(self, 'list_replacements'):
            return None
        self.list_replacements.delete(0, 'end')
        for orig, rep in self.custom_replacements.items():
            self.list_replacements.insert('end', f'''\'{orig}\' ➔ \'{rep}\'''')

    
    def _apply_replacement(self):
        '''בחר מילה'''
        sel = self.tree_strings.selection()
        if not sel:
            messagebox.showinfo('בחר מילה', 'אנא בחר תחילה מילה מרשימת תוצאות החיפוש.')
            return None
        vals = self.tree_strings.item(sel[0], 'values')
        orig_txt = vals[0]
        new_txt = self.entry_str_replace.get().strip()
        if not new_txt:
            return None
        max_chars_str = vals[1].replace('עד ', '').replace(' תווים', '').strip()
        
        try:
            max_chars = int(max_chars_str)
        except Exception:
            max_chars = len(orig_txt)

        if len(new_txt) > max_chars:
            messagebox.showwarning('טקסט ארוך מדי', f'''הטקסט החדש ({len(new_txt)} תווים) חורג מהאורך המקסימלי ({max_chars} תווים).''')
            return None
        if 'replacements' not in self.text_config:
            self.text_config['replacements'] = { }
        self.text_config['replacements'][orig_txt] = new_txt
        text_engine.save_text_config(self.text_config)
        self.custom_replacements = dict(self.text_config['replacements'])
        self._refresh_active_replacements_list()
        self.lbl_status.config(text = f'''✔ המילה \'{orig_txt}\' תוחלף ב-\'{new_txt}\'. לחץ \'החל\' לצריבה.''')
        messagebox.showinfo('ההחלפה נשמרה', f'''המילה \'{orig_txt}\' תוחלף ב-\'{new_txt}\' בכל המכשיר!\nלחץ \'החל שינויי טקסט והכן לצריבה\' כדי לפרוס ל-WOT.''')

    
    def _delete_replacement(self):
        sel = self.list_replacements.curselection()
        if not sel:
            return None
        idx = sel[0]
        keys = list(self.custom_replacements.keys())
        if idx < len(keys):
            target = keys[idx]
            del self.text_config['replacements'][target]
            text_engine.save_text_config(self.text_config)
            self.custom_replacements = dict(self.text_config['replacements'])
            self._refresh_active_replacements_list()
            self.lbl_status.config(text = f'''ההחלפה עבור \'{target}\' נמחקה.''')
            return None

    
    def _apply_text_tab_and_deploy(self):
        '''1.0'''
        title = self.entry_about_title.get().strip()
        body = self.txt_about_body.get('1.0', 'end-1c')
        if len(body) <= 96:
            self.text_config['about_title'] = title
            self.text_config['about_body'] = body
            text_engine.save_text_config(self.text_config)
        self.deploy_to_wot()

    
    def _build_footer(self):
        '''#21242b'''
        footer = tk.Frame(self, bg = '#21242b', padx = 16, pady = 6)
        footer.pack(fill = 'x', side = 'bottom')
        self.lbl_status = tk.Label(footer, text = 'מוכן לפעולה', font = ('Segoe UI', 10), fg = '#06d6a0', bg = '#21242b')
        self.lbl_status.pack(side = 'left')
        self.lbl_credits = tk.Label(footer, text = 'כל הזכויות שמורות ל- @מה-זה-משנה-אה מפורום מתמחים טופ', font = ('Segoe UI', 9, 'bold'), fg = '#ffd166', bg = '#21242b')
        self.lbl_credits.pack(side = 'left', expand = True)
        self.lbl_count = tk.Label(footer, text = 'מותאמים אישית: 0 / 70', font = ('Segoe UI', 10, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        self.lbl_count.pack(side = 'right')

    
    def _on_mousewheel(self, event):
        steps = int(-1 * (event.delta / 120)) * 2
        self.canvas.yview_scroll(steps, 'units')

    
    def _on_canvas_configure(self, event):
        avail_w = event.width - START_X
        new_cols = max(2, avail_w // (CARD_W + GAP_X))
        if new_cols != self.current_cols:
            self.current_cols = new_cols
            self._render_gallery()
            return None

    
    def _render_gallery(self):
        '''all'''
        self.canvas.delete('all')
        cols = self.current_cols
        for slot in range(1, TOTAL_WALLPAPERS + 1):
            item = self.slot_state.get(slot)
            if not item:
                continue
            is_custom = item['is_custom']
            is_selected = slot == self.selected_slot
            idx = slot - 1
            r = idx // cols
            c = idx % cols
            x1 = START_X + c * (CARD_W + GAP_X)
            y1 = START_Y + r * (CARD_H + GAP_Y)
            x2 = x1 + CARD_W
            y2 = y1 + CARD_H
            cx = (x1 + x2) // 2
            bg_col = '#1b3022' if is_custom else '#262930'
            if is_selected:
                pass
            elif is_custom:
                pass
            
            border_col = '#343a40'
            if is_selected:
                pass
            elif is_custom:
                pass
            
            border_w = 1
            self.canvas.create_rectangle(x1, y1, x2, y2, fill = bg_col, outline = border_col, width = border_w, tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''bg_{slot}''', 'card_body'))
            title_col = '#06d6a0' if is_custom else '#f8f9fa'
            self.canvas.create_text(cx, y1 + 14, text = f'''טפט #{slot}''', fill = title_col, font = ('Segoe UI', 10, 'bold'), tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''title_{slot}''', 'card_body'))
            tag_txt = '★ מותאם אישית' if is_custom else 'מקורי'
            tag_col = '#06d6a0' if is_custom else '#6c757d'
            self.canvas.create_text(cx, y1 + 30, text = tag_txt, fill = tag_col, font = ('Segoe UI', 8), tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''tag_{slot}''', 'card_body'))
            if slot in self.thumb_images:
                self.canvas.create_image(cx, y1 + 135, image = self.thumb_images[slot], tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''img_{slot}''', 'card_body'))
            btn_rep_x1 = x1 + 10
            btn_rep_x2 = cx - 4
            btn_y1 = y2 - 34
            btn_y2 = y2 - 10
            self.canvas.create_rectangle(btn_rep_x1, btn_y1, btn_rep_x2, btn_y2, fill = '#3d405b', outline = '', tags = (f'''slot_{slot}''', f'''btn_rep_{slot}''', f'''btn_rep_bg_{slot}''', 'btn_rep'))
            self.canvas.create_text((btn_rep_x1 + btn_rep_x2) // 2, (btn_y1 + btn_y2) // 2, text = 'החלף...', fill = '#ffffff', font = ('Segoe UI', 8, 'bold'), tags = (f'''slot_{slot}''', f'''btn_rep_{slot}''', 'btn_rep'))
            btn_rst_x1 = cx + 4
            btn_rst_x2 = x2 - 10
            rst_bg = '#5c2429' if is_custom else '#252830'
            rst_fg = '#ff6b6b' if is_custom else '#495057'
            self.canvas.create_rectangle(btn_rst_x1, btn_y1, btn_rst_x2, btn_y2, fill = rst_bg, outline = '', tags = (f'''slot_{slot}''', f'''btn_rst_{slot}''', f'''btn_rst_bg_{slot}''', 'btn_rst'))
            self.canvas.create_text((btn_rst_x1 + btn_rst_x2) // 2, (btn_y1 + btn_y2) // 2, text = 'איפוס', fill = rst_fg, font = ('Segoe UI', 8), tags = (f'''slot_{slot}''', f'''btn_rst_{slot}''', f'''btn_rst_txt_{slot}''', 'btn_rst'))
            self._bind_card_events(slot)
        total_rows = (TOTAL_WALLPAPERS + cols - 1) // cols
        total_h = START_Y + total_rows * (CARD_H + GAP_Y) + 20
        self.canvas.config(scrollregion = (0, 0, START_X + cols * (CARD_W + GAP_X), total_h))

    
    def _bind_card_events(self, slot):
        '''card_'''
        card_tag = f'''card_{slot}'''
        rep_tag = f'''btn_rep_{slot}'''
        rst_tag = f'''btn_rst_{slot}'''
        self.canvas.tag_bind(card_tag, '<Button-1>', (lambda e, s = slot: self.select_slot(s)))
        self.canvas.tag_bind(card_tag, '<Double-Button-1>', (lambda e, s = slot: self.replace_wallpaper(s)))
        self.canvas.tag_bind(card_tag, '<Button-3>', (lambda e, s = slot: self._show_card_context_menu(e, s)))
        self.canvas.tag_bind(card_tag, '<Enter>', (lambda e, s = slot: self._on_card_hover(s, True)))
        self.canvas.tag_bind(card_tag, '<Leave>', (lambda e, s = slot: self._on_card_hover(s, False)))
        self.canvas.tag_bind(rep_tag, '<Button-1>', (lambda e, s = slot: self.replace_wallpaper(s)))
        self.canvas.tag_bind(rep_tag, '<Enter>', (lambda e, s = slot: self._on_btn_rep_hover(s, True)))
        self.canvas.tag_bind(rep_tag, '<Leave>', (lambda e, s = slot: self._on_btn_rep_hover(s, False)))
        self.canvas.tag_bind(rst_tag, '<Button-1>', (lambda e, s = slot: self._on_click_reset(s)))
        self.canvas.tag_bind(rst_tag, '<Enter>', (lambda e, s = slot: self._on_btn_rst_hover(s, True)))
        self.canvas.tag_bind(rst_tag, '<Leave>', (lambda e, s = slot: self._on_btn_rst_hover(s, False)))

    
    def _show_card_context_menu(self, event, slot):
        self.select_slot(slot)
        menu = tk.Menu(self, tearoff = 0, bg = '#21242b', fg = '#ffffff', activebackground = '#06d6a0', activeforeground = '#111215')
        menu.add_command(label = f'''🖼️ טפט #{slot}''', state = 'disabled')
        menu.add_separator()
        menu.add_command(label = '✏️ החלף תמונה...', command = (lambda s = slot: self.replace_wallpaper(s)))
        menu.add_command(label = '⇄ החלף מיקום עם טפט אחר...', command = (lambda s = slot: self.open_swap_dialog(s)))
        item = self.slot_state.get(slot, { })
        if item.get('is_custom'):
            menu.add_command(label = '↺ איפוס טפט זה למקור', command = (lambda s = slot: self.reset_wallpaper(s)))
        menu.add_separator()
        menu.add_command(label = '🔍 הגדל פי 2 (480x640)', command = (lambda s = slot: ZoomDialog(self, self.slot_state[s]['image'], s)))
        menu.add_command(label = '💾 שמור תמונה למחשב...', command = (lambda s = slot: self._export_slot_image(s)))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
            return None
        finally:
            menu.grab_release()


    
    def _on_card_hover(self, slot, is_entering):
        if slot == self.selected_slot:
            return None
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if is_entering:
            self.canvas.itemconfig(f'''bg_{slot}''', outline = '#4cc9f0', width = 2)
            self.canvas.config(cursor = 'hand2')
            return None
        border_col = '#06d6a0' if is_custom else '#343a40'
        border_w = 2 if is_custom else 1
        self.canvas.itemconfig(f'''bg_{slot}''', outline = border_col, width = border_w)
        self.canvas.config(cursor = '')

    
    def _on_btn_rep_hover(self, slot, is_entering):
        '''btn_rep_bg_'''
        if is_entering:
            self.canvas.itemconfig(f'''btn_rep_bg_{slot}''', fill = '#05b888')
            self.canvas.config(cursor = 'hand2')
            return None
        self.canvas.itemconfig(f'''btn_rep_bg_{slot}''', fill = '#3d405b')
        self.canvas.config(cursor = '')

    
    def _on_btn_rst_hover(self, slot, is_entering):
        '''is_custom'''
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if not is_custom:
            return None
        if is_entering:
            self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#e63946')
            self.canvas.config(cursor = 'hand2')
            return None
        self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#5c2429')
        self.canvas.config(cursor = '')

    
    def _on_click_reset(self, slot):
        '''is_custom'''
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if is_custom:
            self.reset_wallpaper(slot)
            return None

    
    def select_slot(self, slot):
        if not (1 <= slot) or not (slot <= TOTAL_WALLPAPERS):
            return None

    
    def _navigate_slot(self, delta):
        new_slot = self.selected_slot + delta
        if not (1 <= new_slot) or new_slot <= TOTAL_WALLPAPERS:
            pass
        else:
            return None
        self.select_slot(new_slot)
        idx = new_slot - 1
        row = idx // self.current_cols
        total_rows = (TOTAL_WALLPAPERS + self.current_cols - 1) // self.current_cols
        fraction = max(0, min(1, row / max(1, total_rows - 1)))
        self.canvas.yview_moveto(fraction)

    
    def _update_hd_preview(self):
        slot = self.selected_slot
        item = self.slot_state.get(slot)
        if not item:
            return None
        im = item['image']
        is_custom = item['is_custom']
        self.hd_tk = ImageTk.PhotoImage(im)
        self.hd_canvas.delete('all')
        self.hd_canvas.create_image(120, 160, image = self.hd_tk)
        self.lbl_slot_title.config(text = f'''טפט #{slot}''', fg = '#06d6a0' if is_custom else '#ffffff')
        if is_custom:
            self.lbl_slot_badge.config(text = '★ מותאם אישית (מוכן לצריבה)', fg = '#06d6a0')
            self.btn_hd_reset.config(state = 'normal', bg = '#5c2429', fg = '#ff6b6b')
            return None
        self.lbl_slot_badge.config(text = 'מקורי (ברירת מחדל)', fg = '#adb5bd')
        self.btn_hd_reset.config(state = 'disabled', bg = '#2c3038', fg = '#555b68')

    
    def _open_zoom_modal(self):
        '''image'''
        slot = self.selected_slot
        item = self.slot_state.get(slot)
        if item:
            ZoomDialog(self, item['image'], slot)
            return None

    
    def _export_slot_image(self, slot = None):
        if slot is None:
            slot = self.selected_slot
        item = self.slot_state.get(slot)
        if not item:
            return None
        dest = filedialog.asksaveasfilename(title = f'''שמור טפט #{slot} למחשב''', defaultextension = '.png', initialfile = f'''q8_wallpaper_{slot}.png''', filetypes = [
            ('PNG Image', '*.png'),
            ('JPEG Image', '*.jpg')])
        if dest:
            item['image'].save(dest)
            messagebox.showinfo('נשמר בהצלחה', f'''הטפט נשמר בהצלחה בנתיב:\n{dest}''')
            return None

    
    def _export_current_image(self):
        self._export_slot_image(self.selected_slot)

    
    def load_and_refresh_from_wot(self):
        '''‏טוען נתונים חיים מתוכנת WOT...'''
        self.lbl_status.config(text = '‏טוען נתונים חיים מתוכנת WOT...')
        
        try:
            live_data, live_theme_hex, live_title, live_body = mmi_builder.load_live_wot_state()
            self.slot_state = live_data
            if live_theme_hex:
                self.confirmed_theme_hex = live_theme_hex
                self.current_theme_hex = live_theme_hex
                preset_name = 'מותאם אישית (מ-WOT)'
                for p in theme_engine.PRESETS:
                    if not p['hex'].upper() == live_theme_hex.upper():
                        continue
                    preset_name = p['name']
                    theme_engine.PRESETS
                self.confirmed_theme_name = preset_name
                self.current_theme_name = preset_name
                theme_engine.save_theme_config(live_theme_hex, preset_name)
                if hasattr(self, 'lbl_active_theme_name'):
                    self.lbl_active_theme_name.config(text = preset_name)
                if hasattr(self, 'swatch_canvas'):
                    self.swatch_canvas.config(bg = live_theme_hex)
                if hasattr(self, '_update_theme_info_card'):
                    self._update_theme_info_card()
                if hasattr(self, '_update_theme_mockup'):
                    self._update_theme_mockup()
                if hasattr(self, '_update_preset_card_highlights'):
                    self._update_preset_card_highlights()
            if live_title:
                self.about_title_var.set(live_title)
            if live_body:
                self.about_body_str = live_body
                if hasattr(self, 'txt_about_body'):
                    self.txt_about_body.delete('1.0', 'end')
                    self.txt_about_body.insert('1.0', live_body)
                    self._on_about_text_changed()
            custom_count = 0
            for slot in range(1, TOTAL_WALLPAPERS + 1):
                item = self.slot_state[slot]
                if item['is_custom']:
                    custom_count += 1
                thumb = make_sharp_thumbnail(item['image'])
                self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
            self._render_gallery()
            self.select_slot(self.selected_slot)
            self.lbl_count.configure(text = f'''מותאמים אישית: {custom_count} / {TOTAL_WALLPAPERS}''')
            self.lbl_status.config(text = '‏● מסונכרן בזמן אמת מול מה שמוכן לצריבה בתוכנת WOT')
        except Exception as e:
            self.lbl_status.config(text = f'''‏שגיאה בסנכרון מתוכנת WOT: {e}''')
            return None


    
    def _update_single_card(self, slot):
        item = self.slot_state.get(slot)
        if not item:
            return None
        is_custom = item['is_custom']
        thumb = make_sharp_thumbnail(item['image'])
        self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
        self.canvas.itemconfig(f'''img_{slot}''', image = self.thumb_images[slot])
        self.canvas.itemconfig(f'''tag_{slot}''', text = '★ מותאם אישית' if is_custom else 'מקורי', fill = '#06d6a0' if is_custom else '#6c757d')
        self.canvas.itemconfig(f'''title_{slot}''', fill = '#06d6a0' if is_custom else '#f8f9fa')
        if slot == self.selected_slot:
            pass
        elif is_custom:
            pass
        
        if slot == self.selected_slot:
            pass
        elif is_custom:
            pass
        
        # NOTE(recovery): decompiler lost this canvas call (target + args corrupted);
        # verify against original source. Neutralized so it is a no-op instead of a crash.
        # '#06d6a0'('#343a40', fill = 3, outline = 2, width = 1)
        self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#5c2429' if is_custom else '#252830')
        self.canvas.itemconfig(f'''btn_rst_txt_{slot}''', fill = '#ff6b6b' if is_custom else '#495057')
        custom_count = sum(1 for s in range(1, TOTAL_WALLPAPERS + 1) if self.slot_state.get(s, { }).get('is_custom'))
        self.lbl_count.configure(text = f'''מותאמים אישית: {custom_count} / {TOTAL_WALLPAPERS}''')
        if slot == self.selected_slot:
            self._update_hd_preview()
            return None

    
    def replace_wallpaper(self, slot):
        '''קבצי תמונה'''
        filetypes = [
            ('קבצי תמונה', '*.jpg;*.jpeg;*.png;*.webp;*.bmp'),
            ('JPEG', '*.jpg;*.jpeg'),
            ('PNG', '*.png'),
            ('כל הקבצים', '*.*')]
        chosen = filedialog.askopenfilename(title = f'''בחר תמונה עבור טפט #{slot}''', filetypes = filetypes)
        if chosen:
            dialog = ImageCropDialog(self, chosen, slot)
            self.wait_window(dialog)
            if dialog.result_image:
                if slot not in self.slot_state:
                    self.slot_state[slot] = { }
                self.slot_state[slot]['image'] = dialog.result_image
                self.slot_state[slot]['sjpg'] = None
                self.slot_state[slot]['is_custom'] = True
                png_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
                
                try:
                    dialog.result_image.save(png_path, format = 'PNG')
                except Exception:
                    pass

                sjpg_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
                if os.path.exists(sjpg_path):
                    
                    try:
                        os.remove(sjpg_path)
                    except Exception:
                        pass

                self.select_slot(slot)
                self._update_single_card(slot)
                self.lbl_status.config(text = f'''‏טפט #{slot} עודכן בהצלחה! לחץ על \'החל\' כדי לפרוס לתוכנת WOT.''')
                return None
            return None

    
    def open_swap_dialog(self, initial_slot = None):
        slot_a = initial_slot if initial_slot is not None else self.selected_slot
        WallpaperSwapDialog(self, initial_slot_a = slot_a)

    
    def swap_wallpapers(self, slot_a, slot_b):
        if slot_a == slot_b:
            return False
        if not (1 <= slot_a) or slot_a <= TOTAL_WALLPAPERS:
            pass
        else:
            return False
        if not (1 <= slot_b) or not (slot_b <= TOTAL_WALLPAPERS):
            return False
        return False

    
    def reset_wallpaper(self, slot):
        '''wp_'''
        orig_jpg = os.path.join(ORIG_WP_DIR, f'''wp_{slot}.jpg''')
        if os.path.exists(orig_jpg):
            im = Image.open(orig_jpg).convert('RGB')
        else:
            with open(mmi_builder.MMI_DUMP_PATH, 'rb') as f:
                dump = f.read()
            if slot == 1:
                im = spd_sjpg.sjpg_to_image(dump[892172:894723])
            else:
                idx = slot - 2
                slot_info = mmi_builder.get_slot_info(dump)
                (abs_off, sz, _) = slot_info[idx]
                im = spd_sjpg.sjpg_to_image(dump[abs_off:abs_off + sz])
        if slot not in self.slot_state:
            self.slot_state[slot] = { }
        self.slot_state[slot]['image'] = im
        self.slot_state[slot]['sjpg'] = None
        self.slot_state[slot]['is_custom'] = False
        custom_png = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
        if os.path.exists(custom_png):
            os.remove(custom_png)
        custom_sjpg = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
        if os.path.exists(custom_sjpg):
            os.remove(custom_sjpg)
        self.select_slot(slot)
        self._update_single_card(slot)
        self.lbl_status.config(text = f'''‏טפט #{slot} הוחזר למקור. לחץ על \'החל\' לצריבה.''')

    
    def reset_all_wallpapers(self):
        '''איפוס כל הטפטים'''
        if not messagebox.askyesno('איפוס כל הטפטים', 'האם לשחזר את כל 70 הטפטים לקבצים המקוריים?'):
            return None
        with open(mmi_builder.MMI_DUMP_PATH, 'rb') as f:
            dump = f.read()
        slot_info = mmi_builder.get_slot_info(dump)
        for slot in range(1, TOTAL_WALLPAPERS + 1):
            if slot == 1:
                im = spd_sjpg.sjpg_to_image(dump[892172:894723])
            else:
                idx = slot - 2
                (abs_off, sz, _) = slot_info[idx]
                im = spd_sjpg.sjpg_to_image(dump[abs_off:abs_off + sz])
            if slot not in self.slot_state:
                self.slot_state[slot] = { }
            self.slot_state[slot]['image'] = im
            self.slot_state[slot]['sjpg'] = None
            self.slot_state[slot]['is_custom'] = False
            custom_png = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
            if os.path.exists(custom_png):
                os.remove(custom_png)
            custom_sjpg = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
            if os.path.exists(custom_sjpg):
                os.remove(custom_sjpg)
            thumb = make_sharp_thumbnail(im)
            self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
        self._render_gallery()
        self.select_slot(self.selected_slot)
        self.lbl_count.configure(text = f'''מותאמים אישית: 0 / {TOTAL_WALLPAPERS}''')
        self.lbl_status.config(text = "‏כל הטפטים אופסו למקור. לחץ על 'החל' לצריבה נקייה.")
        messagebox.showinfo('איפוס למקור', "‏כל 70 הטפטים אופסו למקור.\nלחץ על 'החל והכן לצריבה בתוכנת WOT' כדי לעדכן את WOT.")

    
    def deploy_to_wot(self):
        if self.is_deploying:
            return None
        self.is_deploying = True
        self.btn_deploy.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        self.lbl_status.config(text = '‏מעבד נתונים, טקסטים וערכת נושא...')
        
        def _worker():
            
            try:
                import importlib
                importlib.reload(theme_engine)
                importlib.reload(text_engine)
                importlib.reload(mmi_builder)
                custom_wallpapers = { }
                for slot in range(1, TOTAL_WALLPAPERS + 1):
                    item = self.slot_state.get(slot)
                    if not item or not item.get('is_custom'):
                        continue
                    if item.get('image') is not None:
                        custom_wallpapers[slot] = item['image']
                        continue
                    if item.get('sjpg') is not None:
                        custom_wallpapers[slot] = item['sjpg']
                        continue
                    png_p = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
                    if not os.path.exists(png_p):
                        continue
                    custom_wallpapers[slot] = Image.open(png_p).convert('RGB')
                self.post_ui((lambda : self.lbl_status.config(text = '‏בונה את קובץ המשאבים, הטקסטים וערכת הנושא...')))
                use_icons = self.use_unisoc_icons.get() if hasattr(self, 'use_unisoc_icons') else False
                orig, mod = mmi_builder.build_modified_mmi(custom_wallpapers, theme_hex = self.confirmed_theme_hex, use_unisoc_icons = use_icons)
                diff_table = mmi_builder.generate_diff_table(orig, mod)
                self.post_ui((lambda : self.lbl_status.config(text = '‏מטמיע את ה-DLL בתיקיית WOT...')))
                dll_generator.build_and_deploy_dll(diff_table)
                self.post_ui((lambda : self._on_deploy_success(len(custom_wallpapers))))
            except Exception as e:
                self.post_ui((lambda err = e: self._on_deploy_error(err)))
                return None


        threading.Thread(target = _worker, daemon = True).start()

    
    def _on_deploy_success(self, count):
        self.is_deploying = False
        self.btn_deploy.config(state = 'normal', text = '‏🚀 החל והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'normal', text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'normal', text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT')
        self.lbl_status.config(text = '‏הגרסה נפרסה בהצלחה בתוכנת WOT!')
        self.load_and_refresh_from_wot()
        messagebox.showinfo('הצריבה מוכנה בהצלחה!', f'''‏הגרסה הוכנה בהצלחה ונפרסה ישירות לתוכנת WOT!\n\n• טפטים שהותאמו אישית: {count}\n• צבע ערכת נושא: {self.confirmed_theme_name} ({self.confirmed_theme_hex})\n• מסך \'אודות\' וטקסטים מותאמים: נצרבו בהצלחה\n• כל שאר הטפטים והרכיבים: מקוריים ותקינים לחלוטין\n• באנר שיחה נכנסת, פסי הניווט והתפריטים עודכנו בצבע הנבחר.\n\nכעת פתח את תוכנת WOT ולחץ Start לצריבה!''')

    
    def _on_deploy_error(self, error):
        self.is_deploying = False
        self.btn_deploy.config(state = 'normal', text = '‏🚀 החל והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'normal', text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'normal', text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT')
        self.lbl_status.config(text = '‏שגיאה בבנייה')
        messagebox.showerror('שגיאה', f'''‏אירעה שגיאה בעת הכנת הגרסה:\n{error}''')


if __name__ == '__main__':
    app = Q8WallpaperStudio()
    app.mainloop()
