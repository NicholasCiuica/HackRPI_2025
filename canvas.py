from tkinter import Tk, Frame, Button, Label, TclError
from PIL import Image, ImageTk

class Pet_Canvas(Tk):
  def __init__(self, root):
    super().__init__(root, width=400, height=400, bg="white")
    # self.pack()

# ---- Load your frames (list of PIL Images) ----
# For example, frames = [Image.open("f1.png"), Image.open("f2.png"), ...]
# Here is how you convert to PhotoImage:

def load_frames(frame_paths, scale=1):
    pil_frames = [Image.open(p) for p in frame_paths]
    tk_frames = []

    for f in pil_frames:
        if scale != 1:
            w, h = f.size
            f = f.resize((w*scale, h*scale), Image.NEAREST)

        tk_frames.append(ImageTk.PhotoImage(f))
    return tk_frames

# Example list of images (replace with your frames)
# frames = load_frames(["frame1.png", "frame2.png", ...])
frames = []  # fill this later with your real frame list

current_frame = 0

# Create a sprite on the canvas
sprite = canvas.create_image(200, 200, image=None)

# ---- Animation function ----
def animate():
    global current_frame
    canvas.itemconfig(sprite, image=frames[current_frame])
    current_frame = (current_frame + 1) % len(frames)
    root.after(100, animate)  # control speed here (ms per frame)

# Start after frames are loaded:
# animate()

root.mainloop()