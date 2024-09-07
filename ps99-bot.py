import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
import numpy as np
import pyautogui
import keyboard
import time
import pygetwindow as gw
import win32api, win32con
import ttkbootstrap as ttkb
import sys
import os
import queue
import logging
import tempfile

# Get the path to the user's temporary directory
temp_dir = tempfile.gettempdir()
log_file_path = os.path.join(temp_dir, 'script.log')

# Configure logging to use the log file in the temporary directory
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global flag to control the script execution
running = False

# Create a queue for GUI updates
gui_queue = queue.Queue()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./media")
    return os.path.join(base_path, relative_path)

# Load templates once
templates = {
    'claim-button.png':  cv2.imread(resource_path('claim-button.png'), cv2.IMREAD_COLOR),
    'claim-rewards.png': cv2.imread(resource_path('claim-rewards.png'), cv2.IMREAD_COLOR),
    'click-for-more.png': cv2.imread(resource_path('click-for-more.png'), cv2.IMREAD_COLOR),
    'coin-jar-quest.png': cv2.imread(resource_path('coin-jar-quest.png'), cv2.IMREAD_COLOR),
    'coin-jars-quest.png': cv2.imread(resource_path('coin-jars-quest.png'), cv2.IMREAD_COLOR),
    'comet-quest.png': cv2.imread(resource_path('comet-quest.png'), cv2.IMREAD_COLOR),
    'comets-quest.png': cv2.imread(resource_path('comets-quest.png'), cv2.IMREAD_COLOR),
    'daily-gift-button.png': cv2.imread(resource_path('daily-gift-button.png'), cv2.IMREAD_COLOR),
    'ok-button.png': cv2.imread(resource_path('ok-button.png'), cv2.IMREAD_COLOR),
    'pinata-quest.png': cv2.imread(resource_path('pinata-quest.png'), cv2.IMREAD_COLOR),
    'pinatas-quest.png': cv2.imread(resource_path('pinatas-quest.png'), cv2.IMREAD_COLOR),
    'lucky-block-quest.png': cv2.imread(resource_path('lucky-block-quest.png'), cv2.IMREAD_COLOR),
    'potion-quest.png': cv2.imread(resource_path('potion-quest.png'), cv2.IMREAD_COLOR),
    'redeem-button.png': cv2.imread(resource_path('redeem-button.png'), cv2.IMREAD_COLOR),
    'x-button.png': cv2.imread(resource_path('x-button.png'), cv2.IMREAD_COLOR)
}

# Function to bring the specified window into focus
def focus_window(window_title):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window[0].activate()
        return True
    return False

def sleep(sleep_time):
    for remaining in range(sleep_time, 0, -1):
        gui_queue.put(('update_status', f"Waiting {remaining} seconds..."))
        time.sleep(1)

# Function to move the cursor to a specific position or center it on the screen
def move_cursor(x=None, y=None, window=None):
    if window:
        window_rect = window[0].box
        screen_width = window_rect.width
        screen_height = window_rect.height
        if x is None and y is None:
            x = window_rect.left + screen_width // 2
            y = window_rect.top + screen_height // 2
        else:
            x = window_rect.left + x
            y = window_rect.top + y
    else:
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        if x is None and y is None:
            x = screen_width // 2
            y = screen_height // 2
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/screen_width*65535.0), int(y/screen_height*65535.0))
    time.sleep(0.2)  # Small delay to ensure the cursor has moved

# Function to perform a click using win32api and win32con
def click(x, y):
    move_cursor(x, y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# Function to capture a screenshot and convert it to BGR format
def capture_screenshot():
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Function to perform template matching and return match percentage and location
def match_template(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val * 100, max_loc

# Funtion to close window (X button)
def close_window():
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['x-button.png'])
    if match_percentage >= 80.0:
        gui_queue.put(('update_status', "Closing window..."))
        h, w = templates['x-button.png'].shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        click(center_x, center_y)

# Function to check/claim rank rewards
def check_rank_rewards():
    fail_count = 0
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['claim-rewards.png'])
    if match_percentage >= 80.0: # Look for rewards that are ready
        gui_queue.put(('update_status', "Claiming Rewards..."))
        h, w = templates['claim-rewards.png'].shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2 + 100
        click(center_x, center_y)
        time.sleep(2)

        while fail_count < 20 and running:
            screenshot = capture_screenshot()
            match_percentage, max_loc = match_template(screenshot, templates['claim-button.png'])
            if match_percentage >= 60.0:
                h, w = templates['claim-button.png'].shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                click(center_x, center_y)
                time.sleep(0.5)
                fail_count = 0
            else:
                fail_count += 1
                if fail_count < 20:
                    move_cursor()  # Center the cursor on the screen
                    pyautogui.scroll(-500)
                    time.sleep(1)

        # Click to advance after ranking up
        gui_queue.put(('update_status', "Closing rewards window..."))
        screenshot = capture_screenshot()
        match_percentage, max_loc = match_template(screenshot, templates['click-for-more.png'])
        if match_percentage >= 80.0:
            h, w = templates['click-for-more.png'].shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            click(center_x, center_y)    
        time.sleep(2)
        close_window() # Closes the claim rewards window

# Function to claim daily rewards
def redeem_daily_rewards():
    fail_count = 0
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['daily-gift-button.png'])
    #print(f"Match for daily-gift-button.png is {match_percentage}% confidence at location {max_loc}")
    if match_percentage >= 60.0: # Look for rewards that are ready
        gui_queue.put(('update_status', "Redeeming daily rewards..."))
        h, w = templates['daily-gift-button.png'].shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        click(center_x, center_y)
        time.sleep(0.5)
        
        while running and fail_count < 1:
            screenshot = capture_screenshot()
            match_percentage, max_loc = match_template(screenshot, templates['redeem-button.png'])
            if match_percentage >= 60.0: # Look for redeemable rewards
                h, w = templates['redeem-button.png'].shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                click(center_x, center_y)
                time.sleep(0.5)
            else:
                close_window() # Close the window if none found
                fail_count += 1

# Function to update the status label text with "info" style
def update_status(text):
    status_label.config(text=text, bootstyle="info")

# Function to click OK button
def click_ok_button():
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['ok-button.png'])
    if match_percentage >= 80.0:
        gui_queue.put(('update_status', "Clicking OK button..."))
        h, w = templates['ok-button.png'].shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        click(center_x, center_y)

# Function to run the main script
def run_script():
    global running

    # Set start time
    start_time = time.time()
    try:
        # Focus on Roblox window
        window_title = "Roblox"
       
        if not focus_window(window_title):
            gui_queue.put(('update_status', "Launch PS99 first!"))
            running = False
            gui_queue.put(('update_button',))
            return
        
        # Set image matching threshold
        threshold = 80.0

        # Define the patterns and their respective actions and status texts
        patterns = {
            'coin-jar-quest.png': (coin_jar_hotkey.get().lower() if coin_jar_hotkey.get() else None, "Calling Coin Jar..."),
            'coin-jars-quest.png': (coin_jar_hotkey.get().lower() if coin_jar_hotkey.get() else None, "Calling Coin Jar..."),
            'comet-quest.png': (comet_hotkey.get().lower() if comet_hotkey.get() else None, "Calling Comet..."),
            'comets-quest.png': (comet_hotkey.get().lower() if comet_hotkey.get() else None, "Calling Comet..."),
            'pinata-quest.png': (pinata_hotkey.get().lower() if pinata_hotkey.get() else None, "Calling Pinata..."),
            'pinatas-quest.png': (pinata_hotkey.get().lower() if pinata_hotkey.get() else None, "Calling Pinata..."),
            'lucky-block-quest.png': (lucky_block_hotkey.get().lower() if lucky_block_hotkey.get() else None, "Calling Lucky Block..."),
            'potion-quest.png': (potion_hotkey.get().lower() if potion_hotkey.get() else None, "Using Potion..."),
        }

        # Main loop
        while running:
            # Click in the sweet spot                                                           
            #click(960, 710)
            
            # Set wait time between actions
            seconds = 10

            # Execute ultimate if checkbox is checked                      
            if ultimate_var.get():
                gui_queue.put(('update_status', "Executing Ultimate..."))
                keyboard.press_and_release('r')
            
            # Take a screenshot
            screenshot = capture_screenshot()
            
            # Search for patterns and update status text accordingly
            gui_queue.put(('update_status', "Searching for quests..."))
            for pattern, (action, status_text) in patterns.items():
                match_percentage, max_loc = match_template(screenshot, templates[pattern])
                if match_percentage >= threshold:
                    if action:
                        if pattern == 'potion-quest.png':
                            seconds = 1
                        gui_queue.put(('update_status', status_text))
                        keyboard.press_and_release(action) # Call the action
                        time.sleep(1)
                        break  # Break out of the loop once a match is found and action is performed

            # Check for OK button and click it
            click_ok_button()

            # Check and redeem rank rewards
            check_rank_rewards()

            # Check and redeem daily rewards
            redeem_daily_rewards()

            # Call magnet flag every 5 minutes if flag hotkey is set
            elapsed_time = time.time() - start_time
            if flag_hotkey.get() and elapsed_time >= 300:
                gui_queue.put(('update_status', "Calling Magnet Flag..."))
                keyboard.press_and_release(flag_hotkey.get().lower())
                start_time = time.time()

            # Allow time for action execution
            sleep(seconds)
            
        gui_queue.put(('update_button',))

    except Exception as e:
        gui_queue.put(('status_label', "ERROR", "danger"))
        gui_queue.put(('show_error', str(e)))
        running = False
        gui_queue.put(('update_button',))

# Function to start the script in a separate thread with error handling
def start_script():
    global running
    if not running:
        running = True
        threading.Thread(target=run_script).start()
        gui_queue.put(('update_status', "Running..."))
        gui_queue.put(('update_button',))

# Function to stop the script
def stop_script():
    global running
    running = False
    gui_queue.put(('update_status', "Stopped"))
    gui_queue.put(('update_button',))

# Function to update the button text and command
def update_button():
    if running:
        start_button.config(text="Stop", command=stop_script, bootstyle="danger")
    else:
        start_button.config(text="Start", command=start_script, bootstyle="success")

# Function to handle window close event
def on_closing():
    stop_script()
    root.after(0, root.destroy)

# Create the main window with ttkbootstrap theme
style = ttkb.Style("cosmo")  # You can choose other themes like "flatly", "darkly", etc.
root = style.master
root.title("PS99 Bot")
root.geometry("300x400+0+600")  # Set the window size and location
root.attributes("-topmost", True)  # Keep the window on top
root.resizable(False, False)
root.iconbitmap(resource_path('logo.ico'))

# Create a frame for the table
table_frame = ttk.Frame(root)
table_frame.pack(pady=10)

# Add titles
ttk.Label(table_frame, text="Auto Actions", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)
ttk.Label(table_frame, text="Hotkeys", font=("Helvetica", 12), foreground="red").grid(row=0, column=1, padx=10, pady=2)

# Create hotkey entries in a table format
labels = ["Coin Jar", "Comet", "Lucky Block", "Pinata", "Potion"]
hotkeys = {}

# Build hotkey table
for i, label in enumerate(labels):
    ttk.Label(table_frame, text=label).grid(row=i+1, column=0, padx=10, pady=2, sticky=tk.W)
    hotkey_entry = ttk.Entry(table_frame, width=2)
    hotkey_entry.grid(row=i+1, column=1, padx=10, pady=2)
    hotkeys[label.lower().replace(" ", "_") + "_hotkey"] = hotkey_entry # Convert letters to lowercase

# Set default values for the text fields
hotkeys["coin_jar_hotkey"].insert(0, "j")
hotkeys["comet_hotkey"].insert(0, "c")
hotkeys["lucky_block_hotkey"].insert(0, "l")
hotkeys["pinata_hotkey"].insert(0, "p")
hotkeys["potion_hotkey"].insert(0, "0")

# Define hotkeys
coin_jar_hotkey = hotkeys["coin_jar_hotkey"]
comet_hotkey = hotkeys["comet_hotkey"]
lucky_block_hotkey = hotkeys["lucky_block_hotkey"]
pinata_hotkey = hotkeys["pinata_hotkey"]
potion_hotkey = hotkeys["potion_hotkey"]

# Add the "Flag" row with a hotkey text field
ttk.Label(table_frame, text="Flag").grid(row=len(labels) + 1, column=0, padx=10, pady=2, sticky=tk.W)
flag_hotkey = ttk.Entry(table_frame, width=2)
flag_hotkey.grid(row=len(labels) + 1, column=1, padx=10, pady=2)
flag_hotkey.insert(0, "m")

# Add the "Ultimate" row with a checkbox
ultimate_var = tk.BooleanVar(value=True)  # Set the default value to True
ttk.Label(table_frame, text="Ultimate").grid(row=len(labels) + 2, column=0, padx=10, pady=2, sticky=tk.W)
ultimate_check = ttk.Checkbutton(table_frame, variable=ultimate_var)
ultimate_check.grid(row=len(labels) + 2, column=1, padx=10, pady=2)

# Create a status label
status_label = ttkb.Label(root, text="Not running", bootstyle="info", font=("Helvetica", 12))
status_label.pack(pady=10)

# Create a start button with increased size and font
start_button = ttkb.Button(root, text="Start", command=start_script, bootstyle="success")
start_button.place(x=15, y=320, width=270, height=70)

# Set the window close event handler
root.protocol("WM_DELETE_WINDOW", on_closing)

# Function to process the queue and update the GUI
def process_queue():
    while not gui_queue.empty():
        msg = gui_queue.get()
        if msg[0] == 'update_button':
            update_button()
        elif msg[0] == 'update_status':
            update_status(msg[1])
        elif msg[0] == 'status_label':
            status_label.config(text=msg[1], bootstyle=msg[2])
        elif msg[0] == 'show_error':
            messagebox.showerror("Error", msg[1])
    root.after(100, process_queue)

# Start the queue processing loop
root.after(100, process_queue)

# Run the GUI event loop
root.mainloop()
