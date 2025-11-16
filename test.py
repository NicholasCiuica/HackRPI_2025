from tkinter import Button, Frame
from PIL import Image, ImageTk

class Quit_Button(Button):
  def __init__(self):
    super().__init__()

    self.bQuit = Button(self.frame, text="Quit", command=self.quit)
    self.bQuit.pack(pady=20)