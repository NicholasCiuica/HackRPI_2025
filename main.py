from tkinter import *
from tkinter import messagebox
from tkinter import PhotoImage
import os
import time
import random

from PIL import Image, ImageTk

class Widget(Tk):
  def __init__(self):
    super().__init__()

    # --- Window setup ---
    self.overrideredirect(True) # removes title bar
    self.attributes("-topmost", True)

     # --- OS-specific transparency ---
    # Windows (pink is the color that we make transparent)
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
    self.direction = random.choice([-1, 1])
    self.direction_change_timer = time.time()
    self.direction_change_interval = random.uniform(10, 15)  # Random interval between 3-7 seconds
    
    # Dragging variables
    self.dragging = False
    self.drag_offset_x = 0
    self.drag_offset_y = 0
    
    # Falling variables
    self.falling = False
    self.velocity_y = 0
    self.gravity = 0.5
    self.target_y = self.screen_height - self.height - 50

    self.frame = Frame(self, bg='pink')
    self.frame.pack()

    # quit button
    self.bQuit = Button(self.frame, text="Quit", command=self.quit)
    self.bQuit.pack(pady=20)

    # Load spritesheet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(script_dir, "assets", "american_marten.png")
    self.frames = self.split_spritesheet(sheet_path, 1, 4, 32)
    # Animation variables
    self.frame_index = 0
    self.timestamp = time.time()
    # create the label that holds the image
    self.label = Label(self.frame, image=self.frames[0], bg="pink")
    self.label.pack()
    # Start the animation
    self.update_animation()

    # --- Make window draggable ---
    self.label.bind("<Button-1>", self.start_drag)
    self.label.bind("<B1-Motion>", self.do_drag)
    self.label.bind("<ButtonRelease-1>", self.stop_drag)
    
  
  def start_drag(self, event):
    self.dragging = True
    # Store the offset from the window's top-left corner to the mouse position
    self.drag_offset_x = event.x
    self.drag_offset_y = event.y
  
  def do_drag(self, event):
    if self.dragging:
      # Calculate new position based on mouse position and offset
      self.x = self.winfo_pointerx() - self.drag_offset_x
      self.y = self.winfo_pointery() - self.drag_offset_y
      self.geometry('160x200+{x}+{y}'.format(x=self.x, y=self.y))
  
  def stop_drag(self, event):
    self.dragging = False
    # Start falling animation
    self.falling = True
    self.velocity_y = 0

  def split_spritesheet(self, sheet_path, rows, cols, frame_size):
    frames = []
    spritesheet = Image.open(sheet_path).convert("RGBA")
    # Extract all frames from the spritesheet
    try:
      rows = 1
      cols = 4
      frame_size = 32
      for row in range(rows):
        for col in range(cols):
          x = col * frame_size
          y = row * frame_size
          box = (x, y, x + frame_size, y + frame_size)
          frame = spritesheet.crop(box)
          frame.resize((1000, 160), Image.NEAREST)
          frames.append(ImageTk.PhotoImage(frame))
    except EOFError:
      pass  # End of spritesheet frames
    return frames
  
  def update_animation(self):
    # Handle falling animation
    if self.falling:
      self.velocity_y += self.gravity
      self.y += self.velocity_y
      
      # Check if reached the taskbar
      if self.y >= self.target_y:
        self.y = self.target_y
        self.falling = False
        self.velocity_y = 0
      
      self.geometry('160x200+{x}+{y}'.format(x=int(self.x), y=int(self.y)))
    
    # Only move automatically if not being dragged or falling
    elif not self.dragging:
      # Randomly change direction every few seconds
      if time.time() > self.direction_change_timer + self.direction_change_interval:
        # Sometimes change direction, sometimes keep going
        if random.random() < 0.5:  # 50% chance to change direction
          self.direction *= -1
        self.direction_change_timer = time.time()
        self.direction_change_interval = random.uniform(3, 7)
      
      # move by one pixel in current direction
      self.x += self.direction
      
      # Check boundaries and reverse direction if needed
      if self.x <= 0:
        self.x = 0
        self.direction = 1  # Change to move right
      elif self.x >= self.screen_width - self.width:
        self.x = self.screen_width - self.width
        self.direction = -1  # Change to move left
      
      # update window position
      self.geometry('160x200+{x}+{y}'.format(x=self.x, y=self.y))
    
    # advance frame if 50ms have passed
    if time.time() > self.timestamp + 0.15:
      self.timestamp = time.time()
      # advance the frame by one, wrap back to 0 at the end
      self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    # update the image
    self.label.configure(image=self.frames[self.frame_index])
    
    # call update after 10ms
    self.after(10, self.update_animation)


app = Widget()
app.mainloop()

