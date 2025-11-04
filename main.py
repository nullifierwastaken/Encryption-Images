from os import urandom, path, system, name
from PIL import Image
import sqlite3
import base64
import sys

if path.exists("keys.db") == False:
    db = sqlite3.connect("keys.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE keys (id INTEGER PRIMARY KEY AUTOINCREMENT,key STRING);")
    cursor.execute("CREATE TABLE password (password STRING);")
    password = input("Please input a password for the keys: ")
    passkey = base64.b64encode(urandom(len(password))).decode('utf-8')[:len(password)]
    encrypted_password = ""
    for i in range(len(password)):
        encrypted_password += chr(ord(password[i]) ^ ord(passkey[i]))

    cursor.execute("INSERT INTO password (password) VALUES (?)", (encrypted_password,))
    cursor.execute("INSERT INTO keys (key) VALUES (?)", (passkey,))
    db.commit()
    if name == "nt":
        system("icacls keys.db /grant %username%:rw")
        system("icacls keys.db /inheritance:d")
        system("icacls keys.db /remove *S-1-5-11 *S-1-5-18 *S-1-5-32-544 *S-1-5-32-545")
    else:
        system("chmod 600 keys.db")

while True:
    crypt = input("Encrypt or decrypt? (e/d) ").lower()
    if crypt == "e" or crypt == "d":
        break
    else:
        print('Please only input "e" or "d"')

if crypt == "e":
    message = input("Message: ")
    key = base64.b64encode(urandom(len(message))).decode('utf-8')[:len(message)]
    print(f'This is your key: {key}')
    db = sqlite3.connect("keys.db")
    cursor = db.cursor()
    cursor.execute("INSERT INTO keys (key) VALUES (?)", (key,))
    db.commit()
    print("Key added to local database")
    encrypted = ""
    for i in range(len(message)):
        encrypted += chr(ord(message[i]) ^ ord(key[i]))
    heights = []
    for c in encrypted:
        heights.append(ord(c)/256)
    iheight = int(round(max(heights), 0))
    if iheight < max(heights):
        iheight += 1
    img = Image.new(
            mode = "L",
            size = (len(encrypted), iheight),
            color = 0)
    for c in range(len(encrypted)):
        for h in range(iheight):
            if ord(encrypted[c]) > 255:
                n = 255
                temp = ord(encrypted[c]) - 255
            else:
                n = ord(encrypted[c])
                temp = 0
            img.putpixel((c, h), n)
            if temp == 0:
                break
    while True:
        try:
            name = input("Name to save to: ")
            img.save(name)
            break
        except:
            print("Please input a valid PNG image file name")

elif crypt == "d":
    db = sqlite3.connect("keys.db")
    cursor = db.cursor()
    while True:
        message = input("Please input image file with message: ")
        if path.exists(message):
            break
        else:
            print("No such file exists")

    entered = False
    while True:
        key = input('Please input key ID (enter "list" to list keys, type "add" to add keys, type "delete" to delete a key): ').lower()
        while True:
            if entered == True:
                break

            password = input("Please input password: ")
            passkey = cursor.execute("SELECT key FROM keys WHERE id = 1;").fetchone()
            correct_pass = cursor.execute("SELECT * FROM password;").fetchone()
            decrypt = ""
            for i in range(len(correct_pass[0])):
                decrypt += chr(ord(correct_pass[0][i]) ^ ord(passkey[0][i]))

            if decrypt == password:
                print("Correct password")
                entered = True
                break
            else:
                print("Incorrect password")

        passkey = None
        decrypt = None
        correct_pass = None
        if key == "list":
            l = cursor.execute("SELECT * FROM keys WHERE id > 1;").fetchall()
            for row in l:
                print(row)
        elif key == "add":
            k = input("Insert key: ")
            cursor.execute("INSERT INTO keys (key) VALUES (?);", (k,))
            print("Key added!")
            db.commit()
        elif key == "delete":
            while True:
                k = input("Enter key (cannot be 1): ")
                if k != "1":
                    break
                else:
                    print("Key 1 cannot be deleted as it is used to decrypt the password")
            cursor.execute("DELETE FROM keys WHERE id=?;", (k,))
            db.commit()
            print("Key deleted")
        elif key.isdigit():
            keystr = cursor.execute("SELECT key FROM keys WHERE id = ?;", (key,)).fetchone()[0]
            break
        else:
            print('Please input either "list", "add" or a number')

    numbers = []
    img = Image.open(message)
    for i in range(img.width):
        n = 0
        for j in range(img.height):
            n += img.getpixel((i,j))
        numbers.append(n)
    encrypted = ""
    for i in numbers:
        encrypted += chr(i)
    message = ""
    try:
        for i in range(len(encrypted)):
            message += chr(ord(encrypted[i]) ^ ord(keystr[i]))
    except:
        sys.exit("Incorrect key")
    print(message)
