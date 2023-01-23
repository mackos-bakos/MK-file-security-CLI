import subprocess 
import os
import time
import random
import math
import sys
import threading
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
aes_dir = ""
while not aes_dir:
    aes_dir = filedialog.askdirectory()

aescrypt_path = os.path.join(os.getenv('PROGRAMFILES'), 'AESCrypt', 'aescrypt.exe')
appdata_directory = os.path.join(os.getenv('APPDATA'), 'backups')

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
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] not in accepted_file_types):
                continue
            thread = threading.Thread(
                    target=purge_file,
                    args=(file,secure,root)
                    ) #start thread routine
            thread.start()
            progress_bar(math.ceil((files.index(file) / len(files)) * 100), 30, file)
            files_purged += 1
    print(f" \n finished purging {folder} purged {files_purged} files")
    
def purge_file(file,secure,root):
    """purge a file and overwrite its contents before hand if selected"""
    if (secure):
        overwrite_data(os.path.join(root, file))
    os.remove(os.path.join(root, file))
    
def decrypt_directory(folder,delete,secure):
    """traverse a directory and decrypt files"""
    files_decrypted = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] != ".aes"): # cant decrypt non encrypted files
                continue
            thread = threading.Thread(
                        target=decrypt_file,
                        args=(os.path.join(root, file),delete, secure,root)
                        ) #start thread routine
            thread.start()
            files_decrypted += 1
            progress_bar(math.ceil((files.index(file) / len(files)) * 100),30,file)
    print(f" \n finished decrypting {folder} decrypted {files_decrypted} files")

def decrypt_file(file, delete, secure,root):
    """call aes to decrypt files and delete plus overwrite afterwards if selected"""
    subprocess.run([aescrypt_path, '-d', '-p', password, file]) # call AES to decrypt file 
    if delete and os.path.exists(os.path.join(root, file[:-4])): # ensure decrypted file was created
        if (secure):
            overwrite_data(os.path.join(root, file))
        os.remove(os.path.join(root, file))
    
def encrypt_directory(folder,delete,secure,backup):
    """encrypt all files in a directory"""
    files_encrypted = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] == ".aes"): # cant encrypt already encrypted files
                continue
            thread = threading.Thread(
                    target=encrypt_file,
                    args=(file, root, backup, delete, secure)
                    ) #start thread routine
            thread.start()
            progress_bar(math.ceil((files.index(file) / len(files)) * 100),30,file)
            files_encrypted += 1
    print(f" \n finished encrypting {folder} encrypted {files_encrypted} files")

def encrypt_file(file,root,backup,delete,secure):
    """encrypts a file and securely deletes original file if selected, also makes an encrypted backup"""
    subprocess.run([aescrypt_path, '-e', '-p', password, os.path.join(root, file)]) # call AES to encrypt the file
    if backup:
        copy_file_to(os.path.join(root, file) + ".aes",os.path.join(appdata_directory,file) + ".aes")
    if delete and os.path.exists(os.path.join(root, file + ".aes")): #ensure file was encrypted before deleting
        if (secure):
            overwrite_data(os.path.join(root, file))
        os.remove(os.path.join(root, file))
def obscure_directory(folder):
    """randomises file names in a dir"""
    files_obscured = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            thread = threading.Thread(
                    target=obscure_file,
                    args=(root,file)
                    ) # start thread routine
            thread.start()
            files_obscured+=1
            progress_bar(math.ceil((files.index(file) / len(files)) * 100),30,file)
    print(f" \n finished obscuring {folder} obscured {files_obscured} files")

def obscure_file(root,file):
    """randomises a file name"""
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
    print(f" \n finished swapping {folder} and swapped {files_swapped} files")

print(" decrypt - decrypts all .aes files in the selected directory")
print(" purge   - deletes selected file extensions in the directory")
print(" obscure - randomises all file names  the selected directory")
print(" encrypt - encrypts all non .aes file types in the directory")
print(" swap    - swaps all file extensions for  selected directory")
choice = input("enter choice :// ")
if (choice.lower() == "decrypt"):
    password = input("enter decryption key :// ")
    _delete = False
    _secure = False
    if (input("delete encrypted version? y/n ://").lower() == "y"):
        _delete = True
        if (input("make files completely unrecoverable by professional software? (takes longer) y/n ://").lower() == "y"):
            _secure = True
    start = time.time()
    decrypt_directory(aes_dir,_delete,_secure)

elif (choice.lower() == "purge"):
    filters = []
    secure = False
    print("enter file extensions to be purged below and type none in console to stop adding extensions")
    inp = ""
    while True:
        inp = input("add a new extension to purge e.g .png ://")
        if inp.lower() == "none":
            break
        else:
            filters.append(inp)
    if input("make files completely unrecoverable by professional software? (takes longer) y/n ://").lower() == "y":
        secure = True
    start = time.time()
    purge_directory(aes_dir,filters,secure)

elif (choice.lower() == "obscure"):
    start = time.time()
    obscure_directory(aes_dir)

elif (choice.lower() == "encrypt"):
    password = input("enter encryption key ://")
    _delete = False
    _secure = False
    _backup = False
    if (input("delete unencrypted version? y/n ://").lower() == "y"):
        _delete = True
        if (input("make files completely unrecoverable by professional software? (takes longer) y/n ://").lower() == "y"):
            _secure = True
    if (input("backup encrypted file in appdata? y/n ://").lower() == "y"):
        _backup = True
    start = time.time()
    encrypt_directory(aes_dir,_delete,_secure,_backup)
    
elif (choice.lower() == "swap"):
    _swap_from = input("swap from e.g .png :// ")
    _swap_to = input("swap from e.g .jpg :// ")
    if len(_swap_from) < 4 or len(_swap_to) < 4:
        print("invalid input the program will exit in 5 seconds")
        time.sleep(5)
        sys.exit()
    start = time.time()
    swap_file_extensions(aes_dir,_swap_from,_swap_to)
    
else:
    print("nothing selected. program will exit in 5 seconds")
    time.sleep(5)
    sys.exit()

end = time.time()
print("time elapsed", end-start, "seconds")
print("-------------------------------------------console will close in 5 seconds--------------------------------------------")
time.sleep(5)

