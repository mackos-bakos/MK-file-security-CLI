import subprocess 
import os
import time
import random
import sys
aescrypt_path = 'C:/Program Files/AESCrypt/aescrypt.exe'
def openfolderprompt():
    os.chdir(os.getcwd())
    files = os.listdir()
    paths = []
    for file in files:
        if os.path.isdir(file):
            paths.append(file)
    return paths
#def openfileprompt(): # works
#    dlg = win32ui.CreateFileDialog(1)
#    dlg.SetOFNInitialDir(os.getcwd())
#    dlg.DoModal()
#    directory = dlg.GetPathName()
#    return directory
def PurgeFiles2(folder,accepted_file_types):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if (os.path.splitext(file)[1] not in accepted_file_types):
                continue
            try:
                os.remove(os.path.join(root, file))
            except:
                print("failed to remove :", os.path.abspath(os.path.join(root, file)))
        print("traversal branch completed.",root, len(files), "files purged")
    print("finished purging", folder)
def decryptfolder2(_file,delete):
    for root, dirs, files in os.walk(_file):
        for file in files:
            if (os.path.splitext(file)[1] != ".aes"):
                continue
            subprocess.run([aescrypt_path, '-d', '-p', password, os.path.join(root, file)])
            if delete:
                os.remove(os.path.join(root, file))
        print("traversal branch completed.",root, len(files), "files decrypted")
    print("finished decrypting", _file)
def encryptfolder(_file,delete):
    for root, dirs, files in os.walk(_file):
        for file in files:
            if (os.path.splitext(file)[1] == ".aes"):
                continue
            subprocess.run([aescrypt_path, '-e', '-p', password, os.path.join(root, file)])
            if delete:
                os.remove(os.path.join(root, file))
        print("traversal branch completed.",root, len(files), "files encrypted")
    print("finished encrypting", _file)
def obscurefiles(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            extension = os.path.splitext(file)[1]
            newname = ""
            
            for x in range(7):
                newname+=chr(random.randint(128,512))
            if len(os.path.splitext(file)[0].split(".")) > 1:
                newname += "." + os.path.splitext(file)[0].split(".")[1]
                
            newname += extension
            os.rename(os.path.join(root, file), os.path.join(root, newname))
        print("traversal branch completed.",root, len(files), "files obscured")
    print("finished obscuring",folder)
print("this program should be placed one level above the desired folder")

dirs = openfolderprompt()
if len(dirs) == 0:
    print("no directories in this folder, please change the location, the program will exit in 5 seconds")
    time.sleep(5)
    sys.exit()
print("found", len(dirs), "directories")

for dr in dirs:
    print(str(dirs.index(dr) + 1) + ".", os.path.join(os.getcwd(), dr))
    
dirsptr = len(dirs) + 1
while dirsptr > len(dirs):
    dirsptr = int(input("enter choice of directory ://"))
print("selected",os.path.join(os.getcwd(), dirs[dirsptr - 1]))

aes_dir = os.path.join(os.getcwd(), dirs[dirsptr - 1])
choice = input("enter choice decrypt/purge/obscure/encrypt ://")
if (choice.lower() == "decrypt"):
    password = input("enter decryption key ://")
    _delete = False
    if (input("delete encrypted version? y/n ://").lower() == "y"):
        _delete = True
    decryptfolder2(aes_dir,_delete)
if (choice.lower() == "purge"):
    filters = []
    print("enter file extensions to be purged below and type none in console to stop adding extensions")
    inp = ""
    while inp.lower() != "none":
        inp = input("add a new extension to purge e.g .png ://")
        if inp.lower() != "none":
            filters.append(inp)
    print("selected filters:")
    for filt in filters:
        print(str(filters.index(filt) + 1) + ".", filt)
    PurgeFiles2(aes_dir,filters)
if (choice.lower() == "obscure"):
    obscurefiles(aes_dir)
if (choice.lower() == "encrypt"):
    password = input("enter encryption key ://")
    _delete = False
    if (input("delete unencrypted version? y/n ://").lower() == "y"):
        _delete = True
    encryptfolder(aes_dir,_delete)
print("-------------------------------------------console will close in 5 seconds--------------------------------------------")
time.sleep(5)
