import tkinter as tk
from threading import Thread

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pac-Man AI Status")
        
        # Setting up a canvas for drawing the game state
        self.canvas = tk.Canvas(root, width=224, height=248, bg='black')
        self.canvas.pack()

        self.score_label = tk.Label(root, text="Score: 0", font=('Helvetica', 12))
        self.score_label.pack()

        self.lives_label = tk.Label(root, text="Lives: 3", font=('Helvetica', 12))
        self.lives_label.pack()

        self.position_label = tk.Label(root, text="Positions", font=('Helvetica', 12))
        self.position_label.pack()

        self.action_log_label = tk.Label(root, text="Last 10 Actions:", font=('Helvetica', 12))
        self.action_log_label.pack()

        self.action_log_display = tk.Listbox(root, height=10, width=50)
        self.action_log_display.pack()

    def update_gui(self, score, lives, pacman_pos, ghost_positions, walls, action_log):
        # Updating labels and listbox
        self.score_label.config(text=f"Score: {score}")
        self.lives_label.config(text=f"Lives: {lives}")
        position_text = f"Pacman: {pacman_pos}, Ghosts: {ghost_positions}"
        self.position_label.config(text=position_text)
        self.action_log_display.delete(0, tk.END)
        for action in action_log:
            self.action_log_display.insert(tk.END, f"Action: {action[0]}, Score: {action[1]}, Lives: {action[2]}")

        # Clearing and redrawing the canvas
        self.canvas.delete("all")
        self.draw_walls(walls)
        self.draw_pacman(pacman_pos)
        self.draw_ghosts(ghost_positions)

    def draw_walls(self, walls):
        for (x, y, width, height) in walls:
            self.canvas.create_rectangle(x, y, x+width, y+height, fill='blue')
            #Debugging:
            print(f"Drawing wall at x={x}, y={y}, width={width}, height={height}")

    def draw_pacman(self, pos):
        x, y = pos
        radius = 5  # Pac-Man's radius
        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill='yellow', outline='black')
        #Debugging:
        print(f"Drawing Pac at x={x}, y={y}")

    def draw_ghosts(self, ghost_positions):
        radius = 5  # Ghosts' radius
        colors = ['red', 'pink', 'cyan', 'orange']  # Different colors for different ghosts
        for idx, (ghost, pos) in enumerate(ghost_positions.items()):
            x, y = pos
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=colors[idx % len(colors)], outline='black')
            #Debugging:
            print(f"Drawing {ghost} at x={x}, y={y}")

def run_gui():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == '__main__':
    gui_thread = Thread(target=run_gui)
    gui_thread.start()
