from flask import *
import json
import os
import logging
import sqlite3
import uuid
import shutil
from datetime import datetime

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config.update(dict(
    DATABASE='database.db',
    USERS={}))


def authenticate(sessionhash):
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT username FROM sessions WHERE session = ?", (sessionhash,))
        results = cur.fetchall()
        if len(results) == 0:
            return False, ""
        else:
            stored_username = results.pop()
            return True, stored_username[0]


def is_admin(sessionhash):
    valid_sess = authenticate(sessionhash)
    db_connect = sqlite3.connect("database.db")
    if valid_sess[0]:
        with db_connect:
            cur = db_connect.cursor()
            cur.execute("SELECT user_role FROM users WHERE username = ?", (valid_sess[1],))
            results = cur.fetchall()
            if int(results[0][0]) == 1:
                return True
            else:
                return False
    else:
        return False


@app.route('/signup/<username>/<passhash>')
def signup(username, passhash):
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        results = cur.fetchall()

        if len(results) == 0:
            cur.execute("INSERT INTO users (username, passwordhash, user_role, sync) VALUES (?, ?, ?, ?)",
                        (username, passhash, 0, datetime.now()))
            mkdir(username)
            print (username + " has successfully signed up to OneDir")
            return json.dumps(("200", "GOOD"))
        else:
            print (username + "was not signed up!")
            return json.dumps(("404", "BAD"))


@app.route('/signin/<username>/<passhash>')
def signin(username, passhash):
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT passwordhash FROM users WHERE username = ?", (username,))

        results = cur.fetchall()
        if len(results) == 0:
            return json.dumps(("404", "BAD"))
        else:
            stored_hash = results.pop()
            if stored_hash[0] == passhash:
                session_id = uuid.uuid4().hex
                temp_date = datetime.now()
                cur.execute("INSERT INTO sessions (username, session, date) VALUES (?, ?, ?)",
                            (username, session_id, temp_date.strftime('%Y/%m/%d %H:%M:%S')))
                print (username + " has signed into OneDir")
                return json.dumps(("200",session_id))
            else:
                print ("Error while " + username + " tried to sign in!")
                return json.dumps(("401","BAD"))


@app.route('/changepass/<username>/<passhash>/<sessionhash>')
def changepass(username, passhash, sessionhash):
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        if is_admin(sessionhash):
            cur.execute("UPDATE users SET passwordhash = ? WHERE username = ?", (passhash, username))
            return json.dumps("200")
        auth_user = authenticate(sessionhash)

        if auth_user[0]:
            cur_user = auth_user[1]
            if username == cur_user:
                cur.execute("UPDATE users SET passwordhash = ? WHERE username = ?", (passhash, cur_user))
                print (username + "has changed their password!")               
                return json.dumps(("200"))
            else:
                print ("Error occured while " + username + " tried to change their password!")
                return json.dumps(("404","BAD"))
        else:
            print ("Error occured while " + username + " tried to change their password!")
            return json.dumps(("404","BAD"))


#Invoked will create a new directory with given username
#@app.route('/mkdir/<username>')
def mkdir(username):
    """Creates a directory in the user's server-side OneDir directory"""
    full_filename = os.path.join("storage", username)
    if os.path.exists(full_filename):
        return username + " already exists."
    else:
        os.mkdir(full_filename)
        return "Directory for " + username + " has been created."


@app.route('/timestamp/<sessionhash>')
def timestamp(sessionhash):
    user = authenticate(sessionhash)
    if user[0]:
        db_connect = sqlite3.connect("database.db")
        with db_connect:
            cur = db_connect.cursor()
            cur.execute("SELECT sync FROM users WHERE username = ?", (user[1],))
            ret = cur.fetchall()
            if len(ret) == 0:
                return json.dumps(("401", "NONE"))
            else:
                res = ret.pop()
                return json.dumps(("200", res[0]))
    else:
        return json.dumps("400", "BAD")


@app.route('/snapshot/<sessionhash>', methods=['GET', 'POST'])
def snapshot(sessionhash):
    if request.method == 'POST':
        user = authenticate(sessionhash)

        if user[0]:
            db_connect = sqlite3.connect("database.db")
            with db_connect:
                cur = db_connect.cursor()
                date = str(datetime.now())
                cur.execute("DELETE FROM snaptime WHERE username = ?", (user[1],))
                cur.execute("INSERT INTO snaptime (username, time_stamp, snapshot) VALUES (?, ?, ?)", (user[1],date, request.data))
            return json.dumps(("200", date))
        else:
            return json.dumps(("400", "BAD"))
    else:
        print request.method

@app.route('/get-snapshot/<sessionhash>')
def get_snapshot(sessionhash):

    user = authenticate(sessionhash)

    if user[0]:
        db_connect = sqlite3.connect("database.db")
        with db_connect:
            cur = db_connect.cursor()
            cur.execute("SELECT snapshot FROM snaptime WHERE username = ?", (user[1],))
            row = cur.fetchone()
            if row is not None:
                return json.dumps(("200", row[0]))
            else:
                return json.dumps(("400", "BAD"))
    else:
        return json.dumps(("400", "BAD"))


#upload file into user account
@app.route('/upload-file/<sessionhash>/<path:filename>', methods=['GET', 'POST'])
def upload_file(sessionhash, filename):
    if request.method == 'POST':
        user = authenticate(sessionhash)
        if user[0]:
            file = request.files['file']
            user_path = os.path.join("storage", user[1])
            file.save(os.path.join(user_path, filename))

            db_connect = sqlite3.connect("database.db")
            with db_connect:
                cur = db_connect.cursor()
                cur.execute("UPDATE users set sync = ? WHERE username = ?", (datetime.now(), user[1]))
            print "File was successfully uploaded"
            return json.dumps(("200", "OK"))
        else:
            print "Error occured while uploading the file!"
            return json.dumps(("400", "BAD"))


#upload file into user account
@app.route('/new-dir/<sessionhash>/<path:filepath>', methods=['GET', 'POST'])
def new_dir(sessionhash, filepath):
    user = authenticate(sessionhash)

    if user[0]:
        user_path = os.path.join("storage", user[1])
        if not os.path.exists(user_path + "/" + filepath):
            os.makedirs(user_path + "/" + filepath)

        db_connect = sqlite3.connect("database.db")
        with db_connect:
            cur = db_connect.cursor()
            cur.execute("UPDATE users set sync = ? WHERE username = ?", (datetime.now(), user[1]))
        print "New directory has been created."
        return json.dumps(("200", "OK"))
    else:
        print "Error occured during creation of new directory."
        return json.dumps(("400", "BAD"))


@app.route('/delete-file/<sessionhash>/<path:file>')
def delete_file(sessionhash, file):
    user = authenticate(sessionhash)
    if user[0]:
        userpath = os.path.join("storage", user[1], file)
        if os.path.exists(userpath):
            os.remove(userpath)
            db_connect = sqlite3.connect("database.db")
            with db_connect:
                cur = db_connect.cursor()
                cur.execute("UPDATE users set sync = ? WHERE username = ?", (datetime.now(), user[1]))
            print "User has successfully deleted file."
            return json.dumps(("200", "OK"))
        else:
            return json.dumps(("201", "OK"))
    else:
        print "User was unable to delete file"
        return json.dumps(("400"), "BAD")

@app.route('/delete-dir/<sessionhash>/<path:filepath>')
def delete_dir(sessionhash, filepath):
    user = authenticate(sessionhash)
    if user[0]:
        user_path = os.path.join("storage", user[1], filepath)
        if os.path.exists(user_path):
            shutil.rmtree(user_path)
            db_connect = sqlite3.connect("database.db")
            with db_connect:
                cur = db_connect.cursor()
                cur.execute("UPDATE users set sync = ? WHERE username = ?", (datetime.now(), user[1]))
            print "User has successfully deleted user directory"
            return json.dumps(("200", "OK"))
        else:
            return json.dumps(("201", "OK"))
    else:
        print "Error occured while User tried to delete directory."
        return json.dumps(("400"), "BAD")


@app.route('/download-file/<sessionhash>/<path:filepath>')
def download_file(sessionhash, filepath):
    user = authenticate(sessionhash)
    if user[0]:
        return send_file(os.path.join("storage", user[1], filepath))
    else:
        print "File was not successfully downloaded"
        return json.dumps(("400"), "BAD")

@app.route('/is-dir/<sessionhash>/<path:filepath>')
def is_dir(sessionhash, filepath):
    user = authenticate(sessionhash)
    if user[0]:
        return json.dumps(("200", os.path.isdir(os.path.join("storage", user[1], filepath))))
    else:
        return json.dumps("400", "BAD")


def recursealldir(path, filename):
    in_filename = os.path.join(path,str(filename))
    holder = {}
    if (os.stat(in_filename).st_nlink) < 2:
        holder[str(filename)] = os.path.getsize(in_filename)
        return str(holder)
    else :
        subfolder ={}

        for infile in os.listdir(in_filename):
            in_filename2 = os.path.join(in_filename,str(infile))

            if ((os.stat(in_filename2).st_nlink) < 2):

                subfolder[str(infile)] = os.path.getsize(in_filename2)

            else:
                subfolder[str(infile)] = recursealldir(in_filename,str(infile))
        oldholder = str(subfolder)
        temp = oldholder.replace("\\", "")
    return temp


@app.route('/stat/<username>')
def stat(username):
    """Returns the size and number of files stored in a directory on the server"""
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        results = cur.fetchall()
        if len(results) == 0:
            print "This user does not exist!"
            return json.dumps(("400", "User does not exist"))
        else:
            filename = os.path.join("storage", username)
            string = recursealldir(os.path.join("storage"), username)
            foldercount = string.count("{")-1
            filescount = string.count(":") - foldercount
            filesize = os.path.getsize(filename)
            result = "User: " +username + " [ Folder count: " + str(foldercount) \
                   + " , File count:" + str(filescount) + ", Total size: "+ str(filesize) + " kb]"
            return json.dumps(("200",result))


@app.route('/remove_user/<username>/<delfiles>')
def remove_user(username, delfiles):
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", (username,))
        if delfiles:
            user_path = os.path.join("storage", username)
            if os.path.exists(user_path):
                shutil.rmtree(user_path)
        print "User " + username + " has been successfully removed!"
        return json.dumps(("200", "User: " + username + " was successfully removed."))


@app.route('/get-file-data/<filename>')
def get_file_data(filename):
    full_filename = os.path.join(filename)
    if not os.path.exists(full_filename):
        ret_value = { "result" : -1, "msg" : "file does not exist"}
    else:
        with open(full_filename, "rb") as in_file:
            snippet = in_file.read()
        file_size = os.path.getsize(full_filename)
        ret_value = { "result" : 0, "size" : file_size, "value" : snippet}
    return json.dumps(ret_value)


@app.route('/file-list/<sessionhash>')
def file_list(sessionhash):
    user = authenticate(sessionhash)
    if user[0]:
        files_list = []
        user_path = os.path.join("storage", user[1])
        for root, subFolders, files in os.walk(user_path):
            for file in files:
                files_list.append(os.path.join(root, file))
        return json.dumps("200", files_list)
    else:
        return json.dumps("400", "BAD")


@app.route('/view_report')
def view_report():
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT username FROM users ", ())
        results = cur.fetchall()
	user_list = []
        for uni_results in results:
            user_list.append(uni_results[0].encode('ascii', 'ignore'))
    return json.dumps(("200", user_list))


@app.route('/view_log')
def view_log():
    db_connect = sqlite3.connect("database.db")
    with db_connect:
        cur = db_connect.cursor()
        cur.execute("SELECT username, date FROM sessions ", ())
        log_list = cur.fetchall()
	print log_list
    return json.dumps(("200", log_list))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
