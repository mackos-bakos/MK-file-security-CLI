"""
  _|_|    _|_|_|_|    _|_|_|    _|      _|    _|_|    _|      _|    _|_|      _|_|_|  _|_|_|_|  _|_|_|    
_|    _|  _|        _|          _|_|  _|_|  _|    _|  _|_|    _|  _|    _|  _|        _|        _|    _|  
_|_|_|_|  _|_|_|      _|_|      _|  _|  _|  _|_|_|_|  _|  _|  _|  _|_|_|_|  _|  _|_|  _|_|_|    _|_|_|    
_|    _|  _|              _|    _|      _|  _|    _|  _|    _|_|  _|    _|  _|    _|  _|        _|    _|  
_|    _|  _|_|_|_|  _|_|_|      _|      _|  _|    _|  _|      _|  _|    _|    _|_|_|  _|_|_|_|  _|    _|  
                                                                                                          
                          _|_|_|_|_|                                                                      
"""
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
import getpass
from tkinter import filedialog

try:
    import win32api,win32process,win32con
    
    #grab process id
    pid = win32api.GetCurrentProcessId()

    #grab handle to process
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)

    #set priority to high
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    
    print("priority has been set to high.")
    
except:
    print("pywin not installed! please install it although it is not required to run this program.")


#grab path to aescrypt.exe
aescrypt_path = os.path.join(os.getenv('PROGRAMFILES'), 'AESCrypt', 'aescrypt.exe')

#check for aescrypt installation 
if not os.path.exists(aescrypt_path):
    input("aescrypt is not installed! please install it from https://www.aescrypt.com/download/")
    
    #exit program
    sys.exit()


#init tkinter but dont draw ui
root = tk.Tk()
root.withdraw()

aes_dir = ""

#repeatably ask for dir to manipulate
while not aes_dir:
    aes_dir = filedialog.askdirectory()


def count_files(directory):
    """count files in a directory"""
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

def count_folders(directory):
    """count folders in a directory"""
    count = 0
    for root, dirs, files in os.walk(directory):
        count += 1
    return count

def count_size(directory):
    """get file size of folder"""
    size = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            size += os.path.getsize(os.path.join(root,file))
    return size

def size_to_rational(size):
    """get size in understandable terms to gb"""
    gb_size = 1000000000
    mb_size = 1000000
    kb_size = 1000
    b_size = 1
    if (size > gb_size):
        return str(int(size / gb_size)) + "gb"
    elif (size > mb_size):
        return str(int(size / mb_size)) + "mb"
    elif (size > kb_size):
        return str(int(size / kb_size)) + "kb"
    elif (size > b_size):
        return str(int(size / b_size)) + "b"
    
num_files = count_files(aes_dir)
num_folders = count_folders(aes_dir)
size = size_to_rational(count_size(aes_dir))

print(f"\nselected path {aes_dir} containing {num_files} files and {num_folders} folders. (size is {size})\n\nplease double check this is the right directory!")

#grab appdata dir for encrypted backups
appdata_directory = os.path.join(os.getenv('APPDATA'), 'backups')

#grab config file directory from cwd
config_dir = os.getcwd() + "\FastTrack.json"

#define default config
default = {'decrypt': {'delete': False,'seperate': True},'encrypt': {'delete': True,'backup': True},'purge': {'types': [".png",".jpg",".mp4"]},'swap': {'from': ".jpg",'to': ".png"}}

#if config file doesnt exist
if not os.path.exists(config_dir):
    #create new config file
    open(config_dir,"a")

    #dump default config json onto new file
    json.dump(default,open(config_dir,"w"))
    
    print(f"new fast track file made at {config_dir}")
    
with open(config_dir, "r") as f:
    #read config file
    cur_fast_track = json.load(f)

    #close handle to file
    f.close()

#if theres no dir in appdata called backups
if not os.path.exists(appdata_directory):
    #make new one
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
    """return hash to md5 standard"""
    res = hashlib.md5(to_hash.encode('utf-8'))
    return res.hexdigest()

def copy_file_to(source,destination):
    """copy the bytemap of a file elsewhere"""
    with open(source, 'rb') as read_file:
        with open(destination, 'wb') as write_file:
            #write copied data line by line
            for line in read_file:
                write_file.write(line)
                
            #close handle
            write_file.close()
            
        #close handle
        read_file.close()
        
def get_all_dirs(directory):
    """traverse current dir and return all dirs (folders)"""
    return  [file for file in os.listdir(directory) if os.path.isdir(file)]

def overwrite_data(file):
    """write a file with random bytemaps to prevent data recovery"""
    for i in range(5):
        with open(file, 'wb') as f:
            #write random byte map
            f.write(os.urandom(os.path.getsize(file)))

            #close handle
            f.close()
            
def purge_directory(folder, accepted_file_types, secure):
    """traverse a directory and purge all selected files"""
    
    files_purged = 0
    threads = []
    
    for root, dirs, files in os.walk(folder):
        #define thread routine
        thread = threading.Thread(
                target=purge_file,
                args=(files,secure,root,accepted_file_types)
                )

        #start thread routine
        thread.start()

        #add to thread register
        threads.append(thread)
        
    for thread in threads:
        #display progress
        progress_bar(math.ceil(((threads.index(thread) + 1) / len(threads)) * 100),30,f"joining thread {threads.index(thread)+1} out of {len(threads)} threads.")

        #wait for threads to finish before continuing
        thread.join()
        
    print("\n")
    print(f"finished purging {folder}")
    
def purge_file(files,secure,root,accepted_file_types):
    """purge a file and overwrite its contents before hand if selected"""
    for file in files:
        #if the file isnt in the selected file types
        if (os.path.splitext(file)[1] not in accepted_file_types):
            continue
        
        try:
            #try and remove the file
            if (secure):
                #write random data to the file to prevent recovery
                overwrite_data(os.path.join(root, file))

            #delete the file
            os.remove(os.path.join(root, file))
            
        except:
            #if it fails then skip it
            continue
    
def decrypt_directory(folder,delete,secure,seperate):
    """traverse a directory and decrypt files"""
    
    threads = []
    
    for root, dirs, files in os.walk(folder):
        #if there isnt a directory called raw in the currently traversed folder and the seperate option is selected
        if (not os.path.exists(root+"/raw") and seperate and root[-3:] != "raw" and len(files) != 0):
            #make new raw directory to store encrypted files
            os.mkdir(root+"/raw")

        #define thread routine
        thread = threading.Thread(
                    target=decrypt_file,
                    args=(files,delete,seperate, secure,root)
                    )

        #start thread routine
        thread.start()

        #add to threads register
        threads.append(thread)
        
    for thread in threads:
        #display progress
        progress_bar(math.ceil(((threads.index(thread) + 1) / len(threads)) * 100),30,f"joining thread {threads.index(thread) + 1} out of {len(threads)} threads.")

        #wait for threads to finish before continuing
        thread.join()
        
    print("\n")
    print(f"finished decrypting {folder}")

def decrypt_file(files, delete,seperate, secure,root):
    """call aes to decrypt files and delete plus overwrite afterwards if selected"""
    for file in files:
        try:
            #if the file isnt encrypted, skip it
            if (os.path.splitext(file)[1] != ".aes"):
                continue

            #start decryption process by calling aescrypt
            subprocess.run([aescrypt_path, '-d', '-p', password, os.path.join(root, file)])

            #if seperate option is selected and the decrypted file was created
            if (seperate and os.path.exists(os.path.join(root, file[:-4]))):
                #copy to raw directory
                copy_file_to(os.path.join(root, file[:-4]),os.path.join(root+"/raw",file[:-4]))
            
                if (secure):
                    #overwrite data to prevent recovery
                    overwrite_data(os.path.join(root, file[:-4]))

                #delete original file
                os.remove(os.path.join(root, file[:-4]))

            #if decrypted file was created and should delete encrypted original
            if delete and (os.path.exists(os.path.join(root+"/raw",file[:-4])) or os.path.exists(os.path.join(root,file[:-4]))): # ensure decrypted file was created
                if (secure):
                    #prevent recovery by overwriting
                    overwrite_data(os.path.join(root,file))

                #delete encrypted file
                os.remove(os.path.join(root,file))
                
        except:
            #if decryption fails, skip
            continue
        
def encrypt_directory(folder,delete,secure,backup):
    """encrypt all files in a directory"""
    
    threads = []
    
    for root, dirs, files in os.walk(folder):
        #define thread routine
        thread = threading.Thread(
                target=encrypt_file,
                args=(files, root, backup, delete, secure)
                )
        
        #start thread routine
        thread.start()

        #add to thread register
        threads.append(thread)
        
    for thread in threads:
        #display progress
        progress_bar(math.ceil(((threads.index(thread) + 1) / len(threads)) * 100),30,f"joining thread {threads.index(thread) + 1} out of {len(threads)} threads.")

        #wait for thread to complete
        thread.join()
        
    print("\n")
    print(f"finished encrypting {folder}")

def encrypt_file(files,root,backup,delete,secure):
    """encrypts a file and securely deletes original file if selected, also makes an encrypted backup"""
    for file in files:
        #skip files already encrypted
        if (os.path.splitext(file)[1] == ".aes"):
            continue
        
        try:
            #call aes to encrypt the file
            subprocess.run([aescrypt_path, '-e', '-p', password, os.path.join(root, file)])
        except:
            #if fails, skip
            continue
        
        if backup:
            #copy file to appdata
            copy_file_to(os.path.join(root, file) + ".aes",os.path.join(appdata_directory,file) + ".aes")

        #if should delete and file was encrypted successfully
        if delete and os.path.exists(os.path.join(root, file + ".aes")):
            if (secure):
                #write random data to prevent recovery
                overwrite_data(os.path.join(root, file))

            #delete file
            os.remove(os.path.join(root, file))
            
def obscure_directory(folder):
    """randomises file names in a dir"""

    threads = []
    
    for root, dirs, files in os.walk(folder):
        #define thread routine
        thread = threading.Thread(
                target=obscure_file,
                args=(root,files)
                )

        #start thread routine
        thread.start()

        #add to thread register
        threads.append(thread)
        
    for thread in threads:
        #display progress
        progress_bar(math.ceil(((threads.index(thread) + 1) / len(threads)) * 100),30,f"joining thread {threads.index(thread) + 1} out of {len(threads)} threads.")

        #wait for threads to complete
        thread.join()

    print("\n")
    print(f"finished obscuring {folder}")

def obscure_file(root,files):
    """randomises a file name"""
    for file in files:
        #split name and file extension
        name, ext = os.path.splitext(file)

        #add random unicode chars
        _newname = ''.join(chr(random.randint(128, 512)) for _ in range(7))

        #readd old file extension below .aes
        if len(name.split('.')) > 1:
            _newname += '.' + name.split('.')[1]

        #readd extension
        _newname += ext

        #add file number
        newname = f"{files.index(file)}-{_newname}"
        
        #rename file
        os.rename(os.path.join(root, file), os.path.join(root, newname))
        
def swap_file_extensions(folder,swap_from,swap_to):
    """traverses a dir, swapping selected file names"""
    files_swapped = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            #split name and extension
            name, ext = os.path.splitext(file)

            #if not selected to be swapped
            if (ext not in [swap_from,".aes"]):
                continue

            #preserve .aes extension
            if (ext == ".aes" and name.split(".")[1] == swap_from[1:]):
                newname = name[:-4] + swap_to + ".aes"

            #if it should be swapped
            elif (ext == swap_from):
                newname = name + swap_to

            #if not, skip
            else:
                continue

            #rename file
            os.rename(os.path.join(root, file), os.path.join(root, newname))
            
            files_swapped += 1

            #show progress
            progress_bar(math.ceil(((files.index(file) + 1) / len(files)) * 100),30,file)
            
    print("\n")
    print(f" \n finished swapping {folder} and swapped {files_swapped} files")
    
print(f"\ndecrypt -      decrypt all files")
print(f"purge   -        purge all files")
print(f"obscure - obscure all file names")
print(f"encrypt -      encrypt all files")
print(f"swap    -   swap file extensions")

choice = input("enter choice :// ")
if (choice.lower() == "decrypt"):

    #hash password
    if (input("\nuse a hashed key? y/n :// ").lower() == "y"):
        to_hash = getpass.getpass("\nenter decryption key to be hashed (input is hidden):// ")
        print("password: ",'*' * len(to_hash))
        password = hash_md5(to_hash)

    #use raw password
    else:
        password = getpass.getpass("\nenter raw decryption key (input is hidden):// ")
        print("password: ",'*' * len(password))
        
    if (input(f" \nuse FastTrack settings? \ndelete: {cur_fast_track['decrypt']['delete']} \nseperate: {cur_fast_track['decrypt']['seperate']} \ny/n? :// ").lower() == "y"):

        #load fastrack settings
        _delete = cur_fast_track['decrypt']['delete']
        _seperate = cur_fast_track['decrypt']['seperate']
        _secure = True

        #sample time
        start = time.time()
        
        print("\n")

        #perform function
        decrypt_directory(aes_dir,_delete,_secure,_seperate)
        
    else:
        
        _delete = False
        _secure = False
        _seperate = False

        #ask user if they want to delete the encrypted file
        if (input("\ndelete encrypted version? y/n :// ").lower() == "y"):
            _delete = True
            _secure = True

        #ask users if encrypted files should be seperate from raw files
        if (input("seperate encrypted files in different folders? y/n :// ").lower() == "y"):
            _seperate = True

        #sample time    
        start = time.time()
        
        print("\n")

        #perform function
        decrypt_directory(aes_dir,_delete,_secure,_seperate)
        
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):

            #define json attributes
            cur_fast_track['decrypt']['delete'] = _delete
            cur_fast_track['decrypt']['seperate'] = _seperate

            #dump json to file
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
                
elif (choice.lower() == "purge"):
    
    if (input(f"\nuse FastTrack settings? \nfilters: {cur_fast_track['purge']['types']} \ny/n? :// ").lower() == "y"):

        #load fast track settings
        _filters = cur_fast_track['purge']['types']
        _secure = True
        
        print("\n")

        #sample time
        start = time.time()

        #perform function
        purge_directory(aes_dir,_filters,_secure)
        
    else:
        
        _filters = []
        secure = False
        
        print("\nenter file extensions to be purged below and type none in console to stop adding extensions")
        
        
        #get filters from user
        inp = ""
        while True:
            inp = input("add a new extension to purge. :// ")
            if inp.lower() == "none":
                print("\n")
                break
            else:
                _filters.append(inp)

        _secure = True

        #sample time
        start = time.time()
        
        print("\n")

        #perfrom function
        purge_directory(aes_dir,_filters,_secure)

        #dump fasttrack settings
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['purge']['types'] = _filters
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
                
elif (choice.lower() == "obscure"):
    #sample time
    start = time.time()
    
    print("\n")

    #perform function
    obscure_directory(aes_dir)

elif (choice.lower() == "encrypt"):

    #hash key
    if (input("\nuse a hashed key? y/n :// ").lower() == "y"):
        to_hash = getpass.getpass("\nenter key to be hashed (input is hidden):// ")
        print("password: ",'*' * len(to_hash))
        password = hash_md5(to_hash)
        

    #raw key
    else:
        password = getpass.getpass("\nenter raw decryption key (input is hidden):// ")
        print("password: ",'*' * len(password))
    
    if (input(f"\nuse FastTrack settings? \ndelete: {cur_fast_track['encrypt']['delete']} \nbackup: {cur_fast_track['encrypt']['backup']} \ny/n? :// ").lower() == "y"):

        #load fast track settings
        _backup = cur_fast_track['encrypt']['backup']
        _delete = cur_fast_track['encrypt']['delete']
        _secure = False

        #perform function
        encrypt_directory(aes_dir,_delete,_secure,_backup)

        #sample time
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

        #sample time
        start = time.time()
        
        print("\n")

        #perform function
        encrypt_directory(aes_dir,_delete,_secure,_backup)

        #save settings to fastrack
        if (input("\nsave to fast track? y/n :// ").lower() == "y"):
            cur_fast_track['encrypt']['delete'] = _delete
            cur_fast_track['encrypt']['backup'] = _backup
            with open(config_dir,"w") as f:
                json.dump(cur_fast_track,f)
                f.close()
                
elif (choice.lower() == "swap"):
    
    if (input(f"\nuse FastTrack settings? \nfrom: {cur_fast_track['swap']['from']} \nto: {cur_fast_track['swap']['to']} \ny/n? :// ").lower() == "y"):
        #load fastrack settings
        _swap_from = cur_fast_track['swap']['from']
        _swap_to = cur_fast_track['swap']['to']

        #sample time
        start = time.time()

        #perform function
        swap_file_extensions(aes_dir,_swap_from,_swap_to)
        
    else:
        
        _swap_from = input("\nswap from e.g .png :// ")
        _swap_to = input("swap from e.g .jpg :// ")

        #check for invalid input
        if len(_swap_from) < 4 or len(_swap_to) < 4:
            print("\ninvalid input the program will exit in 5 seconds")
            time.sleep(5)
            sys.exit()

        #sample time
        start = time.time()

        #perform function
        swap_file_extensions(aes_dir,_swap_from,_swap_to)

        #save fastrack settings
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
new_file_size = size_to_rational(count_size(aes_dir))
end = time.time()
print(f"\ntime elapsed {end-start} seconds")
print(f"\nnet file gain: {new_num_files-num_files}\nnet folder gain: {new_num_folders-num_folders}\nnew file size: {new_file_size}\n")
print("-------------------------------------------console will close in 5 seconds--------------------------------------------")
time.sleep(5)

