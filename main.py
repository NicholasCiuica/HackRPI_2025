from tkinter import Tk, Frame, Button, Canvas, TclError
from PIL import Image, ImageTk

import os
import time
import random

from specific_states import Sleep_State, Idle_State, Move_State

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

    self.screen_width = self.winfo_screenwidth()
    self.screen_height = self.winfo_screenheight()
    self.screen_bottom_offset = 50

    # Canvas for animated sprite
    self.canvas = Canvas(self, 
                         width=self.screen_width, 
                         height=self.screen_height - self.screen_bottom_offset, 
                         bg='pink', 
                         highlightthickness=0)
    self.canvas.pack()

    # Quit button
    self.bQuit = Button(self, text="Quit", command=self.quit)
    self.bQuit.place(relx=1.0, rely=1.0, x=-4, y=-4,anchor="se")

    # Position the pet
    self.pet_width = 160
    self.pet_height = 160

    # Calculate position x and y coordinates
    self.pet_x = self.screen_width - self.pet_width
    self.pet_y = self.screen_height - self.pet_height - self.screen_bottom_offset

    # Dragging variables
    self.dragging = False
    self.drag_offset_x = 0
    self.drag_offset_y = 0
    
    # Falling variables
    self.falling = False
    self.velocity_y = 0
    self.gravity = 0.5
    self.target_y = self.screen_height - self.pet_height - 100

    # Animation variables
    self.anim_index = 0
    self.pet_state = Sleep_State()
    self.frame_start_time = time.time()
    
    # Create sprite on canvas
    self.sprite = self.canvas.create_image(self.pet_x, self.pet_y, 
                                           image=self.pet_state.anim_frames[0], anchor="nw")
    
    # Start the animation
    self.update_animation()

    # --- Make sprite draggable ---
    self.canvas.bind("<Button-1>", self.start_drag)
    self.canvas.bind("<B1-Motion>", self.do_drag)
    self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
    
  
  def start_drag(self, event):
    self.dragging = True
    # Store the offset from the sprite's position to the mouse position
    self.drag_offset_x = event.x - self.pet_x
    self.drag_offset_y = event.y - self.pet_y
  
  def do_drag(self, event):
    if self.dragging:
      # Calculate new position based on mouse position and offset
      self.pet_x = event.x - self.drag_offset_x
      self.pet_y = event.y - self.drag_offset_y
      # Update sprite position on canvas
      self.canvas.coords(self.sprite, self.pet_x, self.pet_y)
  
  def stop_drag(self, event):
    self.dragging = False
    # Start falling animation
    self.falling = True
    self.velocity_y = 0

  def update_animation(self):
    # Handle falling animation
    if self.falling:
      self.velocity_y += self.gravity
      self.pet_y += self.velocity_y
      
      # Check if reached the target position
      if self.pet_y >= self.target_y:
        self.pet_y = self.target_y
        self.falling = False
        self.velocity_y = 0
      
      self.canvas.coords(self.sprite, self.pet_x, self.pet_y)
    
    # Only move automatically if not being dragged or falling
    elif not self.dragging:
      
      match self.pet_state.name:
        case "move":
          self.pet_x += self.pet_state.direction
          # Check boundaries and reverse direction if needed
          if self.pet_x <= 0:
            self.pet_x = 0
            self.pet_state = Move_State(1)
          elif self.pet_x >= self.screen_width - self.pet_width:
            self.pet_x = self.screen_width - self.pet_width
            self.pet_state = Move_State(-1)
          # Update sprite position on canvas
          self.canvas.coords(self.sprite, self.pet_x, self.pet_y)
    
    # Advance frame when enough time has passed
    if time.time() > self.frame_start_time + 0.15:
      self.frame_start_time = time.time()
      # Advance the frame by one, wrap back to 0 at the end
      self.anim_index = (self.anim_index + 1) % self.pet_state.num_frames

    # check if the current state has run out of duration
    if self.pet_state.has_duration and time.time() > self.pet_state.start_time + self.pet_state.duration:
      self.anim_index = 0
      match self.pet_state.name:
        case "idle":
          self.pet_state = Move_State()
        case "move":
          self.pet_state = Idle_State()
    
    # Update the image on canvas
    self.canvas.itemconfig(self.sprite, image=self.pet_state.anim_frames[self.anim_index])
    
    # Call update after 10ms
    self.after(10, self.update_animation)


app = Widget()
app.mainloop()