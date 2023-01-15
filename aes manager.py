import subprocess 
import os
import time
import random
import sys
aescrypt_path = 'C:/Program Files/AESCrypt/aescrypt.exe'
appdata_directory = os.path.join(os.getenv('APPDATA'), 'backups')
if not os.path.exists(appdata_directory):
    os.makedirs(appdata_directory)
    print(f"created a directory at {appdata_directory}")
def copy_file_to(source,destination):
    with open(source, 'rb') as read_file: 
        with open(destination, 'wb') as write_file: 
            for line in read_file: 
                write_file.write(line) 
def get_all_dirs(directory):
    return  [file for file in os.listdir(directory) if os.path.isdir(file)]
def overwrite_data(file):
    for i in range(5):
        with open(file, 'wb') as f:
            f.write(os.urandom(os.path.getsize(file)))
def purge_directory(folder,accepted_file_types,secure):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] not in accepted_file_types):
                continue
            if (secure):
                overwrite_data(os.path.join(root, file))
            os.remove(os.path.join(root, file))
        print(f"succesful operation completed at {root}, {len(files)} files traversed")
    print(f"finished purging {folder}")
def decrypt_directory(folder,delete,secure):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] != ".aes"):
                continue
            subprocess.run([aescrypt_path, '-d', '-p', password, os.path.join(root, file)])
            if delete and os.path.exists(os.path.join(root, file[:-4])):
                if (secure):
                    overwrite_data(os.path.join(root, file))
                os.remove(os.path.join(root, file))
        print(f"succesful operation completed at {root}, {len(files)} files traversed")
    print(f"finished decrypting {folder}")
def encrypt_directory(folder,delete,secure,backup):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] != ".aes"):
                subprocess.run([aescrypt_path, '-e', '-p', password, os.path.join(root, file)])
                if backup:
                    copy_file_to(os.path.join(root, file) + ".aes",os.path.join(appdata_directory,file) + ".aes")
                if delete and os.path.exists(os.path.join(root, file + ".aes")):
                    if (secure):
                        overwrite_data(os.path.join(root, file))
                    os.remove(os.path.join(root, file))
        print(f"succesful operation completed at {root}, {len(files)} files traversed")
    print(f"finished encrypting {folder}")
def obscure_directory(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            name, ext = os.path.splitext(file)
            newname = ''.join(chr(random.randint(128, 512)) for _ in range(7))
            if len(name.split('.')) > 1:
                newname += '.' + name.split('.')[1]
            newname += ext
            os.rename(os.path.join(root, file), os.path.join(root, newname))
        print(f"succesful operation completed at {root}, {len(files)} files traversed")
    print(f"finished obscuring {folder}")
    
dirs = get_all_dirs(os.getcwd())
if not dirs:
    print("No directories in this folder, please change this program's location. The program will exit in 5 seconds.")
    time.sleep(5)
    sys.exit()

print(f"{len(dirs)} directories discovered in directory {os.getcwd()}")

for i, dr in enumerate(dirs):
    print(f"{i+1}. {os.path.join(os.getcwd(), dr)}")

while True:
    dirsptr = int(input("Choose directory: "))
    if 0 < dirsptr <= len(dirs):
        break

aes_dir = os.path.join(os.getcwd(), dirs[dirsptr - 1])
print(" decrypt - decrypts all .aes files in the selected directory")
print(" purge   - deletes selected file extensions in the directory")
print(" obscure - randomises all file names  the selected directory")
print(" encrypt - encrypts all non .aes file types in the directory")
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

else:
    print("nothing selected. program will exit in 5 seconds")
    time.sleep(5)
    sys.exit()

end = time.time()
print("time elapsed", end-start, "seconds")
print("-------------------------------------------console will close in 5 seconds--------------------------------------------")
time.sleep(5)

#def openfileprompt(): # works
#    dlg = win32ui.CreateFileDialog(1)
#    dlg.SetOFNInitialDir(os.getcwd())
#    dlg.DoModal()
#    directory = dlg.GetPathName()
#    return directory
