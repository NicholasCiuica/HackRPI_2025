import random
import os
import time

from state import State

script_dir = os.path.dirname(os.path.abspath(__file__))

sleep_path = os.path.join(script_dir, "assets", "american_marten_sleep.png")
idle_path = os.path.join(script_dir, "assets", "american_marten.png")

class Sleep_State(State):
  def __init__(self):
    super().__init__("sleep", sleep_path, 4, False)

class Idle_State(State):
  def __init__(self):
    super().__init__("idle", idle_path, 4, True, 3, 6)

class Move_State(State):
  def __init__(self, direction=0):
    super().__init__("move", idle_path, 4, True, 4, 5)
    #determines whether pet will move left (-1) or right for this movement
    if direction == 0:
      self.direction = random.choice([-1, 1])
    elif direction < 0:
      self.direction = -1
    else:
      self.direction = 1

class Chat_State(State):
  def __init__(self):
    super().__init__("chat", idle_path, 4, True, 3, 5)
    self.messages = [
      "Hello! 👋",
      "I'm sleepy... 😴",
      "Pet me! 🐾",
      "Having a good day?",
      "Let's be friends! ❤️",
      "I love walking around!",
      "What's up? 🌟"
    ]
    self.message = random.choice(self.messages)