import tkinter as tk
from threading import Thread

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pac-Man AI Status")

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
        
    def update_gui(self, score, lives, pacman_pos, ghost_positions, action_log):
        # Using lambda to ensure the update happens in the main thread
        self.root.after(0, self.score_label.config, {"text": f"Score: {score}"})
        self.root.after(0, self.lives_label.config, {"text": f"Lives: {lives}"})
        position_text = f"Pacman: {pacman_pos}, Ghosts: {ghost_positions}"
        self.root.after(0, self.position_label.config, {"text": position_text})
        self.root.after(0, self.action_log_display.delete, 0, tk.END)
        for action in action_log:
            self.root.after(0, self.action_log_display.insert, tk.END, f"Action: {action[0]}, Score: {action[1]}, Lives: {action[2]}")

def run_gui():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == '__main__':
    gui_thread = Thread(target=run_gui)
    gui_thread.start()

