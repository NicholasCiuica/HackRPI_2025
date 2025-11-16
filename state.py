from PIL import Image, ImageTk
import random
import time

class State():
  def __init__(self, name, spritesheet_path, num_frames, has_duration, min_duration = -1, max_duration = -1):
    self.anim_frames = self.split_spritesheet(spritesheet_path, num_frames, 1, 32, 160)
    self.name = name
    self.num_frames = num_frames
    self.has_duration = has_duration
    if self.has_duration:
      self.duration = random.uniform(min_duration, max_duration)
      self.start_time = time.time()
    
  def split_spritesheet(self, spritesheet_path, rows, cols, frame_size, new_frame_size):
    frames = []
    spritesheet = Image.open(spritesheet_path).convert("RGBA")
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
          frame = frame.resize((new_frame_size, new_frame_size), Image.NEAREST)
          frames.append(frame)
    except EOFError:
      pass  # End of spritesheet frames
    return frames