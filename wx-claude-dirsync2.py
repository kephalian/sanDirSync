#Debugged with Claude AI Engine
#
import os
import filecmp
import shutil
import hashlib
import wx
import threading

class SyncFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Directory Synchronizer')
        panel = wx.Panel(self)
        
        self.source_label = wx.StaticText(panel, label="Source Directory:")
        self.source_input = wx.TextCtrl(panel)
        self.source_button = wx.Button(panel, label="Browse...")
        
        self.dest_label = wx.StaticText(panel, label="Destination Directory:")
        self.dest_input = wx.TextCtrl(panel)
        self.dest_button = wx.Button(panel, label="Browse...")
        
        self.verbose_check = wx.CheckBox(panel, label="Verbose")
        self.purge_check = wx.CheckBox(panel, label="Purge")
        self.forcecopy_check = wx.CheckBox(panel, label="Force Copy")
        self.use_content_check = wx.CheckBox(panel, label="Use Content")
        self.two_way_check = wx.CheckBox(panel, label="Two-Way Sync")
        self.hverify_check = wx.CheckBox(panel, label="Hash Verify")
        
        self.sync_button = wx.Button(panel, label="Synchronize")
        
        self.progress_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        # Sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        source_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dest_sizer = wx.BoxSizer(wx.HORIZONTAL)
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        source_sizer.Add(self.source_label, 0, wx.ALL, 5)
        source_sizer.Add(self.source_input, 1, wx.ALL | wx.EXPAND, 5)
        source_sizer.Add(self.source_button, 0, wx.ALL, 5)
        
        dest_sizer.Add(self.dest_label, 0, wx.ALL, 5)
        dest_sizer.Add(self.dest_input, 1, wx.ALL | wx.EXPAND, 5)
        dest_sizer.Add(self.dest_button, 0, wx.ALL, 5)
        
        options_sizer.Add(self.verbose_check, 0, wx.ALL, 5)
        options_sizer.Add(self.purge_check, 0, wx.ALL, 5)
        options_sizer.Add(self.forcecopy_check, 0, wx.ALL, 5)
        options_sizer.Add(self.use_content_check, 0, wx.ALL, 5)
        options_sizer.Add(self.two_way_check, 0, wx.ALL, 5)
        options_sizer.Add(self.hverify_check, 0, wx.ALL, 5)
        
        main_sizer.Add(source_sizer, 0, wx.EXPAND)
        main_sizer.Add(dest_sizer, 0, wx.EXPAND)
        main_sizer.Add(options_sizer, 0, wx.EXPAND)
        main_sizer.Add(self.sync_button, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(self.progress_text, 1, wx.ALL | wx.EXPAND, 5)
        
        panel.SetSizer(main_sizer)
        
        # Bind events
        self.source_button.Bind(wx.EVT_BUTTON, self.on_browse_source)
        self.dest_button.Bind(wx.EVT_BUTTON, self.on_browse_dest)
        self.sync_button.Bind(wx.EVT_BUTTON, self.on_sync)
        
        self.Show()
    
    def on_browse_source(self, event):
        self.browse_directory(self.source_input)
    
    def on_browse_dest(self, event):
        self.browse_directory(self.dest_input)
    
    def browse_directory(self, text_ctrl):
        dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            text_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy()
    
    def on_sync(self, event):
        source = self.source_input.GetValue()
        dest = self.dest_input.GetValue()
        verbose = self.verbose_check.GetValue()
        purge = self.purge_check.GetValue()
        forcecopy = self.forcecopy_check.GetValue()
        use_content = self.use_content_check.GetValue()
        two_way = self.two_way_check.GetValue()
        hverify = self.hverify_check.GetValue()
        
        if not source or not dest:
            wx.MessageBox("Please select both source and destination directories.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        self.progress_text.Clear()
        self.sync_button.Disable()
        
        thread = threading.Thread(target=self.run_sync, args=(source, dest, verbose, purge, forcecopy, use_content, two_way, hverify))
        thread.start()
    
    def run_sync(self, source, dest, verbose, purge, forcecopy, use_content, two_way, hverify):
        def log(message):
            wx.CallAfter(self.progress_text.AppendText, message + "\n")
        
        try:
            self.synchronize_directories(source, dest, verbose, purge, forcecopy, False, use_content, two_way, hverify, log)
            wx.CallAfter(self.show_success)
        except Exception as e:
            wx.CallAfter(self.show_error, str(e))
        finally:
            wx.CallAfter(self.sync_button.Enable)
    
    def show_success(self):
        wx.MessageBox("Synchronization completed successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
    
    def show_error(self, message):
        wx.MessageBox(f"An error occurred: {message}", "Error", wx.OK | wx.ICON_ERROR)
    
    def synchronize_directories(self, source, dest, verbose, purge, forcecopy, use_ctime, use_content, two_way, hverify, log_func):
        if not os.path.exists(dest):
            os.makedirs(dest)
            if verbose:
                log_func(f"Created target directory: {dest}")

        def compare_and_copy(src, dst, reverse=False):
            comparison = filecmp.dircmp(src, dst)
            copy_files(comparison, src, dst, reverse)
            if purge:
                delete_files(comparison, dst)

        def copy_files(comp, src, dst, reverse):
            for name in comp.left_only:
                srcpath = os.path.join(src, name)
                dstpath = os.path.join(dst, name)
                if os.path.isdir(srcpath):
                    shutil.copytree(srcpath, dstpath)
                    if verbose:
                        log_func(f"Copied directory: {srcpath} to {dstpath}")
                else:
                    shutil.copy2(srcpath, dstpath)
                    if verbose:
                        log_func(f"Copied file: {srcpath} to {dstpath}")

            for name in comp.common_files:
                srcpath = os.path.join(src, name)
                dstpath = os.path.join(dst, name)
                if forcecopy or not filecmp.cmp(srcpath, dstpath, shallow=not use_content):
                    if reverse:
                        shutil.copy2(dstpath, srcpath)
                        if verbose:
                            log_func(f"Updated file: {dstpath} to {srcpath}")
                    else:
                        shutil.copy2(srcpath, dstpath)
                        if verbose:
                            log_func(f"Updated file: {srcpath} to {dstpath}")

            for subdir in comp.common_dirs:
                compare_and_copy(os.path.join(src, subdir), os.path.join(dst, subdir), reverse)

        def delete_files(comp, dst):
            for name in comp.right_only:
                dstpath = os.path.join(dst, name)
                if os.path.isdir(dstpath):
                    shutil.rmtree(dstpath)
                    if verbose:
                        log_func(f"Deleted directory: {dstpath}")
                else:
                    os.remove(dstpath)
                    if verbose:
                        log_func(f"Deleted file: {dstpath}")

        def compute_file_md5(file_path):
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()

        def verify_md5(src, dst):
            src_files = []
            dst_files = []

            for root, _, files in os.walk(src):
                for name in files:
                    src_files.append(os.path.relpath(os.path.join(root, name), src))

            for root, _, files in os.walk(dst):
                for name in files:
                    dst_files.append(os.path.relpath(os.path.join(root, name), dst))

            all_files = set(src_files + dst_files)
            match = True

            for file in all_files:
                src_file = os.path.join(src, file)
                dst_file = os.path.join(dst, file)

                if os.path.exists(src_file) and os.path.exists(dst_file):
                    src_md5 = compute_file_md5(src_file)
                    dst_md5 = compute_file_md5(dst_file)
                    if src_md5 != dst_md5:
                        match = False
                        log_func(f"MD5 mismatch for {file}: {src_md5} (source) vs {dst_md5} (destination)")
                    else: 
                        log_func(f"MD5 match for {file}: {src_md5}")
                else:
                    match = False
                    log_func(f"File {file} is not present in both source and destination")

            if match:
                log_func("All files are synchronized (MD5 hashes match).")
            else:
                log_func("Some files are not synchronized (MD5 hashes do not match).")

        compare_and_copy(source, dest)
        if two_way:
            compare_and_copy(dest, source, reverse=True)

        if hverify:
            verify_md5(source, dest)

if __name__ == '__main__':
    app = wx.App()
    frame = SyncFrame()
    app.MainLoop()

