from tkinter import Tk, Frame, Button, Canvas, TclError, Label
from PIL import Image, ImageTk

import os
import time
import random

from specific_states import Sleep_State, Idle_State, Move_State, Chat_State
from marten_integration import get_marten_integration

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
    self.pet_direction = -1 #left

    # Dragging variables
    self.dragging = False
    self.drag_start_time = 0
    self.drag_threshold = 0.2  # Time threshold to distinguish click from drag (in seconds)
    self.drag_offset_x = 0
    self.drag_offset_y = 0
    
    # Falling variables
    self.falling = False
    self.velocity_y = 0
    self.gravity = 0.5
    self.target_y = self.screen_height - self.pet_height - self.screen_bottom_offset

    # Animation variables
    self.anim_index = 0
    self.pet_state = Sleep_State()
    self.frame_start_time = time.time()
    
    # Chat text box
    self.chat_label = None
    
    # Marten integration
    self.marten = get_marten_integration()
    self.marten.start()
    self.last_news_check = time.time()
    
    # Create sprite on canvas
    starting_image = self.pet_state.anim_frames[0]
    self.sprite = self.canvas.create_image(self.pet_x, self.pet_y, 
                                           image=ImageTk.PhotoImage(starting_image), anchor="nw")
    
    # Start the animation
    self.update_animation()

    # --- Make sprite draggable ---
    self.canvas.bind("<Button-1>", self.pet_mouse_click_down)
    self.canvas.bind("<B1-Motion>", self.do_drag)
    self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

  def pet_mouse_click_down(self, event):
    match self.pet_state.name:
      case "sleep":
        self.pet_state = Idle_State()
        return
      case _:
        self.start_drag(event)

  def start_drag(self, event):
    # Check if click is on the pet sprite
    sprite_bbox = self.canvas.bbox(self.sprite)
    if sprite_bbox and (sprite_bbox[0] <= event.x <= sprite_bbox[2] and 
                        sprite_bbox[1] <= event.y <= sprite_bbox[3]):
      self.dragging = True
      self.drag_start_time = time.time()
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
      
      # Remove chat box while dragging
      if self.chat_label:
        self.canvas.delete(self.chat_label)
        self.canvas.delete(self.chat_bg)
        self.chat_label = None
  
  def stop_drag(self, event):
    if self.dragging:
      drag_duration = time.time() - self.drag_start_time
      
      # If it was a quick click (not a drag), trigger chat
      if drag_duration < self.drag_threshold:
        self.show_chat()
      else:
        # It was a drag, start falling animation
        self.falling = True
        self.velocity_y = 0
      
      self.dragging = False
  
  def show_chat(self, custom_message=None):
    """Show chat message near the pet"""
    # Switch to chat state
    self.pet_state = Chat_State(custom_message)
    self.anim_index = 0
    
    # Calculate position for text box
    text_x, text_y = self.calculate_text_position()
    
    # Remove existing chat label if present
    if self.chat_label:
      self.canvas.delete(self.chat_label)
      self.canvas.delete(self.chat_bg)
    
    # Create text box on canvas
    self.chat_label = self.canvas.create_text(
      text_x, text_y,
      text=self.pet_state.message,
      font=("Arial", 10, "bold"),
      fill="black",
      justify="center",
      width=300  # Wrap text at 300 pixels
    )
    
    # Create background rectangle for text
    bbox = self.canvas.bbox(self.chat_label)
    padding = 8
    self.chat_bg = self.canvas.create_rectangle(
      bbox[0] - padding, bbox[1] - padding,
      bbox[2] + padding, bbox[3] + padding,
      fill="lightblue" if custom_message else "white",
      outline="darkblue" if custom_message else "black",
      width=2
    )
    # Move text to front
    self.canvas.tag_raise(self.chat_label)

  def calculate_text_position(self):
    # Calculate available space on each side
    space_left = self.pet_x
    space_right = self.screen_width - (self.pet_x + self.pet_width)
    space_top = self.pet_y
    space_bottom = self.screen_height - self.screen_bottom_offset - (self.pet_y + self.pet_height)
    
    # Determine which side has the most room
    max_space = max(space_left, space_right, space_top, space_bottom)
    
    text_offset = 20  # Distance from pet
    
    if max_space == space_right: # Position to the right
      return (self.pet_x + self.pet_width + text_offset, self.pet_y + self.pet_height // 2)
    elif max_space == space_left: # Position to the left
      return (self.pet_x - text_offset, self.pet_y + self.pet_height // 2)
    elif max_space == space_top: # Position above
      return (self.pet_x + self.pet_width // 2, self.pet_y - text_offset)
    else: # Position below
      return (self.pet_x + self.pet_width // 2, self.pet_y + self.pet_height + text_offset)

  def update_animation(self):
    # Handle falling animation
    if self.falling:
      self.velocity_y += self.gravity
      self.pet_y += self.velocity_y
      
      # Check if pet has reached the ground
      if self.pet_y >= self.target_y:
        self.pet_y = self.target_y
        self.falling = False
        self.velocity_y = 0
        self.pet_state = Idle_State()  # Create instance, not class
      
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
            self.pet_direction = 1
          elif self.pet_x >= self.screen_width - self.pet_width:
            self.pet_x = self.screen_width - self.pet_width
            self.pet_state = Move_State(-1)
            self.pet_direction = -1
          # Update sprite position on canvas
          self.canvas.coords(self.sprite, self.pet_x, self.pet_y)
        case _:
          if self.pet_x <= 0:
            self.pet_x = 0
          elif self.pet_x >= self.screen_width - self.pet_width:
            self.pet_x = self.screen_width - self.pet_width
          # Update sprite position on canvas
          self.canvas.coords(self.sprite, self.pet_x, self.pet_y)
    
    # Advance frame when enough time has passed
    if time.time() > self.frame_start_time + 0.15:
      self.frame_start_time = time.time()
      # Advance the frame by one, wrap back to 0 at the end
      self.anim_index = (self.anim_index + 1) % self.pet_state.num_frames
  
    # Check for new messages from Marten (every 5 seconds)
    if time.time() > self.last_news_check + 5:
      self.last_news_check = time.time()
      message = self.marten.get_next_message()
      
      if message and not self.chat_label and not self.dragging:
        # Display the sustainability tip from Marten
        tip_text = message['text']
        if message.get('rating') is not None:
          emoji = "🌟" if message['rating'] >= 7 else "⚠️" if message['rating'] <= 4 else "📰"
          tip_text = f"{emoji} {tip_text}"
        
        self.show_chat(tip_text)

    # check if the current state has run out of duration
    if self.pet_state.has_duration and time.time() > self.pet_state.start_time + self.pet_state.duration:
      # Reset animations and textboxes
      self.anim_index = 0
      
      match self.pet_state.name:
        case "idle":
          self.pet_state = Move_State()
          self.pet_direction = self.pet_state.direction
        case "move":
          self.pet_state = Idle_State()
        case "chat":
          self.pet_state = Idle_State()
          if self.chat_label:
            self.canvas.delete(self.chat_label)
            self.canvas.delete(self.chat_bg)
            self.chat_label = None
    
    # Update the image on canvas
    next_image = self.pet_state.anim_frames[self.anim_index]
    if self.pet_direction == 1: # flip the image if the pet moved right
      next_image = next_image.transpose(Image.FLIP_LEFT_RIGHT)
    self.pet_image = ImageTk.PhotoImage(next_image)
    self.canvas.itemconfig(self.sprite, image=self.pet_image)
    
    # Call update after 10ms
    self.after(10, self.update_animation)


app = Widget()
app.mainloop()