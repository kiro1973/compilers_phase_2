from tkinter.tix import IMAGETEXT
#from DFA import Dfa
import tkinter as tk
from tkinter import ttk
from tkinter import*
#from PIL import Image,ImageTk
import sys,re
print(sys.executable)
class screen2(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.newTestflag=1
        self.button1 = ttk.Button(self, text ="test",
        command = self.m)
        self.new_test_button = ttk.Button(self, text ="test",
        command = self.newTest)
        self.button1.place(x=10,y=300)
        self.new_test_button.place(x=300,y=500)
        self.name = StringVar()
        self.textEntry=Entry(self,textvariable=self.name,width=40,font=('Georgia 12'))
        self.textEntry.place(x=13,y=250,height=28)
        
        self.resultLabel=ttk.Label(self,text="",font=('Helvetica 6 bold'))
        self.resultLabel.place(x=10,y=700)
    def m (self):
        self.button1.place_forget()
        
    def newTest(self):
        self.button1.place(x=10,y=300)
        
        


    