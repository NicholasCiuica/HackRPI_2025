from tkinter import *
from tkinter import messagebox
from tkinter import PhotoImage
import os
import time

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
    self.width = 160
    self.height = 200

    self.screen_width = self.winfo_screenwidth()
    self.screen_height = self.winfo_screenheight()

    # calculate position x and y coordinates
    self.x = self.screen_width - self.width
    self.y = self.screen_height - self.height - 50
    self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x, self.y))
    
    # Movement direction (-1 for left, 1 for right)
    self.direction = -1

    self.frame = Frame(self, bg='pink')
    self.frame.pack()

    # quit button
    self.bQuit = Button(self.frame, text="Quit", command=self.quit)
    self.bQuit.pack(pady=20)

    # Load GIF frames
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gif_path = os.path.join(script_dir, "assets", "spinCat.gif")
    
    self.frames = []
    gif = Image.open(gif_path)
    
    # Extract all frames from the GIF
    try:
      while True:
        frame = gif.copy().convert("RGBA")
        self.frames.append(ImageTk.PhotoImage(frame))
        gif.seek(gif.tell() + 1)
    except EOFError:
      pass  # End of GIF frames
    
    # Animation variables
    self.frame_index = 0
    self.timestamp = time.time()
    
    # create the label that holds the image
    self.label = Label(self.frame, image=self.frames[0], bg="pink")
    self.label.pack()

    # --- Make window draggable ---
    #self.label.bind("<Button-1>", self.start_move)
    #self.label.bind("<B1-Motion>", self.do_move)
    
    # Start the animation
    self.update_animation()
  
  def update_animation(self):
    # move by one pixel in current direction
    self.x += self.direction
    
    # Check boundaries and reverse direction if needed
    if self.x <= 0:
      self.x = 0
      self.direction = 1  # Change to move right
    elif self.x >= self.screen_width - self.width:
      self.x = self.screen_width - self.width
      self.direction = -1  # Change to move left
    
    # advance frame if 50ms have passed
    if time.time() > self.timestamp + 0.05:
      self.timestamp = time.time()
      # advance the frame by one, wrap back to 0 at the end
      self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    # update window position
    self.geometry('160x200+{x}+{y}'.format(x=self.x, y=self.y))
    # update the image
    self.label.configure(image=self.frames[self.frame_index])
    
    # call update after 10ms
    self.after(10, self.update_animation)


app = Widget()
app.mainloop()

