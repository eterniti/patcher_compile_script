import os
import subprocess
import sys
import shutil
import requests
import git
import py7zr
import zipfile
from urllib.parse import urlparse

minhook_dir = "./minhook-1.3.3"
jobs = os.cpu_count()

def printc(msg, c):
    if c == 'R':
        print(f"\033[31m{msg}\033[0m")
    elif c == 'G':
        print(f"\033[32m{msg}\033[0m")
    else:
        print(f"\033[34m{msg}\033[0m")

def option_menu(msg, options):
    print(msg)
    
    for i, option in enumerate(options):
        print(f"{i + 1}) {option}")

    while True:
        choice = input("")
        if choice.isdigit() and 0 < int(choice) <= len(options):
            print("")
            return int(choice) - 1
        else:
            print("Invalid choice. Please enter a valid option number.")

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if os.path.isdir(save_path):
        save_path = os.path.join(directory, filename)
    with open(save_path, 'wb') as file:
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024*1024  # 1 MB
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                print(f"Downloading {filename}: {round(file.tell()/1048576, 2)}/{round(total_size/1048576, 2)} MB", end='\r')
                
    print("")

def download_repo(repo_url, destination_path):
    print(f"Downloading repository {repo_url}")
    git.Repo.clone_from(repo_url, destination_path)
            
def extract_7z(file_path, output_dir, remove=True):
    print(f"Extracting {os.path.basename(file_path)}...")
    with py7zr.SevenZipFile(file_path, 'r') as archive:
        archive.extractall(output_dir)

    if remove:
        os.remove(file_path)

def extract_zip(file_path, output_dir, remove=True):
    print(f"Extracting {os.path.basename(file_path)}...")
    os.makedirs(output_dir, exist_ok=True)
        
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    if remove:
        os.remove(file_path)

def extract(file_path, output_dir, remove=True):
    if file_path.endswith(".7z"):
        extract_7z(file_path, output_dir, remove)
    else:
        extract_zip(file_path, output_dir, remove)

# Need this to remove the .git directories *sigh*
def force_remove_readonly(func, path, excinfo):
    os.chmod(path, 0o777)
    func(path)

def clear_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.unlink(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path, onerror=force_remove_readonly)

def is_mingw64_installed():
    return os.path.isfile("./mingw64/bin/mingw32-make.exe")

def is_minhook_installed():
    return os.path.isfile("./mingw64/x86_64-w64-mingw32/include/MinHook.h") and os.path.isfile("./mingw64/x86_64-w64-mingw32/lib/libMinHook.a")

def make_minhook():
    subprocess.run(["mingw32-make.exe", "-f", "./build/MinGW/Makefile", "-j", str(jobs)], cwd=os.path.abspath(minhook_dir), shell=True)

    if not os.path.isfile(f"{minhook_dir}/libMinHook.a"):
        sys.exit("Compilation of MinHook failed")

    print("MinHook was compiled successfully.")

def make_xv2patcher(dinput8=False):
    if dinput8:
        subprocess.run(["mingw32-make.exe", "-f", "Makefile.dinput8", "-j", str(jobs)], cwd=os.path.abspath("./xv2patcher"), shell=True)
        if not os.path.isfile("./xv2patcher/dinput8.dll"):
            printc("Compilation of xv2patcher failed", 'R')
            exit(-1)
        
        shutil.copy("./xv2patcher/dinput8.dll", "./dinput8.dll")
    else:
        subprocess.run(["mingw32-make.exe", "-j", str(jobs)], cwd=os.path.abspath("./xv2patcher"), shell=True)
        if not os.path.isfile("./xv2patcher/xinput1_3.dll"):
            printc("Compilation of xv2patcher failed", 'R')
            exit(-1)
        
        shutil.copy("./xv2patcher/xinput1_3.dll", "./xinput1_3.dll")

    printc("xv2patcher was compiled successfully.", 'G')

def make_clean_xv2patcher(dinput8=False):
    try:
        if dinput8:
            subprocess.run(["mingw32-make.exe", "-f", "Makefile.dinput8", "clean_windowfied"], cwd=os.path.abspath("./xv2patcher"), shell=True)
        else:
            subprocess.run(["mingw32-make.exe", "clean_windowfied"], cwd=os.path.abspath("./xv2patcher"), shell=True)
        
        printc("Clean successful.", 'G')
    except Exception:
        printc("Clean failed (not critical)", 'R')

def install_minhook():
    try:
        shutil.copy(f"{minhook_dir}/include/MinHook.h", "./mingw64/x86_64-w64-mingw32/include/")
        shutil.copy(f"{minhook_dir}/libMinHook.a", "./mingw64/x86_64-w64-mingw32/lib/")
        printc("Minhook succesfully installed into mingw64.", 'G')
    except Exception:
        printc("Failed to install minhook.", 'R')
        exit(-1)
        
def start():
    global jobs
    
    print("Welcome. This script will build xv2patcher from source and optionally install it.")
    custom_mode = option_menu("Choose a mode:", ["Default (default values will be chosen, you will be asked less questions)", "Custom (you will be asked more questions)"]) == 1
    
    if not is_mingw64_installed():
        download_url = ""
        source_list = [ "github.com/niXman", "github.com/brechtsanders (winlibs)" ]
        dest = "./mingw64.7z"
        
        source_option = 0 
        if custom_mode:
            source_option = option_menu("Choose desired source for MingW64:", source_list)
            
        if source_option == 0: 
            # Not adding 13.2 in this source, because padlock.dll from MSVCRT version has a false positive in AV *sigh*
            download_list = [ "https://github.com/niXman/mingw-builds-binaries/releases/download/13.1.0-rt_v11-rev1/x86_64-13.1.0-release-win32-seh-msvcrt-rt_v11-rev1.7z", "https://github.com/niXman/mingw-builds-binaries/releases/download/13.1.0-rt_v11-rev1/x86_64-13.1.0-release-win32-seh-ucrt-rt_v11-rev1.7z", "https://github.com/niXman/mingw-builds-binaries/releases/download/11.2.0-rt_v9-rev0/x86_64-11.2.0-release-win32-seh-rt_v9-rev0.7z" ]
            option_names = [ "GCC 13.1 (MSVCRT)", "GCC 13.1 (UCRT)", "GCC 11.2 (MSVCRT)" ]
            
            download_idx = 0
            if custom_mode:
                download_idx = option_menu("Choose version (UCRT will only work in Windows 10/11):", option_names)

            download_url = download_list[download_idx]
        else:
            # The 7zip of this source are not compatible with py7zr ("BCJ2 filter"), so have to use the zip versions
            dest = "./mingw64.zip"
            download_list = [ "https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0posix-18.1.1-11.0.1-msvcrt-r6/winlibs-x86_64-posix-seh-gcc-13.2.0-mingw-w64msvcrt-11.0.1-r6.zip", "https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0posix-17.0.6-11.0.1-ucrt-r5/winlibs-x86_64-posix-seh-gcc-13.2.0-mingw-w64ucrt-11.0.1-r5.zip", "https://github.com/brechtsanders/winlibs_mingw/releases/download/8.5.0-9.0.0-r1/winlibs-x86_64-posix-seh-gcc-8.5.0-mingw-w64-9.0.0-r1.zip"]
            option_names = [ "GCC 13.2 (MSVCRT)", "GCC 13.2 (UCRT)", "GCC 8.5 (MSVCRT)"]

            download_idx = 0
            if custom_mode:
                download_idx = option_menu("Choose version (UCRT will only work in Windows 10/11):", option_names)

            download_url = download_list[download_idx]
                        
        download_file(download_url, dest)
        extract(dest, "./")

    current_path = os.environ.get('PATH', '')
    mingwbin_path = os.path.abspath("./mingw64/bin")
    new_path = f"{current_path};{mingwbin_path}"
    os.environ['PATH'] = new_path

    if custom_mode:
        options = [f"Number of Cores ({jobs})", "1", "2", "4", "8", "16", "32"]
        idx = option_menu("Choose the number of jobs for compilation.", options)
        if idx > 0:
            jobs = int(options[idx])

    if not is_minhook_installed():
        clear_directory(minhook_dir)
        printc("MinHook 1.3.3 source will be downloaded now.", 'B')
        download_file("https://github.com/TsudaKageyu/minhook/archive/refs/tags/v1.3.3.zip", "minhook.zip")
        extract("minhook.zip", "./")

        printc("Will compile MinHook now...", 'B')
        make_minhook()
        print("Will install MinHook to MingW64 now...", 'B')
        install_minhook()

    clear_directory("./eternity_common")
    clear_directory("./xv2patcher")

    download_repo("https://github.com/eterniti/eternity_common", "./eternity_common")
    download_repo("https://github.com/eterniti/xv2patcher", "./xv2patcher")

    printc("Will compile xv2patcher now...", 'B')
    make_xv2patcher()

    printc("Cleaning compilation...", 'B')
    make_clean_xv2patcher() 

    printc("Will now compile the dinput8 version of xv2patcher...", 'B')
    make_xv2patcher(True)

    printc("Cleaning compilation...", 'B')
    make_clean_xv2patcher(True) 

    printc("The script has terminated successfully (probably!)", 'G')
