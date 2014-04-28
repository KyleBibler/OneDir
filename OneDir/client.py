from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.utils import dirsnapshot
import hashlib
import requests
import yaml
import os
from datetime import time, datetime, date
import time
import urllib2
from Queue import *
from threading import Thread
import threading
import pickle
from os.path import expanduser


HOST = 'http://192.168.1.153:5000/'

home = ""
session = ""
holderQueue = Queue()
currenttime = ""
sync = True
dirsnap = dirsnapshot.DirectorySnapshot


def job_processor(name, stop_event):
    takesnap = False
    while (1):
        if stop_event.is_set():
            break
        elif holderQueue.empty() == False:
            if sync == True:
                try:
                    job = holderQueue.get()
                    if job[0] == "Upload":
                        r = requests.post(HOST + "upload-file/" + session + "/" + secure_filepass(job[1]), files={'file': open(job[1], 'rb')})
                        result = yaml.load(r.text)
                        if result[0] == "200":
                            print ("Uploaded file: " + secure_filepass(job[1]))
                            takesnap = True
                        elif result[0] == "400":
                            print ("Error: Authentication Failure")
                    elif job[0] == "Delete":
                        r = requests.get(HOST + "delete-file/" + session + "/" + secure_filepass(job[1]))
                        result = yaml.load(r.text)
                        if result[0] == "200":
                            takesnap = True
                            print ("Deleted file: " + secure_filepass(job[1]))
                        elif result[0] == "400":
                            print ("Error: Authentication Failure")
                    elif job[0] == "New Dir":
                        r = requests.get(HOST + "new-dir/" + session + "/" + secure_filepass(job[1]))
                        result = yaml.load(r.text)
                        if result[0] == "200":
                            takesnap = True
                            print ("Directory Created: " + secure_filepass(job[1]))
                        elif result[0] == "400":
                            print ("Error: Authentication Failure")
                    elif job[0] == "Remove Dir":
                        r = requests.get(HOST + "delete-dir/" + session + "/" + secure_filepass(job[1]))
                        result = yaml.load(r.text)
                        if result[0] == "200":
                            takesnap = True
                            print ("Directory Created: " + secure_filepass(job[1]))
                        elif result[0] == "400":
                            print ("Error: Authentication Failure")
                    elif job[0] == "Download":
                        r = urllib2.urlopen(HOST + "download-file/" + session + "/" + secure_filepass(job[1]))
                        print "hello"
                        print os.path.join(home, job[1])
                        with open(os.path.join(home, job[1]), 'wb') as f:
                            print "hello"
                            f.write(r.read())

                    holderQueue.task_done()

                except:
                    print ("Error: Could not preform this task")

        elif holderQueue.empty() == True & takesnap == True:
            if  sync == True:
                takesnap = False
                global currenttime

            dirsnap = dirsnapshot.DirectorySnapshot(home, recursive=True)
            send = pickle.dumps(dirsnap)
            r = requests.post(HOST + "snapshot/" + session, data=send)
            result = yaml.load(r.text)
            if result[0] == "200":
                currenttime = result[1]
            elif result[0] == "400":
                print ("Error: Authentication Failure")
        else:
            server_sync()

        stop_event.wait(1)

def secure_filepass(filename):
    return filename.replace(home,"")

def server_sync():
    global currenttime
    dummy = True
    temp_time = ""
    r = requests.get(HOST + "timestamp/" + session)
    result = yaml.load(r.text)
    if result[0] == "200":
        # print currenttime + " " + result[1]
        temp_time = currenttime
        if currenttime != result[1]:
            r = requests.get(HOST + "get-snapshot/" + session)
            result = yaml.load(r.text)

            if result[0] == "200":
                server_snap = pickle.loads(result[1])
                paths_given = []
                ONCE = False
                ROOT = ""
                for path in server_snap.paths:
                    # print path
                    paths_given.append(path)
                paths = sorted(paths_given)
                for path in paths:
                    if ONCE:
                        temphome = home[:-1]
                        path = path.replace(ROOT, temphome)
                        # print path
                        if os.path.exists(path) == False:
                            # print path
                            r = requests.get(HOST + "is-dir/" + session + "/" + secure_filepass(path))
                            result = yaml.load(r.text)
                            if result[0] == "200":
                                if result[1]:
                                    os.makedirs(path)
                                else:
                                    holderQueue.put(("Download", path))
                            elif result[0] == "400":
                                dummy = False #print ("Error: Authentication Failure")
                        else:
                            currenttime = temp_time

                    else:
                        ONCE = True
                        ROOT = path
                        # print "ROOT: " + ROOT
            elif result[0] == "400":
                dummy = False #print ("Error: Authentication Failure")
    elif result[0] == "401":
        dummy = False #print "No timestamp"
    elif result[0] == "400":
        dummy = False #print ("Error: Authentication Failure")

class OneDirFileHandles(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print ("Directory: " + event.src_path + " has been created locally.")
            holderQueue.put(("New Dir", event.src_path))
        else:
            print ("File: " + event.src_path + " has been created locally.")
            holderQueue.put(("Upload", event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print ("Directory: " + event.src_path + " has been modified locally.")
            holderQueue.put(("Remove Dir", event.src_path))
            holderQueue.put(("New Dir", event.src_path))
        else:
            print ("File: " + event.src_path + " has been modified locally.")
            holderQueue.put(("Delete", event.src_path))
            holderQueue.put(("Upload", event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            print ("Directory: " + event.src_path + " has been moved locally.")
            holderQueue.put(("Remove Dir", event.src_path))
            holderQueue.put(("New Dir", event.src_path))
        else:
            print ("File: " + event.src_path + " has been moved locally.")
            holderQueue.put(("Delete", event.src_path))
            holderQueue.put(("Upload", event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print ("Directory: " + event.src_path + " has been deleted locally.")
            holderQueue.put(("Remove Dir", event.src_path))
        else:
            print ("File: " + event.src_path + " has been deleted locally.")
            holderQueue.put(("Delete", event.src_path))

def new_user():
    print "Creating new account. Please fill out the following details:"
    username = raw_input('Username: ')
    password = hashlib.sha224(raw_input('Password: ')).hexdigest()
    confirm = hashlib.sha224(raw_input('Confirm Password: ')).hexdigest()
    if password == confirm :
        r = requests.get(HOST + "signup/" + username + "/" + password)

    print ("You have successfully signed up!")
    print ("You can find the folder to use for OneDir in in your User C Drive in a folder named OneDir with your username in it")
    global home
    home = expanduser("~") + "/OneDir"
    if os.path.exists(home + "/" + username):
        home = home + "/" + username + "/"
    elif os.path.exists(home):
        os.mkdir(home + "/" + username)
        home = home + "/" + username +"/"
    else:
        os.makedir(home)
        os.mkdir(home + "/" + username)
        home = home + "/" + username +"/"
    init()

def sign_in():
    global home
    global session
    global currenttime
    global dirsnap
    print "Signing in. Please fill out the following details:"
    username = raw_input('Username: ')
    password = hashlib.sha224(raw_input('Password: ')).hexdigest()
    r = requests.get(HOST + "signin/" + username + "/" + password)
    result = yaml.load(r.text)
    if result[0] == "200" and not username == "admin":
        print "Successfully signed in! Your local folder has been put here: "
        currenttime = datetime.now()
        if os.path.exists(home + "/" + username):
            home = home + "/" + username + "/"
            print home
            runtime()
        elif os.path.exists(home):
            sesson = result[1]
            os.mkdir(home + "/" + username)
            home = home + "/" + username + "/"
            print home
            runtime()
        else:
            session = result[1]
            os.mkdir(home)
            os.mkdir(home + "/" + username)
            home = home + "/" + username + "/"
            print home
            runtime()

        currenttime = time.time()
        dirsnap = dirsnapshot.DirectorySnapshot(home, recursive=True)
    elif result[0] == "200" and username == "admin":
        print "Signed in to admin account."
        session = result[1]
        admin_menu()
    elif result[0] == "401":
        print "ERROR: Password is incorrect! Please try again!"
        init()
    elif result[0] == "404":
        print "ERROR: Username was not found! Please try again!"
        init()

#somehow need to give the users and admins the option to do this after sign in
def change_pass():
    print "To change password, please input"
    username = raw_input('Username: ')
    oldpass = hashlib.sha224(raw_input('Old Password: ')).hexdigest()
    password = hashlib.sha224(raw_input('New Password: ')).hexdigest()
    r = requests.get(HOST + "signin/" + username + "/" + oldpass)
    result = yaml.load(r.text)
    if result[0] == "200":
        session = result[1]
    elif result[0] == "401":
        print "ERROR: Password is incorrect! Please try again!"
        init()
    elif result[0] == "404":
        print "ERROR: Username was not found! Please try again!"
        init()

    r = requests.get(HOST + "changepass/" + username + "/" + password + "/" + session)
    result = yaml.load(r.text)

    if result == "200":
        print "Password successfully changed!"
        init()
    else:
        print "ERROR: Username not found! Please try again!"
        init()


def synchronize():
    global sync
    global home
    global session
    global holderQueue
    global currenttime
    global dirsnap
    if sync:
        print "1 : Turn off Autosync!"
        print "2 : Change my password!"
        print "3 : Logout"
        selection = int(raw_input("Option Selected: "))
        if str(selection) is "1":
            sync = False
        elif str(selection) is "2":
            change_pass()
        elif str(selection) is "3":
            home = ""
            session = ""
            holderQueue = Queue()
            currenttime = ""
            sync = True
            dirsnap = dirsnapshot.DirectorySnapshot
            start_menu()

    else:
        print "1 : Turn on Autosync!"
        print "2 : Change my password!"
        print "3 : Logout"
        selection = int(raw_input("Option Selected: "))
        if str(selection) is "1":
            sync = True
        elif str(selection) is "2":
            change_pass()
        elif str(selection) is "3":
            home = ""
            session = ""
            holderQueue = Queue()
            currenttime = ""
            sync = True
            dirsnap = dirsnapshot.DirectorySnapshot
            start_menu()
    

def admin_menu():
    print "Welcome to OneDir! Please Select from the following options!"
    print "1 : View Users on Server"
    print "2 : View Statistics for Server"
    print "3 : View Connection Log"
    print "4 : Remove a User"
    print "5 : Change a User's Password"
    selection = int(raw_input("Option Selected: "))
    if selection == 1:
        view_report()
    elif selection == 2:
        user_stat()
    elif selection == 3:
        view_log()
    elif selection == 4:
        remove_user()
    elif selection == 5:
        admin_change_pass()
    else:
        print "Unrecognized command."
    if selection != 5:
        admin_menu()
    admin_menu()

def view_report():
    r = requests.get(HOST+"view_report")
    result = yaml.load(r.text)

    if result[0] == "400":
        print "Unsuccessful retrieval of user list"
    else:
        #print "Why"
        print result[1]

def user_stat():
    print "To see stats of user, please input"
    username = raw_input('Username: ')
    r = requests.get(HOST+"stat/"+username)
    result = yaml.load(r.text)

    if result[0] == "400":
        print "Unsuccessful retrieval of " + username + " stats"
    elif result[0] == "200":
        print result[1]
    else:
        print "Successfully retrieved " + username + " stats"

def view_log():
    r = requests.get(HOST+"view_log")
    result = yaml.load(r.text)

    if result[0] == "400":
        print "Unsuccessful retrieval of server log"
    else:
        print result[1]

def remove_user():
    print "To permanently remove a user, please input"
    username = raw_input('Username: ')
    delfiles = raw_input('Delete files for this user? 1 for yes, 0 for no: ')
    r = requests.get(HOST+"remove_user/"+username + "/" + delfiles)
    result = yaml.load(r.text)

    if result [0] == "400":
        print "Error: Could not remove " + username + "."
    else:
        print "Succesfully removed " + username + "."

def admin_change_pass():
    print "To change user's password, please input"
    username = raw_input('Username: ')
    password = hashlib.sha224(raw_input('New Password: ')).hexdigest()

    print session
    r = requests.get(HOST + "changepass/" + username + "/" + password + "/" + session)
    result = yaml.load(r.text)

    if result == "200":
        print "Password successfully changed."
    else:
        print "ERROR: Username was not found! Please try again!"

def runtime():
    print "Setup Complete: Intializing OneDir!"
    event_handler = OneDirFileHandles()
    observer = Observer()
    #print home

    #the recursive variable here determines whether the program watches subdirectories
    observer.schedule(event_handler, home, recursive=True)
    observer.start()
    stop = threading.Event()
    th = Thread(target=job_processor, args=("Thread",stop))
    th.setDaemon(True)
    th.start()

    try:
        while True:
            synchronize()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        stop.set()
    observer.join()
    th.join()

def start_menu():
    print "Welcome to OneDir! Please Select from the following options!"
    print "1 : Create New Account!"
    print "2 : Sign into Account!"
    print "3 : Change my password!"
    selection = int(raw_input("Option Selected: "))
    if selection == 1:
        new_user()
    elif selection == 3:
        change_pass()
    else:
        sign_in()

def init():
    global home
    home = expanduser("~") + "/OneDir"
    if os.path.exists(home):
        print "If your username is in the list below, please enter your password, if not type 0"
        for filename in os.listdir(home):
            print filename
        password = hashlib.sha224(raw_input('Password: ')).hexdigest()
        if password == hashlib.sha224('0').hexdigest():
            start_menu()
        else:
            global session
            global currenttime
            global dirsnap
            for filename in os.listdir(home):
                r = requests.get(HOST + "signin/" + filename + "/" + password)
                result = yaml.load(r.text)
                if result[0] == "200" and not filename == "admin":
                    home += "/" + filename + "/"
                    session = result[1]
                    runtime()
                elif result[0] == "200" and filename == "admin":
                    print "Signed in to the admin account."
                    session = result[1]
                    admin_menu()
            start_menu()
    else:
        start_menu()

if __name__ == '__main__':
    init()
