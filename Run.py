import random
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import xml.etree.ElementTree as ET
import time
from GUI import GameGUI
import tkinter as tk
from threading import Thread

# Q-Learning and game setup
actions = [Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT]
action_names = {Keys.UP: "UP", Keys.DOWN: "DOWN", Keys.LEFT: "LEFT", Keys.RIGHT: "RIGHT"}
num_actions = len(actions)
q_table = {}
learning_rate, discount_factor, epsilon = 0.1, 0.99, 0.1
action_log = []

# Function to check if the button is disabled
def button_disabled(driver):
    button = driver.find_element(By.ID, "game-start")
    return button.get_attribute("disabled") is not None

# Functions to get positions of Pac-Man and ghosts
def get_positions(driver):
    pacman = driver.find_element(By.ID, "pacman")
    pacman_pos = (int(float(pacman.value_of_css_property('left')[:-2])), 
                  int(float(pacman.value_of_css_property('top')[:-2])))
    ghosts = {}
    for ghost_id in ["blinky", "pinky", "inky", "clyde"]:
        ghost_elem = driver.find_element(By.ID, ghost_id)
        ghosts[ghost_id] = (int(float(ghost_elem.value_of_css_property('left')[:-2])), 
                            int(float(ghost_elem.value_of_css_property('top')[:-2])))
    return pacman_pos, ghosts

def get_state(driver, walls):
    score = int(driver.find_element(By.ID, "points-display").text)
    lives = len(driver.find_elements(By.CSS_SELECTOR, "#extra-lives img"))
    pacman_pos, ghost_positions = get_positions(driver)
    # Include logic to detect nearby walls based on the pacman's position and the walls data

    ghost_pos_tuple = tuple(ghost_positions[ghost] for ghost in sorted(ghost_positions))
    state = (score, lives, pacman_pos) + ghost_pos_tuple  # Consider including wall data in the state if useful
    return state


def choose_action(state):
    if random.random() < epsilon:  # Exploration: choose a random action
        return random.choice(actions)
    else:  # Exploitation: choose the best known action
        return actions[np.argmax(q_table.get(state, np.zeros(num_actions)))]


def update_q_table(state, action, reward, next_state):
    action_index = actions.index(action)
    old_q_value = q_table.get(state, np.zeros(num_actions))[action_index]
    future_rewards = max(q_table.get(next_state, np.zeros(num_actions)))
    # Q-learning formula
    new_q_value = old_q_value + learning_rate * (reward + discount_factor * future_rewards - old_q_value)
    # Update the Q-table
    if state not in q_table:
        q_table[state] = np.zeros(num_actions)
    q_table[state][action_index] = new_q_value


def play_one_step(driver, action, walls):
    # Get the current position before action, pass walls to get_state
    current_state = get_state(driver, walls)
    current_score, current_lives, current_pacman_pos, _ = current_state[:4]
    
    # Perform the action
    driver.find_element(By.TAG_NAME, 'body').send_keys(action)
    time.sleep(0.5)
    
    # Get the new state after action, also pass walls to get_state
    new_state = get_state(driver, walls)
    new_score, new_lives, new_pacman_pos, _ = new_state[:4]
    
    # Calculate reward based on the movement and score change
    if new_pacman_pos == current_pacman_pos:
        reward = -5  # Penalize for no movement (hitting a wall or ineffective movement)
    else:
        reward = new_score - current_score  # Reward is the increase in score
    
    return new_state, reward

def get_maze_layout():
    # This example assumes a static layout that you define.
    # E.g., walls = [(x1, y1), (x2, y2), ...]
    walls = []  # Add the coordinates of walls based on your static analysis
    return walls

def game_over(driver):
    lives = len(driver.find_elements(By.CSS_SELECTOR, "#extra-lives img"))
    start_button_disabled = driver.find_element(By.ID, "game-start").get_attribute("disabled")
    return lives == 0 and not start_button_disabled

def restart_game(driver):
    start_button = driver.find_element(By.ID, "game-start")
    if not start_button.get_attribute("disabled"):
        start_button.click()
        WebDriverWait(driver, 20).until(lambda d: button_disabled(d))

def run_game_logic(gui, epsilon):
    service = Service(executable_path="C:/Users/hsonm_3kx9v94/Downloads/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get('https://freepacman.org/')
    WebDriverWait(driver, 20).until(lambda d: button_disabled(d))
    
    walls = get_maze_layout("maze_blue.svg")
    last_update_time = time.time()
    
    while True:
        current_time = time.time()
        if current_time - last_update_time > 0.1:  # Update every 100 ms
            state = get_state(driver, walls)
            action = choose_action(state)
            next_state, reward = play_one_step(driver, action, walls)
            update_q_table(state, action, reward, next_state)

            # Extract score, lives, pacman position, and ghost positions correctly
            score = state[0]
            lives = state[1]
            pacman_pos = state[2]
            ghost_positions = {ghost: state[i+3] for i, ghost in enumerate(["blinky", "pinky", "inky", "clyde"])}
            
            action_log.append((action_names[action], score, lives))
            if len(action_log) > 10:
                action_log.pop(0)

            gui.update_gui(score, lives, pacman_pos, ghost_positions, walls, action_log)

            if game_over(driver):
                restart_game(driver)
                state = get_state(driver, walls)
                epsilon *= 0.99  # Optionally decay epsilon
            
            last_update_time = current_time

def parse_svg(svg_path):
    # Parse the SVG file to extract walls
    tree = ET.parse(svg_path)
    root = tree.getroot()
    walls = []
    # Assuming walls are represented as rect elements in the SVG
    for elem in root.findall('.//{http://www.w3.org/2000/svg}rect'):
        x = elem.get('x')
        y = elem.get('y')
        width = elem.get('width')
        height = elem.get('height')

        # Check if any necessary attribute is None before converting to float
        if x is not None and y is not None and width is not None and height is not None:
            x = float(x)
            y = float(y)
            width = float(width)
            height = float(height)
            walls.append((x, y, width, height))
        else:
            print(f"Skipping rect with missing attributes: x={x}, y={y}, width={width}, height={height}")
    return walls


def get_maze_layout(svg_path):
    walls = parse_svg(svg_path)
    # Convert the wall data into a useful format for the game AI
    # Here you may need to adjust this to fit how you handle coordinates in your game
    return walls

def main():
    root = tk.Tk()
    gui = GameGUI(root)
    epsilon = 0.1  # Initial value of epsilon defined here
    game_thread = Thread(target=run_game_logic, args=(gui, epsilon))
    game_thread.start()
    root.mainloop()

if __name__ == '__main__':
    main()