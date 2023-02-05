import subprocess 
import os
import time
import random
import math
import sys
import threading
import json
import tkinter as tk
import hashlib
from tkinter import filedialog
try:
    import win32api,win32process,win32con
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    print("priority has been set to high.")
except:
    print("pywin not installed! please install it although it is not required to run this program.")

aescrypt_path = os.path.join(os.getenv('PROGRAMFILES'), 'AESCrypt', 'aescrypt.exe')
if not os.path.exists(aescrypt_path):
    input("aescrypt is not installed! please install it from https://www.aescrypt.com/download/")
    
root = tk.Tk()
root.withdraw()

aes_dir = ""

while not aes_dir:
    aes_dir = filedialog.askdirectory()
    
def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count
def count_folders(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += 1
    return count

num_files = count_files(aes_dir)
num_folders = count_folders(aes_dir)

print(f"\nselected path {aes_dir} containing {num_files} files and {num_folders} folders.")
appdata_directory = os.path.join(os.getenv('APPDATA'), 'backups')
config_dir = os.getcwd() + "\FastTrack.json"
default = {'decrypt': {'delete': False,'seperate': True},'encrypt': {'delete': True,'backup': True},'purge': {'types': [".png",".jpg",".mp4"]},'swap': {'from': ".jpg",'to': ".png"}} #wont store password for obvious reasons
if not os.path.exists(config_dir):
    open(config_dir,"a")
    json.dump(default,open(config_dir,"w"))
    print(f"new fast track file made at {config_dir}")
    
with open(config_dir, "r") as f:
    cur_fast_track = json.load(f)
    f.close()

if not os.path.exists(appdata_directory):
    os.makedirs(appdata_directory)
    print(f"created a directory at {appdata_directory}")
    
def progress_bar(percent=0, width=30, file = None):
    """display a updating progress bar with static position in cmd prompt"""
    left = width * percent // 100 
    right = width - left 
    print('\r[', '#' * left, ' ' * right, ']',
        f' {percent:.0f}%   {file}',
        sep='', end='', flush=True)
    
def hash_md5(to_hash):
    res = hashlib.md5(to_hash.encode('utf-8'))
    return res.hexdigest()

def copy_file_to(source,destination):
    """copy the bytemap of a file elsewhere"""
    with open(source, 'rb') as read_file: 
        with open(destination, 'wb') as write_file: 
            for line in read_file: 
                write_file.write(line) # write copied bytes to new path
            write_file.close()
        read_file.close()
def get_all_dirs(directory):
    """traverse current dir and return all dirs (folders)"""
    return  [file for file in os.listdir(directory) if os.path.isdir(file)]

def overwrite_data(file):
    """write a file with random bytemaps to prevent data recovery"""
    for i in range(5):
        with open(file, 'wb') as f:
            f.write(os.urandom(os.path.getsize(file))) # write random byte map
            f.close()


def purge_directory(folder, accepted_file_types, secure):
    """traverse a directory and purge all selected files"""
    files_purged = 0
    threads = []
    for root, dirs, files in os.walk(folder):
        thread = threading.Thread(
                target=purge_file,
                args=(files,secure,root,accepted_file_types)
                ) #start thread routine
        thread.start()
        threads.append(thread)
    for thread in threads:
        progress_bar(math.floor((threads.index(thread) / len(threads)) * 100),30,f"joining thread {threads.index(thread)} out of {len(threads)} threads.")
        thread.join()
    print("\n")
    print(f"finished purging {folder}")
    
def purge_file(files,secure,root,accepted_file_types):
    """purge a file and overwrite its contents before hand if selected"""
    for file in files:
        if (os.path.splitext(file)[1] not in accepted_file_types):
            continue
        try:
            if (secure):
                overwrite_data(os.path.join(root, file))
            os.remove(os.path.join(root, file))
        except:
            continue
    
def decrypt_directory(folder,delete,secure,seperate):
    """traverse a directory and decrypt files"""
    threads = []
    for root, dirs, files in os.walk(folder):
        if (not os.path.exists(root+"/raw") and seperate and root[-3:] != "raw" and len(files) != 0):
            os.mkdir(root+"/raw")
        thread = threading.Thread(
                    target=decrypt_file,
                    args=(files,delete,seperate, secure,root)
                    ) #start thread routine
        thread.start()
        threads.append(thread)
    for thread in threads:
        progress_bar(math.floor((threads.index(thread) / len(threads)) * 100),30,f"joining thread {threads.index(thread)} out of {len(threads)} threads.")
        thread.join()
    print("\n")
    print(f"finished decrypting {folder}")

def decrypt_file(files, delete,seperate, secure,root):
    """call aes to decrypt files and delete plus overwrite afterwards if selected"""
    for file in files:
        try:
            if (os.path.splitext(file)[1] != ".aes"): # cant decrypt non encrypted files
                continue
            subprocess.run([aescrypt_path, '-d', '-p', password, os.path.join(root, file)]) # call AES to decrypt file
            if (seperate and os.path.exists(os.path.join(root, file[:-4]))):
                copy_file_to(os.path.join(root, file[:-4]),os.path.join(root+"/raw",file[:-4]))
                if (secure):
                    overwrite_data(os.path.join(root, file[:-4]))
                os.remove(os.path.join(root, file[:-4]))
            if delete and (os.path.exists(os.path.join(root+"/raw",file[:-4])) or os.path.exists(os.path.join(root,file[:-4]))): # ensure decrypted file was created
                if (secure):
                    overwrite_data(os.path.join(root,file))
                os.remove(os.path.join(root,file))
        except:
            continue
        
def encrypt_directory(folder,delete,secure,backup):
    """encrypt all files in a directory"""
    threads = []
    for root, dirs, files in os.walk(folder):
        thread = threading.Thread(
                target=encrypt_file,
                args=(files, root, backup, delete, secure)
                ) #start thread routine
        thread.start()
        threads.append(thread)
    for thread in threads:
        progress_bar(math.floor((threads.index(thread) / len(threads)) * 100),30,f"joining thread {threads.index(thread)} out of {len(threads)} threads.")
        thread.join()
    print("\n")
    print(f"finished encrypting {folder}")

def encrypt_file(files,root,backup,delete,secure):
    """encrypts a file and securely deletes original file if selected, also makes an encrypted backup"""
    for file in files:
        if (os.path.splitext(file)[1] == ".aes"): # cant encrypt already encrypted files
            continue
        try:
            subprocess.run([aescrypt_path, '-e', '-p', password, os.path.join(root, file)]) # call AES to encrypt the file
        except:
            continue
        if backup:
            copy_file_to(os.path.join(root, file) + ".aes",os.path.join(appdata_directory,file) + ".aes")
        if delete and os.path.exists(os.path.join(root, file + ".aes")): #ensure file was encrypted before deleting
            if (secure):
                overwrite_data(os.path.join(root, file))
            os.remove(os.path.join(root, file))
            
def obscure_directory(folder):
    """randomises file names in a dir"""
    threads = []
    for root, dirs, files in os.walk(folder):
        thread = threading.Thread(
                target=obscure_file,
                args=(root,files)
                ) # start thread routine
        thread.start()
        threads.append(thread)
    for thread in threads:
        progress_bar(math.floor((threads.index(thread) / len(threads)) * 100),30,f"joining thread {threads.index(thread)} out of {len(threads)} threads.")
        thread.join()
    print("\n")
    print(f"finished obscuring {folder}")

def obscure_file(root,files):
    """randomises a file name"""
    for file in files:
        name, ext = os.path.splitext(file)
        newname = ''.join(chr(random.randint(128, 512)) for _ in range(7)) #add random unicode chars
        if len(name.split('.')) > 1: # add file extensions before .aes to ensure recreation
            newname += '.' + name.split('.')[1]
        newname += ext
        os.rename(os.path.join(root, file), os.path.join(root, newname))
        
def swap_file_extensions(folder,swap_from,swap_to):
    """traverses a dir, swapping selected file names"""
    files_swapped = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            name, ext = os.path.splitext(file)
            if (ext not in [swap_from,".aes"]):
                continue
            if (ext == ".aes" and name.split(".")[1] == swap_from[1:]): # only swap non .aes file extension
                newname = name[:-4] + swap_to + ".aes"
            elif (ext == swap_from):
                newname = name + swap_to
            else:
                continue
            os.rename(os.path.join(root, file), os.path.join(root, newname))
            files_swapped += 1
            progress_bar(math.ceil((files.index(file) / len(files)) * 100),30,file)
    print("\n")
    print(f" \n finished swapping {folder} and swapped {files_swapped} files")

print(f"\ndecrypt -      decrypt all files")
print(f"purge   -        purge all files")
print(f"obscure - obscure all file names")
print(f"encrypt -      encrypt all files")
print(f"swap    -   swap file extensions")
choice = input("enter choice :// ")
if (choice.lower() == "decrypt"):
    if (input("\nuse a hashed key? y/n :// ").lower() == "y"):
        password = hash_md5(input("\nenter key to be hashed :// "))
    else:
        password = input("\nenter raw decryption key :// ")
    if (input(f" \nuse FastTrack settings? \ndelete: {cur_fast_track['decrypt']['delete']} \nseperate: {cur_fast_track['decrypt']['seperate']} \ny/n? :// ").lower() == "y"):
        _delete = cur_fast_track['decrypt']['delete']
        _seperate = cur_fast_track['decrypt']['seperate']
        _secure = True
        start = time.time()
        print("\n")
        decrypt_directory(aes_dir,_delete,_secure,_seperate)
    else:
        _delete = False
        _secure = False
        _seperate = False
        if (input("\ndelete encrypted version? y/n :// ").lower() == "y"):
            _delete = True
            _secure = True
        if (input("seperate encrypted files in different folders? y/n :// ").lower() == "y"):
            _seperate = True
        start = time.time()
        print("\n")
        decrypt_directory(aes_dir,_delete,_secure,_seperate)
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['decrypt']['delete'] = _delete
            cur_fast_track['decrypt']['seperate'] = _seperate
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
elif (choice.lower() == "purge"):
    if (input(f"\nuse FastTrack settings? \nfilters: {cur_fast_track['purge']['types']} \ny/n? :// ").lower() == "y"):
        _filters = cur_fast_track['purge']['types']
        _secure = True
        print("\n")
        start = time.time()
        purge_directory(aes_dir,_filters,_secure)
    else:
        _filters = []
        secure = False
        print("\nenter file extensions to be purged below and type none in console to stop adding extensions")
        inp = ""
        while True:
            inp = input("add a new extension to purge. :// ")
            if inp.lower() == "none":
                print("\n")
                break
            else:
                _filters.append(inp)
        _secure = True
        start = time.time()
        print("\n")
        purge_directory(aes_dir,_filters,_secure)
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['purge']['types'] = _filters
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
elif (choice.lower() == "obscure"):
    start = time.time()
    print("\n")
    obscure_directory(aes_dir)

elif (choice.lower() == "encrypt"):
    if (input("\nuse a hashed key? y/n :// ").lower() == "y"):
        password = hash_md5(input("\nenter key to be hashed :// "))
    else:
        password = input("\nenter raw decryption key :// ")
    if (input(f"\nuse FastTrack settings? \ndelete: {cur_fast_track['encrypt']['delete']} \nbackup: {cur_fast_track['encrypt']['backup']} \ny/n? :// ").lower() == "y"):
        _backup = cur_fast_track['encrypt']['backup']
        _delete = cur_fast_track['encrypt']['delete']
        _secure = False
        encrypt_directory(aes_dir,_delete,_secure,_backup)
        start = time.time()
    else:
        _delete = False
        _secure = False
        _backup = False
        if (input("\ndelete unencrypted version? y/n :// ").lower() == "y"):
            _delete = True
            _secure = True
        if (input("backup encrypted file in appdata? y/n :// ").lower() == "y"):
            _backup = True
        start = time.time()
        print("\n")
        encrypt_directory(aes_dir,_delete,_secure,_backup)
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['encrypt']['delete'] = _delete
            cur_fast_track['encrypt']['backup'] = _backup
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
elif (choice.lower() == "swap"):
    if (input(f"\nuse FastTrack settings? \nfrom: {cur_fast_track['swap']['from']} \nto: {cur_fast_track['swap']['to']} \ny/n? :// ").lower() == "y"):
        _swap_from = cur_fast_track['swap']['from']
        _swap_to = cur_fast_track['swap']['to']
        start = time.time()
        swap_file_extensions(aes_dir,_swap_from,_swap_to)
    else:
        _swap_from = input("\nswap from e.g .png :// ")
        _swap_to = input("swap from e.g .jpg :// ")
        if len(_swap_from) < 4 or len(_swap_to) < 4:
            print("\ninvalid input the program will exit in 5 seconds")
            time.sleep(5)
            sys.exit()
        start = time.time()
        swap_file_extensions(aes_dir,_swap_from,_swap_to)
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['swap']['from'] = _swap_from
            cur_fast_track['swap']['to'] = _swap_to
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
else:
    print("\nnothing selected. program will exit in 5 seconds")
    time.sleep(5)
    sys.exit()
    
new_num_files = count_files(aes_dir)
new_num_folders = count_folders(aes_dir)

end = time.time()
print(f"\ntime elapsed {end-start} seconds")
print(f"\nnet file gain: {new_num_files-num_files}\nnet folder gain: {new_num_folders-num_folders}\n")
print("-------------------------------------------console will close in 5 seconds--------------------------------------------")
time.sleep(5)

