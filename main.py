from tkinter import *
from tkinter import messagebox
from tkinter import PhotoImage

from PIL import Image, ImageTk

class Widget(Tk):
  def __init__(self):
    super().__init__()

    # --- Window setup ---
    self.overrideredirect(True) # removes title bar
    self.attributes("-topmost", True)

     # --- OS-specific transparency ---
    # Windows
    try:
      self.wm_attributes("-transparentcolor", "pink")
    except TclError:
      pass

    # position the pet
    width = 160
    height = 200

    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()

    # calculate position x and y coordinates
    x = screen_width - width
    y = screen_height - height - 50
    self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    self.frame = Frame(self, bg='pink')
    self.frame.pack()

    # quit button
    self.bQuit = Button(self.frame, text="Quit", command=self.quit)
    self.bQuit.pack(pady=20)

    # create the image, and the label that holds it
    img = Image.open("assets/test_bird.png").convert("RGBA")
    self.photo = ImageTk.PhotoImage(img)
    self.label = Label(self.frame, image=self.photo, bg="pink")
    self.label.pack()

    # --- Make window draggable ---
    #self.label.bind("<Button-1>", self.start_move)
    #self.label.bind("<B1-Motion>", self.do_move)


app = Widget()
app.mainloop()