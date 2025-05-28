# Purpose : To copy file from source directory to target directory
#           As requested by K. Wuttipan 
# Note	  : Use "auto-py-to-exe" to compile to .exe file under Python 3.7.9
#					  ( Python 3.7.9 is compatible with Windows7 )
# Date : 21 May 2025
# By   : ChatGPT 
# Prompter : Mana M.

import os
import shutil
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import sys
from datetime import datetime

CONFIG_FILE = 'ckdmove.cfg'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        messagebox.showerror("Config Error", f"Configuration file '{CONFIG_FILE}' not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        source = config['source']['path']
        target = config['target']['path']
        interval = int(config['settings']['interval'])
        max_rows = int(config['settings'].get('max_rows', 100))

        if not os.path.isdir(source):
            raise ValueError(f"Source path does not exist: {source}")
        if not os.path.isdir(target):
            raise ValueError(f"Target path does not exist: {target}")
    except Exception as e:
        messagebox.showerror("Config Error", f"Invalid configuration: {e}")
        sys.exit(1)

    return source, target, interval, max_rows

class FileMoverApp:

    def __init__(self, root, source_dir, target_dir, interval, max_rows):
        self.root = root
        self.root.title("File Mover GUI V0.3")

        self.source_dir = source_dir
        self.target_dir = target_dir
        self.interval = interval
        self.max_rows = max_rows

        self.is_running = False
        self.thread = None
        self.last_status_text = "Waiting to move..."

        # Buttons
        self.start_button = ttk.Button(root, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        # Frame for table + scrollbar
        table_frame = ttk.Frame(root)
        table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=('Datetime', 'Filename', 'Status'),
            show='headings',
            yscrollcommand=tree_scroll.set
        )
        self.tree.heading('Datetime', text='Datetime')
        self.tree.heading('Filename', text='Filename')
        self.tree.heading('Status', text='Status')
        self.tree.column('Datetime', width=160, anchor='center')
        self.tree.column('Filename', width=300, anchor='w')
        self.tree.column('Status', width=150, anchor='center')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll.config(command=self.tree.yview)

        # Success/Fail label
        self.status_label = ttk.Label(root, text="Waiting to move...")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(5, 10))

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.move_files_loop, daemon=True)
            self.thread.start()
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

    def stop(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def move_files_loop(self):
        while self.is_running:
            self.move_files()
            time.sleep(self.interval)

    def move_files(self):
        success_count = 0
        fail_count = 0
        file_checked = False

        for filename in os.listdir(self.source_dir):
            src_path = os.path.join(self.source_dir, filename)
            dst_path = os.path.join(self.target_dir, filename)

            if not os.path.isfile(src_path):
                continue

            file_checked = True        
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                with open(src_path, 'rb'):
                    pass
                shutil.move(src_path, dst_path)
                status = "Moved"
                success_count += 1
            except Exception as e:
                status = f"Not Moved ({str(e)})"
                fail_count += 1

            self.root.after(0, lambda t=timestamp, f=filename, s=status: self.add_to_table(t, f, s))

        # Update the status label with success/fail count
        if file_checked:
            self.last_status_text = f"Last run - Success: {success_count}, Failed: {fail_count}"
        self.root.after(0, lambda: self.status_label.config(text=self.last_status_text))

    def add_to_table(self, timestamp, filename, status):
        if len(self.tree.get_children()) >= self.max_rows:
            oldest = self.tree.get_children()[0]
            self.tree.delete(oldest)
        self.tree.insert('', tk.END, values=(timestamp, filename, status))


if __name__ == "__main__":
    # Pre-GUI config check
    root = tk.Tk()
    root.withdraw()  # Hide main window during config check
    source_dir, target_dir, interval, max_rows = load_config()
    root.deiconify()  # Show main window again

    root.resizable(False, False)  
    
		# Start the GUI with valid config
    app = FileMoverApp(root, source_dir, target_dir, interval, max_rows)
    root.mainloop()