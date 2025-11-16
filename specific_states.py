import random
import os
import time

from state import State

script_dir = os.path.dirname(os.path.abspath(__file__))

sleep_path = os.path.join(script_dir, "assets", "american_marten_sleep.png")
idle_path = os.path.join(script_dir, "assets", "american_marten.png")
move_path = os.path.join(script_dir, "assets", "american_marten_move.png")
dragged_path = os.path.join(script_dir, "assets", "american_marten_uppies.png")

class Sleep_State(State):
  def __init__(self):
    super().__init__("sleep", sleep_path, 4, False)

class Idle_State(State):
  def __init__(self):
    super().__init__("idle", idle_path, 4, True, 3, 5)

class Move_State(State):
  def __init__(self, direction=0):
    super().__init__("move", move_path, 4, True, 4, 5)
    #determines whether pet will move left (-1) or right for this movement
    if direction == 0:
      self.direction = random.choice([-1, 1])
    elif direction < 0:
      self.direction = -1
    else:
      self.direction = 1

class Dragged_State(State):
  def __init__(self):
    super().__init__("dragged", dragged_path, 4, False)

class Chat_State(State):
  def __init__(self, custom_message=None):
    # Increase duration to 10 seconds if it's a custom message (news tip)
    # Keep 6 seconds for regular messages
    
    if custom_message:
      super().__init__("chat", idle_path, 4, True, 10, 10)
      self.message = custom_message
      self.is_news = True
    else:
      super().__init__("chat", idle_path, 4, True, 6, 6)
      self.messages = [
        "Hello!",
        "I'm sleepy...",
        "Pet me! ",
        "Having a good day?",
        "Let's be friends!",
        "I love walking around!",
        "What's up?"
      ]
      self.message = random.choice(self.messages)
      self.is_news = False
