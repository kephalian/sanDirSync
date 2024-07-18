
import os
import sys
import filecmp
import shutil
import hashlib

def synchronize_directories(source, dest, verbose=False, purge=False, forcecopy=False, use_ctime=False, use_content=False, two_way=False, hverify=False):
    if not os.path.exists(dest):
        os.makedirs(dest)
        if verbose:
            print(f"Created target directory: {dest}")

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
                    print(f"Copied directory: {srcpath} to {dstpath}")
            else:
                shutil.copy2(srcpath, dstpath)
                if verbose:
                    print(f"Copied file: {srcpath} to {dstpath}")

        for name in comp.common_files:
            srcpath = os.path.join(src, name)
            dstpath = os.path.join(dst, name)
            if forcecopy or not filecmp.cmp(srcpath, dstpath, shallow=not use_content):
                if reverse:
                    shutil.copy2(dstpath, srcpath)
                    if verbose:
                        print(f"Updated file: {dstpath} to {srcpath}")
                else:
                    shutil.copy2(srcpath, dstpath)
                    if verbose:
                        print(f"Updated file: {srcpath} to {dstpath}")

        for subdir in comp.common_dirs:
            compare_and_copy(os.path.join(src, subdir), os.path.join(dst, subdir), reverse)

    def delete_files(comp, dst):
        for name in comp.right_only:
            dstpath = os.path.join(dst, name)
            if os.path.isdir(dstpath):
                shutil.rmtree(dstpath)
                if verbose:
                    print(f"Deleted directory: {dstpath}")
            else:
                os.remove(dstpath)
                if verbose:
                    print(f"Deleted file: {dstpath}")

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
                    print(f"MD5 mismatch for {file}: {src_md5} (source) vs {dst_md5} (destination)")
                else: 
                    print(f"MD5 match for {file}: {src_md5}")
            else:
                match = False
                print(f"File {file} is not present in both source and destination")

        if match:
            print("All files are synchronized (MD5 hashes match).")
        else:
            print("Some files are not synchronized (MD5 hashes do not match).")

    compare_and_copy(source, dest)
    if two_way:
        compare_and_copy(dest, source, reverse=True)

    if hverify:
        verify_md5(source, dest)



# Example usage
if __name__ == "__main__":
	synchronize_directories('/storage/emulated/0/t/source', '/storage/emulated/0/t/destination', verbose=True, use_content=True, purge=True, hverify=True)
#    if len(sys.argv) < 3:
#        print("Usage: python sync.py <source_directory> <destination_directory> [options]")
#        sys.exit(1)

#    source_directory = sys.argv[1]
#    destination_directory = sys.argv[2]
#    verbose_mode = '--verbose' in sys.argv
#    purge_mode = '--purge' in sys.argv
#    forcecopy_mode = '--forcecopy' in sys.argv
#    use_ctime_mode = '--use-ctime' in sys.argv
#    use_content_mode = '--use-content' in sys.argv
#    two_way_sync = '--2sync' in sys.argv
#    hverify_mode = '--hverify' in sys.argv

#    synchronize_directories(
#        source_directory,
#        destination_directory,
#        verbose=verbose_mode,
#        purge=purge_mode,
#        forcecopy=forcecopy_mode,
#        use_ctime=use_ctime_mode,
#        use_content=use_content_mode,
#        two_way=two_way_sync,
#        hverify=hverify_mode
#    )