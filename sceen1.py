from tkinter import*
import tkinter as tk
from tkinter import ttk
from screen2 import screen2
#from screen3 import screen3
class tkinterApp(tk.Tk):
     
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        self.frames = {}  
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.minsize(400,200)
        self.state('zoom')
        # creating a container
        
        container = tk.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
  
        frame = screen2(container, self)
        self.frames[screen2] = frame
  
        frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(screen2)
  
   
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
  
# first window frame startpage
app = tkinterApp()
app.mainloop()