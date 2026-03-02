import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import re
import random
import time
import math
import os
import shutil
import platform
import webbrowser
import threading
import json

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCode Playground")
        self.root.geometry("900x600")
        self.root.configure(bg="#f4f4f4")

        # --- Settings ---
        self.settings = {
            "font": "Consolas",
            "size": 12,
            "theme": "Light",
            "minimap": True,
            "default_ai_model": "Intelligent",
            "username": "Coder"
        }
        self.ai_history = []
        self.shift_pressed = False
        self.ai_usage = {"Casual": 0, "Intelligent": 0, "Advanced Mode": 0}
        self.ai_recharge_time = {"Casual": 0, "Intelligent": 0, "Advanced Mode": 0}
        self.taskbar_buttons = {}

        # Load CodePlace Data
        self.codeplace_data = []
        try:
            with open("codeplace.json", "r") as f:
                self.codeplace_data = json.load(f)
        except:
            self.codeplace_data = []

        # --- Main Layout ---
        # Use a main frame with padding for a clean look
        self.main_container = tk.Frame(root, bg="#f4f4f4", padx=15, pady=15)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # --- Toolbar Section ---
        self.toolbar = tk.Frame(self.main_container, bg="#f4f4f4")
        self.toolbar.pack(fill=tk.X, pady=(0, 10))

        # Button Styling (Neutral and Minimal)
        btn_style = {
            "bg": "#e0e0e0", 
            "fg": "#333333", 
            "activebackground": "#d0d0d0",
            "relief": "flat",
            "padx": 15, 
            "pady": 6, 
            "font": ("Segoe UI", 9),
            "bd": 0
        }

        # Buttons
        tk.Button(self.toolbar, text="▶ Run", command=self.run_code, **btn_style).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(self.toolbar, text="🗑 Clear", command=self.clear_all, **btn_style).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(self.toolbar, text="💾 File", command=self.show_file_options, **btn_style).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(self.toolbar, text="📖 Manual", command=self.show_manual, **btn_style).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(self.toolbar, text="🤖 AI Builder", command=self.show_ai_builder, **btn_style).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(self.toolbar, text="☁ CodePlace", command=self.show_codeplace, **btn_style).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(self.toolbar, text="⚙ Settings", command=self.show_settings, **btn_style).pack(side=tk.LEFT, padx=(8, 0))

        self.root.bind("<Shift_L>", lambda e: self.set_shift(True))
        self.root.bind("<KeyRelease-Shift_L>", lambda e: self.set_shift(False))
        self.root.bind("<Shift_R>", lambda e: self.set_shift(True))
        self.root.bind("<KeyRelease-Shift_R>", lambda e: self.set_shift(False))

        # --- Workspace Section ---
        self.paned = tk.PanedWindow(self.main_container, orient=tk.VERTICAL, sashwidth=5, bg="#f4f4f4", bd=0)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.frame_editor = tk.Frame(self.paned, bg="#f4f4f4")
        self.lbl_workspace = tk.Label(self.frame_editor, text="Workspace", bg="#f4f4f4", fg="#555", font=("Segoe UI", 10, "bold"))
        self.lbl_workspace.pack(anchor="w", pady=(0, 5))
        
        self.editor_container = tk.Frame(self.frame_editor, bg="#f4f4f4")
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            self.editor_container,
            width=4,
            padx=5,
            pady=10,
            takefocus=0,
            border=0,
            background="#f0f0f0",
            foreground="#888",
            state="disabled",
            font=("Consolas", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.minimap = tk.Text(
            self.editor_container,
            width=18,
            font=("Consolas", 3),
            bg="white",
            fg="#555",
            relief="flat",
            state="disabled",
            takefocus=0,
            bd=0,
            pady=10
        )
        self.minimap.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            self.editor_container, 
            height=14, 
            font=("Consolas", 12), 
            bg="white", 
            fg="#2c3e50", 
            relief="flat", 
            padx=10, 
            pady=10,
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.config(yscrollcommand=self.sync_scroll)
        
        self.editor.tag_configure("keyword", foreground="#0000FF", font=("Consolas", 12, "bold"))
        self.editor.tag_configure("string", foreground="#008000")
        self.editor.tag_configure("comment", foreground="#AAAAAA", font=("Consolas", 12, "italic"))
        self.editor.tag_configure("ai_comment", foreground="#505050", font=("Consolas", 12, "italic"))
        self.editor.tag_configure("variable", foreground="#FF8000")
        self.editor.bind("<KeyRelease>", self.highlight_syntax)

        self.paned.add(self.frame_editor, height=400)

        # --- Output Window Section ---
        self.frame_output = tk.Frame(self.paned, bg="#f4f4f4")
        self.lbl_output = tk.Label(self.frame_output, text="Output", bg="#f4f4f4", fg="#555", font=("Segoe UI", 10, "bold"))
        self.lbl_output.pack(anchor="w", pady=(5, 5))
        
        self.output = tk.Text(
            self.frame_output, 
            height=6, 
            font=("Consolas", 11), 
            bg="#fafafa", 
            fg="#333", 
            relief="flat", 
            padx=10, 
            pady=10,
            state="disabled",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        self.paned.add(self.frame_output)

        # --- Taskbar for Windows ---
        self.taskbar_frame = tk.Frame(self.main_container, bg="#e0e0e0", height=30)
        self.taskbar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        # Load the sample program on startup
        self.load_sample()
        self.highlight_syntax()

    def sync_scroll(self, *args):
        self.line_numbers.yview_moveto(args[0])
        self.minimap.yview_moveto(args[0])

    def update_line_numbers(self):
        lines = int(self.editor.index('end-1c').split('.')[0])
        line_content = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_content)
        self.line_numbers.config(state="disabled")

    def update_minimap(self):
        content = self.editor.get("1.0", tk.END)
        self.minimap.config(state="normal")
        self.minimap.delete("1.0", tk.END)
        self.minimap.insert("1.0", content)
        self.minimap.config(state="disabled")
        self.minimap.yview_moveto(self.editor.yview()[0])

    def set_shift(self, pressed):
        self.shift_pressed = pressed

    def load_sample(self):
        sample_code = """# MiniAI Chatbot
show "Hello! I am MiniAI."
ask "What is your name?" name
show "Nice to meet you,"
show $name

rand 1 3 mood
if $mood == 1
    show "I am happy today!"
end
if $mood == 2
    show "I am feeling sleepy."
end
if $mood == 3
    show "I am ready to code!"
end
"""
        self.editor.insert("1.0", sample_code)

    def log(self, message):
        self.output.config(state="normal")
        self.output.insert(tk.END, str(message) + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def clear_output(self):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")

    def clear_all(self):
        self.editor.delete("1.0", tk.END)
        self.clear_output()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MiniCode Files", "*.mcd"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.highlight_syntax()
                self.log(f"Opened {file_path}")
            except Exception as e:
                self.log(f"Error opening file: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mcd", 
            filetypes=[("MiniCode Files", "*.mcd"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.editor.get("1.0", tk.END))
                self.log(f"Saved to {file_path}")
            except Exception as e:
                self.log(f"Error saving file: {e}")

    def save_as_python(self):
        code = self.editor.get("1.0", tk.END)
        py_code = self.transpile_to_python(code)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(py_code)
                self.log(f"Saved Python to {file_path}")
            except Exception as e:
                self.log(f"Error saving python file: {e}")

    def save_as_js(self):
        code = self.editor.get("1.0", tk.END)
        js_code = self.transpile_to_js(code)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".js",
            filetypes=[("JavaScript Files", "*.js"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(js_code)
                self.log(f"Saved JS to {file_path}")
            except Exception as e:
                self.log(f"Error saving JS file: {e}")

    def save_as_csharp(self):
        code = self.editor.get("1.0", tk.END)
        cs_code = self.transpile_to_csharp(code)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cs",
            filetypes=[("C# Files", "*.cs"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(cs_code)
                self.log(f"Saved C# to {file_path}")
            except Exception as e:
                self.log(f"Error saving C# file: {e}")

    def show_file_options(self):
        c = self.get_theme_colors(self.settings["theme"])
        file_win = tk.Toplevel(self.root)
        file_win.title("File Operations")
        file_win.geometry("300x300")
        file_win.configure(bg=c["bg"])

        tk.Label(file_win, text="Save / Load", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 12, "bold")).pack(pady=10)

        btn_style = {"bg": c["btn_bg"], "fg": c["btn_fg"], "relief": "flat", "padx": 10, "pady": 5, "width": 30}

        tk.Button(file_win, text="📂 Open File", command=lambda: [self.open_file(), file_win.destroy()], **btn_style).pack(pady=5)
        tk.Button(file_win, text="💾 Save as MiniScript (.mcd)", command=lambda: [self.save_file(), file_win.destroy()], **btn_style).pack(pady=5)
        tk.Button(file_win, text="🐍 Save as Python (.py)", command=lambda: [self.save_as_python(), file_win.destroy()], **btn_style).pack(pady=5)
        tk.Button(file_win, text="📜 Save as JavaScript (.js)", command=lambda: [self.save_as_js(), file_win.destroy()], **btn_style).pack(pady=5)
        tk.Button(file_win, text="#️⃣ Save as C# (.cs)", command=lambda: [self.save_as_csharp(), file_win.destroy()], **btn_style).pack(pady=5)

    def save_codeplace_data(self):
        try:
            with open("codeplace.json", "w") as f:
                json.dump(self.codeplace_data, f)
        except Exception as e:
            print(f"Error saving CodePlace data: {e}")

    def show_codeplace(self):
        c = self.get_theme_colors(self.settings["theme"])
        cp_win = tk.Toplevel(self.root)
        cp_win.title("CodePlace - Community Code")
        cp_win.geometry("600x500")
        cp_win.configure(bg=c["bg"])

        notebook = ttk.Notebook(cp_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Browse Tab
        frame_browse = tk.Frame(notebook, bg=c["bg"])
        notebook.add(frame_browse, text="Browse")

        search_frame = tk.Frame(frame_browse, bg=c["bg"])
        search_frame.pack(fill=tk.X, pady=5)
        tk.Label(search_frame, text="Search:", bg=c["bg"], fg=c["fg"]).pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30, bg=c["edit_bg"], fg=c["edit_fg"], insertbackground=c["fg"])
        search_entry.pack(side=tk.LEFT, padx=5)
        
        list_frame = tk.Frame(frame_browse, bg=c["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        code_list = tk.Listbox(list_frame, bg=c["edit_bg"], fg=c["edit_fg"], selectbackground=c["btn_bg"], selectforeground=c["btn_fg"])
        code_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=code_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        code_list.config(yscrollcommand=scrollbar.set)

        def refresh_list():
            code_list.delete(0, tk.END)
            query = search_var.get().lower()
            for item in self.codeplace_data:
                if query in item["title"].lower() or query in item["desc"].lower() or query in item["author"].lower():
                    code_list.insert(tk.END, f"{item['title']} (by {item['author']})")

        tk.Button(search_frame, text="Go", command=refresh_list, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat").pack(side=tk.LEFT)
        search_entry.bind("<Return>", lambda e: refresh_list())

        def load_selected():
            sel = code_list.curselection()
            if sel:
                query = search_var.get().lower()
                filtered = [item for item in self.codeplace_data if query in item["title"].lower() or query in item["desc"].lower() or query in item["author"].lower()]
                if sel[0] < len(filtered):
                    item = filtered[sel[0]]
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", item["code"])
                    self.highlight_syntax()
                    cp_win.destroy()
                    messagebox.showinfo("CodePlace", f"Loaded '{item['title']}'")

        tk.Button(frame_browse, text="Load Selected Code", command=load_selected, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat").pack(pady=5)
        refresh_list()

        # Upload Tab
        frame_upload = tk.Frame(notebook, bg=c["bg"])
        notebook.add(frame_upload, text="Upload")

        tk.Label(frame_upload, text="Title:", bg=c["bg"], fg=c["fg"]).pack(anchor="w", padx=10, pady=(10, 0))
        title_entry = tk.Entry(frame_upload, width=40, bg=c["edit_bg"], fg=c["edit_fg"], insertbackground=c["fg"])
        title_entry.pack(anchor="w", padx=10, pady=5)

        tk.Label(frame_upload, text="Description:", bg=c["bg"], fg=c["fg"]).pack(anchor="w", padx=10)
        desc_entry = tk.Entry(frame_upload, width=40, bg=c["edit_bg"], fg=c["edit_fg"], insertbackground=c["fg"])
        desc_entry.pack(anchor="w", padx=10, pady=5)

        def upload_code():
            title = title_entry.get().strip()
            desc = desc_entry.get().strip()
            code = self.editor.get("1.0", tk.END).strip()
            author = self.settings.get("username", "Anonymous")
            
            if not title:
                messagebox.showwarning("Upload", "Title is required.")
                return
            if not code:
                messagebox.showwarning("Upload", "Editor is empty.")
                return

            new_item = {"title": title, "desc": desc, "code": code, "author": author, "date": time.strftime("%Y-%m-%d")}
            self.codeplace_data.append(new_item)
            self.save_codeplace_data()
            messagebox.showinfo("CodePlace", "Code uploaded successfully!")
            title_entry.delete(0, tk.END)
            desc_entry.delete(0, tk.END)
            refresh_list()
            notebook.select(frame_browse)

        tk.Button(frame_upload, text="Upload Current Code", command=upload_code, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat").pack(pady=20)

    def get_manual_text(self):
        return """MiniCode Language Guide
=======================

1. Variables
   - Syntax: var = value
   - Example: x = 10
   - Example: name = "Alex"

2. Output
   - Syntax: show value
   - Example: show $x
   - Example: show "Hello"

3. Conditionals
   - Use 'if' and 'end'.
   - Operators: >, <, ==, !=, >=, <=
   
   Example:
   if $x > 5
       show "Big"
   end

4. Rules
   - Loops use 'repeat'.
   - Keywords < 5 letters.

5. Functions
   - Define: func name ... end
   - Call: call name
   - Note: Functions must be defined before calling.

6. Input & Random
   - Input: ask "Prompt" var
   - Random: rand min max var
   
   Example:
   ask "Name?" n
   rand 1 10 x

7. Windows
   - Create: window var
   - Title: title var "Text"
   - Size: size var w h
   - Text: text var "Content" x y
   - Color: color var "Hex/Name"
   - Close: close var
   
   Example:
   window win
   title win "My App"
   size win 300 200
   text win "Hello" 50 50
   color win "white"
   wait 2
   close win

8. Utilities
   - Wait: wait seconds
   
   Example:
   show "Loading..."
   wait 2
   show "Done"

9. Arrays
   - Create: array name v1 v2 ...
   - Access: $name[index]
   
   Example:
   array nums 10 20 30
   show $nums[1]

10. Loops
   - Repeat: repeat n ... end
   
   Example:
   repeat 3
       show "Hello"
   end

11. System
   - Clear: clear

12. Math
   - Operators: +, -, *, /
   - Syntax: var = val1 op val2
   
   Example:
   sum = $a + $b

13. Extras
   - Popup: popup "Message"
   - Write: write "file.txt" "content"
   
   Example:
   popup "Hello"
   write "log.txt" "Log entry"

14. File I/O (Advanced)
   - Read: read var "file.txt"
   - Append: append "file.txt" "content"

15. Math & Data
   - Math: math var op value
     Ops: sqrt, sin, cos, tan, abs, floor, ceil
   - Length: len var $array_or_string
   
   Example:
   math root sqrt 16
   len l "Hello"

16. System
   - Time: time var
   - Beep: beep

17. String Ops
   - Upper: upper var source
   - Lower: lower var source
   - Replace: replace var source old new
   - Split: split var source delim
   
   Example:
   upper u "hello"

18. Advanced Ops
   - Round: round var val
   - Min/Max: min var v1 v2
   - Date: date var
   - Exists: exists var "file.txt"
   - Delete: delete "file.txt"
   - Reverse: reverse var source
   - Sort: sort var array
   - Find: find var source target
   - Substring: sub var source start end

19. File & String Extras
   - Mkdir: mkdir "folder"
   - Rmdir: rmdir "folder"
   - Trim: trim var " string "
   - Join: join var "A" "B"
   - Type: type var val

20. Math Extras & File Ops
   - Pow: pow var base exp
   - Mod: mod var a b
   - Inc: inc var
   - Dec: dec var
   - Copy: copy src dst
   - Move: move src dst
   - Cwd: cwd var
   - List: list var path
   - Abs: abs var val
   - Floor: floor var val

23. System Utilities
   - Clipboard Set: clipset "text"
   - Clipboard Get: clipget var
   - Screen Size: screen w h
   - Mouse Pos: mouse x y
   - Username: username var

21. Advanced Window & File Ops
   - Icon: icon win_var "path.ico"
   - Topmost: topmost win_var 1
   - Center: center win_var
   - Get Size: getsize var "file.txt"
   - Copy File: copyfile "src" "dst"
   - Sleep: sleep milliseconds

22. More Window Control
   - Opacity: opacity win_var 0.8
   - Resizable: resizable win_var 0 0
   - Fullscreen: fullscreen win_var 1
   - Get Position: getpos win_var x_var y_var
   * Note: Press Ctrl+Tab to close any window (useful for fullscreen).

24. Web & System Extras
   - Browser: browser "url"
   - Minimize: minimize win_var
   - Restore: restore win_var
   - Focus: focus win_var
   - File Time: filetime var "path"
   - Is Dir: isdir var "path"
   - Is File: isfile var "path"
   - Constants: pi var, e var
   - RGB: rgb var r g b

25. System & Advanced
   - Platform: platform var
   - Env Var: env var "KEY"
   - Execute: exec "command"
   - Hash: hash var "text"
   - Warp Mouse: warp x y
"""

    def search_manual_func(self, text_widget, entry_widget):
        text_widget.tag_remove("search", "1.0", tk.END)
        query = entry_widget.get()
        if query:
            start = "1.0"
            while True:
                pos = text_widget.search(query, start, stopindex=tk.END, nocase=True)
                if not pos: break
                end = f"{pos}+{len(query)}c"
                text_widget.tag_add("search", pos, end)
                start = end
            text_widget.tag_config("search", background="yellow", foreground="black")

    def show_manual(self):
        c = self.get_theme_colors(self.settings["theme"])
        manual_win = tk.Toplevel(self.root)
        manual_win.title("MiniCode Manual")
        manual_win.geometry("500x400")
        
        manual_win.configure(bg=c["bg"])
        
        search_frame = tk.Frame(manual_win, bg=c["bg"])
        search_frame.pack(fill=tk.X, padx=15, pady=(15, 0))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 10), bg=c["edit_bg"], fg=c["edit_fg"], insertbackground=c["fg"])
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(search_frame, text="Search", command=lambda: self.search_manual_func(manual_text, search_entry), bg=c["btn_bg"], fg=c["btn_fg"], relief="flat").pack(side=tk.LEFT)

        manual_text = tk.Text(
            manual_win, 
            font=("Consolas", 11), 
            bg=c["edit_bg"], 
            fg=c["edit_fg"], 
            relief="flat", 
            padx=15, 
            pady=15,
            highlightthickness=0
        )
        manual_text.pack(fill=tk.BOTH, expand=True)
        
        manual_text.tag_configure("title", foreground=c["fg"], font=("Consolas", 11, "bold"))
        manual_text.tag_configure("desc", foreground=c["edit_fg"])
        manual_text.tag_configure("code", foreground=c.get("keyword", "#0000FF"))
        manual_text.tag_bind("code", "<Button-1>", lambda e: self.handle_manual_click(e, manual_text))
        manual_text.tag_bind("code", "<Enter>", lambda e: manual_text.config(cursor="hand2"))
        manual_text.tag_bind("code", "<Leave>", lambda e: manual_text.config(cursor=""))

        info = self.get_manual_text()
        for line in info.splitlines():
            if line.strip().startswith("-"):
                tag = "code"
            else:
                tag = "title" if line and not line[0].isspace() else "desc"
            manual_text.insert(tk.END, line + "\n", tag)
        
        # Apply syntax highlighting to manual
        keywords = ["if", "end", "func", "call", "show", "ask", "rand", "window", "title", "size", "text", "color", "close", "wait", "array", "repeat", "clear", "popup", "write", "read", "append", "math", "len", "time", "beep", "upper", "lower", "replace", "split", "round", "min", "max", "date", "exists", "delete", "reverse", "sort", "find", "sub", "mkdir", "rmdir", "trim", "join", "type", "pow", "mod", "inc", "dec", "copy", "move", "cwd", "list", "abs", "floor", "icon", "topmost", "center", "getsize", "copyfile", "sleep", "opacity", "resizable", "fullscreen", "getpos", "clipset", "clipget", "screen", "mouse", "username", "browser", "minimize", "restore", "focus", "filetime", "isdir", "isfile", "pi", "e", "rgb", "platform", "env", "exec", "hash", "warp", "starts", "ends", "contains", "index", "speak", "notify"]
        content = manual_text.get("1.0", tk.END)
        for kw in keywords:
            for match in re.finditer(rf"\b{kw}\b", content):
                manual_text.tag_add("code", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
                
        manual_text.config(state="disabled")

    def handle_manual_click(self, event, text_widget):
        try:
            index = text_widget.index(f"@{event.x},{event.y}")
            line_idx = int(index.split('.')[0])
            char_idx = int(index.split('.')[1])
            
            line_text = text_widget.get(f"{line_idx}.0", f"{line_idx}.end")
            
            # Find word boundaries
            start = char_idx
            while start > 0 and (line_text[start-1].isalnum() or line_text[start-1] == '_'):
                start -= 1
            
            end = char_idx
            while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == '_'):
                end += 1
                
            word = line_text[start:end]
            if not word: return

            cmd = word.lower()
            details = self.get_command_details(cmd)
            
            if details:
                self.show_help_window(cmd, details)
        except Exception as e:
            print(f"Error handling click: {e}")

    def show_help_window(self, command, details):
        c = self.get_theme_colors(self.settings["theme"])
        win = tk.Toplevel(self.root)
        win.title(f"Help: {command}")
        win.geometry("400x300")
        win.configure(bg=c["bg"])
        
        tk.Label(win, text=f"Command: {command}", font=("Segoe UI", 12, "bold"), bg=c["bg"], fg=c["fg"]).pack(pady=10)
        
        text = tk.Text(win, font=("Consolas", 10), bg=c["edit_bg"], fg=c["edit_fg"], relief="flat", padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", details)
        text.config(state="disabled")

    def get_command_details(self, cmd):
        docs = {
            "show": "Usage: show [value]\n\nDisplays text or variable value in the output window.\n\nExample:\nshow \"Hello World\"\nshow $myVar",
            "ask": "Usage: ask \"[Prompt]\" [variable]\n\nPrompts the user for input and stores it in a variable.\n\nExample:\nask \"What is your name?\" name\nshow $name",
            "if": "Usage: if [condition]\n    [code]\nend\n\nExecutes code only if the condition is true.\n\nExample:\nif $x > 5\n    show \"Greater than 5\"\nend",
            "repeat": "Usage: repeat [count]\n    [code]\nend\n\nRepeats code a specific number of times.\n\nExample:\nrepeat 3\n    show \"Looping\"\nend",
            "window": "Usage: window [var]\n\nCreates a new window and stores its reference in a variable.\n\nExample:\nwindow myWin\ntitle myWin \"My App\"",
            "title": "Usage: title [win_var] \"[Text]\"\n\nSets the title of a window.\n\nExample:\ntitle w \"Calculator\"",
            "size": "Usage: size [win_var] [width] [height]\n\nSets the size of a window.\n\nExample:\nsize w 400 300",
            "text": "Usage: text [win_var] \"[Content]\" [x] [y]\n\nPlaces a text label on a window at coordinates (x, y).\n\nExample:\ntext w \"Welcome\" 50 50",
            "color": "Usage: color [win_var] \"[Color]\"\n\nSets the background color of a window.\n\nExample:\ncolor w \"lightblue\"",
            "close": "Usage: close [win_var]\n\nCloses a specific window.\n\nExample:\nclose w",
            "wait": "Usage: wait [seconds]\n\nPauses execution for the specified time.\n\nExample:\nwait 2.5",
            "rand": "Usage: rand [min] [max] [var]\n\nGenerates a random number between min and max.\n\nExample:\nrand 1 100 num\nshow $num",
            "math": "Usage: math [var] [op] [val]\n\nPerforms advanced math operations (sqrt, sin, floor, etc.).\n\nExample:\nmath s sqrt 16\nshow $s",
            "time": "Usage: time [var]\n\nGets the current system time (HH:MM:SS).\n\nExample:\ntime now\nshow $now",
            "beep": "Usage: beep\n\nPlays a system beep sound.\n\nExample:\nbeep",
            "popup": "Usage: popup \"[Message]\"\n\nShows a popup alert with a message.\n\nExample:\npopup \"Operation Complete\"",
            "write": "Usage: write \"[file]\" \"[content]\"\n\nWrites content to a file (overwrites).\n\nExample:\nwrite \"log.txt\" \"Started\"",
            "read": "Usage: read [var] \"[file]\"\n\nReads content from a file into a variable.\n\nExample:\nread content \"data.txt\"",
            "append": "Usage: append \"[file]\" \"[content]\"\n\nAppends content to the end of a file.\n\nExample:\nappend \"log.txt\" \"\\nNew Entry\"",
            "len": "Usage: len [var] [source]\n\nGets the length of a string or array.\n\nExample:\nlen l \"Hello\"\nshow $l",
            "upper": "Usage: upper [var] [string]\n\nConverts string to uppercase.\n\nExample:\nupper u \"hello\"\nshow $u",
            "lower": "Usage: lower [var] [string]\n\nConverts string to lowercase.\n\nExample:\nlower l \"HELLO\"\nshow $l",
            "replace": "Usage: replace [var] [source] [old] [new]\n\nReplaces text in a string.\n\nExample:\nreplace s \"Hello World\" \"World\" \"Python\"",
            "split": "Usage: split [var] [source] [delimiter]\n\nSplits a string into an array.\n\nExample:\nsplit words \"a,b,c\" \",\"",
            "join": "Usage: join [var] [str1] [str2]\n\nJoins two strings together.\n\nExample:\njoin res \"Hi \" \"There\"",
            "trim": "Usage: trim [var] [string]\n\nRemoves whitespace from start and end.\n\nExample:\ntrim t \"  hello  \"",
            "type": "Usage: type [var] [value]\n\nGets the type of a value.\n\nExample:\ntype t 123",
            "mkdir": "Usage: mkdir \"[folder]\"\n\nCreates a new directory.\n\nExample:\nmkdir \"data\"",
            "rmdir": "Usage: rmdir \"[folder]\"\n\nRemoves a directory.\n\nExample:\nrmdir \"temp\"",
            "copy": "Usage: copy \"[src]\" \"[dst]\"\n\nCopies a file.\n\nExample:\ncopy \"a.txt\" \"b.txt\"",
            "move": "Usage: move \"[src]\" \"[dst]\"\n\nMoves a file.\n\nExample:\nmove \"old.txt\" \"new.txt\"",
            "exists": "Usage: exists [var] \"[path]\"\n\nChecks if a file exists (1 or 0).\n\nExample:\nexists e \"file.txt\"",
            "delete": "Usage: delete \"[file]\"\n\nDeletes a file.\n\nExample:\ndelete \"temp.txt\"",
            "icon": "Usage: icon [win_var] \"[path]\"\n\nSets the window icon (.ico).\n\nExample:\nicon w \"app.ico\"",
            "opacity": "Usage: opacity [win_var] [0.0-1.0]\n\nSets window transparency.\n\nExample:\nopacity w 0.8",
            "fullscreen": "Usage: fullscreen [win_var] [1/0]\n\nToggles fullscreen mode.\n\nExample:\nfullscreen w 1",
            "speak": "Usage: speak \"[text]\"\n\nUses text-to-speech (simulated in console).\n\nExample:\nspeak \"Hello user\"",
            "notify": "Usage: notify \"[Title]\" \"[Message]\"\n\nShows a system notification popup.\n\nExample:\nnotify \"Alert\" \"Done!\"",
            "browser": "Usage: browser \"[url]\"\n\nOpens a URL in the default web browser.\n\nExample:\nbrowser \"https://google.com\"",
            "clipset": "Usage: clipset \"[text]\"\n\nSets the clipboard content.\n\nExample:\nclipset \"Copied text\"",
            "clipget": "Usage: clipget [var]\n\nGets the clipboard content.\n\nExample:\nclipget c\nshow $c",
            "screen": "Usage: screen [w_var] [h_var]\n\nGets screen dimensions.\n\nExample:\nscreen w h",
            "mouse": "Usage: mouse [x_var] [y_var]\n\nGets current mouse position.\n\nExample:\nmouse x y",
            "username": "Usage: username [var]\n\nGets current system username.\n\nExample:\nusername u",
            "platform": "Usage: platform [var]\n\nGets OS name.\n\nExample:\nplatform p",
            "env": "Usage: env [var] \"[KEY]\"\n\nGets environment variable.\n\nExample:\nenv path \"PATH\"",
            "exec": "Usage: exec \"[command]\"\n\nExecutes a system command.\n\nExample:\nexec \"dir\"",
            "starts": "Usage: starts [var] [str] [prefix]\n\nChecks if string starts with prefix.\n\nExample:\nstarts b \"Hello\" \"He\"",
            "ends": "Usage: ends [var] [str] [suffix]\n\nChecks if string ends with suffix.\n\nExample:\nends b \"Hello\" \"lo\"",
            "contains": "Usage: contains [var] [haystack] [needle]\n\nChecks if string contains substring.\n\nExample:\ncontains b \"Hello\" \"el\"",
            "index": "Usage: index [var] [haystack] [needle]\n\nFinds index of substring.\n\nExample:\nindex i \"Hello\" \"e\"",
            "pi": "Usage: pi [var]\n\nSets variable to Pi.\n\nExample:\npi p",
            "e": "Usage: e [var]\n\nSets variable to Euler's number.\n\nExample:\ne v",
            "rgb": "Usage: rgb [var] [r] [g] [b]\n\nCreates a hex color string.\n\nExample:\nrgb c 255 0 0\ncolor w $c",
            "array": "Usage: array [name] [items...]\n\nCreates an array.\n\nExample:\narray list 1 2 3",
            "inc": "Usage: inc [var]\n\nIncrements a variable by 1.\n\nExample:\ninc x",
            "dec": "Usage: dec [var]\n\nDecrements a variable by 1.\n\nExample:\ndec x",
            "pow": "Usage: pow [var] [base] [exp]\n\nCalculates power.\n\nExample:\npow r 2 3",
            "mod": "Usage: mod [var] [a] [b]\n\nCalculates modulus.\n\nExample:\nmod r 10 3",
            "abs": "Usage: abs [var] [val]\n\nCalculates absolute value.\n\nExample:\nabs a -5",
            "floor": "Usage: floor [var] [val]\n\nRounds down.\n\nExample:\nfloor f 5.9",
            "round": "Usage: round [var] [val]\n\nRounds to nearest integer.\n\nExample:\nround r 5.5",
            "min": "Usage: min [var] [a] [b]\n\nGets minimum of two numbers.\n\nExample:\nmin m 10 20",
            "max": "Usage: max [var] [a] [b]\n\nGets maximum of two numbers.\n\nExample:\nmax m 10 20",
            "date": "Usage: date [var]\n\nGets current date (YYYY-MM-DD).\n\nExample:\ndate d",
            "filetime": "Usage: filetime [var] \"[path]\"\n\nGets file modification time.\n\nExample:\nfiletime t \"file.txt\"",
            "isdir": "Usage: isdir [var] \"[path]\"\n\nChecks if path is a directory.\n\nExample:\nisdir d \"folder\"",
            "isfile": "Usage: isfile [var] \"[path]\"\n\nChecks if path is a file.\n\nExample:\nisfile f \"file.txt\"",
            "minimize": "Usage: minimize [win_var]\n\nMinimizes a window.\n\nExample:\nminimize w",
            "restore": "Usage: restore [win_var]\n\nRestores a minimized window.\n\nExample:\nrestore w",
            "focus": "Usage: focus [win_var]\n\nBrings window to front.\n\nExample:\nfocus w",
            "topmost": "Usage: topmost [win_var] [1/0]\n\nSets window always on top.\n\nExample:\ntopmost w 1",
            "center": "Usage: center [win_var]\n\nCenters window on screen.\n\nExample:\ncenter w",
            "getpos": "Usage: getpos [win_var] [x_var] [y_var]\n\nGets window position.\n\nExample:\ngetpos w x y",
            "resizable": "Usage: resizable [win_var] [w_bool] [h_bool]\n\nSets window resizability.\n\nExample:\nresizable w 0 0",
            "warp": "Usage: warp [x] [y]\n\nMoves mouse cursor to coordinates.\n\nExample:\nwarp 100 100",
            "hash": "Usage: hash [var] \"[text]\"\n\nCalculates hash of text.\n\nExample:\nhash h \"password\"",
            "func": "Usage: func [name]\n    ...\nend\n\nDefines a function.\n\nExample:\nfunc greet\n    show \"Hi\"\nend",
            "call": "Usage: call [name]\n\nCalls a function.\n\nExample:\ncall greet",
            "end": "Usage: end\n\nEnds a block (if, repeat, func).\n\nExample:\nif $x\n    ...\nend",
            "clear": "Usage: clear\n\nClears the output console.\n\nExample:\nclear",
            "reverse": "Usage: reverse [var] [string]\n\nReverses a string.\n\nExample:\nreverse r \"hello\"\nshow $r",
            "sort": "Usage: sort [var] [array/string]\n\nSorts an array or string.\n\nExample:\nsort s \"cba\"\nshow $s",
            "find": "Usage: find [var] [source] [target]\n\nFinds substring index.\n\nExample:\nfind i \"hello\" \"e\"",
            "sub": "Usage: sub [var] [source] [start] [end]\n\nExtracts a substring.\n\nExample:\nsub s \"hello\" 1 3\nshow $s",
            "cwd": "Usage: cwd [var]\n\nGets the current working directory.\n\nExample:\ncwd d\nshow $d",
            "list": "Usage: list [var] [path]\n\nLists files in a directory.\n\nExample:\nlist f \".\"\nshow $f",
            "getsize": "Usage: getsize [var] [path]\n\nGets file size in bytes.\n\nExample:\ngetsize s \"file.txt\"",
            "copyfile": "Usage: copyfile [src] [dst]\n\nCopies a file.\n\nExample:\ncopyfile \"a.txt\" \"b.txt\"",
            "sleep": "Usage: sleep [ms]\n\nPauses execution for milliseconds.\n\nExample:\nsleep 1000"
        }
        return docs.get(cmd, None)

    def highlight_syntax(self, event=None):
        for tag in ["keyword", "string", "comment", "variable", "ai_comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
        
        text = self.editor.get("1.0", tk.END)
        
        # Highlight Keywords
        keywords = ["if", "end", "func", "call", "show", "ask", "rand", "window", "title", "size", "text", "color", "close", "wait", "array", "repeat", "clear", "popup", "write", "read", "append", "math", "len", "time", "beep", "upper", "lower", "replace", "split", "round", "min", "max", "date", "exists", "delete", "reverse", "sort", "find", "sub", "mkdir", "rmdir", "trim", "join", "type", "pow", "mod", "inc", "dec", "copy", "move", "cwd", "list", "abs", "floor", "icon", "topmost", "center", "getsize", "copyfile", "sleep", "opacity", "resizable", "fullscreen", "getpos", "clipset", "clipget", "screen", "mouse", "username", "browser", "minimize", "restore", "focus", "filetime", "isdir", "isfile", "pi", "e", "rgb", "platform", "env", "exec", "hash", "warp", "starts", "ends", "contains", "index", "speak", "notify"]
        for kw in keywords:
            for match in re.finditer(rf"\b{kw}\b", text):
                self.editor.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        
        # Highlight Variables ($var)
        for match in re.finditer(r"\$\w+", text):
            self.editor.tag_add("variable", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            
        # Highlight Strings
        for match in re.finditer(r'"[^"]*"', text):
            self.editor.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            
        # Highlight Comments
        for match in re.finditer(r"#.*", text):
            tag = "comment"
            if match.group(0).startswith("# AI:"):
                tag = "ai_comment"
            self.editor.tag_add(tag, f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            
        self.update_line_numbers()
        self.update_minimap()

    def transpile_to_python(self, code):
        lines = code.splitlines()
        py_lines = ["import random", "import time", "import math", "import os", "import shutil", "import platform", "import tkinter as tk", "from tkinter import simpledialog", "", "# Generated Python Code", "root = tk.Tk()", "root.withdraw()", ""]
        indent = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                py_lines.append("    " * indent + line)
                continue
            
            # Replace variable access $var with var
            line = line.replace("$", "")
            
            if "=" in line and not line.startswith("if"):
                py_lines.append("    " * indent + line)
            
            elif line.startswith("show "):
                py_lines.append("    " * indent + f"print({line[5:].strip()})")
            
            elif line.startswith("if "):
                py_lines.append("    " * indent + f"{line}:")
                indent += 1
            
            elif line == "end":
                indent = max(0, indent - 1)
            
            elif line.startswith("repeat "):
                count = line[7:].strip()
                py_lines.append("    " * indent + f"for _ in range({count}):")
                indent += 1
            
            elif line.startswith("func "):
                name = line[5:].strip()
                py_lines.append("    " * indent + f"def {name}():")
                indent += 1
            
            elif line.startswith("call "):
                py_lines.append("    " * indent + f"{line[5:].strip()}()")
            
            elif line.startswith("ask "):
                match = re.match(r'ask\s+"(.+?)"\s+(\w+)', line)
                if match:
                    prompt, var = match.groups()
                    py_lines.append("    " * indent + f"{var} = simpledialog.askstring('Input', '{prompt}')")
            
            elif line.startswith("rand "):
                parts = line.split()
                if len(parts) == 4:
                    py_lines.append("    " * indent + f"{parts[3]} = random.randint({parts[1]}, {parts[2]})")
            
            elif line.startswith("wait "):
                py_lines.append("    " * indent + f"time.sleep({line[5:].strip()})")
                
            elif line.startswith("window "):
                py_lines.append("    " * indent + f"{line[7:].strip()} = tk.Toplevel()")
                
            elif line.startswith("title "):
                match = re.match(r'title\s+(\w+)\s+(.+)', line)
                if match:
                    var, title = match.groups()
                    py_lines.append("    " * indent + f"{var}.title({title})")
                    
            elif line.startswith("size "):
                parts = line.split()
                if len(parts) >= 4:
                    py_lines.append("    " * indent + f"{parts[1]}.geometry(f'{{ {parts[2]} }}x{{ {parts[3]} }}')")
            
            elif line.startswith("text "):
                match = re.search(r'text\s+(\w+)\s+(.+)\s+(\S+)\s+(\S+)$', line)
                if match:
                    var, content, x, y = match.groups()
                    py_lines.append("    " * indent + f"tk.Label({var}, text={content}).place(x={x}, y={y})")
            
            elif line.startswith("color "):
                match = re.match(r'color\s+(\w+)\s+(.+)', line)
                if match:
                    var, content = match.groups()
                    py_lines.append("    " * indent + f"{var}.configure(bg={content})")

            elif line.startswith("popup "):
                py_lines.append("    " * indent + f"messagebox.showinfo('Popup', {line[6:].strip()})")

            elif line.startswith("write "):
                match = re.match(r'write\s+(.+?)\s+(.+)', line)
                if match:
                    f, c = match.groups()
                    py_lines.append("    " * indent + f"with open({f}, 'w') as f: f.write(str({c}))")

            elif line.startswith("read "):
                match = re.match(r'read\s+(\w+)\s+(.+)', line)
                if match:
                    var, f = match.groups()
                    py_lines.append("    " * indent + f"with open({f}, 'r') as f: {var} = f.read()")

            elif line.startswith("append "):
                match = re.match(r'append\s+(.+?)\s+(.+)', line)
                if match:
                    f, c = match.groups()
                    py_lines.append("    " * indent + f"with open({f}, 'a') as f: f.write(str({c}))")

            elif line.startswith("math "):
                parts = line.split()
                if len(parts) >= 4:
                    py_lines.append("    " * indent + f"{parts[1]} = math.{parts[2]}({parts[3]})")

            elif line.startswith("len "):
                parts = line.split()
                if len(parts) >= 3:
                    py_lines.append("    " * indent + f"{parts[1]} = len({parts[2]})")

            elif line.startswith("time "):
                var = line[5:].strip()
                py_lines.append("    " * indent + f"{var} = time.strftime('%H:%M:%S')")

            elif line.startswith("upper "):
                parts = line.split()
                if len(parts) >= 3:
                    py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).upper()")

            elif line.startswith("lower "):
                parts = line.split()
                if len(parts) >= 3:
                    py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).lower()")

            elif line.startswith("replace "):
                parts = line.split()
                if len(parts) >= 5:
                    py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).replace(str({parts[3]}), str({parts[4]}))")

            elif line.startswith("split "):
                parts = line.split()
                if len(parts) >= 4:
                    py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).split(str({parts[3]}))")

            elif line.startswith("round "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = round(float({parts[2]}))")

            elif line.startswith("min "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = min({parts[2]}, {parts[3]})")

            elif line.startswith("max "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = max({parts[2]}, {parts[3]})")

            elif line.startswith("date "):
                var = line[5:].strip()
                py_lines.append("    " * indent + f"{var} = time.strftime('%Y-%m-%d')")

            elif line.startswith("exists "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = 1 if os.path.exists({parts[2]}) else 0")

            elif line.startswith("delete "):
                py_lines.append("    " * indent + f"if os.path.exists({line[7:].strip()}): os.remove({line[7:].strip()})")

            elif line.startswith("reverse "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = {parts[2]}[::-1]")

            elif line.startswith("sort "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = sorted({parts[2]})")

            elif line.startswith("find "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).find(str({parts[3]}))")

            elif line.startswith("sub "):
                parts = line.split()
                if len(parts) >= 5: py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]})[{parts[3]}:{parts[4]}]")

            elif line.startswith("mkdir "):
                py_lines.append("    " * indent + f"os.makedirs({line[6:].strip()}, exist_ok=True)")

            elif line.startswith("rmdir "):
                py_lines.append("    " * indent + f"os.rmdir({line[6:].strip()})")

            elif line.startswith("trim "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).strip()")

            elif line.startswith("join "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}) + str({parts[3]})")

            elif line.startswith("type "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = type({parts[2]}).__name__")

            elif line.startswith("pow "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = math.pow({parts[2]}, {parts[3]})")

            elif line.startswith("mod "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = {parts[2]} % {parts[3]}")

            elif line.startswith("inc "):
                py_lines.append("    " * indent + f"{line[4:].strip()} += 1")

            elif line.startswith("dec "):
                py_lines.append("    " * indent + f"{line[4:].strip()} -= 1")

            elif line.startswith("copy "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"shutil.copy({parts[1]}, {parts[2]})")

            elif line.startswith("move "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"shutil.move({parts[1]}, {parts[2]})")

            elif line.startswith("cwd "):
                py_lines.append("    " * indent + f"{line[4:].strip()} = os.getcwd()")

            elif line.startswith("list "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = os.listdir({parts[2]})")

            elif line.startswith("abs "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = abs({parts[2]})")

            elif line.startswith("floor "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = math.floor({parts[2]})")

            elif line.startswith("icon "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"try: {parts[1]}.iconbitmap({parts[2]}) \nexcept: pass")

            elif line.startswith("topmost "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]}.attributes('-topmost', {parts[2]})")

            elif line.startswith("center "):
                py_lines.append("    " * indent + f"# Centering not directly supported in transpiled Python")

            elif line.startswith("getsize "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = os.path.getsize({parts[2]})")

            elif line.startswith("sleep "):
                py_lines.append("    " * indent + f"time.sleep(float({line[6:].strip()}) / 1000)")

            elif line.startswith("opacity "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]}.attributes('-alpha', {parts[2]})")
            elif line.startswith("resizable "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]}.resizable({parts[2]}, {parts[3]})")
            elif line.startswith("fullscreen "):
                parts = line.split()
                if len(parts) >= 3:
                    py_lines.append("    " * indent + f"if int({parts[2]}):")
                    py_lines.append("    " * (indent + 1) + f"try: {parts[1]}.state('zoomed')")
                    py_lines.append("    " * (indent + 1) + f"except: {parts[1]}.attributes('-fullscreen', True)")
                    py_lines.append("    " * indent + "else:")
                    py_lines.append("    " * (indent + 1) + f"{parts[1]}.state('normal'); {parts[1]}.attributes('-fullscreen', False)")
            elif line.startswith("getpos "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append(f"    " * indent + f"{parts[2]} = {parts[1]}.winfo_x()\n" + "    " * indent + f"{parts[3]} = {parts[1]}.winfo_y()")

            elif line.startswith("browser "):
                py_lines.append("    " * indent + f"webbrowser.open({line[8:].strip()})")

            elif line.startswith("minimize "):
                py_lines.append("    " * indent + f"{line[9:].strip()}.iconify()")

            elif line.startswith("restore "):
                py_lines.append("    " * indent + f"{line[8:].strip()}.deiconify()")

            elif line.startswith("focus "):
                py_lines.append("    " * indent + f"{line[6:].strip()}.lift()")

            elif line.startswith("filetime "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = os.path.getmtime({parts[2]})")

            elif line.startswith("isdir "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = 1 if os.path.isdir({parts[2]}) else 0")

            elif line.startswith("isfile "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = 1 if os.path.isfile({parts[2]}) else 0")

            elif line.startswith("pi "):
                py_lines.append("    " * indent + f"{line[3:].strip()} = math.pi")

            elif line.startswith("e "):
                py_lines.append("    " * indent + f"{line[2:].strip()} = math.e")

            elif line.startswith("rgb "):
                parts = line.split()
                if len(parts) >= 5: py_lines.append("    " * indent + f"{parts[1]} = f'#{{int({parts[2]}):02x}}{{int({parts[3]}):02x}}{{int({parts[4]}):02x}}'")

            elif line.startswith("platform "):
                py_lines.append("    " * indent + f"{line[9:].strip()} = platform.system()")

            elif line.startswith("env "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = os.environ.get({parts[2]}, '')")

            elif line.startswith("exec "):
                py_lines.append("    " * indent + f"os.system({line[5:].strip()})")

            elif line.startswith("hash "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = abs(hash({parts[2]}))")

            elif line.startswith("warp "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"root.warp_pointer({parts[1]}, {parts[2]})")

            elif line.startswith("starts "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = 1 if str({parts[2]}).startswith(str({parts[3]})) else 0")

            elif line.startswith("ends "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = 1 if str({parts[2]}).endswith(str({parts[3]})) else 0")

            elif line.startswith("contains "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = 1 if str({parts[3]}) in str({parts[2]}) else 0")

            elif line.startswith("index "):
                parts = line.split()
                if len(parts) >= 4: py_lines.append("    " * indent + f"{parts[1]} = str({parts[2]}).find(str({parts[3]}))")

            elif line.startswith("speak "):
                py_lines.append("    " * indent + f"print('SPEAK:', {line[6:].strip()})")

            elif line.startswith("notify "):
                match = re.match(r'notify\s+(".*?"|\S+)\s+(.+)', line)
                if match:
                    py_lines.append("    " * indent + f"messagebox.showinfo({match.group(1)}, {match.group(2)})")

            elif line.startswith("clipset "):
                py_lines.append("    " * indent + f"root.clipboard_clear(); root.clipboard_append(str({line[8:].strip()})); root.update()")

            elif line.startswith("clipget "):
                var = line[8:].strip()
                py_lines.append("    " * indent + f"try: {var} = root.clipboard_get()\n" + "    " * indent + f"except: {var} = \"\"")

            elif line.startswith("screen "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = root.winfo_screenwidth()\n" + "    " * indent + f"{parts[2]} = root.winfo_screenheight()")

            elif line.startswith("mouse "):
                parts = line.split()
                if len(parts) >= 3: py_lines.append("    " * indent + f"{parts[1]} = root.winfo_pointerx()\n" + "    " * indent + f"{parts[2]} = root.winfo_pointery()")

            elif line.startswith("username "):
                py_lines.append("    " * indent + f"{line[9:].strip()} = os.getlogin()")



            elif line == "beep":
                py_lines.append("    " * indent + "root.bell()")

            elif line.startswith("close "):
                var = line[6:].strip()
                py_lines.append("    " * indent + f"{var}.destroy()")

            elif line.startswith("array "):
                parts = line.split()
                if len(parts) >= 2:
                    items = ", ".join(parts[2:])
                    py_lines.append("    " * indent + f"{parts[1]} = [{items}]")
            
            elif line == "clear":
                py_lines.append("    " * indent + "print('\\n' * 50)")

        return "\n".join(py_lines)

    def transpile_to_lua(self, code):
        lines = code.splitlines()
        lua_lines = ["-- Generated Lua Code", "math.randomseed(os.time())", ""]
        indent = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                lua_lines.append("    " * indent + line.replace("#", "--"))
                continue
            
            # Replace variable access $var with var
            line = line.replace("$", "")
            
            if "=" in line and not line.startswith("if"):
                lua_lines.append("    " * indent + line)
            
            elif line.startswith("show "):
                lua_lines.append("    " * indent + f"print({line[5:].strip()})")
            
            elif line.startswith("if "):
                cond = line[3:].strip()
                cond = cond.replace("!=", "~=")
                lua_lines.append("    " * indent + f"if {cond} then")
                indent += 1
            
            elif line == "end":
                indent = max(0, indent - 1)
                lua_lines.append("    " * indent + "end")
            
            elif line.startswith("repeat "):
                count = line[7:].strip()
                lua_lines.append("    " * indent + f"for i = 1, {count} do")
                indent += 1
            
            elif line.startswith("func "):
                name = line[5:].strip()
                lua_lines.append("    " * indent + f"function {name}()")
                indent += 1
            
            elif line.startswith("call "):
                lua_lines.append("    " * indent + f"{line[5:].strip()}()")
            
            elif line.startswith("ask "):
                match = re.match(r'ask\s+"(.+?)"\s+(\w+)', line)
                if match:
                    prompt, var = match.groups()
                    lua_lines.append("    " * indent + f"print(\"{prompt}\")")
                    lua_lines.append("    " * indent + f"{var} = io.read()")
            
            elif line.startswith("rand "):
                parts = line.split()
                if len(parts) == 4:
                    lua_lines.append("    " * indent + f"{parts[3]} = math.random({parts[1]}, {parts[2]})")
            
            elif line.startswith("wait "):
                sec = line[5:].strip()
                lua_lines.append("    " * indent + f"-- wait {sec} (sleep not standard in Lua)")
            
            elif line.startswith("popup ") or line.startswith("write ") or line.startswith("window ") or line.startswith("title ") or line.startswith("size ") or line.startswith("text ") or line.startswith("color ") or line.startswith("close "):
                lua_lines.append("    " * indent + f"-- GUI command ignored: {line}")

            elif line.startswith("read "):
                match = re.match(r'read\s+(\w+)\s+(.+)', line)
                if match:
                    var, f = match.groups()
                    lua_lines.append("    " * indent + f"local f = io.open({f}, 'r'); {var} = f:read('*all'); f:close()")

            elif line.startswith("append "):
                match = re.match(r'append\s+(.+?)\s+(.+)', line)
                if match:
                    f, c = match.groups()
                    lua_lines.append("    " * indent + f"local f = io.open({f}, 'a'); f:write({c}); f:close()")

            elif line.startswith("math "):
                parts = line.split()
                if len(parts) >= 4:
                    lua_lines.append("    " * indent + f"{parts[1]} = math.{parts[2]}({parts[3]})")

            elif line.startswith("len "):
                parts = line.split()
                if len(parts) >= 3:
                    lua_lines.append("    " * indent + f"{parts[1]} = #{parts[2]}")

            elif line.startswith("time "):
                var = line[5:].strip()
                lua_lines.append("    " * indent + f"{var} = os.date('%H:%M:%S')")
            
            elif line.startswith("upper "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = string.upper({parts[2]})")

            elif line.startswith("lower "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = string.lower({parts[2]})")

            elif line.startswith("mkdir "):
                lua_lines.append("    " * indent + f"os.execute(\"mkdir \" .. {line[6:].strip()})")

            elif line.startswith("rmdir "):
                lua_lines.append("    " * indent + f"os.execute(\"rmdir \" .. {line[6:].strip()})")

            elif line.startswith("trim "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = {parts[2]}:match(\"^%s*(.-)%s*$\")")

            elif line.startswith("join "):
                parts = line.split()
                if len(parts) >= 4: lua_lines.append("    " * indent + f"{parts[1]} = tostring({parts[2]}) .. tostring({parts[3]})")

            elif line.startswith("type "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = type({parts[2]})")

            elif line.startswith("pow "):
                parts = line.split()
                if len(parts) >= 4: lua_lines.append("    " * indent + f"{parts[1]} = {parts[2]} ^ {parts[3]}")

            elif line.startswith("mod "):
                parts = line.split()
                if len(parts) >= 4: lua_lines.append("    " * indent + f"{parts[1]} = {parts[2]} % {parts[3]}")

            elif line.startswith("inc "):
                var = line[4:].strip()
                lua_lines.append("    " * indent + f"{var} = {var} + 1")

            elif line.startswith("dec "):
                var = line[4:].strip()
                lua_lines.append("    " * indent + f"{var} = {var} - 1")

            elif line.startswith("copy "):
                lua_lines.append("    " * indent + f"-- copy not supported natively in Lua")

            elif line.startswith("move "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"os.rename({parts[1]}, {parts[2]})")

            elif line.startswith("cwd "):
                lua_lines.append("    " * indent + f"-- cwd not supported natively in Lua")

            elif line.startswith("abs "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = math.abs({parts[2]})")

            elif line.startswith("floor "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"{parts[1]} = math.floor({parts[2]})")

            elif line.startswith("getsize "):
                parts = line.split()
                if len(parts) >= 3: lua_lines.append("    " * indent + f"local f = io.open({parts[2]}, 'r'); if f then {parts[1]} = f:seek('end'); f:close(); end")

            elif line.startswith("sleep "):
                lua_lines.append("    " * indent + f"-- sleep not standard in Lua")

            elif line.startswith("icon ") or line.startswith("topmost ") or line.startswith("center ") or line.startswith("opacity ") or line.startswith("resizable ") or line.startswith("fullscreen ") or line.startswith("getpos ") or line.startswith("minimize ") or line.startswith("restore ") or line.startswith("focus "):
                lua_lines.append("    " * indent + f"-- GUI command ignored: {line}")

            elif line.startswith("clipset ") or line.startswith("clipget ") or line.startswith("screen ") or line.startswith("mouse ") or line.startswith("username ") or line.startswith("browser ") or line.startswith("filetime ") or line.startswith("isdir ") or line.startswith("isfile ") or line.startswith("rgb ") or line.startswith("platform ") or line.startswith("env ") or line.startswith("exec ") or line.startswith("hash ") or line.startswith("warp ") or line.startswith("starts ") or line.startswith("ends ") or line.startswith("contains ") or line.startswith("index ") or line.startswith("speak ") or line.startswith("notify "):
                lua_lines.append("    " * indent + f"-- System command ignored in Lua: {line}")

            elif line == "beep":
                lua_lines.append("    " * indent + "print('\\7')")

            elif line.startswith("array "):
                parts = line.split()
                if len(parts) >= 2:
                    items = ", ".join(parts[2:])
                    lua_lines.append("    " * indent + f"{parts[1]} = {{{items}}}")
            
            elif line == "clear":
                lua_lines.append("    " * indent + "for i=1,50 do print(\"\") end")

        return "\n".join(lua_lines)

    def transpile_to_js(self, code):
        lines = code.splitlines()
        js_lines = ["// Generated JavaScript Code", ""]
        indent = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                js_lines.append("    " * indent + line.replace("#", "//"))
                continue
            
            line = line.replace("$", "")
            
            if "=" in line and not line.startswith("if"):
                js_lines.append("    " * indent + "let " + line + ";")
            
            elif line.startswith("show "):
                js_lines.append("    " * indent + f"console.log({line[5:].strip()});")
            
            elif line.startswith("if "):
                cond = line[3:].strip()
                js_lines.append("    " * indent + f"if ({cond}) {{")
                indent += 1
            
            elif line == "end":
                indent = max(0, indent - 1)
                js_lines.append("    " * indent + "}")
            
            elif line.startswith("repeat "):
                count = line[7:].strip()
                js_lines.append("    " * indent + f"for (let i = 0; i < {count}; i++) {{")
                indent += 1
            
            elif line.startswith("func "):
                name = line[5:].strip()
                js_lines.append("    " * indent + f"function {name}() {{")
                indent += 1
            
            elif line.startswith("call "):
                js_lines.append("    " * indent + f"{line[5:].strip()}();")
            
            elif line.startswith("ask "):
                match = re.match(r'ask\s+"(.+?)"\s+(\w+)', line)
                if match:
                    prompt, var = match.groups()
                    js_lines.append("    " * indent + f"let {var} = prompt(\"{prompt}\");")
            
            elif line.startswith("rand "):
                parts = line.split()
                if len(parts) == 4:
                    min_v, max_v, var = parts[1], parts[2], parts[3]
                    js_lines.append("    " * indent + f"let {var} = Math.floor(Math.random() * ({max_v} - {min_v} + 1)) + {min_v};")
            
            elif line.startswith("upper "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = String({parts[2]}).toUpperCase();")

            elif line.startswith("lower "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = String({parts[2]}).toLowerCase();")

            elif line.startswith("mkdir "):
                js_lines.append("    " * indent + f"// Node: fs.mkdirSync({line[6:].strip()});")

            elif line.startswith("rmdir "):
                js_lines.append("    " * indent + f"// Node: fs.rmdirSync({line[6:].strip()});")

            elif line.startswith("trim "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = String({parts[2]}).trim();")

            elif line.startswith("join "):
                parts = line.split()
                if len(parts) >= 4: js_lines.append("    " * indent + f"let {parts[1]} = String({parts[2]}) + String({parts[3]});")

            elif line.startswith("type "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = typeof {parts[2]};")

            elif line.startswith("pow "):
                parts = line.split()
                if len(parts) >= 4: js_lines.append("    " * indent + f"let {parts[1]} = Math.pow({parts[2]}, {parts[3]});")

            elif line.startswith("mod "):
                parts = line.split()
                if len(parts) >= 4: js_lines.append("    " * indent + f"let {parts[1]} = {parts[2]} % {parts[3]};")

            elif line.startswith("inc "):
                js_lines.append("    " * indent + f"{line[4:].strip()}++;")

            elif line.startswith("dec "):
                js_lines.append("    " * indent + f"{line[4:].strip()}--;")

            elif line.startswith("copy "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"// Node: fs.copyFileSync({parts[1]}, {parts[2]});")

            elif line.startswith("move "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"// Node: fs.renameSync({parts[1]}, {parts[2]});")

            elif line.startswith("cwd "):
                js_lines.append("    " * indent + f"let {line[4:].strip()} = process.cwd();")

            elif line.startswith("abs "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = Math.abs({parts[2]});")

            elif line.startswith("floor "):
                parts = line.split()
                if len(parts) >= 3: js_lines.append("    " * indent + f"let {parts[1]} = Math.floor({parts[2]});")

            elif line.startswith("getsize "):
                js_lines.append("    " * indent + f"// Node: let {parts[1]} = fs.statSync({parts[2]}).size;")

            elif line.startswith("sleep "):
                js_lines.append("    " * indent + f"// sleep not standard in browser JS")

            elif line.startswith("icon ") or line.startswith("topmost ") or line.startswith("center ") or line.startswith("opacity ") or line.startswith("resizable ") or line.startswith("fullscreen ") or line.startswith("getpos ") or line.startswith("minimize ") or line.startswith("restore ") or line.startswith("focus "):
                js_lines.append("    " * indent + f"// GUI command ignored: {line}")

            elif line.startswith("clipset ") or line.startswith("clipget ") or line.startswith("screen ") or line.startswith("mouse ") or line.startswith("username ") or line.startswith("browser ") or line.startswith("filetime ") or line.startswith("isdir ") or line.startswith("isfile ") or line.startswith("rgb ") or line.startswith("platform ") or line.startswith("env ") or line.startswith("exec ") or line.startswith("hash ") or line.startswith("warp ") or line.startswith("starts ") or line.startswith("ends ") or line.startswith("contains ") or line.startswith("index ") or line.startswith("speak ") or line.startswith("notify "):
                js_lines.append("    " * indent + f"// System command ignored in JS: {line}")


        return "\n".join(js_lines)

    def transpile_to_csharp(self, code):
        lines = code.splitlines()
        cs_lines = ["// Generated C# Code", "using System;", "using System.IO;", "using System.Collections.Generic;", "using System.Threading;", "", "class Program {", "    static void Main() {", "        Random random = new Random();"]
        indent = 2
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                cs_lines.append("    " * indent + line.replace("#", "//"))
                continue
            
            line = line.replace("$", "")
            
            if "=" in line and not line.startswith("if"):
                cs_lines.append("    " * indent + "var " + line + ";")
            
            elif line.startswith("show "):
                cs_lines.append("    " * indent + f"Console.WriteLine({line[5:].strip()});")
            
            elif line.startswith("if "):
                cond = line[3:].strip()
                cs_lines.append("    " * indent + f"if ({cond}) {{")
                indent += 1
            
            elif line == "end":
                indent = max(2, indent - 1)
                cs_lines.append("    " * indent + "}")
            
            elif line.startswith("repeat "):
                count = line[7:].strip()
                cs_lines.append("    " * indent + f"for (int i = 0; i < {count}; i++) {{")
                indent += 1
            
            elif line.startswith("func "):
                name = line[5:].strip()
                cs_lines.append("    " * indent + f"void {name}() {{")
                indent += 1
            
            elif line.startswith("call "):
                cs_lines.append("    " * indent + f"{line[5:].strip()}();")
            
            elif line.startswith("ask "):
                match = re.match(r'ask\s+"(.+?)"\s+(\w+)', line)
                if match:
                    prompt, var = match.groups()
                    cs_lines.append("    " * indent + f"Console.WriteLine(\"{prompt}\");")
                    cs_lines.append("    " * indent + f"var {var} = Console.ReadLine();")
            
            elif line.startswith("rand "):
                parts = line.split()
                if len(parts) == 4:
                    min_v, max_v, var = parts[1], parts[2], parts[3]
                    cs_lines.append("    " * indent + f"var {var} = random.Next({min_v}, {max_v} + 1);")
            
            elif line.startswith("wait "):
                sec = line[5:].strip()
                cs_lines.append("    " * indent + f"Thread.Sleep((int)({sec} * 1000));")

            elif line.startswith("mkdir "):
                cs_lines.append("    " * indent + f"Directory.CreateDirectory({line[6:].strip()});")

            elif line.startswith("rmdir "):
                cs_lines.append("    " * indent + f"Directory.Delete({line[6:].strip()});")

            elif line.startswith("trim "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"var {parts[1]} = {parts[2]}.ToString().Trim();")

            elif line.startswith("join "):
                parts = line.split()
                if len(parts) >= 4: cs_lines.append("    " * indent + f"var {parts[1]} = {parts[2]}.ToString() + {parts[3]}.ToString();")

            elif line.startswith("type "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"var {parts[1]} = {parts[2]}.GetType().Name;")

            elif line.startswith("pow "):
                parts = line.split()
                if len(parts) >= 4: cs_lines.append("    " * indent + f"var {parts[1]} = Math.Pow({parts[2]}, {parts[3]});")

            elif line.startswith("mod "):
                parts = line.split()
                if len(parts) >= 4: cs_lines.append("    " * indent + f"var {parts[1]} = {parts[2]} % {parts[3]};")

            elif line.startswith("inc "):
                cs_lines.append("    " * indent + f"{line[4:].strip()}++;")

            elif line.startswith("dec "):
                cs_lines.append("    " * indent + f"{line[4:].strip()}--;")

            elif line.startswith("copy "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"File.Copy({parts[1]}, {parts[2]});")

            elif line.startswith("move "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"File.Move({parts[1]}, {parts[2]});")

            elif line.startswith("cwd "):
                cs_lines.append("    " * indent + f"var {line[4:].strip()} = Directory.GetCurrentDirectory();")

            elif line.startswith("abs "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"var {parts[1]} = Math.Abs({parts[2]});")

            elif line.startswith("floor "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"var {parts[1]} = Math.Floor({parts[2]});")

            elif line.startswith("getsize "):
                parts = line.split()
                if len(parts) >= 3: cs_lines.append("    " * indent + f"var {parts[1]} = new FileInfo({parts[2]}).Length;")

            elif line.startswith("sleep "):
                cs_lines.append("    " * indent + f"Thread.Sleep((int)({line[6:].strip()}));")

            elif line.startswith("icon ") or line.startswith("topmost ") or line.startswith("center ") or line.startswith("opacity ") or line.startswith("resizable ") or line.startswith("fullscreen ") or line.startswith("getpos ") or line.startswith("minimize ") or line.startswith("restore ") or line.startswith("focus "):
                cs_lines.append("    " * indent + f"// GUI command ignored: {line}")

            elif line.startswith("clipset ") or line.startswith("clipget ") or line.startswith("screen ") or line.startswith("mouse ") or line.startswith("username ") or line.startswith("browser ") or line.startswith("filetime ") or line.startswith("isdir ") or line.startswith("isfile ") or line.startswith("rgb ") or line.startswith("platform ") or line.startswith("env ") or line.startswith("exec ") or line.startswith("hash ") or line.startswith("warp ") or line.startswith("starts ") or line.startswith("ends ") or line.startswith("contains ") or line.startswith("index ") or line.startswith("speak ") or line.startswith("notify "):
                cs_lines.append("    " * indent + f"// System command ignored in C#: {line}")



        cs_lines.append("    }")
        cs_lines.append("}")
        return "\n".join(cs_lines)

    def show_ai_builder(self):
        c = self.get_theme_colors(self.settings["theme"])
        ai_win = tk.Toplevel(self.root)
        ai_win.title("AI Code Builder")
        ai_win.geometry("600x500")
        ai_win.configure(bg=c["bg"])

        tk.Label(ai_win, text="Tell the AI what to build:", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 10)).pack(pady=10)
        tk.Label(ai_win, text="Warning: AI generated code may be inaccurate.", bg=c["bg"], fg="red", font=("Segoe UI", 8)).pack(pady=(0, 5))
        prompt_entry = tk.Entry(ai_win, width=40, font=("Segoe UI", 10), bg=c["edit_bg"], fg=c["edit_fg"], insertbackground=c["fg"])
        prompt_entry.pack(pady=5)
        prompt_entry.focus_set()
        
        teach_var = tk.BooleanVar()
        tk.Checkbutton(ai_win, text="🎓 Teach Mode", variable=teach_var, bg=c["bg"], fg=c["fg"], selectcolor=c["bg"], activebackground=c["bg"], activeforeground=c["fg"]).pack(pady=2)
        
        tk.Label(ai_win, text="History:", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 8)).pack(pady=(5, 0))
        history_cb = ttk.Combobox(ai_win, values=self.ai_history, state="readonly", width=37)
        history_cb.pack(pady=2)
        
        tk.Label(ai_win, text="Model:", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 8)).pack(pady=(5, 0))
        model_var = tk.StringVar(value=self.settings.get("default_ai_model", "Intelligent"))
        model_cb = ttk.Combobox(ai_win, textvariable=model_var, values=["Casual", "Intelligent", "Advanced Mode"], state="readonly", width=37)
        model_cb.pack(pady=2)
        
        def use_history(event):
            prompt_entry.delete(0, tk.END)
            prompt_entry.insert(0, history_cb.get())
        history_cb.bind("<<ComboboxSelected>>", use_history)

        status_label = tk.Label(ai_win, text="AI is ready.", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 9, "italic"))
        status_label.pack(pady=5)

        def start_thinking(delay, prompt, model, btn, callback):
            step = max(600, delay // 4)
            total_delay = step * 4
            chats = ["Hmm, let me think...", "Analyzing your request...", "Writing the logic...", "Optimizing code...", "Almost done...", "Here you go!", "Checking for errors...", "Structuring data...", "Applying best practices...", "Finalizing script...", "Reviewing logic..."]
            btn.config(text="AI Working...")
            self.root.after(step, lambda: status_label.config(text=random.choice(chats)))
            self.root.after(step * 2, lambda: status_label.config(text=random.choice(chats)))
            self.root.after(step * 3, lambda: status_label.config(text=random.choice(chats)))
            self.root.after(total_delay, lambda: callback(prompt, model))

        def generate():
            prompt = prompt_entry.get()
            model = model_var.get()

            if time.time() < self.ai_recharge_time.get(model, 0):
                rem = int(self.ai_recharge_time[model] - time.time())
                messagebox.showwarning("Recharging", f"{model} AI is recharging. Wait {rem}s.")
                return
            
            if prompt and (not self.ai_history or self.ai_history[0] != prompt):
                self.ai_history.insert(0, prompt)
                history_cb['values'] = self.ai_history
            
            self.ai_usage[model] += 1
            
            limit = 10 if model == "Casual" else (5 if model == "Intelligent" else 3)
            recharge = 20 if model == "Casual" else (60 if model == "Intelligent" else 120)

            if self.ai_usage[model] >= limit:
                self.ai_recharge_time[model] = time.time() + recharge
                self.ai_usage[model] = 0
                messagebox.showinfo("AI Limit", f"{model} Limit reached ({limit}/{limit}). Recharging for {recharge}s.")

            delay = len(prompt) * 30
            if model == "Advanced Mode":
                delay = len(prompt) * 250 + 2000 # Extra thinking time for Advanced Mode

            btn_build.config(state="disabled")
            start_thinking(delay, prompt, model, btn_build, lambda p, m: finalize(p, m, teach_var.get()))

        def finalize(prompt, model, teach):
            code = self.ai_generate(prompt, model, teach)
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", code)
            self.highlight_syntax()
            ai_win.destroy()

        btn_build = tk.Button(ai_win, text="Build Code", command=generate, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", padx=10, pady=5)
        btn_build.pack(pady=15)

        def convert_to_python():
            try:
                code = self.editor.get("1.0", tk.END)
                py_code = self.transpile_to_python(code)
                try:
                    compile(py_code, "<string>", "exec")
                except Exception as e:
                    raise Exception(f"Validation failed: {e}")
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", py_code)
                ai_win.destroy()
                messagebox.showinfo("Converter", "Code converted to Python!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def convert_to_lua():
            try:
                code = self.editor.get("1.0", tk.END)
                lua_code = self.transpile_to_lua(code)
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", lua_code)
                ai_win.destroy()
                messagebox.showinfo("Converter", "Code converted to Lua!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def convert_to_js():
            try:
                code = self.editor.get("1.0", tk.END)
                js_code = self.transpile_to_js(code)
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", js_code)
                ai_win.destroy()
                messagebox.showinfo("Converter", "Code converted to JavaScript!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def convert_to_csharp():
            try:
                code = self.editor.get("1.0", tk.END)
                cs_code = self.transpile_to_csharp(code)
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", cs_code)
                ai_win.destroy()
                messagebox.showinfo("Converter", "Code converted to C#!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        conv_frame = tk.Frame(ai_win, bg=c["bg"])
        conv_frame.pack(side=tk.TOP, pady=(0, 10))

        tk.Button(conv_frame, text="Convert to Python", command=convert_to_python, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(conv_frame, text="Convert to Lua", command=convert_to_lua, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(conv_frame, text="Convert to JS", command=convert_to_js, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(conv_frame, text="Convert to C#", command=convert_to_csharp, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", padx=10, pady=5).pack(side=tk.LEFT, padx=5)

        sugg_frame = tk.Frame(ai_win, bg=c["bg"])
        sugg_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        inner_sugg = tk.Frame(sugg_frame, bg=c["bg"])
        inner_sugg.pack()
        
        tk.Label(inner_sugg, text="💡 Suggestion:", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        sugg_lbl = tk.Label(inner_sugg, text="", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 9, "italic"))
        sugg_lbl.pack(side=tk.LEFT, padx=5)
        
        def use_sugg():
            prompt_entry.delete(0, tk.END)
            prompt_entry.insert(0, sugg_lbl.cget("text"))
            
        def pick_new_sugg():
            sugg_lbl.config(text=random.choice(suggs))

        tk.Button(inner_sugg, text="Use", command=use_sugg, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", font=("Segoe UI", 7), padx=5).pack(side=tk.LEFT, padx=(0, 2))
        tk.Button(inner_sugg, text="Skip", command=pick_new_sugg, bg=c["btn_bg"], fg=c["btn_fg"], relief="flat", font=("Segoe UI", 7), padx=5).pack(side=tk.LEFT)
        
        suggs = [
            "Create a rock paper scissors game with score tracking",
            "Make a digital clock that updates every second",
            "Build a login system with 3 attempts",
            "Create a todo list with array and loop",
            "Generate a fibonacci sequence up to 100",
            "Make a guessing game with random numbers 1-50",
            "Create a window with a button that shows a popup",
            "Write a text adventure game with multiple choices",
            "Calculate the factorial of a user input number",
            "Check if a word is a palindrome",
            "Create a slot machine with 3 reels",
            "Make a countdown timer from 10 to 0",
            "Create a directory called 'logs'",
            "Join two strings together",
            "Trim whitespace from input",
            "Check the type of a variable",
            "Remove a directory",
            "Create a simple calculator with add and subtract",
            "Make a window that changes color every second",
            "Write a program to reverse a user's name",
            "Create a file and write a secret message in it",
            "Read a file and show its content",
            "Generate a random password with 8 characters",
            "Check if a number is even or odd",
            "Create a loop that prints numbers 1 to 20",
            "Make a window with a title and specific size",
            "Ask for age and check if user is an adult",
            "Create an array of fruits and show the second one",
            "Calculate the area of a circle with radius 5",
            "Make a beep sound 3 times",
            "Show the current system time and date",
            "Create a folder named 'backup' and copy a file into it",
            "Convert a sentence to uppercase",
            "Find the length of a user input string",
            "Replace 'cat' with 'dog' in a sentence",
            "Sort an array of numbers",
            "Check if a file exists before deleting it"
        ]
        def refresh_sugg():
            if ai_win.winfo_exists():
                pick_new_sugg()
                delay = 2000 if self.shift_pressed else 4000
                self.root.after(delay, refresh_sugg)
        refresh_sugg()

    def ai_generate(self, prompt, model="Casual", teach=False):
        # The AI "reads" the manual to understand available commands
        manual_knowledge = self.get_manual_text()
        
        if model == "Advanced Mode":
            for _ in range(4): manual_knowledge += "\n" + self.get_manual_text()
        else:
            manual_knowledge += "\n" + self.get_manual_text() # Read twice
            manual_knowledge += "\n" + self.get_manual_text() # Read thrice
        
        prompt_lower = prompt.lower() + " " + prompt.lower() # Read prompt twice
        
        # Optimization: Removed heavy simulation loop for Advanced Mode to prevent freezing.

        lines = []
        
        # Helper to extract numbers
        def get_num(text, default=1):
            match = re.search(r'\d+', text)
            return int(match.group(0)) if match else default

        # Helper to extract string content
        def get_str(text):
            match = re.search(r'["\'](.+?)["\']', text)
            return match.group(1) if match else None

        # Variable overrides from prompt (e.g. "x=10")
        overrides = []
        vars_found = re.findall(r'\b(\w+)\s*=\s*(\S+)', prompt)
        for var, val in vars_found:
             overrides.append(f"{var} = {val}")
             if teach: overrides.append(f"# AI: You requested {var} to be {val}")
        if overrides: lines.extend(overrides)

        if model in ["Intelligent", "Advanced Mode"]:
            # Intelligent model generates more complex/robust code
            if "game" in prompt_lower or "guess" in prompt_lower:
                lines.append("# AI (Intelligent): Advanced Guessing Game")
                max_val = 100
                match = re.search(r'to (\d+)', prompt_lower)
                if match: max_val = int(match.group(1))
                
                lines.append(f"rand 1 {max_val} target")
                lines.append(f"show \"I picked a number 1-{max_val}.\"")
                lines.append("lives = 5")
                lines.append("func turn")
                lines.append("    if $lives > 0")
                lines.append("        show \"Lives left:\"")
                lines.append("        show $lives")
                lines.append("        ask \"Guess:\" g")
                lines.append("        if $g == $target")
                lines.append("            show \"You Win!\"")
                lines.append("            lives = 0")
                lines.append("        end")
                lines.append("        if $g != $target")
                lines.append("            show \"Wrong!\"")
                lines.append("            lives = $lives - 1")
                lines.append("            call turn")
                lines.append("        end")
                lines.append("    end")
                lines.append("    if $lives == 0")
                lines.append("        show \"Game Over. Target was:\"")
                lines.append("        show $target")
                lines.append("    end")
                lines.append("end")
                lines.append("call turn")
                return "\n".join(lines)
            
            if "count" in prompt_lower or "loop" in prompt_lower or "repeat" in prompt_lower:
                lines.append("# AI (Intelligent): Loop Example")
                limit = get_num(prompt_lower, 10)
                lines.append("i = 1")
                lines.append(f"repeat {limit}")
                lines.append("    show $i")
                lines.append("    i = $i + 1")
                lines.append("    wait 0.2")
                lines.append("end")
                lines.append("show \"Done counting!\"")
                return "\n".join(lines)

            if "fibonacci" in prompt_lower or "sequence" in prompt_lower:
                lines.append("# AI (Intelligent): Fibonacci Sequence")
                lines.append("a = 0")
                lines.append("b = 1")
                lines.append("show \"Fibonacci Sequence:\"")
                lines.append("show $a")
                lines.append("show $b")
                lines.append("repeat 10")
                lines.append("    c = $a + $b")
                lines.append("    show $c")
                lines.append("    a = $b")
                lines.append("    b = $c")
                lines.append("    wait 0.2")
                lines.append("end")
                return "\n".join(lines)

            if "rock" in prompt_lower and "paper" in prompt_lower:
                lines.append("# AI (Intelligent): Rock Paper Scissors")
                lines.append("show \"1: Rock, 2: Paper, 3: Scissors\"")
                lines.append("ask \"Choose (1-3):\" p")
                lines.append("rand 1 3 cpu")
                lines.append("show \"CPU chose:\"")
                lines.append("show $cpu")
                lines.append("if $p == $cpu")
                lines.append("    show \"Draw!\"")
                lines.append("end")
                lines.append("if $p == 1")
                lines.append("    if $cpu == 3")
                lines.append("        show \"You Win!\"")
                lines.append("    end")
                lines.append("    if $cpu == 2")
                lines.append("        show \"You Lose!\"")
                lines.append("    end")
                lines.append("end")
                lines.append("if $p == 2")
                lines.append("    if $cpu == 1")
                lines.append("        show \"You Win!\"")
                lines.append("    end")
                lines.append("    if $cpu == 3")
                lines.append("        show \"You Lose!\"")
                lines.append("    end")
                lines.append("end")
                lines.append("if $p == 3")
                lines.append("    if $cpu == 2")
                lines.append("        show \"You Win!\"")
                lines.append("    end")
                lines.append("    if $cpu == 1")
                lines.append("        show \"You Lose!\"")
                lines.append("    end")
                lines.append("end")
                return "\n".join(lines)

            if "todo" in prompt_lower or "list" in prompt_lower:
                lines.append("# AI (Intelligent): Todo List")
                lines.append("array tasks \"Buy Milk\" \"Walk Dog\" \"Code\"")
                lines.append("show \"Your Tasks:\"")
                lines.append("repeat 3")
                lines.append("    show $tasks[0]")
                lines.append("    wait 1")
                lines.append("end")
                return "\n".join(lines)

            if "clock" in prompt_lower:
                lines.append("# AI (Intelligent): Digital Clock")
                lines.append("show \"Clock started (10 seconds):\"")
                lines.append("repeat 10")
                lines.append("    time now")
                lines.append("    show $now")
                lines.append("    wait 1")
                lines.append("end")
                return "\n".join(lines)

            if "math" in prompt_lower and "demo" in prompt_lower:
                lines.append("# AI (Intelligent): Math Demo")
                lines.append("math s sqrt 64")
                lines.append("show \"Sqrt of 64 is:\"")
                lines.append("show $s")
                return "\n".join(lines)

            if "coin" in prompt_lower:
                lines.append("# AI: Coin Flip")
                lines.append("rand 1 2 r")
                lines.append("if $r == 1")
                lines.append("    show \"Heads\"")
                lines.append("end")
                lines.append("if $r == 2")
                lines.append("    show \"Tails\"")
                lines.append("end")
                return "\n".join(lines)

            if "dice" in prompt_lower:
                lines.append("# AI: Dice Roll")
                lines.append("rand 1 6 r")
                lines.append("show \"You rolled:\"")
                lines.append("show $r")
                return "\n".join(lines)

            if "slot" in prompt_lower:
                lines.append("# AI: Slot Machine")
                lines.append("rand 1 5 a")
                lines.append("rand 1 5 b")
                lines.append("rand 1 5 c")
                lines.append("show $a")
                lines.append("show $b")
                lines.append("show $c")
                lines.append("if $a == $b")
                lines.append("    if $b == $c")
                lines.append("        show \"JACKPOT!\"")
                lines.append("    end")
                lines.append("end")
                return "\n".join(lines)

            if "magic" in prompt_lower:
                lines.append("# AI: Magic 8 Ball")
                lines.append("array answers \"Yes\" \"No\" \"Maybe\" \"Ask again\"")
                lines.append("ask \"Ask a question:\" q")
                lines.append("rand 0 3 i")
                lines.append("show $answers[$i]")
                return "\n".join(lines)

            if "higher" in prompt_lower:
                lines.append("# AI: Higher Lower")
                lines.append("rand 1 100 a")
                lines.append("show \"Number is:\"")
                lines.append("show $a")
                lines.append("rand 1 100 b")
                lines.append("ask \"Is next higher or lower? (h/l)\" g")
                lines.append("show \"Next was:\"")
                lines.append("show $b")
                lines.append("if $b > $a")
                lines.append("    if $g == \"h\"")
                lines.append("        show \"Correct!\"")
                lines.append("    end")
                lines.append("end")
                return "\n".join(lines)

            if "math game" in prompt_lower:
                lines.append("# AI: Math Master")
                lines.append("score = 0")
                lines.append("repeat 3")
                lines.append("    rand 1 10 a")
                lines.append("    rand 1 10 b")
                lines.append("    ans = $a + $b")
                lines.append("    show $a")
                lines.append("    show \"+\"")
                lines.append("    show $b")
                lines.append("    ask \"=\" u")
                lines.append("    if $u == $ans")
                lines.append("        score = $score + 1")
                lines.append("        show \"Correct\"")
                lines.append("    end")
                lines.append("end")
                lines.append("show \"Score:\"")
                lines.append("show $score")
                return "\n".join(lines)

            if "memory" in prompt_lower:
                lines.append("# AI: Memory Test")
                lines.append("rand 1000 9999 code")
                lines.append("show \"Remember this:\"")
                lines.append("show $code")
                lines.append("wait 2")
                lines.append("clear")
                lines.append("ask \"What was the code?\" g")
                lines.append("if $g == $code")
                lines.append("    show \"Correct!\"")
                lines.append("end")
                return "\n".join(lines)

            if "roulette" in prompt_lower:
                lines.append("# AI: Russian Roulette")
                lines.append("rand 1 6 bullet")
                lines.append("show \"Spinning cylinder...\"")
                lines.append("wait 1")
                lines.append("ask \"Pull trigger? (y/n)\" a")
                lines.append("if $a == \"y\"")
                lines.append("    if $bullet == 1")
                lines.append("        show \"BANG! You lose.\"")
                lines.append("    end")
                lines.append("    if $bullet != 1")
                lines.append("        show \"Click. You live.\"")
                lines.append("    end")
                lines.append("end")
                return "\n".join(lines)

            if "blackjack" in prompt_lower:
                lines.append("# AI: Simple Blackjack")
                lines.append("rand 1 11 c1")
                lines.append("rand 1 11 c2")
                lines.append("total = $c1 + $c2")
                lines.append("show \"Cards:\"")
                lines.append("show $c1")
                lines.append("show $c2")
                lines.append("show \"Total:\"")
                lines.append("show $total")
                lines.append("if $total == 21")
                lines.append("    show \"Blackjack!\"")
                lines.append("end")
                return "\n".join(lines)

            if "word" in prompt_lower:
                lines.append("# AI: Word Guess")
                lines.append("secret = \"apple\"")
                lines.append("show \"Guess the fruit (5 letters)\"")
                lines.append("ask \"Guess:\" g")
                lines.append("if $g == $secret")
                lines.append("    show \"Correct!\"")
                lines.append("end")
                return "\n".join(lines)

            if "trivia" in prompt_lower:
                lines.append("# AI: Trivia")
                lines.append("ask \"Capital of France?\" a")
                lines.append("if $a == \"Paris\"")
                lines.append("    show \"Correct\"")
                lines.append("end")
                lines.append("ask \"2+2?\" b")
                lines.append("if $b == \"4\"")
                lines.append("    show \"Correct\"")
                lines.append("end")
                return "\n".join(lines)

            if "clicker" in prompt_lower:
                lines.append("# AI: Clicker")
                lines.append("clicks = 0")
                lines.append("show \"Press enter to click. Type 'exit' to stop.\"")
                lines.append("repeat 10")
                lines.append("    ask \"Click!\" i")
                lines.append("    if $i == \"exit\"")
                lines.append("        show \"Final Score:\"")
                lines.append("        show $clicks")
                lines.append("    end")
                lines.append("    clicks = $clicks + 1")
                lines.append("    show $clicks")
                lines.append("end")
                return "\n".join(lines)

            if "lottery" in prompt_lower:
                lines.append("# AI: Lottery")
                lines.append("ask \"Pick 1-10:\" p")
                lines.append("rand 1 10 w")
                lines.append("show \"Winning number:\"")
                lines.append("show $w")
                lines.append("if $p == $w")
                lines.append("    show \"You won!\"")
                lines.append("end")
                return "\n".join(lines)

            if "typing" in prompt_lower:
                lines.append("# AI: Typing Test")
                lines.append("target = \"The quick brown fox\"")
                lines.append("show \"Type this:\"")
                lines.append("show $target")
                lines.append("ask \">\" input")
                lines.append("if $input == $target")
                lines.append("    show \"Perfect!\"")
                lines.append("end")
                return "\n".join(lines)

            if "riddle" in prompt_lower:
                lines.append("# AI: Riddle")
                lines.append("show \"I speak without a mouth and hear without ears. What am I?\"")
                lines.append("ask \"Answer:\" a")
                lines.append("if $a == \"echo\"")
                lines.append("    show \"Correct\"")
                lines.append("end")
                return "\n".join(lines)

            if "fortune" in prompt_lower:
                lines.append("# AI: Fortune Teller")
                lines.append("array f \"Good luck\" \"Bad luck\" \"Surprise coming\"")
                lines.append("ask \"Name?\" n")
                lines.append("rand 0 2 i")
                lines.append("show $f[$i]")
                return "\n".join(lines)

            if "reaction" in prompt_lower:
                lines.append("# AI: Reaction")
                lines.append("show \"Get ready...\"")
                lines.append("wait 2")
                lines.append("show \"GO!\"")
                lines.append("ask \"Type 'go'\" i")
                lines.append("show \"Done\"")
                return "\n".join(lines)

            if "stopwatch" in prompt_lower:
                lines.append("# AI: Stopwatch Game")
                lines.append("show \"Count 5 seconds in your head...\"")
                lines.append("ask \"Press enter to start\" s")
                lines.append("time t1")
                lines.append("ask \"Press enter at 5s\" e")
                lines.append("time t2")
                lines.append("show \"Start:\"")
                lines.append("show $t1")
                lines.append("show \"End:\"")
                lines.append("show $t2")
                return "\n".join(lines)

            if "simon" in prompt_lower:
                lines.append("# AI: Simon Says")
                lines.append("show \"Simon says: Jump\"")
                lines.append("ask \"Action:\" a")
                lines.append("if $a == \"Jump\"")
                lines.append("    show \"Good\"")
                lines.append("end")
                return "\n".join(lines)

            if "battleship" in prompt_lower:
                lines.append("# AI: Battleship 1D")
                lines.append("rand 1 5 ship")
                lines.append("ask \"Bomb index 1-5:\" b")
                lines.append("if $b == $ship")
                lines.append("    show \"Hit!\"")
                lines.append("end")
                lines.append("if $b != $ship")
                lines.append("    show \"Miss. Ship was at:\"")
                lines.append("    show $ship")
                lines.append("end")
                return "\n".join(lines)

            if "prime" in prompt_lower:
                lines.append("# AI (Intelligent): Prime Checker")
                lines.append("ask \"Enter number:\" n")
                lines.append("is_prime = 1")
                lines.append("if $n < 2")
                lines.append("    is_prime = 0")
                lines.append("end")
                lines.append("div = 2")
                lines.append("repeat $n")
                lines.append("    if $div < $n")
                lines.append("        rem = $n / $div")
                lines.append("        check = $rem * $div")
                lines.append("        if $check == $n")
                lines.append("            is_prime = 0")
                lines.append("        end")
                lines.append("        div = $div + 1")
                lines.append("    end")
                lines.append("end")
                lines.append("if $is_prime == 1")
                lines.append("    show \"It is Prime\"")
                lines.append("end")
                lines.append("if $is_prime == 0")
                lines.append("    show \"Not Prime\"")
                lines.append("end")
                return "\n".join(lines)

            if "factorial" in prompt_lower:
                lines.append("# AI (Intelligent): Factorial")
                lines.append("ask \"Enter number:\" n")
                lines.append("res = 1")
                lines.append("i = 1")
                lines.append("repeat $n")
                lines.append("    res = $res * $i")
                lines.append("    i = $i + 1")
                lines.append("end")
                lines.append("show \"Factorial is:\"")
                lines.append("show $res")
                return "\n".join(lines)

            if "palindrome" in prompt_lower:
                lines.append("# AI (Intelligent): Palindrome Checker")
                lines.append("ask \"Enter word:\" w")
                lines.append("len l $w")
                lines.append("rev = \"\"")
                lines.append("i = $l - 1")
                lines.append("repeat $l")
                lines.append("    char = $w[$i]")
                lines.append("    rev = $rev + $char")
                lines.append("    i = $i - 1")
                lines.append("end")
                lines.append("if $w == $rev")
                lines.append("    show \"Palindrome!\"")
                lines.append("end")
                lines.append("if $w != $rev")
                lines.append("    show \"Not a palindrome.\"")
                lines.append("end")
                return "\n".join(lines)
            
            if "search" in prompt_lower or "google" in prompt_lower:
                lines.append("# AI: Web Search")
                lines.append("ask \"Search Query:\" q")
                lines.append("join url \"https://www.google.com/search?q=\" $q")
                lines.append("browser $url")
                return "\n".join(lines)

            if "shutdown" in prompt_lower:
                lines.append("# AI: Fake Shutdown")
                lines.append("show \"Shutting down...\"")
                lines.append("wait 2")
                lines.append("clear")
                lines.append("show \"It is now safe to turn off your computer.\"")
                return "\n".join(lines)

            # --- 70 New Templates (Dictionary Based for Efficiency) ---
            simple_templates = {
                "window basic": "window w\ntitle w \"Basic\"\nsize w 300 200\ntext w \"Hello\" 100 80",
                "window form": "window f\ntitle f \"Form\"\nsize f 300 150\ntext f \"Name:\" 20 20\ntext f \"[Input]\" 80 20\ntext f \"[Submit]\" 100 80",
                "window animation": "window a\ntitle a \"Move\"\nsize a 200 200\nrepeat 10\n    size a 200 200\n    wait 0.1\n    size a 210 210\n    wait 0.1\nend",
                "window color": "window c\ntitle c \"Colors\"\nsize c 300 300\nrepeat 5\n    color c \"red\"\n    wait 0.5\n    color c \"blue\"\n    wait 0.5\nend",
                "window multi": "window w1\ntitle w1 \"One\"\nwindow w2\ntitle w2 \"Two\"\nwait 2\nclose w1\nclose w2",
                "calculator": "ask \"A:\" a\nask \"B:\" b\nres = $a + $b\nshow $res",
                "converter": "ask \"Miles:\" m\nkm = $m * 1.6\nshow $km",
                "joke": "speak \"Why did the chicken cross the road?\"\nwait 2\nspeak \"To get to the other side!\"",
                "quote": "speak \"To be or not to be.\"",
                "alarm": "wait 5\nbeep\nnotify \"Alarm\" \"Wake up!\"",
                "timer": "c = 10\nrepeat 10\n    show $c\n    c = $c - 1\n    wait 1\nend",
                "countdown": "repeat 5\n    speak \"Tick...\"\n    wait 1\nend\nspeak \"Boom!\"",
                "progress": "show \"[      ]\"\nwait 1\nshow \"[==    ]\"\nwait 1\nshow \"[====  ]\"\nwait 1\nshow \"[======]\"",
                "loading": "repeat 3\n    show \"Loading...\"\n    wait 0.5\nend",
                "matrix": "repeat 20\n    rand 0 1 b\n    show $b\n    wait 0.1\nend",
                "hack": "show \"Hacking...\"\nwait 2\nnotify \"Hack\" \"Access Granted\"",
                "system": "time t\nnotify \"System\" \"Time: $t\"",
                "info": "speak \"MiniCode v1.0\"\nshow \"User: Admin\"",
                "help": "show \"Commands: show, ask, if, repeat\"",
                "menu": "show \"1. Start\"\nshow \"2. Exit\"\nask \"Opt:\" o",
                "shop": "show \"Sword: 10g\"\nshow \"Shield: 5g\"",
                "inventory": "array inv \"Potion\" \"Map\"\nshow $inv[0]",
                "stats": "hp = 100\nmp = 50\nshow $hp",
                "score": "score = 0\nscore = $score + 10\nshow $score",
                "level": "xp = 0\nlevel = 1\nshow \"Level Up!\"",
                "xp": "xp = 50\nreq = 100\nneed = $req - $xp\nshow $need",
                "health": "hp = 100\ndmg = 10\nhp = $hp - $dmg\nshow $hp",
                "mana": "mp = 10\ncost = 5\nmp = $mp - $cost\nshow $mp",
                "attack": "rand 1 10 dmg\nshow \"Hit for:\"\nshow $dmg",
                "defend": "def = 5\nshow \"Blocked 5 dmg\"",
                "magic": "show \"Casting Fireball...\"\nwait 1\nshow \"Boom!\"",
                "potion": "hp = 10\nhp = $hp + 20\nshow \"Healed!\"",
                "enemy": "speak \"A goblin appears!\"",
                "boss": "notify \"Warning\" \"BOSS FIGHT!\"\nbeep",
                "loot": "rand 1 100 gold\nshow \"Found gold:\"\nshow $gold",
                "chest": "show \"Opening chest...\"\nwait 1\nshow \"Found Sword!\"",
                "key": "has_key = 1\nshow \"Key acquired\"",
                "door": "if $has_key == 1\n    show \"Door opens\"\nend",
                "map": "show \"You are here: [X]\"",
                "compass": "show \"North is up\"",
                "weather": "rand 1 3 w\nif $w == 1\n    show \"Sunny\"\nend",
                "sun": "show \"The sun is bright\"",
                "moon": "show \"Full moon tonight\"",
                "stars": "show \"Look at the stars\"",
                "space": "show \"Zero gravity...\"",
                "planet": "show \"Landing on Mars...\"",
                "galaxy": "show \"Milky Way\"",
                "universe": "show \"Expanding...\"",
                "atom": "show \"Protons and electrons\"",
                "molecule": "show \"H2O\"",
                "cell": "show \"Mitosis...\"",
                "dna": "show \"GATTACA\"",
                "virus": "show \"Infected!\"",
                "bacteria": "show \"Microscopic life\"",
                "plant": "show \"Photosynthesis...\"",
                "tree": "show \"Timber!\"",
                "flower": "show \"Blooming...\"",
                "fruit": "array f \"Apple\" \"Pear\"\nshow $f[0]",
                "vegetable": "show \"Eat your greens\"",
                "animal": "show \"Woof!\"",
                "bird": "show \"Chirp!\"",
                "fish": "show \"Blub blub\"",
                "insect": "show \"Buzz...\"",
                "robot": "show \"Beep boop\"",
                "cyborg": "show \"Half man half machine\"",
                "android": "show \"Humanoid detected\"",
                "ai": "speak \"I am alive\"",
                "network": "show \"Connecting...\"",
                "server": "show \"Server online\"",
                "database": "show \"Querying DB...\"",
                "cloud": "show \"Uploading...\"",
                "internet": "show \"Browsing...\"",
                "web": "show \"404 Not Found\"",
                "site": "show \"Welcome to my site\"",
                "page": "show \"Page 1\"",
                "reverse string": "ask \"Text:\" t\nreverse r $t\nshow $r",
                "random color": "array c \"red\" \"blue\" \"green\"\nrand 0 2 i\nnotify \"Color\" $c[$i]",
                "password gen": "array c \"a\" \"b\" \"c\" \"1\" \"2\" \"3\"\npass = \"\"\nrepeat 4\n    rand 0 5 i\n    char = $c[$i]\n    pass = $pass + $char\nend\nspeak \"Password generated\"\nshow $pass",
                "area rect": "ask \"W:\" w\nask \"H:\" h\na = $w * $h\nshow $a",
                "volume cube": "ask \"L:\" l\nv = $l * $l\nv = $v * $l\nshow $v",
                "max of 3": "ask \"A:\" a\nask \"B:\" b\nask \"C:\" c\nmax m $a $b\nmax m $m $c\nshow $m",
                "min of 3": "ask \"A:\" a\nask \"B:\" b\nask \"C:\" c\nmin m $a $b\nmin m $m $c\nshow $m",
                "greet user": "ask \"Name:\" n\nspeak \"Hello\"\nshow $n",
                "count chars": "ask \"Text:\" t\nlen l $t\nshow $l",
                "check file": "ask \"File:\" f\nexists e $f\nif $e == 1\n    show \"Found\"\nend\nends txt $f \".txt\"\nif $txt == 1\n show \"Is Text\"\nend",
                "create folder": "mkdir \"new_folder\"\nshow \"Folder created\"",
                "delete folder": "rmdir \"old_folder\"\nshow \"Folder deleted\"",
                "trim string": "text = \"  hello  \"\ntrim t $text\nshow $t",
                "join strings": "a = \"Hello\"\nb = \"World\"\njoin c $a $b\nspeak $c",
                "check type": "x = 10\ntype t $x\nshow $t",
                "file manager": "mkdir \"data\"\nwrite \"data/info.txt\" \"123\"\nshow \"Data saved\"",
                "clean input": "ask \"Name:\" n\ntrim n $n\nstarts a $n \"A\"\nif $a == 1\n show \"Starts with A\"\nend",
                "path builder": "folder = \"users\"\nfile = \"data.txt\"\njoin path $folder \"/\"\njoin path $path $file\nshow $path",
                "type validator": "ask \"Age:\" a\ntype t $a\nspeak $t",
                "cleanup": "if exists \"temp\" == 1\n    rmdir \"temp\"\n    show \"Cleaned temp\"\nend",
                "power calc": "ask \"Base:\" b\nask \"Exp:\" e\npow r $b $e\nshow $r",
                "modulo check": "ask \"Num:\" n\nmod m $n 2\nif $m == 0\n    show \"Even\"\nend",
                "increment loop": "i = 0\nrepeat 5\n    inc i\n    show $i\nend",
                "file copy": "copy \"data.txt\" \"backup.txt\"\nshow \"Copied\"",
                "file move": "move \"old.txt\" \"new.txt\"\nshow \"Moved\"",
                "current dir": "cwd d\nshow \"Dir:\"\nshow $d",
                "list files": "cwd d\nlist f $d\nshow $f",
                "absolute value": "x = -10\nabs a $x\nshow $a",
                "floor value": "x = 5.9\nfloor f $x\nshow $f",
                "backup system": "mkdir \"backup\"\ncopy \"save.dat\" \"backup/save.dat\"\nshow \"Backup done\"",
                "center window": "window w\nsize w 200 100\ncenter w",
                "topmost window": "window w\ntopmost w 1\ntext w \"I am on top\" 50 50",
                "window icon": "write \"icon.ico\" \"placeholder\"\nwindow w\nicon w \"icon.ico\"",
                "get file size": "write \"test.txt\" \"hello\"\ngetsize s \"test.txt\"\nshow $s",
                "copy a file": "write \"a.txt\" \"A\"\ncopyfile \"a.txt\" \"b.txt\"\nshow \"Copied\"",
                "millisecond sleep": "show \"start\"\nsleep 500\nnotify \"Done\" \"Sleep finished\"",
                "transparent window": "window w\nopacity w 0.7",
                "fixed window": "window w\nresizable w 0 0",
                "fullscreen app": "window w\nfullscreen w 1\nwait 2\nclose w",
                "get window position": "window w\nsize w 200 200\ncenter w\ngetpos w x y\nshow $x",
                "clipboard manager": "clipget c\ncontains h $c \"http\"\nif $h == 1\n show \"Link detected\"\nend",
                "screen info": "screen w h\nshow \"Width:\"\nshow $w\nshow \"Height:\"\nshow $h",
                "mouse tracker": "repeat 10\n    mouse x y\n    show $x\n    show $y\n    wait 0.5\nend",
                "user greeting": "username u\nspeak \"Hello\"\nshow $u",
                "system info": "username u\ntime t\nnotify \"System\" $u\nshow $t"
            }
            
            for key, code_block in simple_templates.items():
                if key in prompt_lower:
                    prefix = f"# AI: {key.title()}\n"
                    if teach: prefix += "# AI: Loading template...\n"
                    if overrides: prefix = "\n".join(overrides) + "\n" + prefix
                    return prefix + code_block

            # Fallback for intelligent model if no specific complex template matches
            # lines.append(f"# AI (Intelligent): Optimized script for '{prompt}'")
            # Fall through to sequential parsing
        
        # Sequential Command Parsing (Natural Language Understanding)
        # Try to break down the prompt into steps
        steps = re.split(r' and | then |\. |, ', prompt_lower)
        parsed_lines = []
        last_window = "app"
        
        for step in steps:
            step = step.strip()
            if not step: continue
            
            # Window
            if "window" in step and ("create" in step or "make" in step or "open" in step or step.startswith("window")):
                name = "win"
                match = re.search(r'window (?:called|named) (\w+)', step)
                if match: name = match.group(1)
                last_window = name
                if teach: parsed_lines.append(f"# AI: Creating window '{name}'")
                parsed_lines.append(f"window {name}")
                
                # Inline properties
                if "title" in step:
                    t = get_str(step)
                    if not t: 
                        match_t = re.search(r'title(?:d)? (?:is )?(\w+)', step)
                        t = match_t.group(1) if match_t else "My App"
                    if teach: parsed_lines.append(f"# AI: Setting title to '{t}'")
                    parsed_lines.append(f"title {name} \"{t}\"")
                if "size" in step:
                    nums = re.findall(r'\d+', step)
                    if len(nums) >= 2: parsed_lines.append(f"size {name} {nums[0]} {nums[1]}")
                    else: parsed_lines.append(f"size {name} 500 400")
            
            # Title (standalone)
            elif "title" in step and "window" not in step:
                t = get_str(step)
                if not t:
                    match_t = re.search(r'title (?:is |to )?(\w+)', step)
                    t = match_t.group(1) if match_t else "Title"
                if teach: parsed_lines.append(f"# AI: Changing title of '{last_window}'")
                parsed_lines.append(f"title {last_window} \"{t}\"")

            # Size (standalone)
            elif "size" in step and "window" not in step:
                nums = re.findall(r'\d+', step)
                if len(nums) >= 2: 
                    if teach: parsed_lines.append(f"# AI: Resizing '{last_window}'")
                    parsed_lines.append(f"size {last_window} {nums[0]} {nums[1]}")

            # Color
            elif "color" in step or "background" in step:
                c = get_str(step)
                if not c:
                    match_c = re.search(r'(?:color|background) (?:is |to )?(\w+)', step)
                    c = match_c.group(1) if match_c else "white"
                if teach: parsed_lines.append(f"# AI: Setting color to '{c}'")
                parsed_lines.append(f"color {last_window} \"{c}\"")

            # Text
            elif "text" in step or "write" in step or "label" in step:
                c = get_str(step)
                if not c: c = "Hello"
                x, y = 50, 50
                nums = re.findall(r'\d+', step)
                if len(nums) >= 2: x, y = nums[0], nums[1]
                if teach: parsed_lines.append(f"# AI: Adding text '{c}'")
                parsed_lines.append(f"text {last_window} \"{c}\" {x} {y}")

            # Wait
            elif "wait" in step or "delay" in step or "sleep" in step:
                sec = get_num(step, 1)
                if teach: parsed_lines.append(f"# AI: Waiting for {sec}s")
                parsed_lines.append(f"wait {sec}")

            # Show/Print
            elif "show" in step or "print" in step or "say" in step:
                c = get_str(step)
                if c: 
                    parsed_lines.append(f"show \"{c}\"")
                else:
                    # Try variable
                    match_v = re.search(r'(?:show|print|say) \$?(\w+)', step)
                    if match_v: parsed_lines.append(f"show ${match_v.group(1)}")

            # Close
            elif "close" in step:
                target = last_window
                match = re.search(r'close (\w+)', step)
                if match: target = match.group(1)
                if teach: parsed_lines.append(f"# AI: Closing '{target}'")
                parsed_lines.append(f"close {target}")

            # Popup
            elif "popup" in step or "alert" in step or "message" in step:
                c = get_str(step)
                if c: 
                    if teach: parsed_lines.append("# AI: Showing popup")
                    parsed_lines.append(f"popup \"{c}\"")

            # Write File
            elif "write" in step or "save" in step or "file" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"write \"output.txt\" \"{c}\"")

            # Beep
            elif "beep" in step or "sound" in step:
                parsed_lines.append("beep")

            # Time
            elif "time" in step:
                parsed_lines.append("time now")
                if teach: parsed_lines.append("# AI: Getting current time")
                parsed_lines.append("show $now")

            # Math
            elif "math" in step or "calc" in step:
                match = re.search(r'(?:math|calc|calculate)\s+(\w+)\s+(\d+)', step)
                if match:
                    parsed_lines.append(f"math res {match.group(1)} {match.group(2)}")
                    parsed_lines.append("show $res")

            # New Ops
            elif "date" in step:
                parsed_lines.append("date d")
                parsed_lines.append("show $d")
            elif "upper" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"upper res \"{c}\"\nshow $res")
            elif "lower" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"lower res \"{c}\"\nshow $res")
            elif "reverse" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"reverse res \"{c}\"\nshow $res")
            elif "round" in step:
                n = get_num(step, 10.5)
                parsed_lines.append(f"round res {n}\nshow $res")
            elif "len" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"len l \"{c}\"\nshow $l")
            
            # New Ops 2
            elif "mkdir" in step or "create folder" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"mkdir \"{c}\"")
            elif "rmdir" in step or "delete folder" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"rmdir \"{c}\"")
            elif "trim" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"trim res \"{c}\"\nshow $res")
            elif "join" in step:
                parsed_lines.append("join res \"A\" \"B\"\nshow $res")
            elif "type" in step:
                parsed_lines.append("type t 123\nshow $t")
            
            # New Ops 3
            elif "pow" in step or "power" in step:
                parsed_lines.append("pow r 2 3\nshow $r")
            elif "mod" in step or "modulo" in step:
                parsed_lines.append("mod r 10 3\nshow $r")
            elif "inc" in step:
                parsed_lines.append("inc x\nshow $x")
            elif "dec" in step:
                parsed_lines.append("dec x\nshow $x")
            elif "copy" in step:
                parsed_lines.append("copy \"src.txt\" \"dst.txt\"")
            elif "move" in step:
                parsed_lines.append("move \"src.txt\" \"dst.txt\"")
            elif "cwd" in step:
                parsed_lines.append("cwd d\nshow $d")
            elif "list" in step:
                parsed_lines.append("cwd d\nlist f $d\nshow $f")
            elif "abs" in step:
                parsed_lines.append("abs a -5\nshow $a")
            elif "floor" in step:
                parsed_lines.append("floor f 5.9\nshow $f")
            
            # New Ops 4
            elif "icon" in step:
                parsed_lines.append("window w\nicon w \"icon.ico\"")
            elif "topmost" in step or "always on top" in step:
                parsed_lines.append("window w\ntopmost w 1")
            elif "center" in step:
                parsed_lines.append("window w\ncenter w")
            elif "getsize" in step or "file size" in step:
                parsed_lines.append("write \"f.txt\" \"data\"\ngetsize s \"f.txt\"\nshow $s")
            elif "copyfile" in step:
                parsed_lines.append("write \"a.txt\" \"A\"\ncopyfile \"a.txt\" \"b.txt\"")
            elif "sleep" in step:
                sec = get_num(step, 500)
                parsed_lines.append(f"sleep {sec}")
            
            # New Ops 5
            elif "opacity" in step or "transparent" in step:
                parsed_lines.append("window w\nopacity w 0.5")
            elif "resizable" in step:
                parsed_lines.append("window w\nresizable w 0 0")
            elif "fullscreen" in step:
                parsed_lines.append("window w\nfullscreen w 1")
            elif "getpos" in step or "position" in step:
                parsed_lines.append("window w\ngetpos w x y\nshow $x")

            # New Ops 6
            elif "browser" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"browser \"{c}\"")
            elif "minimize" in step:
                parsed_lines.append("window w\nminimize w")
            elif "restore" in step:
                parsed_lines.append("restore w")
            elif "focus" in step:
                parsed_lines.append("focus w")
            elif "filetime" in step:
                parsed_lines.append("filetime t \"f.txt\"\nshow $t")
            elif "isdir" in step:
                parsed_lines.append("isdir d \"folder\"\nshow $d")
            elif "isfile" in step:
                parsed_lines.append("isfile f \"file.txt\"\nshow $f")
            elif "pi" in step:
                parsed_lines.append("pi p\nshow $p")
            elif "rgb" in step:
                parsed_lines.append("rgb c 255 0 0\nshow $c")
            
            # New Ops 7
            elif "platform" in step:
                parsed_lines.append("platform p\nshow $p")
            elif "env" in step:
                parsed_lines.append("env u \"USERNAME\"\nshow $u")
            elif "exec" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"exec \"{c}\"")
            elif "hash" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"hash h \"{c}\"\nshow $h")
            elif "warp" in step:
                parsed_lines.append("warp 100 100")
            
            # New Ops 8
            elif "starts" in step:
                parsed_lines.append("starts r \"Hello\" \"He\"\nshow $r")
            elif "ends" in step:
                parsed_lines.append("ends r \"Hello\" \"lo\"\nshow $r")
            elif "contains" in step:
                parsed_lines.append("contains r \"Hello\" \"el\"\nshow $r")
            elif "index" in step:
                parsed_lines.append("index i \"Hello\" \"e\"\nshow $i")
            elif "speak" in step or "say" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"speak \"{c}\"")
            elif "notify" in step:
                c = get_str(step)
                if c: parsed_lines.append(f"notify \"Alert\" \"{c}\"")




        if parsed_lines:
            lines.extend(parsed_lines)
            return "\n".join(lines)

        if "window" in prompt_lower:
            lines.append("# AI: Window Setup")
            name = "app"
            match = re.search(r'window (?:called|named) (\w+)', prompt_lower)
            if match: name = match.group(1)
            lines.append(f"window {name}")
            
            match = re.search(r'title(?:d)? ["\'](.+?)["\']', prompt_lower)
            if match: lines.append(f"title {name} \"{match.group(1)}\"")
            else: lines.append(f"title {name} \"My App\"")
            
            match = re.search(r'size (\d+) (\d+)', prompt_lower)
            if match: lines.append(f"size {name} {match.group(1)} {match.group(2)}")
            else: lines.append(f"size {name} 400 300")
            
            if "text" in prompt_lower or "label" in prompt_lower:
                lines.append(f"text {name} \"Hello World\" 50 50")

        elif "calc" in prompt_lower or "add" in prompt_lower:
            lines.append("# AI: Calculator")
            lines.append("ask \"Num 1:\" a")
            lines.append("ask \"Num 2:\" b")
            lines.append("res = $a + $b")
            lines.append("show \"Result:\"")
            lines.append("show $res")
            lines.append("sub = $a - $b")
            lines.append("show \"Difference:\"")
            lines.append("show $sub")
            lines.append("mul = $a * $b")
            lines.append("show \"Product:\"")
            lines.append("show $res")

        elif "game" in prompt_lower or "guess" in prompt_lower:
            lines.append("# AI: Guessing Game")
            max_val = 10
            match = re.search(r'to (\d+)', prompt_lower)
            if match: max_val = int(match.group(1))
            
            lines.append(f"rand 1 {max_val} target")
            lines.append(f"ask \"Guess (1-{max_val}):\" g")
            lines.append("if $g == $target")
            lines.append("    show \"Win!\"")
            lines.append("end")
            lines.append("if $g != $target")
            lines.append("    show \"Lose!\"")
            lines.append("    show $target")
            lines.append("end")
            
        elif "array" in prompt_lower or "list" in prompt_lower:
            lines.append("# AI: Array Example")
            items = "\"Apple\" \"Banana\" \"Cherry\""
            if "number" in prompt_lower:
                items = "10 20 30 40 50"
            lines.append(f"array items {items}")
            lines.append("show \"First item:\"")
            lines.append("show $items[0]")
            lines.append("wait 1")
            lines.append("show \"Second item:\"")
            lines.append("show $items[1]")
            
        elif "wait" in prompt_lower or "timer" in prompt_lower:
            lines.append("# AI: Timer")
            sec = 5
            match = re.search(r'(\d+) (?:seconds|sec|s)', prompt_lower)
            if match: sec = int(match.group(1))
            
            lines.append(f"show \"Counting down from {sec}...\"")
            lines.append(f"count = {sec}")
            lines.append(f"repeat {sec}")
            lines.append("    show $count")
            lines.append("    count = $count - 1")
            lines.append("    wait 1")
            lines.append("end")
            lines.append("show \"Done!\"")

        elif "set" in prompt_lower or "variable" in prompt_lower:
            lines.append("# AI: Variable Assignment")
            match = re.search(r'set (\w+) to (.+)', prompt_lower)
            if match:
                var = match.group(1)
                val = match.group(2).strip()
                if not val.isdigit() and not val.startswith('"'):
                    val = f'"{val}"'
                lines.append(f"{var} = {val}")
                lines.append(f"show ${var}")
            else:
                lines.append("x = 10")
                lines.append("show $x")

        elif "function" in prompt_lower or "routine" in prompt_lower:
            lines.append("# AI: Function Definition")
            func_name = "myFunc"
            match = re.search(r'(?:function|routine) (?:called|named)?\s*(\w+)', prompt_lower)
            if match: func_name = match.group(1)
            
            lines.append(f"func {func_name}")
            lines.append("    show \"Function executed.\"")
            lines.append("end")
            lines.append(f"call {func_name}")

        elif "quiz" in prompt_lower:
            lines.append("# AI: Simple Quiz")
            lines.append("score = 0")
            lines.append("ask \"Q1: What is 5 + 5?\" ans")
            lines.append("if $ans == 10")
            lines.append("    show \"Correct!\"")
            lines.append("    score = $score + 1")
            lines.append("end")
            lines.append("ask \"Q2: What is 10 * 2?\" ans")
            lines.append("if $ans == 20")
            lines.append("    show \"Correct!\"")
            lines.append("    score = $score + 1")
            lines.append("end")
            lines.append("show \"Final Score:\"")
            lines.append("show $score")

        elif "login" in prompt_lower or "password" in prompt_lower:
            lines.append("# AI: Login System")
            lines.append("ask \"Enter Password:\" pass")
            lines.append("if $pass == \"1234\"")
            lines.append("    show \"Access Granted.\"")
            lines.append("    show \"Welcome User!\"")
            lines.append("end")
            lines.append("if $pass != \"1234\"")
            lines.append("    show \"Access Denied.\"")
            lines.append("end")

        elif "adventure" in prompt_lower or "story" in prompt_lower:
            lines.append("# AI: Text Adventure")
            lines.append("show \"You are in a dark room.\"")
            lines.append("show \"1: Open Door, 2: Sleep\"")
            lines.append("ask \"Choice:\" c")
            lines.append("if $c == 1")
            lines.append("    show \"You found treasure!\"")
            lines.append("end")
            lines.append("if $c == 2")
            lines.append("    show \"You slept and woke up later.\"")
            lines.append("end")

        elif "even" in prompt_lower or "odd" in prompt_lower:
            lines.append("# AI: Even/Odd (Simple check)")
            lines.append("show \"Note: This language supports simple math.\"")
            lines.append("ask \"Enter a number:\" n")
            lines.append("rem = $n / 2")
            lines.append("check = $rem * 2")
            lines.append("if $check == $n")
            lines.append("    show \"Number is Even\"")
            lines.append("end")
            lines.append("if $check != $n")
            lines.append("    show \"Number is Odd\"")
            lines.append("end")

        elif "clear" in prompt_lower or "clean" in prompt_lower:
            lines.append("# AI: Clear Screen")
            lines.append("show \"Screen will clear in 2 seconds...\"")
            lines.append("wait 2")
            lines.append("clear")

        else:
            lines.append("# AI: Hello World")
            lines.append("show \"I didn't understand, so here is hello world.\"")
            lines.append("show \"Hello World\"")
            
        return "\n".join(lines)

    def show_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("300x350")
        win.configure(bg="#f4f4f4")

        tk.Label(win, text="Font Family:", bg="#f4f4f4").pack(pady=(10, 0))
        font_var = tk.StringVar(value=self.settings["font"])
        fonts = ["Consolas", "Arial", "Courier New", "Verdana", "Times New Roman", "Lucida Console", "Segoe UI", "Comic Sans MS", "Georgia", "Impact", "Trebuchet MS", "Helvetica", "Calibri", "Cambria", "Roboto", "Open Sans", "Fira Code", "JetBrains Mono", "Source Code Pro", "Ubuntu Mono", "Droid Sans Mono", "Inconsolata", "Monaco", "Menlo", "DejaVu Sans Mono", "Hack", "Cascadia Code", "Liberation Mono", "Bitstream Vera Sans Mono", "Courier", "Fixedsys", "MS Gothic"]
        ttk.Combobox(win, textvariable=font_var, values=fonts, state="readonly").pack(pady=5)

        tk.Label(win, text="Font Size:", bg="#f4f4f4").pack(pady=(10, 0))
        size_var = tk.IntVar(value=self.settings["size"])
        tk.Spinbox(win, from_=8, to=30, textvariable=size_var).pack(pady=5)

        tk.Label(win, text="Theme:", bg="#f4f4f4").pack(pady=(10, 0))
        theme_var = tk.StringVar(value=self.settings["theme"])
        themes = ["Light", "Dark", "Blue", "Hacker", "Retro", "Night", "Monokai", "Solarized", "Oceanic", "Forest", "Sunset", "Dracula", "High Contrast", "Cyberpunk", "Coffee", "Matrix", "Neon", "Pastel", "Midnight", "Solar Flare", "Mint", "Lavender", "Crimson", "Olive", "Grape", "Steel", "Mocha", "Rose", "Amber", "Emerald", "Sapphire", "Ruby", "Gold", "Platinum", "Obsidian", "Ivory", "Coral", "Teal"]
        ttk.Combobox(win, textvariable=theme_var, values=themes, state="readonly").pack(pady=5)

        minimap_var = tk.BooleanVar(value=self.settings.get("minimap", True))
        tk.Checkbutton(win, text="Show Minimap", variable=minimap_var, bg="#f4f4f4").pack(pady=5)

        tk.Label(win, text="Default AI Model:", bg="#f4f4f4").pack(pady=(5, 0))
        ai_model_var = tk.StringVar(value=self.settings.get("default_ai_model", "Intelligent"))
        ttk.Combobox(win, textvariable=ai_model_var, values=["Casual", "Intelligent", "Advanced Mode"], state="readonly").pack(pady=5)

        tk.Label(win, text="Username:", bg="#f4f4f4").pack(pady=(5, 0))
        username_var = tk.StringVar(value=self.settings.get("username", "Coder"))
        tk.Entry(win, textvariable=username_var).pack(pady=5)

        def apply():
            self.settings["font"] = font_var.get()
            self.settings["size"] = size_var.get()
            self.settings["theme"] = theme_var.get()
            self.settings["minimap"] = minimap_var.get()
            self.settings["default_ai_model"] = ai_model_var.get()
            self.settings["username"] = username_var.get()
            self.apply_theme()
            
            # Refresh layout for minimap
            self.refresh_layout()
            win.destroy()

        tk.Button(win, text="Apply", command=apply, bg="#e0e0e0").pack(pady=20)

    def apply_theme(self):
        theme = self.settings["theme"]
        font_cfg = (self.settings["font"], int(self.settings["size"]))
        
        colors = {
            "Light": {"bg": "#f4f4f4", "fg": "#333", "edit_bg": "white", "edit_fg": "#2c3e50", "btn_bg": "#e0e0e0", "btn_fg": "#333333"},
            "Dark": {"bg": "#2d2d2d", "fg": "#d4d4d4", "edit_bg": "#1e1e1e", "edit_fg": "#d4d4d4", "btn_bg": "#3d3d3d", "btn_fg": "#d4d4d4"},
            "Blue": {"bg": "#e3f2fd", "fg": "#0d47a1", "edit_bg": "#ffffff", "edit_fg": "#01579b", "btn_bg": "#bbdefb", "btn_fg": "#0d47a1"},
            "Hacker": {"bg": "#0d1117", "fg": "#00ff41", "edit_bg": "#000000", "edit_fg": "#00ff41", "btn_bg": "#161b22", "btn_fg": "#00ff41"},
            "Retro": {"bg": "#fdf6e3", "fg": "#657b83", "edit_bg": "#eee8d5", "edit_fg": "#586e75", "btn_bg": "#eee8d5", "btn_fg": "#657b83"},
            "Night": {"bg": "#1a1b26", "fg": "#a9b1d6", "edit_bg": "#24283b", "edit_fg": "#c0caf5", "btn_bg": "#24283b", "btn_fg": "#a9b1d6"},
            "Monokai": {"bg": "#272822", "fg": "#f8f8f2", "edit_bg": "#272822", "edit_fg": "#f8f8f2", "btn_bg": "#3e3d32", "btn_fg": "#f8f8f2"},
            "Solarized": {"bg": "#fdf6e3", "fg": "#657b83", "edit_bg": "#fdf6e3", "edit_fg": "#657b83", "btn_bg": "#eee8d5", "btn_fg": "#657b83"},
            "Oceanic": {"bg": "#e0f7fa", "fg": "#006064", "edit_bg": "#e0f2f1", "edit_fg": "#004d40", "btn_bg": "#b2ebf2", "btn_fg": "#006064"},
            "Forest": {"bg": "#e8f5e9", "fg": "#1b5e20", "edit_bg": "#f1f8e9", "edit_fg": "#2e7d32", "btn_bg": "#c8e6c9", "btn_fg": "#1b5e20"},
            "Sunset": {"bg": "#FFF3E0", "fg": "#5D4037", "edit_bg": "#FFFFFF", "edit_fg": "#E65100", "btn_bg": "#FFE0B2", "btn_fg": "#5D4037"},
            "Dracula": {"bg": "#282A36", "fg": "#F8F8F2", "edit_bg": "#44475A", "edit_fg": "#F8F8F2", "btn_bg": "#44475A", "btn_fg": "#F8F8F2"},
            "High Contrast": {"bg": "#000000", "fg": "#FFFFFF", "edit_bg": "#000000", "edit_fg": "#FFFFFF", "btn_bg": "#333333", "btn_fg": "#FFFFFF"},
            "Cyberpunk": {"bg": "#050510", "fg": "#00FF99", "edit_bg": "#000000", "edit_fg": "#FF00FF", "btn_bg": "#1a1a2e", "btn_fg": "#00FF99"},
            "Coffee": {"bg": "#D7CCC8", "fg": "#3E2723", "edit_bg": "#EFEBE9", "edit_fg": "#4E342E", "btn_bg": "#BCAAA4", "btn_fg": "#3E2723"},
            "Matrix": {"bg": "#000000", "fg": "#00FF00", "edit_bg": "#0D0D0D", "edit_fg": "#00FF00", "btn_bg": "#003300", "btn_fg": "#00FF00"},
            "Neon": {"bg": "#111111", "fg": "#FF00FF", "edit_bg": "#1A1A1A", "edit_fg": "#00FFFF", "btn_bg": "#333333", "btn_fg": "#FF00FF"},
            "Pastel": {"bg": "#FFD1DC", "fg": "#555555", "edit_bg": "#E0F7FA", "edit_fg": "#555555", "btn_bg": "#FFB7B2", "btn_fg": "#555555"},
            "Midnight": {"bg": "#0f0f23", "fg": "#aabbc3", "edit_bg": "#15152e", "edit_fg": "#d4d4d4", "btn_bg": "#15152e", "btn_fg": "#aabbc3"},
            "Solar Flare": {"bg": "#ffecb3", "fg": "#e65100", "edit_bg": "#fff8e1", "edit_fg": "#bf360c", "btn_bg": "#ffe082", "btn_fg": "#e65100"},
            "Mint": {"bg": "#E0F2F1", "fg": "#004D40", "edit_bg": "#F1F8E9", "edit_fg": "#1B5E20", "btn_bg": "#B2DFDB", "btn_fg": "#004D40"},
            "Lavender": {"bg": "#F3E5F5", "fg": "#4A148C", "edit_bg": "#FFFFFF", "edit_fg": "#6A1B9A", "btn_bg": "#E1BEE7", "btn_fg": "#4A148C"},
            "Crimson": {"bg": "#2b0000", "fg": "#ffcccc", "edit_bg": "#400000", "edit_fg": "#ffcccc", "btn_bg": "#550000", "btn_fg": "#ffcccc"},
            "Olive": {"bg": "#F4F3E8", "fg": "#556B2F", "edit_bg": "#FFFFFF", "edit_fg": "#6B8E23", "btn_bg": "#E9E8D9", "btn_fg": "#556B2F"},
            "Grape": {"bg": "#EAEAF3", "fg": "#483D8B", "edit_bg": "#FFFFFF", "edit_fg": "#6A5ACD", "btn_bg": "#DCDCF8", "btn_fg": "#483D8B"},
            "Steel": {"bg": "#E6E8EB", "fg": "#4682B4", "edit_bg": "#FFFFFF", "edit_fg": "#5F9EA0", "btn_bg": "#D6D8DB", "btn_fg": "#4682B4"},
            "Mocha": {"bg": "#EFEBE9", "fg": "#6D4C41", "edit_bg": "#FFFFFF", "edit_fg": "#8D6E63", "btn_bg": "#D7CCC8", "btn_fg": "#6D4C41"},
            "Rose": {"bg": "#FFF0F5", "fg": "#C71585", "edit_bg": "#FFFFFF", "edit_fg": "#DB7093", "btn_bg": "#FFE4E1", "btn_fg": "#C71585"},
            "Amber": {"bg": "#2b1b00", "fg": "#ffb000", "edit_bg": "#1a1000", "edit_fg": "#ffb000", "btn_bg": "#3d2600", "btn_fg": "#ffb000"},
            "Emerald": {"bg": "#002b1b", "fg": "#00ff80", "edit_bg": "#001a10", "edit_fg": "#00ff80", "btn_bg": "#003d26", "btn_fg": "#00ff80"},
            "Sapphire": {"bg": "#001b2b", "fg": "#0080ff", "edit_bg": "#00101a", "edit_fg": "#0080ff", "btn_bg": "#00263d", "btn_fg": "#0080ff"},
            "Ruby": {"bg": "#2b0000", "fg": "#ff0040", "edit_bg": "#1a0000", "edit_fg": "#ff0040", "btn_bg": "#3d0000", "btn_fg": "#ff0040"},
            "Gold": {"bg": "#2b2b00", "fg": "#ffff00", "edit_bg": "#1a1a00", "edit_fg": "#ffff00", "btn_bg": "#3d3d00", "btn_fg": "#ffff00"},
            "Platinum": {"bg": "#e0e0e0", "fg": "#202020", "edit_bg": "#ffffff", "edit_fg": "#202020", "btn_bg": "#d0d0d0", "btn_fg": "#202020"},
            "Obsidian": {"bg": "#101010", "fg": "#606060", "edit_bg": "#000000", "edit_fg": "#606060", "btn_bg": "#202020", "btn_fg": "#606060"},
            "Ivory": {"bg": "#fffff0", "fg": "#303030", "edit_bg": "#fffff0", "edit_fg": "#303030", "btn_bg": "#f0f0e0", "btn_fg": "#303030"},
            "Coral": {"bg": "#2b1010", "fg": "#ff7f50", "edit_bg": "#1a0a0a", "edit_fg": "#ff7f50", "btn_bg": "#3d1616", "btn_fg": "#ff7f50"},
            "Teal": {"bg": "#002b2b", "fg": "#008080", "edit_bg": "#001a1a", "edit_fg": "#008080", "btn_bg": "#003d3d", "btn_fg": "#008080"}
        }
        c = colors.get(theme, colors["Light"])

        self.root.configure(bg=c["bg"])
        self.main_container.configure(bg=c["bg"])
        self.toolbar.configure(bg=c["bg"])
        self.paned.configure(bg=c["bg"])
        self.frame_editor.configure(bg=c["bg"])
        self.frame_output.configure(bg=c["bg"])
        
        self.lbl_workspace.configure(bg=c["bg"], fg=c["fg"])
        self.lbl_output.configure(bg=c["bg"], fg=c["fg"])
        
        self.editor.configure(bg=c["edit_bg"], fg=c["edit_fg"], font=font_cfg, insertbackground=c["fg"])
        self.output.configure(bg=c["edit_bg"], fg=c["edit_fg"], font=font_cfg)
        self.line_numbers.configure(bg=c["bg"], fg=c["fg"], font=font_cfg)
        self.minimap.configure(bg=c["edit_bg"], fg=c["edit_fg"])
        self.taskbar_frame.configure(bg=c.get("btn_bg", "#e0e0e0"))
        
        for btn in self.toolbar.winfo_children():
            if isinstance(btn, tk.Button):
                btn.configure(bg=c.get("btn_bg", "#e0e0e0"), fg=c.get("btn_fg", "#333333"), activebackground=c.get("bg", "#f4f4f4"), activeforeground=c.get("fg", "#333"))
        
        for btn in self.taskbar_frame.winfo_children():
            if isinstance(btn, tk.Button):
                btn.configure(bg=c.get("btn_bg", "#e0e0e0"), fg=c.get("btn_fg", "#333333"))
        
        if theme == "Dark":
            self.editor.tag_configure("keyword", foreground="#569cd6")
            self.editor.tag_configure("variable", foreground="#9cdcfe")
        elif theme == "Hacker":
            self.editor.tag_configure("keyword", foreground="#00ff41")
            self.editor.tag_configure("variable", foreground="#008f11")
            self.editor.tag_configure("string", foreground="#003300")
        elif theme == "Retro":
            self.editor.tag_configure("keyword", foreground="#b58900")
            self.editor.tag_configure("variable", foreground="#268bd2")
        elif theme == "Night":
            self.editor.tag_configure("keyword", foreground="#ff79c6")
            self.editor.tag_configure("variable", foreground="#8be9fd")
            self.editor.tag_configure("ai_comment", foreground="#6272a4")
        elif theme == "Monokai":
            self.editor.tag_configure("keyword", foreground="#f92672")
            self.editor.tag_configure("variable", foreground="#66d9ef")
            self.editor.tag_configure("string", foreground="#e6db74")
            self.editor.tag_configure("comment", foreground="#75715e")
            self.editor.tag_configure("ai_comment", foreground="#49483e")
        elif theme == "Solarized":
            self.editor.tag_configure("keyword", foreground="#859900")
            self.editor.tag_configure("variable", foreground="#268bd2")
            self.editor.tag_configure("string", foreground="#2aa198")
            self.editor.tag_configure("comment", foreground="#93a1a1")
            self.editor.tag_configure("ai_comment", foreground="#586e75")
        elif theme == "Oceanic":
            self.editor.tag_configure("keyword", foreground="#006064")
            self.editor.tag_configure("variable", foreground="#0097a7")
            self.editor.tag_configure("string", foreground="#004d40")
            self.editor.tag_configure("comment", foreground="#00838f")
            self.editor.tag_configure("ai_comment", foreground="#006064")
        elif theme == "Forest":
            self.editor.tag_configure("keyword", foreground="#1b5e20")
            self.editor.tag_configure("variable", foreground="#2e7d32")
            self.editor.tag_configure("string", foreground="#33691e")
            self.editor.tag_configure("comment", foreground="#558b2f")
            self.editor.tag_configure("ai_comment", foreground="#1b5e20")
        elif theme == "Sunset":
            self.editor.tag_configure("keyword", foreground="#E65100")
            self.editor.tag_configure("variable", foreground="#BF360C")
            self.editor.tag_configure("string", foreground="#F57C00")
            self.editor.tag_configure("comment", foreground="#8D6E63")
            self.editor.tag_configure("ai_comment", foreground="#5D4037")
        elif theme == "Dracula":
            self.editor.tag_configure("keyword", foreground="#FF79C6")
            self.editor.tag_configure("variable", foreground="#8BE9FD")
            self.editor.tag_configure("string", foreground="#F1FA8C")
            self.editor.tag_configure("comment", foreground="#6272A4")
            self.editor.tag_configure("ai_comment", foreground="#6272A4")
        elif theme == "High Contrast":
            self.editor.tag_configure("keyword", foreground="#FFFF00")
            self.editor.tag_configure("variable", foreground="#00FFFF")
            self.editor.tag_configure("string", foreground="#00FF00")
            self.editor.tag_configure("comment", foreground="#808080")
            self.editor.tag_configure("ai_comment", foreground="#808080")
        elif theme == "Cyberpunk":
            self.editor.tag_configure("keyword", foreground="#FF00FF")
            self.editor.tag_configure("variable", foreground="#00FFFF")
            self.editor.tag_configure("string", foreground="#FFFF00")
            self.editor.tag_configure("comment", foreground="#00FF99")
            self.editor.tag_configure("ai_comment", foreground="#00FF99")
        elif theme == "Coffee":
            self.editor.tag_configure("keyword", foreground="#3E2723")
            self.editor.tag_configure("variable", foreground="#5D4037")
            self.editor.tag_configure("string", foreground="#795548")
            self.editor.tag_configure("comment", foreground="#A1887F")
            self.editor.tag_configure("ai_comment", foreground="#8D6E63")
        elif theme == "Matrix":
            self.editor.tag_configure("keyword", foreground="#008000")
            self.editor.tag_configure("variable", foreground="#00FF00")
            self.editor.tag_configure("string", foreground="#006400")
            self.editor.tag_configure("comment", foreground="#004000")
            self.editor.tag_configure("ai_comment", foreground="#00FF00")
        elif theme == "Neon":
            self.editor.tag_configure("keyword", foreground="#FF00FF")
            self.editor.tag_configure("variable", foreground="#00FFFF")
            self.editor.tag_configure("string", foreground="#FFFF00")
            self.editor.tag_configure("comment", foreground="#888888")
            self.editor.tag_configure("ai_comment", foreground="#FFFFFF")
        elif theme == "Pastel":
            self.editor.tag_configure("keyword", foreground="#FF6961")
            self.editor.tag_configure("variable", foreground="#77DD77")
            self.editor.tag_configure("string", foreground="#AEC6CF")
            self.editor.tag_configure("comment", foreground="#CFCFC4")
            self.editor.tag_configure("ai_comment", foreground="#B39EB5")
        elif theme == "Midnight":
            self.editor.tag_configure("keyword", foreground="#ff0055")
            self.editor.tag_configure("variable", foreground="#00ccff")
            self.editor.tag_configure("string", foreground="#00ff99")
            self.editor.tag_configure("comment", foreground="#5c5c8a")
            self.editor.tag_configure("ai_comment", foreground="#5c5c8a")
        elif theme == "Solar Flare":
            self.editor.tag_configure("keyword", foreground="#d84315")
            self.editor.tag_configure("variable", foreground="#ef6c00")
            self.editor.tag_configure("string", foreground="#f9a825")
            self.editor.tag_configure("comment", foreground="#8d6e63")
            self.editor.tag_configure("ai_comment", foreground="#8d6e63")
        elif theme == "Mint":
            self.editor.tag_configure("keyword", foreground="#00796B")
            self.editor.tag_configure("variable", foreground="#388E3C")
            self.editor.tag_configure("string", foreground="#004D40")
            self.editor.tag_configure("comment", foreground="#80CBC4")
            self.editor.tag_configure("ai_comment", foreground="#8d6e63")
        elif theme == "Lavender":
            self.editor.tag_configure("keyword", foreground="#7B1FA2")
            self.editor.tag_configure("variable", foreground="#9C27B0")
            self.editor.tag_configure("string", foreground="#6A1B9A")
            self.editor.tag_configure("comment", foreground="#CE93D8")
            self.editor.tag_configure("ai_comment", foreground="#8d6e63")
        elif theme == "Crimson":
            self.editor.tag_configure("keyword", foreground="#ff0000")
            self.editor.tag_configure("variable", foreground="#ff6666")
            self.editor.tag_configure("string", foreground="#ff9999")
            self.editor.tag_configure("comment", foreground="#800000")
            self.editor.tag_configure("ai_comment", foreground="#800000")
        elif theme == "Olive":
            self.editor.tag_configure("keyword", foreground="#808000")
            self.editor.tag_configure("variable", foreground="#556B2F")
            self.editor.tag_configure("string", foreground="#6B8E23")
            self.editor.tag_configure("comment", foreground="#BDB76B")
            self.editor.tag_configure("ai_comment", foreground="#BDB76B")
        elif theme == "Grape":
            self.editor.tag_configure("keyword", foreground="#9370DB")
            self.editor.tag_configure("variable", foreground="#8A2BE2")
            self.editor.tag_configure("string", foreground="#9932CC")
            self.editor.tag_configure("comment", foreground="#BA55D3")
            self.editor.tag_configure("ai_comment", foreground="#BA55D3")
        elif theme == "Steel":
            self.editor.tag_configure("keyword", foreground="#708090")
            self.editor.tag_configure("variable", foreground="#778899")
            self.editor.tag_configure("string", foreground="#B0C4DE")
            self.editor.tag_configure("comment", foreground="#D3D3D3")
            self.editor.tag_configure("ai_comment", foreground="#D3D3D3")
        elif theme == "Mocha":
            self.editor.tag_configure("keyword", foreground="#A0522D")
            self.editor.tag_configure("variable", foreground="#8B4513")
            self.editor.tag_configure("string", foreground="#D2691E")
            self.editor.tag_configure("comment", foreground="#F4A460")
            self.editor.tag_configure("ai_comment", foreground="#F4A460")
        elif theme == "Rose":
            self.editor.tag_configure("keyword", foreground="#FF1493")
            self.editor.tag_configure("variable", foreground="#FF69B4")
            self.editor.tag_configure("string", foreground="#DB7093")
            self.editor.tag_configure("comment", foreground="#FFC0CB")
            self.editor.tag_configure("ai_comment", foreground="#FFC0CB")
        elif theme == "Amber":
            self.editor.tag_configure("keyword", foreground="#ffcc00")
            self.editor.tag_configure("variable", foreground="#ffaa00")
            self.editor.tag_configure("string", foreground="#ffee00")
            self.editor.tag_configure("comment", foreground="#805500")
            self.editor.tag_configure("ai_comment", foreground="#805500")
        elif theme == "Emerald":
            self.editor.tag_configure("keyword", foreground="#00ff80")
            self.editor.tag_configure("variable", foreground="#00cc66")
            self.editor.tag_configure("string", foreground="#66ffb3")
            self.editor.tag_configure("comment", foreground="#006633")
            self.editor.tag_configure("ai_comment", foreground="#006633")
        elif theme == "Sapphire":
            self.editor.tag_configure("keyword", foreground="#0080ff")
            self.editor.tag_configure("variable", foreground="#0066cc")
            self.editor.tag_configure("string", foreground="#66b3ff")
            self.editor.tag_configure("comment", foreground="#003366")
            self.editor.tag_configure("ai_comment", foreground="#003366")
        elif theme == "Ruby":
            self.editor.tag_configure("keyword", foreground="#ff0040")
            self.editor.tag_configure("variable", foreground="#cc0033")
            self.editor.tag_configure("string", foreground="#ff668c")
            self.editor.tag_configure("comment", foreground="#66001a")
            self.editor.tag_configure("ai_comment", foreground="#66001a")
        elif theme == "Gold":
            self.editor.tag_configure("keyword", foreground="#ffff00")
            self.editor.tag_configure("variable", foreground="#cccc00")
            self.editor.tag_configure("string", foreground="#ffff66")
            self.editor.tag_configure("comment", foreground="#666600")
            self.editor.tag_configure("ai_comment", foreground="#666600")
        elif theme == "Platinum":
            self.editor.tag_configure("keyword", foreground="#404040")
            self.editor.tag_configure("variable", foreground="#606060")
            self.editor.tag_configure("string", foreground="#202020")
            self.editor.tag_configure("comment", foreground="#a0a0a0")
            self.editor.tag_configure("ai_comment", foreground="#a0a0a0")
        elif theme == "Obsidian":
            self.editor.tag_configure("keyword", foreground="#808080")
            self.editor.tag_configure("variable", foreground="#a0a0a0")
            self.editor.tag_configure("string", foreground="#c0c0c0")
            self.editor.tag_configure("comment", foreground="#404040")
            self.editor.tag_configure("ai_comment", foreground="#404040")
        elif theme == "Ivory":
            self.editor.tag_configure("keyword", foreground="#505050")
            self.editor.tag_configure("variable", foreground="#707070")
            self.editor.tag_configure("string", foreground="#303030")
            self.editor.tag_configure("comment", foreground="#b0b0b0")
            self.editor.tag_configure("ai_comment", foreground="#b0b0b0")
        elif theme == "Coral":
            self.editor.tag_configure("keyword", foreground="#ff7f50")
            self.editor.tag_configure("variable", foreground="#cc6640")
            self.editor.tag_configure("string", foreground="#ff9f80")
            self.editor.tag_configure("comment", foreground="#663320")
            self.editor.tag_configure("ai_comment", foreground="#663320")
        elif theme == "Teal":
            self.editor.tag_configure("keyword", foreground="#008080")
            self.editor.tag_configure("variable", foreground="#006666")
            self.editor.tag_configure("string", foreground="#00b3b3")
            self.editor.tag_configure("comment", foreground="#003333")
            self.editor.tag_configure("ai_comment", foreground="#003333")
        else:
            self.editor.tag_configure("keyword", foreground="#0000FF")
            self.editor.tag_configure("variable", foreground="#FF8000")
            self.editor.tag_configure("ai_comment", foreground="#505050")

    def refresh_layout(self):
        self.line_numbers.pack_forget()
        self.editor.pack_forget()
        self.minimap.pack_forget()
        
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        if self.settings.get("minimap", True):
            self.minimap.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def run_code(self):
        self.clear_output()
        code = self.editor.get("1.0", tk.END)
        interpreter = SimpleInterpreter(self.log, self.root, self.clear_output, self)
        interpreter.execute(code)

    def add_taskbar_button(self, window, title):
        theme = self.settings["theme"]
        c = self.get_theme_colors(theme)
        
        btn = tk.Button(self.taskbar_frame, text=title, bg=c.get("btn_bg", "#e0e0e0"), fg=c.get("btn_fg", "#333333"), relief="flat", command=lambda w=window: w.lift())
        self.taskbar_buttons[window] = btn
        
        # Animation
        btn.pack(side=tk.LEFT, padx=2, pady=2, ipadx=0)
        btn.config(width=1)
        
        def animate(step=1):
            if step <= 10 and btn.winfo_exists():
                btn.config(width=step)
                self.root.after(15, lambda: animate(step + 1))
        animate()

    def remove_taskbar_button(self, window, destroy=False):
        if window in self.taskbar_buttons:
            btn = self.taskbar_buttons[window]
            
            def animate(step=10):
                if step >= 0 and btn.winfo_exists():
                    btn.config(width=step)
                    self.root.after(15, lambda: animate(step - 1))
                else:
                    if btn.winfo_exists(): btn.destroy()
                    if destroy:
                        try:
                            window.destroy()
                        except: pass
            animate()
            del self.taskbar_buttons[window]

    def update_taskbar_button_title(self, window, new_title):
        if window in self.taskbar_buttons:
            self.taskbar_buttons[window].config(text=new_title)

    def get_theme_colors(self, theme):
        return { "Light": {"bg": "#f4f4f4", "fg": "#333", "edit_bg": "white", "edit_fg": "#2c3e50", "btn_bg": "#e0e0e0", "btn_fg": "#333333"}, "Dark": {"bg": "#2d2d2d", "fg": "#d4d4d4", "edit_bg": "#1e1e1e", "edit_fg": "#d4d4d4", "btn_bg": "#3d3d3d", "btn_fg": "#d4d4d4"}, "Blue": {"bg": "#e3f2fd", "fg": "#0d47a1", "edit_bg": "#ffffff", "edit_fg": "#01579b", "btn_bg": "#bbdefb", "btn_fg": "#0d47a1"}, "Hacker": {"bg": "#0d1117", "fg": "#00ff41", "edit_bg": "#000000", "edit_fg": "#00ff41", "btn_bg": "#161b22", "btn_fg": "#00ff41"}, "Retro": {"bg": "#fdf6e3", "fg": "#657b83", "edit_bg": "#eee8d5", "edit_fg": "#586e75", "btn_bg": "#eee8d5", "btn_fg": "#657b83"}, "Night": {"bg": "#1a1b26", "fg": "#a9b1d6", "edit_bg": "#24283b", "edit_fg": "#c0caf5", "btn_bg": "#24283b", "btn_fg": "#a9b1d6"}, "Monokai": {"bg": "#272822", "fg": "#f8f8f2", "edit_bg": "#272822", "edit_fg": "#f8f8f2", "btn_bg": "#3e3d32", "btn_fg": "#f8f8f2"}, "Solarized": {"bg": "#fdf6e3", "fg": "#657b83", "edit_bg": "#fdf6e3", "edit_fg": "#657b83", "btn_bg": "#eee8d5", "btn_fg": "#657b83"}, "Oceanic": {"bg": "#e0f7fa", "fg": "#006064", "edit_bg": "#e0f2f1", "edit_fg": "#004d40", "btn_bg": "#b2ebf2", "btn_fg": "#006064"}, "Forest": {"bg": "#e8f5e9", "fg": "#1b5e20", "edit_bg": "#f1f8e9", "edit_fg": "#2e7d32", "btn_bg": "#c8e6c9", "btn_fg": "#1b5e20"}, "Sunset": {"bg": "#FFF3E0", "fg": "#5D4037", "edit_bg": "#FFFFFF", "edit_fg": "#E65100", "btn_bg": "#FFE0B2", "btn_fg": "#5D4037"}, "Dracula": {"bg": "#282A36", "fg": "#F8F8F2", "edit_bg": "#44475A", "edit_fg": "#F8F8F2", "btn_bg": "#44475A", "btn_fg": "#F8F8F2"}, "High Contrast": {"bg": "#000000", "fg": "#FFFFFF", "edit_bg": "#000000", "edit_fg": "#FFFFFF", "btn_bg": "#333333", "btn_fg": "#FFFFFF"}, "Cyberpunk": {"bg": "#050510", "fg": "#00FF99", "edit_bg": "#000000", "edit_fg": "#FF00FF", "btn_bg": "#1a1a2e", "btn_fg": "#00FF99"}, "Coffee": {"bg": "#D7CCC8", "fg": "#3E2723", "edit_bg": "#EFEBE9", "edit_fg": "#4E342E", "btn_bg": "#BCAAA4", "btn_fg": "#3E2723"}, "Matrix": {"bg": "#000000", "fg": "#00FF00", "edit_bg": "#0D0D0D", "edit_fg": "#00FF00", "btn_bg": "#003300", "btn_fg": "#00FF00"}, "Neon": {"bg": "#111111", "fg": "#FF00FF", "edit_bg": "#1A1A1A", "edit_fg": "#00FFFF", "btn_bg": "#333333", "btn_fg": "#FF00FF"}, "Pastel": {"bg": "#FFD1DC", "fg": "#555555", "edit_bg": "#E0F7FA", "edit_fg": "#555555", "btn_bg": "#FFB7B2", "btn_fg": "#555555"}, "Midnight": {"bg": "#0f0f23", "fg": "#aabbc3", "edit_bg": "#15152e", "edit_fg": "#d4d4d4", "btn_bg": "#15152e", "btn_fg": "#aabbc3"}, "Solar Flare": {"bg": "#ffecb3", "fg": "#e65100", "edit_bg": "#fff8e1", "edit_fg": "#bf360c", "btn_bg": "#ffe082", "btn_fg": "#e65100"}, "Mint": {"bg": "#E0F2F1", "fg": "#004D40", "edit_bg": "#F1F8E9", "edit_fg": "#1B5E20", "btn_bg": "#B2DFDB", "btn_fg": "#004D40"}, "Lavender": {"bg": "#F3E5F5", "fg": "#4A148C", "edit_bg": "#FFFFFF", "edit_fg": "#6A1B9A", "btn_bg": "#E1BEE7", "btn_fg": "#4A148C"}, "Crimson": {"bg": "#2b0000", "fg": "#ffcccc", "edit_bg": "#400000", "edit_fg": "#ffcccc", "btn_bg": "#550000", "btn_fg": "#ffcccc"}, "Olive": {"bg": "#F4F3E8", "fg": "#556B2F", "edit_bg": "#FFFFFF", "edit_fg": "#6B8E23", "btn_bg": "#E9E8D9", "btn_fg": "#556B2F"}, "Grape": {"bg": "#EAEAF3", "fg": "#483D8B", "edit_bg": "#FFFFFF", "edit_fg": "#6A5ACD", "btn_bg": "#DCDCF8", "btn_fg": "#483D8B"}, "Steel": {"bg": "#E6E8EB", "fg": "#4682B4", "edit_bg": "#FFFFFF", "edit_fg": "#5F9EA0", "btn_bg": "#D6D8DB", "btn_fg": "#4682B4"}, "Mocha": {"bg": "#EFEBE9", "fg": "#6D4C41", "edit_bg": "#FFFFFF", "edit_fg": "#8D6E63", "btn_bg": "#D7CCC8", "btn_fg": "#6D4C41"}, "Rose": {"bg": "#FFF0F5", "fg": "#C71585", "edit_bg": "#FFFFFF", "edit_fg": "#DB7093", "btn_bg": "#FFE4E1", "btn_fg": "#C71585"} }.get(theme, {"bg": "#f4f4f4", "fg": "#333", "edit_bg": "white", "edit_fg": "#2c3e50", "btn_bg": "#e0e0e0", "btn_fg": "#333333"})

class SimpleInterpreter:
    """
    A minimal interpreter for the new language.
    Rules:
    1. Loops use 'repeat' and 'end'.
    2. Conditionals use 'if' and 'end' (keywords < 5 letters).
    3. Syntax: var = value, show value.
    """
    def __init__(self, print_func, root, clear_func, ide_instance):
        self.variables = {}
        self.functions = {}
        self.print_func = print_func
        self.root = root
        self.clear_func = clear_func
        self.ide = ide_instance

    def execute(self, code):
        lines = code.splitlines()
        try:
            self.process_block(lines)
        except Exception as e:
            self.print_func(f"Error: {str(e)}")

    def process_block(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                i += 1
                continue

            # Rule: Some loops allowed
            if any(line.startswith(kw) for kw in ["for", "while", "loop"]):
                self.print_func("Error: Use 'repeat' for loops.")
                return

            # Command: Assignment (var = val)
            if "=" in line and not line.startswith("if"):
                parts = line.split("=", 1)
                var_name = parts[0].strip().lstrip("$")
                value = self.evaluate(parts[1].strip())
                self.variables[var_name] = value

            # Command: Output (show val)
            elif line.startswith("show "):
                content = line[5:].strip()
                self.print_func(self.evaluate(content))

            # Command: Function Definition (func name ... end)
            elif line.startswith("func "):
                func_name = line[5:].strip()
                block = []
                j = i + 1
                nested_depth = 0
                while j < len(lines):
                    curr_line = lines[j].strip()
                    if curr_line.startswith("if ") or curr_line.startswith("func ") or curr_line.startswith("repeat "):
                        nested_depth += 1
                    elif curr_line == "end":
                        if nested_depth == 0:
                            break
                        nested_depth -= 1
                    block.append(lines[j])
                    j += 1
                self.functions[func_name] = block
                i = j

            # Command: Function Call (call name)
            elif line.startswith("call "):
                func_name = line[5:].strip()
                if func_name in self.functions:
                    self.process_block(self.functions[func_name])
                else:
                    self.print_func(f"Error: Undefined function '{func_name}'")

            # Command: Input (ask "Prompt" var)
            elif line.startswith("ask "):
                match = re.match(r'ask\s+"(.+?)"\s+(\w+)', line)
                if match:
                    prompt, var_name = match.groups()
                    val = simpledialog.askstring("Input", prompt, parent=self.root)
                    self.variables[var_name] = val if val else ""

            # Command: Random (rand min max var)
            elif line.startswith("rand "):
                parts = line.split()
                if len(parts) == 4:
                    try:
                        min_val = int(self.evaluate(parts[1]))
                        max_val = int(self.evaluate(parts[2]))
                        var_name = parts[3]
                        self.variables[var_name] = random.randint(min_val, max_val)
                    except Exception as e:
                        self.print_func(f"Error in rand: {e}")

            # Command: Window (window var)
            elif line.startswith("window "):
                var_name = line[7:].strip()
                win = tk.Toplevel(self.root)
                win.title("New Window")
                self.variables[var_name] = win
                self.ide.add_taskbar_button(win, "New Window")
                win.protocol("WM_DELETE_WINDOW", lambda w=win: self.ide.remove_taskbar_button(w, destroy=True))
                win.bind("<Control-Tab>", lambda e, w=win: self.ide.remove_taskbar_button(w, destroy=True))

            # Command: Title (title var "Text")
            elif line.startswith("title "):
                match = re.match(r'title\s+(\w+)\s+(.+)', line)
                if match:
                    var_name, content = match.groups()
                    if var_name in self.variables and isinstance(self.variables[var_name], (tk.Tk, tk.Toplevel)):
                        win = self.variables[var_name]
                        title_text = str(self.evaluate(content))
                        win.title(title_text)
                        self.ide.update_taskbar_button_title(win, title_text)

            # Command: Size (size var w h)
            elif line.startswith("size "):
                match = re.match(r'size\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    var_name = match.group(1)
                    w = self.evaluate(match.group(2))
                    h = self.evaluate(match.group(3))
                    if var_name in self.variables and isinstance(self.variables[var_name], (tk.Tk, tk.Toplevel)):
                        self.variables[var_name].geometry(f"{w}x{h}")

            # Command: Text (text var "Content" x y)
            elif line.startswith("text "):
                match = re.search(r'text\s+(\w+)\s+(.+)\s+(\S+)\s+(\S+)$', line)
                if match:
                    var_name, content, x_expr, y_expr = match.groups()
                    if var_name in self.variables and isinstance(self.variables[var_name], (tk.Tk, tk.Toplevel)):
                        win = self.variables[var_name]
                        try:
                            val = self.evaluate(content)
                            x = int(self.evaluate(x_expr))
                            y = int(self.evaluate(y_expr))
                            tk.Label(win, text=str(val), font=("Segoe UI", 10)).place(x=x, y=y)
                        except Exception as e:
                            self.print_func(f"Error placing text: {e}")

            # Command: Color (color var "Hex")
            elif line.startswith("color "):
                match = re.match(r'color\s+(\w+)\s+(.+)', line)
                if match:
                    var_name, content = match.groups()
                    if var_name in self.variables and isinstance(self.variables[var_name], (tk.Tk, tk.Toplevel)):
                        val = self.evaluate(content)
                        try:
                            self.variables[var_name].configure(bg=str(val))
                        except:
                            self.print_func(f"Error: Invalid color '{val}'")

            # Command: Close (close var)
            elif line.startswith("close "):
                var_name = line[6:].strip()
                if var_name in self.variables and isinstance(self.variables[var_name], (tk.Tk, tk.Toplevel)):
                    win_to_close = self.variables[var_name]
                    self.ide.remove_taskbar_button(win_to_close, destroy=True)
                    del self.variables[var_name]

            # Command: Popup (popup "Message")
            elif line.startswith("popup "):
                content = line[6:].strip()
                messagebox.showinfo("Popup", str(self.evaluate(content)), parent=self.root)

            # Command: Write (write "file" "content")
            elif line.startswith("write "):
                match = re.match(r'write\s+(".*?"|\S+)\s+(.+)', line)
                if match:
                    fname_expr, content_expr = match.groups()
                    fname = str(self.evaluate(fname_expr))
                    content = str(self.evaluate(content_expr))
                    try:
                        with open(fname, "w") as f:
                            f.write(content)
                    except Exception as e:
                        self.print_func(f"Error writing file: {e}")

            # Command: Read (read var "file")
            elif line.startswith("read "):
                match = re.match(r'read\s+(\w+)\s+(".*?"|\S+)', line)
                if match:
                    var_name, fname_expr = match.groups()
                    fname = str(self.evaluate(fname_expr))
                    try:
                        with open(fname, "r") as f:
                            self.variables[var_name] = f.read()
                    except Exception as e:
                        self.print_func(f"Error reading file: {e}")

            # Command: Append (append "file" "content")
            elif line.startswith("append "):
                match = re.match(r'append\s+(".*?"|\S+)\s+(.+)', line)
                if match:
                    fname_expr, content_expr = match.groups()
                    fname = str(self.evaluate(fname_expr))
                    content = str(self.evaluate(content_expr))
                    try:
                        with open(fname, "a") as f:
                            f.write(content)
                    except Exception as e:
                        self.print_func(f"Error appending file: {e}")

            # Command: Math (math var op val)
            elif line.startswith("math "):
                match = re.match(r'math\s+(\w+)\s+(\w+)\s+(.+)', line)
                if match:
                    var_name = match.group(1)
                    op = match.group(2)
                    val = float(self.evaluate(match.group(3)))
                    try:
                        if op == "sqrt": self.variables[var_name] = math.sqrt(val)
                        elif op == "sin": self.variables[var_name] = math.sin(val)
                        elif op == "cos": self.variables[var_name] = math.cos(val)
                        elif op == "tan": self.variables[var_name] = math.tan(val)
                        elif op == "floor": self.variables[var_name] = math.floor(val)
                        elif op == "ceil": self.variables[var_name] = math.ceil(val)
                        elif op == "abs": self.variables[var_name] = abs(val)
                    except Exception as e:
                        self.print_func(f"Math error: {e}")

            # Command: Length (len var source)
            elif line.startswith("len "):
                match = re.match(r'len\s+(\w+)\s+(.+)', line)
                if match:
                    var_name = match.group(1)
                    source = self.evaluate(match.group(2))
                    if hasattr(source, "__len__"):
                        self.variables[var_name] = len(source)
                    else:
                        self.variables[var_name] = 0

            # Command: Time (time var)
            elif line.startswith("time "):
                var_name = line[5:].strip()
                self.variables[var_name] = time.strftime("%H:%M:%S")

            # Command: Upper (upper var source)
            elif line.startswith("upper "):
                match = re.match(r'upper\s+(\w+)\s+(.+)', line)
                if match:
                    var_name = match.group(1)
                    source = str(self.evaluate(match.group(2)))
                    self.variables[var_name] = source.upper()

            # Command: Lower (lower var source)
            elif line.startswith("lower "):
                match = re.match(r'lower\s+(\w+)\s+(.+)', line)
                if match:
                    var_name = match.group(1)
                    source = str(self.evaluate(match.group(2)))
                    self.variables[var_name] = source.lower()

            # Command: Replace (replace var source old new)
            elif line.startswith("replace "):
                # replace var "source" "old" "new"
                # Use regex to capture arguments safely
                match = re.match(r'replace\s+(\w+)\s+(".*?"|\S+)\s+(".*?"|\S+)\s+(".*?"|\S+)', line)
                if match:
                    self.variables[match.group(1)] = str(self.evaluate(match.group(2))).replace(str(self.evaluate(match.group(3))), str(self.evaluate(match.group(4))))

            # Command: Split (split var source delim)
            elif line.startswith("split "):
                match = re.match(r'split\s+(\w+)\s+(".*?"|\S+)\s+(".*?"|\S+)', line)
                if match:
                    self.variables[match.group(1)] = str(self.evaluate(match.group(2))).split(str(self.evaluate(match.group(3))))

            # Command: Round (round var val)
            elif line.startswith("round "):
                match = re.match(r'round\s+(\w+)\s+(.+)', line)
                if match:
                    try:
                        self.variables[match.group(1)] = round(float(self.evaluate(match.group(2))))
                    except Exception as e:
                        self.print_func(f"Error in round: {e}")

            # Command: Min/Max (min var v1 v2)
            elif line.startswith("min "):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        self.variables[parts[1]] = min(self.evaluate(parts[2]), self.evaluate(parts[3]))
                    except Exception as e:
                        self.print_func(f"Error in min: {e}")
            elif line.startswith("max "):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        self.variables[parts[1]] = max(self.evaluate(parts[2]), self.evaluate(parts[3]))
                    except Exception as e:
                        self.print_func(f"Error in max: {e}")

            # Command: Date (date var)
            elif line.startswith("date "):
                self.variables[line[5:].strip()] = time.strftime("%Y-%m-%d")

            # Command: Exists (exists var file)
            elif line.startswith("exists "):
                parts = line.split()
                if len(parts) >= 3:
                    self.variables[parts[1]] = 1 if os.path.exists(str(self.evaluate(parts[2]))) else 0

            # Command: Delete (delete file)
            elif line.startswith("delete "):
                fname = str(self.evaluate(line[7:].strip()))
                if os.path.exists(fname): os.remove(fname)

            # Command: Reverse (reverse var source)
            elif line.startswith("reverse "):
                match = re.match(r'reverse\s+(\w+)\s+(.+)', line)
                if match:
                    try:
                        val = self.evaluate(match.group(2))
                        self.variables[match.group(1)] = val[::-1]
                    except Exception as e:
                        self.print_func(f"Error in reverse: {e}")

            # Command: Sort (sort var source)
            elif line.startswith("sort "):
                match = re.match(r'sort\s+(\w+)\s+(.+)', line)
                if match:
                    try:
                        val = self.evaluate(match.group(2))
                        if isinstance(val, list):
                            self.variables[match.group(1)] = sorted(val)
                        else:
                            self.variables[match.group(1)] = "".join(sorted(str(val)))
                    except Exception as e:
                        self.print_func(f"Error in sort: {e}")

            # Command: Find (find var source target)
            elif line.startswith("find "):
                parts = line.split()
                if len(parts) >= 4:
                    src = str(self.evaluate(parts[2]))
                    tgt = str(self.evaluate(parts[3]))
                    self.variables[parts[1]] = src.find(tgt)

            # Command: Substring (sub var source start end)
            elif line.startswith("sub "):
                parts = line.split()
                if len(parts) >= 5:
                    src = str(self.evaluate(parts[2]))
                    s = int(self.evaluate(parts[3]))
                    e = int(self.evaluate(parts[4]))
                    self.variables[parts[1]] = src[s:e]

            # Command: Mkdir (mkdir "folder")
            elif line.startswith("mkdir "):
                try:
                    os.makedirs(str(self.evaluate(line[6:].strip())), exist_ok=True)
                except Exception as e:
                    self.print_func(f"Error creating directory: {e}")

            # Command: Rmdir (rmdir "folder")
            elif line.startswith("rmdir "):
                try:
                    os.rmdir(str(self.evaluate(line[6:].strip())))
                except Exception as e:
                    self.print_func(f"Error removing directory: {e}")

            # Command: Trim (trim var source)
            elif line.startswith("trim "):
                parts = line.split()
                if len(parts) >= 3:
                    self.variables[parts[1]] = str(self.evaluate(parts[2])).strip()

            # Command: Join (join var s1 s2)
            elif line.startswith("join "):
                parts = line.split()
                if len(parts) >= 4:
                    self.variables[parts[1]] = str(self.evaluate(parts[2])) + str(self.evaluate(parts[3]))

            # Command: Type (type var val)
            elif line.startswith("type "):
                parts = line.split()
                if len(parts) >= 3:
                    self.variables[parts[1]] = type(self.evaluate(parts[2])).__name__

            # Command: Pow (pow var base exp)
            elif line.startswith("pow "):
                parts = line.split()
                if len(parts) >= 4:
                    self.variables[parts[1]] = math.pow(float(self.evaluate(parts[2])), float(self.evaluate(parts[3])))

            # Command: Mod (mod var a b)
            elif line.startswith("mod "):
                parts = line.split()
                if len(parts) >= 4:
                    self.variables[parts[1]] = self.evaluate(parts[2]) % self.evaluate(parts[3])

            # Command: Inc (inc var)
            elif line.startswith("inc "):
                var = line[4:].strip()
                if var in self.variables:
                    self.variables[var] = self.evaluate(self.variables[var]) + 1

            # Command: Dec (dec var)
            elif line.startswith("dec "):
                var = line[4:].strip()
                if var in self.variables:
                    self.variables[var] = self.evaluate(self.variables[var]) - 1

            # Command: Copy (copy src dst)
            elif line.startswith("copy "):
                parts = line.split()
                if len(parts) >= 3:
                    shutil.copy(str(self.evaluate(parts[1])), str(self.evaluate(parts[2])))

            # Command: Move (move src dst)
            elif line.startswith("move "):
                parts = line.split()
                if len(parts) >= 3:
                    shutil.move(str(self.evaluate(parts[1])), str(self.evaluate(parts[2])))

            # Command: Cwd (cwd var)
            elif line.startswith("cwd "):
                self.variables[line[4:].strip()] = os.getcwd()

            # Command: List (list var path)
            elif line.startswith("list "):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        self.variables[parts[1]] = os.listdir(str(self.evaluate(parts[2])))
                    except:
                        self.variables[parts[1]] = []

            # Command: Abs (abs var val)
            elif line.startswith("abs "):
                parts = line.split()
                if len(parts) >= 3:
                    self.variables[parts[1]] = abs(self.evaluate(parts[2]))

            # Command: Floor (floor var val)
            elif line.startswith("floor "):
                parts = line.split()
                if len(parts) >= 3:
                    self.variables[parts[1]] = math.floor(float(self.evaluate(parts[2])))

            # Command: Icon (icon var "path")
            elif line.startswith("icon "):
                match = re.match(r'icon\s+(\w+)\s+(.+)', line)
                if match:
                    var, path_expr = match.groups()
                    if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                        try: self.variables[var].iconbitmap(self.evaluate(path_expr))
                        except: self.print_func("Error: Invalid icon file.")

            # Command: Topmost (topmost var 1/0)
            elif line.startswith("topmost "):
                match = re.match(r'topmost\s+(\w+)\s+(.+)', line)
                if match:
                    var, val_expr = match.groups()
                    if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                        self.variables[var].attributes("-topmost", int(self.evaluate(val_expr)))

            # Command: Center (center var)
            elif line.startswith("center "):
                var = line[7:].strip()
                if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                    win = self.variables[var]
                    win.update_idletasks()
                    w, h = win.winfo_width(), win.winfo_height()
                    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
                    x, y = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
                    win.geometry(f'{w}x{h}+{x}+{y}')

            # Command: GetSize (getsize var "path")
            elif line.startswith("getsize "):
                match = re.match(r'getsize\s+(\w+)\s+(.+)', line)
                if match:
                    var, path_expr = match.groups()
                    try: self.variables[var] = os.path.getsize(str(self.evaluate(path_expr)))
                    except: self.print_func("Error: File not found for getsize.")

            # Command: CopyFile (copyfile src dst)
            elif line.startswith("copyfile "):
                match = re.match(r'copyfile\s+(.+?)\s+(.+)', line)
                if match:
                    shutil.copyfile(str(self.evaluate(match.group(1))), str(self.evaluate(match.group(2))))

            # Command: Opacity (opacity var 0.8)
            elif line.startswith("opacity "):
                match = re.match(r'opacity\s+(\w+)\s+(.+)', line)
                if match:
                    var, val_expr = match.groups()
                    if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                        self.variables[var].attributes("-alpha", float(self.evaluate(val_expr)))

            # Command: Resizable (resizable var 0 1)
            elif line.startswith("resizable "):
                match = re.match(r'resizable\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    var, w_expr, h_expr = match.groups()
                    if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                        self.variables[var].resizable(bool(int(self.evaluate(w_expr))), bool(int(self.evaluate(h_expr))))

            # Command: Fullscreen (fullscreen var 1)
            elif line.startswith("fullscreen "):
                match = re.match(r'fullscreen\s+(\w+)\s+(.+)', line)
                if match:
                    var, val_expr = match.groups()
                    if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                        if bool(int(self.evaluate(val_expr))):
                            try: self.variables[var].state('zoomed')
                            except: self.variables[var].attributes("-fullscreen", True)
                        else:
                            try: self.variables[var].state('normal')
                            except: pass
                            self.variables[var].attributes("-fullscreen", False)

            # Command: Get Position (getpos var x_var y_var)
            elif line.startswith("getpos "):
                match = re.match(r'getpos\s+(\w+)\s+(\w+)\s+(\w+)', line)
                if match:
                    win_var, x_var, y_var = match.groups()
                    if win_var in self.variables and isinstance(self.variables[win_var], (tk.Tk, tk.Toplevel)):
                        win = self.variables[win_var]
                        self.variables[x_var] = win.winfo_x()
                        self.variables[y_var] = win.winfo_y()

            # Command: ClipSet (clipset "text")
            elif line.startswith("clipset "):
                val = self.evaluate(line[8:].strip())
                self.root.clipboard_clear()
                self.root.clipboard_append(str(val))
                self.root.update()

            # Command: ClipGet (clipget var)
            elif line.startswith("clipget "):
                var = line[8:].strip()
                try: self.variables[var] = self.root.clipboard_get()
                except: self.variables[var] = ""

            # Command: Screen (screen w h)
            elif line.startswith("screen "):
                match = re.match(r'screen\s+(\w+)\s+(\w+)', line)
                if match:
                    w_var, h_var = match.groups()
                    self.variables[w_var] = self.root.winfo_screenwidth()
                    self.variables[h_var] = self.root.winfo_screenheight()

            # Command: Mouse (mouse x y)
            elif line.startswith("mouse "):
                match = re.match(r'mouse\s+(\w+)\s+(\w+)', line)
                if match:
                    x_var, y_var = match.groups()
                    self.variables[x_var] = self.root.winfo_pointerx()
                    self.variables[y_var] = self.root.winfo_pointery()

            # Command: Username (username var)
            elif line.startswith("username "):
                var = line[9:].strip()
                try: self.variables[var] = os.getlogin()
                except: self.variables[var] = "User"

            # Command: Browser (browser "url")
            elif line.startswith("browser "):
                webbrowser.open(str(self.evaluate(line[8:].strip())))

            # Command: Minimize (minimize var)
            elif line.startswith("minimize "):
                var = line[9:].strip()
                if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                    self.variables[var].iconify()

            # Command: Restore (restore var)
            elif line.startswith("restore "):
                var = line[8:].strip()
                if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                    self.variables[var].deiconify()

            # Command: Focus (focus var)
            elif line.startswith("focus "):
                var = line[6:].strip()
                if var in self.variables and isinstance(self.variables[var], (tk.Tk, tk.Toplevel)):
                    self.variables[var].lift()

            # Command: FileTime (filetime var "path")
            elif line.startswith("filetime "):
                match = re.match(r'filetime\s+(\w+)\s+(.+)', line)
                if match:
                    try: self.variables[match.group(1)] = os.path.getmtime(str(self.evaluate(match.group(2))))
                    except: self.variables[match.group(1)] = 0

            # Command: IsDir/IsFile
            elif line.startswith("isdir "):
                match = re.match(r'isdir\s+(\w+)\s+(.+)', line)
                if match: self.variables[match.group(1)] = 1 if os.path.isdir(str(self.evaluate(match.group(2)))) else 0
            elif line.startswith("isfile "):
                match = re.match(r'isfile\s+(\w+)\s+(.+)', line)
                if match: self.variables[match.group(1)] = 1 if os.path.isfile(str(self.evaluate(match.group(2)))) else 0

            # Constants
            elif line.startswith("pi "): self.variables[line[3:].strip()] = math.pi
            elif line.startswith("e "): self.variables[line[2:].strip()] = math.e
            elif line.startswith("rgb "):
                match = re.match(r'rgb\s+(\w+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
                if match: self.variables[match.group(1)] = f"#{int(match.group(2)):02x}{int(match.group(3)):02x}{int(match.group(4)):02x}"

            # Command: Platform (platform var)
            elif line.startswith("platform "):
                self.variables[line[9:].strip()] = platform.system()

            # Command: Env (env var "KEY")
            elif line.startswith("env "):
                match = re.match(r'env\s+(\w+)\s+(.+)', line)
                if match:
                    self.variables[match.group(1)] = os.environ.get(str(self.evaluate(match.group(2))), "")

            # Command: Exec (exec "cmd")
            elif line.startswith("exec "):
                os.system(str(self.evaluate(line[5:].strip())))

            # Command: Hash (hash var "text")
            elif line.startswith("hash "):
                match = re.match(r'hash\s+(\w+)\s+(.+)', line)
                if match: self.variables[match.group(1)] = abs(hash(str(self.evaluate(match.group(2)))))

            # Command: Warp (warp x y)
            elif line.startswith("warp "):
                parts = line.split()
                if len(parts) >= 3: self.root.warp_pointer(int(self.evaluate(parts[1])), int(self.evaluate(parts[2])))

            # Command: Starts (starts var str prefix)
            elif line.startswith("starts "):
                match = re.match(r'starts\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    self.variables[match.group(1)] = 1 if str(self.evaluate(match.group(2))).startswith(str(self.evaluate(match.group(3)))) else 0

            # Command: Ends (ends var str suffix)
            elif line.startswith("ends "):
                match = re.match(r'ends\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    self.variables[match.group(1)] = 1 if str(self.evaluate(match.group(2))).endswith(str(self.evaluate(match.group(3)))) else 0

            # Command: Contains (contains var haystack needle)
            elif line.startswith("contains "):
                match = re.match(r'contains\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    self.variables[match.group(1)] = 1 if str(self.evaluate(match.group(3))) in str(self.evaluate(match.group(2))) else 0

            # Command: Index (index var haystack needle)
            elif line.startswith("index "):
                match = re.match(r'index\s+(\w+)\s+(.+)\s+(.+)', line)
                if match:
                    self.variables[match.group(1)] = str(self.evaluate(match.group(2))).find(str(self.evaluate(match.group(3))))

            # Command: Speak (speak "text")
            elif line.startswith("speak "):
                text = str(self.evaluate(line[6:].strip()))
                self.print_func(f"🗣 {text}")

            # Command: Notify (notify "Title" "Message")
            elif line.startswith("notify "):
                match = re.match(r'notify\s+(.+?)\s+(.+)', line)
                if match:
                    title = str(self.evaluate(match.group(1)))
                    msg = str(self.evaluate(match.group(2)))
                    t = tk.Toplevel(self.root)
                    t.overrideredirect(True)
                    t.geometry(f"300x80+{self.root.winfo_screenwidth()-320}+{self.root.winfo_screenheight()-100}")
                    t.configure(bg="#333")
                    tk.Label(t, text=title, fg="white", bg="#333", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(5,0))
                    tk.Label(t, text=msg, fg="#ddd", bg="#333", font=("Segoe UI", 9)).pack(anchor="w", padx=10)
                    t.after(3000, t.destroy)

            # Command: Beep
            elif line == "beep":
                self.root.bell()

            # Command: Wait (wait seconds)
            elif line.startswith("wait "):
                try:
                    sec = float(self.evaluate(line[5:].strip()))
                    end_time = time.time() + sec
                    while time.time() < end_time:
                        try:
                            self.root.update()
                        except:
                            return # Stop if window closed
                        time.sleep(0.01)
                except:
                    self.print_func("Error: Invalid wait time")

            # Command: Sleep (sleep ms)
            elif line.startswith("sleep "):
                try:
                    ms = float(self.evaluate(line[6:].strip()))
                    end_time = time.time() + (ms / 1000.0)
                    while time.time() < end_time:
                        try:
                            self.root.update()
                        except:
                            return
                        time.sleep(0.01)
                except: self.print_func("Error: Invalid sleep time")

            # Command: Repeat (repeat n ... end)
            elif line.startswith("repeat "):
                try:
                    count = int(self.evaluate(line[7:].strip()))
                    block = []
                    j = i + 1
                    nested_depth = 0
                    while j < len(lines):
                        curr_line = lines[j].strip()
                        if curr_line.startswith("if ") or curr_line.startswith("func ") or curr_line.startswith("repeat "):
                            nested_depth += 1
                        elif curr_line == "end":
                            if nested_depth == 0:
                                break
                            nested_depth -= 1
                        block.append(lines[j])
                        j += 1
                    
                    for _ in range(count):
                        self.process_block(block)
                    
                    i = j
                except Exception as e:
                    self.print_func(f"Error in repeat loop: {e}")

            # Command: Clear Output
            elif line == "clear":
                self.clear_func()

            # Command: Array (array name v1 v2 ...)
            elif line.startswith("array "):
                match = re.match(r'array\s+(\w+)\s+(.+)', line)
                if match:
                    name = match.group(1)
                    args = re.findall(r'(?:".*?"|\S+)', match.group(2))
                    self.variables[name] = [self.evaluate(x) for x in args]

            # Command: Conditional (if condition ... end)
            elif line.startswith("if "):
                condition = line[3:].strip()
                
                # Extract the block of code inside the if statement
                block = []
                j = i + 1
                nested_depth = 0
                
                while j < len(lines):
                    curr_line = lines[j].strip()
                    if curr_line.startswith("if ") or curr_line.startswith("func ") or curr_line.startswith("repeat "):
                        nested_depth += 1
                    elif curr_line == "end":
                        if nested_depth == 0:
                            break
                        nested_depth -= 1
                    block.append(lines[j])
                    j += 1
                
                # Execute block if condition is true
                if self.check_condition(condition):
                    self.process_block(block)
                
                # Move pointer past the 'end' keyword
                i = j 

            i += 1

    def evaluate(self, expr):
        """Evaluates numbers, strings, or variables."""
        expr = str(expr).strip()
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        # Basic Math (Left-associative)
        # Level 1: +, - (Split on last occurrence)
        balance = 0
        quote = False
        for i in range(len(expr) - 1, -1, -1):
            char = expr[i]
            if char == '"': quote = not quote
            if quote: continue
            if char == ')': balance += 1
            if char == '(': balance -= 1
            if balance == 0 and char in ['+', '-']:
                l = self.evaluate(expr[:i])
                r = self.evaluate(expr[i+1:])
                try:
                    if char == '+': return l + r
                    if char == '-': return l - r
                except: pass

        # Level 2: *, /
        for i in range(len(expr) - 1, -1, -1):
            char = expr[i]
            if char == '"': quote = not quote
            if quote: continue
            if char == ')': balance += 1
            if char == '(': balance -= 1
            if balance == 0 and char in ['*', '/']:
                l = self.evaluate(expr[:i])
                r = self.evaluate(expr[i+1:])
                try:
                    if char == '*': return l * r
                    if char == '/': return l / r
                except: pass

        # Number literal
        try:
            f = float(expr)
            if f.is_integer(): return int(f)
            return f
        except: pass

        # Variable lookup
        if expr.startswith("$") and expr[1:] in self.variables:
            val = self.variables[expr[1:]]
            if isinstance(val, str):
                try:
                    f = float(val)
                    if f.is_integer(): return int(f)
                    return f
                except: pass
            return val
        
        # Array Indexing $var[i]
        if expr.startswith("$") and "[" in expr and expr.endswith("]"):
            try:
                var_part, idx_part = expr[:-1].split("[")
                var_name = var_part[1:]
                if var_name in self.variables and isinstance(self.variables[var_name], list):
                    idx = int(self.evaluate(idx_part))
                    return self.variables[var_name][idx]
            except: pass
            
        return expr

    def check_condition(self, condition):
        """Parses simple conditions like 'x > 10'."""
        match = re.match(r'(.+?)\s*(>=|<=|==|!=|>|<)\s*(.+)', condition)
        if match:
            left, op, right = match.groups()
            l_val = self.evaluate(left)
            r_val = self.evaluate(right)
            
            try:
                if op == ">": return l_val > r_val
                if op == "<": return l_val < r_val
                if op == "==": return l_val == r_val
                if op == "!=": return l_val != r_val
                if op == ">=": return l_val >= r_val
                if op == "<=": return l_val <= r_val
            except TypeError:
                return False # Mismatched types (e.g. string > int)
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleIDE(root)
    root.mainloop()
