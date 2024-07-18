
#### Work in Progress ##
## Gives  errors.. please pull and debug###
## might delete files or crash###
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import sync

# Make sure sync.py is in the same directory

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Directory Synchronizer")

        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.verbose = tk.BooleanVar()
        self.purge = tk.BooleanVar()
        self.forcecopy = tk.BooleanVar()
        self.use_ctime = tk.BooleanVar()
        self.use_content = tk.BooleanVar()
        self.twoway_sync = tk.BooleanVar()
        self.hash_verify = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Source Directory:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.source_dir).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_source).grid(row=0, column=2)

        tk.Label(self.root, text="Destination Directory:").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.dest_dir).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_dest).grid(row=1, column=2)

        tk.Checkbutton(self.root, text="Verbose", variable=self.verbose).grid(row=2, column=0, sticky=tk.W)
        tk.Checkbutton(self.root, text="Purge", variable=self.purge).grid(row=2, column=1, sticky=tk.W)
        tk.Checkbutton(self.root, text="Force Copy", variable=self.forcecopy).grid(row=3, column=0, sticky=tk.W)
        tk.Checkbutton(self.root, text="Use Creation Time", variable=self.use_ctime).grid(row=3, column=1, sticky=tk.W)
        tk.Checkbutton(self.root, text="Use Content", variable=self.use_content).grid(row=4, column=0, sticky=tk.W)
        tk.Checkbutton(self.root, text="Two-way Sync", variable=self.twoway_sync).grid(row=4, column=1, sticky=tk.W)
        tk.Checkbutton(self.root, text="Hash Verify", variable=self.hash_verify).grid(row=5, column=0, sticky=tk.W)

        tk.Button(self.root, text="Sync", command=self.sync_directories).grid(row=6, column=0, columnspan=3, pady=10)

    def browse_source(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir.set(directory)

    def browse_dest(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dest_dir.set(directory)

    def sync_directories(self):
        source = self.source_dir.get()
        destination = self.dest_dir.get()
        
        if not source or not destination:
            messagebox.showerror("Error", "Please select both source and destination directories.")
            return
        
        options = {
            "verbose": self.verbose.get(),
            "purge": self.purge.get(),
            "forcecopy": self.forcecopy.get(),
            "use_ctime": self.use_ctime.get(),
            "use_content": self.use_content.get(),
            "two_way_sync": self.twoway_sync.get(),
            "hash_verify": self.hash_verify.get()
        }
        
        try:
            sync.synchronize_directories(source, destination, **options)
            messagebox.showinfo("Success", "Directories synchronized successfully.")
        except Exception as e:
            messagebox.showerror("Error", f" {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()
