import cv2
import keyboard
import numpy as np
import os
import pyautogui
import pydirectinput
import pygetwindow as gw
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
import traceback
import ttkbootstrap as ttkb

# Enable DEBUG mode
DEBUG = True

# Define stuff
start_times = {}
window_title = "Roblox"

# Global flag to control the script execution
running = False

# Create a queue for GUI updates
gui_queue = queue.Queue()

# Check-if-running decorator
def check_running(func):
    def wrapper(*args, **kwargs):
        if not running:
            return (None, None)  # Return a default tuple when the script is stopped
        return func(*args, **kwargs)
    return wrapper

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, 'media', relative_path)

@check_running
# Function to check if window is in focus
def check_focus(window_title):
    while True:
        if not running: return
        window = gw.getWindowsWithTitle(window_title)
        if window and window[0].isActive:  # Check if the window is active
            break  # Break out of the loop if the window is in focus
        else:
            gui_queue.put(('update_status', "Roblox not detected. Paused..."))
            time.sleep(1)

# Function to bring the specified window into focus
def focus_window(window_title):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window[0].activate()  # Activate the window
        return True
    return False

# Function for verbose sleeping
@check_running
def sleep(action, sleep_time):
    for remaining in range(sleep_time, 0, -1):
        if not running: return
        gui_queue.put(('update_status', f"{action} for {remaining} seconds..."))
        time.sleep(1)

# Function to get the screen size
def get_screen_size(window=None):
    if window:
        window_rect = window[0].box
        if window_rect:
            return window_rect.width, window_rect.height
        else:
            print("Error: window_rect is None")
            return None, None
    else:
        size = pydirectinput.size()
        if size:
            return size
        else:
            print("Error: pydirectinput.size() returned None")
            return None, None

# Get the screen size
screen_width, screen_height = get_screen_size()
if screen_width is None or screen_height is None:
    print("Error: Unable to get screen size")
    sys.exit()  # Exit the script
else:
    # Define center of screen
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Function to move the cursor smoothly to a specific position
    @check_running
    def move_cursor(x=None, y=None, window=None, duration=0.02):

        screen_width, screen_height = get_screen_size(window)
        if screen_width is None or screen_height is None:
            print("Error: Unable to get screen size in move_cursor")
            return

        if window:
            window_rect = window[0].box
            if window_rect:
                if x is None and y is None:
                    x = window_rect.left + center_x
                    y = window_rect.top + center_y
                else:
                    x = window_rect.left + x
                    y = window_rect.top + y
            else:
                print("Error: window_rect is None in move_cursor")
                return
        else:
            if x is None and y is None:
                x = center_x
                y = center_y

        start_x, start_y = pydirectinput.position()

        # Check if the cursor is already at the destination
        if start_x == x and start_y == y:
            # Move the cursor slightly before clicking
            pydirectinput.moveRel(5, 0)  # Move the cursor 5 pixels right
            time.sleep(0.01)  # Small delay to simulate natural movement

        steps = int(duration * 100)
        for i in range(steps):
            if not running: return
            progress = i / steps
            new_x = int(start_x + (x - start_x) * progress)
            new_y = int(start_y + (y - start_y) * progress)
            pydirectinput.moveTo(new_x, new_y)
            time.sleep(duration / steps)

        pydirectinput.moveTo(x, y)  # Ensure the cursor ends at the exact position
        if DEBUG: print(f"Moving cursor to: ({x}, {y})")  

# Function to perform a click using pydirectinput
@check_running
def click(x, y):
    move_cursor(x, y)  # Move the cursor smoothly to the position
    pydirectinput.click()  # Perform a left click
    if DEBUG: print(f"Clicking: ({x}, {y})")  

# Load templates once
templates = {
    'best-eggs-quest': cv2.imread(resource_path('best-eggs-quest.png'), cv2.IMREAD_COLOR),
    'buy-button': cv2.imread(resource_path('buy-button.png'), cv2.IMREAD_COLOR),
    'claim-button': cv2.imread(resource_path('claim-button.png'), cv2.IMREAD_COLOR),
    'claim-rewards': cv2.imread(resource_path('claim-rewards.png'), cv2.IMREAD_COLOR),
    'click-for-more': cv2.imread(resource_path('click-for-more.png'), cv2.IMREAD_COLOR),
    'click-to-close': cv2.imread(resource_path('click-to-close.png'), cv2.IMREAD_COLOR),
    'coin-jar-quest': cv2.imread(resource_path('coin-jar-quest.png'), cv2.IMREAD_COLOR),
    'coin-jars-quest': cv2.imread(resource_path('coin-jars-quest.png'), cv2.IMREAD_COLOR),
    'comet-quest': cv2.imread(resource_path('comet-quest.png'), cv2.IMREAD_COLOR),
    'comets-quest': cv2.imread(resource_path('comets-quest.png'), cv2.IMREAD_COLOR),
    'daily-gift-button': cv2.imread(resource_path('daily-gift-button.png'), cv2.IMREAD_COLOR),
    'e-button': cv2.imread(resource_path('e-button.png'), cv2.IMREAD_COLOR),
    'lucky-block-quest': cv2.imread(resource_path('lucky-block-quest.png'), cv2.IMREAD_COLOR),
    'ok-button': cv2.imread(resource_path('ok-button.png'), cv2.IMREAD_COLOR),
    'pinata-quest': cv2.imread(resource_path('pinata-quest.png'), cv2.IMREAD_COLOR),
    'pinatas-quest': cv2.imread(resource_path('pinatas-quest.png'), cv2.IMREAD_COLOR),
    'potion-quest': cv2.imread(resource_path('potion-quest.png'), cv2.IMREAD_COLOR),
    'rare-eggs-quest': cv2.imread(resource_path('rare-eggs-quest.png'), cv2.IMREAD_COLOR),
    'redeem-button-1': cv2.imread(resource_path('redeem-button-1.png'), cv2.IMREAD_COLOR),
    'redeem-button-2': cv2.imread(resource_path('redeem-button-2.png'), cv2.IMREAD_COLOR),
    'redeem-button-3': cv2.imread(resource_path('redeem-button-3.png'), cv2.IMREAD_COLOR),
    'redeem-button-4': cv2.imread(resource_path('redeem-button-4.png'), cv2.IMREAD_COLOR),
    'tap-to-continue': cv2.imread(resource_path('tap-to-continue.png'), cv2.IMREAD_COLOR),
    'x-button': cv2.imread(resource_path('x-button.png'), cv2.IMREAD_COLOR)
}

# Function to capture a screenshot and convert it to BGR format
@check_running
def capture_screenshot():
    check_focus(window_title)
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Function to perform template matching and return match percentage and location
@check_running
def match_template(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val * 100, max_loc

# Funtion to close window (X button)
@check_running
def close_window():
    time.sleep(1)
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['x-button'])
    if DEBUG: print(f"Match for x-button is {match_percentage}% confidence at location {max_loc}") 
    if match_percentage is not None and match_percentage >= 80.0:
        gui_queue.put(('update_status', "Closing window..."))
        h, w = templates['x-button'].shape[:2]
        pattern_center_x = max_loc[0] + w // 2
        pattern_center_y = max_loc[1] + h // 2
        click(pattern_center_x, pattern_center_y)

# Function to check/claim rank rewards
@check_running
def claim_rank_rewards(screenshot):
    fail_count = 0
    match_percentage, max_loc = match_template(screenshot, templates['claim-rewards'])
    if DEBUG: print(f"Match for claim-rewards is {match_percentage}% confidence at location {max_loc}")  
    if match_percentage is not None and match_percentage >= 80.0:
        gui_queue.put(('update_status', "Claiming Rewards..."))
        h, w = templates['claim-rewards'].shape[:2]
        pattern_center_x = max_loc[0] + w // 2
        pattern_center_y = max_loc[1] + h // 2 + 100
        click(pattern_center_x, pattern_center_y)
        time.sleep(2)  # Allow time for window to open

        while fail_count < 20 and running:
            if not running: return
            screenshot = capture_screenshot()
            match_percentage, max_loc = match_template(screenshot, templates['claim-button'])
            if DEBUG: print(f"Match for claim-button is {match_percentage}% confidence at location {max_loc}")  
            if match_percentage is not None and match_percentage >= 60.0:
                h, w = templates['claim-button'].shape[:2]
                pattern_center_x = max_loc[0] + w // 2
                pattern_center_y = max_loc[1] + h // 2
                click(pattern_center_x, pattern_center_y)
                fail_count = 0
            else:
                fail_count += 1
                if fail_count < 20:
                    move_cursor()  # Center the cursor on the screen
                    pyautogui.scroll(-500)

        # Click to advance after ranking up
        time.sleep(3)
        gui_queue.put(('update_status', "Closing rewards window..."))
        patterns = ['click-for-more', 'tap-to-continue', 'click-to-close']
        for _ in range(3):  # Check each pattern 3 times
            if not running: return
            check_focus(window_title)
            for pattern in patterns:
                if not running: return
                screenshot = capture_screenshot()
                match_percentage, max_loc = match_template(screenshot, templates[pattern])
                if DEBUG: print(f"Match for {pattern} is {match_percentage}% confidence at location {max_loc}")  
                if match_percentage is not None and match_percentage >= 80.0:
                    h, w = templates[pattern].shape[:2]
                    pattern_center_x = max_loc[0] + w // 2
                    pattern_center_y = max_loc[1] + h // 2
                    click(pattern_center_x, pattern_center_y)
                    time.sleep(2)

        sleep("Waiting", 5)
        close_window()  # Closes the claim rewards window

# Function to claim daily rewards
@check_running
def redeem_daily_rewards(screenshot):
    match_percentage, max_loc = match_template(screenshot, templates['daily-gift-button'])
    if DEBUG: print(f"Match for daily-gift-button is {match_percentage}% confidence at location {max_loc}")  
    if match_percentage is not None and match_percentage >= 60.0:  # Look for rewards that are ready
        gui_queue.put(('update_status', "Redeeming daily rewards..."))
        h, w = templates['daily-gift-button'].shape[:2]
        pattern_center_x = max_loc[0] + w // 2
        pattern_center_y = max_loc[1] + h // 2
        click(pattern_center_x, pattern_center_y)  # Click on Present
        time.sleep(2)

        while running:
            screenshot = capture_screenshot()
            patterns = ['redeem-button-1', 'redeem-button-2', 'redeem-button-3', 'redeem-button-4']
            match = False

            for pattern in patterns:
                if not running: return
                template = templates[pattern]
                match_percentage, max_loc = match_template(screenshot, template)
                if DEBUG: print(f"Match for {pattern} is {match_percentage}% confidence at location {max_loc}")  
                if match_percentage is not None and match_percentage >= 81.0:
                    h, w = template.shape[:2]
                    pattern_center_x = max_loc[0] + w // 2
                    pattern_center_y = max_loc[1] + h // 2
                    click(pattern_center_x, pattern_center_y)
                    time.sleep(0.5)
                    match = True
                    break  # Exit for loop if match found

            if not match:
                break  # Exit the while loop if no patterns found

        sleep("Waiting", 2)
        close_window()
        
# Function to check for open menus
@check_running
def check_for_menus():
    while True:
        screenshot = capture_screenshot()
        
        # Templates for x-button and ok-button
        x_button_template = templates['x-button']
        ok_button_template = templates['ok-button']

        # Check for x-button
        match_percentage, _ = match_template(screenshot, x_button_template)
        if DEBUG: print(f"Match for x-button is {match_percentage}% confidence")  

        # If x-button is found
        if match_percentage is not None and match_percentage >= 80.0:
            # Check for ok-button
            match_percentage, _ = match_template(screenshot, ok_button_template)
            if DEBUG: print(f"Match for ok-button is {match_percentage}% confidence")  

            # Return True only if ok-button is NOT found
            if match_percentage is not None and match_percentage < 80.0:
                if DEBUG: print("Menu detected. Waiting...")
                gui_queue.put(('update_status', "Menu detected. Waiting..."))
                time.sleep(3)
            else:
                if DEBUG: print("ok-button found. Exiting loop...")                
                break
        else:
            if DEBUG: print("x-button not found. Exiting loop...")                
            break

# Function to update the status label text with "info" style
def update_status(text):
    status_label.config(text=text, bootstyle="info")

# Function to click OK button
@check_running
def click_ok_button():
    time.sleep(1)  # Delay to allow window to open
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, templates['ok-button'])
    if DEBUG: print(f"Match for ok-button is {match_percentage}% confidence at location {max_loc}")  
    if match_percentage is not None and match_percentage >= 80.0:
        gui_queue.put(('update_status', "Clicking OK button..."))
        h, w = templates['ok-button'].shape[:2]
        pattern_center_x = max_loc[0] + w // 2
        pattern_center_y = max_loc[1] + h // 2
        if DEBUG: print(f"Clicking at coordinates: ({pattern_center_x}, {pattern_center_y})")  
        click(pattern_center_x, pattern_center_y)

# Function to use items at defined intervals
@check_running
def use_item(item, time_interval, gui_queue, hotkey):
    current_time = time.time()
    start_time = start_times.get(item, current_time)
    elapsed_time = current_time - start_time
    
    if hotkey and elapsed_time >= time_interval:
        gui_queue.put(('update_status', f"Using {item}..."))
        if hotkey is not None:
            print(f"Using hotkey: {hotkey} for item: {item}")
            keyboard.press_and_release(hotkey.lower())
        start_times[item] = current_time

@check_running
# Function to move character
def move_character(direction, times, duration):
    for _ in range(times):
        if direction == 'left':
            pyautogui.keyDown('a')
            time.sleep(duration)
            pyautogui.keyUp('a')
        elif direction == 'right':
            pyautogui.keyDown('d')
            time.sleep(duration)
            pyautogui.keyUp('d')
        time.sleep(1.5)  # Adjust this sleep time as needed

@check_running
def hatch_eggs(hatch_duration):
    check_for_menus()
    
    move_duration = 0.3
    
    gui_queue.put(('update_status', "Attempting to hatch some eggs..."))
    
    e_button_template = templates['e-button']
    buy_button_template = templates['buy-button']

    # Nudge character to the left up to 10 times
    for i in range(10):
        if not running: return
        move_character('left', 1, move_duration)
        screenshot = capture_screenshot()
        match_percentage, max_loc = match_template(screenshot, e_button_template)
        if match_percentage is not None and match_percentage >= 80.0:
            if DEBUG: print("Found e-button. Clicking...")
            pyautogui.press('e')
            break
    else:
        if DEBUG: print("e-button not found after 10 moves.")
        return

    # Check for buy-button pattern
    screenshot = capture_screenshot()
    match_percentage, max_loc = match_template(screenshot, buy_button_template)
    if match_percentage is not None and match_percentage >= 80.0:
        if DEBUG: print("Found buy-button pattern. Clicking...")
        h, w = buy_button_template.shape[:2]
        pattern_center_x = max_loc[0] + w // 2
        pattern_center_y = max_loc[1] + h // 2
        click(pattern_center_x, pattern_center_y)

    # Wait while hatching eggs
    sleep("Hatching eggs", hatch_duration)

    # Return character
    total_duration = int(i * move_duration) + (1 if (i * move_duration) % 1 > 0 else 0)  # Round up to the nearest full second
    if DEBUG: print(f"Moving right continuously for {total_duration} seconds...")
    gui_queue.put(('update_status', "Returning..."))
    move_character('right', 1, total_duration)  # Move continuously with total duration

# Function to run the main script
@check_running
def run_script():
    global running

    # Timers for items using
    start_times['Flag'] = time.time()
    start_times['Fruit'] = time.time()

    try:
        # Focus on Roblox window      
        if not focus_window(window_title):
            gui_queue.put(('update_status', "Launch PS99 first!"))
            running = False
            gui_queue.put(('update_button',))
            return
        
        # Set matching vars
        threshold = 80.0
        no_match_count = 0

        # Define the patterns and their respective actions and status texts
        patterns = {
            'coin-jar-quest': (coin_jar_hotkey.get().lower() if coin_jar_hotkey.get() else None, "Calling Coin Jar"),
            'coin-jars-quest': (coin_jar_hotkey.get().lower() if coin_jar_hotkey.get() else None, "Calling Coin Jar"),
            'comet-quest': (comet_hotkey.get().lower() if comet_hotkey.get() else None, "Calling Comet"),
            'comets-quest': (comet_hotkey.get().lower() if comet_hotkey.get() else None, "Calling Comet"),
            'lucky-block-quest': (lucky_block_hotkey.get().lower() if lucky_block_hotkey.get() else None, "Calling Lucky Block"),
            'pinata-quest': (pinata_hotkey.get().lower() if pinata_hotkey.get() else None, "Calling Pinata"),
            'pinatas-quest': (pinata_hotkey.get().lower() if pinata_hotkey.get() else None, "Calling Pinata"),
            'potion-quest': (potion_hotkey.get().lower() if potion_hotkey.get() else None, "Using Potion"),
            'best-eggs-quest': (None, None),
            'rare-eggs-quest': (None, None)
        }

        # Initialize variable to keep track of the last matched pattern
        last_matched_pattern = None
        
        # Main loop
        while running:
            # Check if Roblox window is still open
            if check_focus(window_title):
                gui_queue.put(('update_status', "Running..."))

            # Set wait time between iterations
            seconds = 3

            # Pause for menus
            check_for_menus()

            # No match loop count
            if DEBUG: print(f"No match count: {no_match_count}")  

            # Click perform so failsafe clicks if no match in 10 loops
            if no_match_count >= 10:
                gui_queue.put(('update_status', "Executing failsafe clicks..."))
                for _ in range(4):  # Click 4 times
                    if not running: return
                    check_focus(window_title)
                    click(center_x, center_y)
                no_match_count = 0
           
            # Reset match count
            match_count = 0
            
            # Take a screenshot
            screenshot = capture_screenshot()

            # Check for OK button and click it
            click_ok_button()
            
            # Use items periodically
            use_item('Flag', 300, gui_queue, flag_hotkey.get())
            use_item('Fruit', 360, gui_queue, fruit_hotkey.get()) 

            # Check and redeem rank rewards
            claim_rank_rewards(screenshot)

            # Check and redeem daily rewards
            redeem_daily_rewards(screenshot)

            # Execute ultimate if checkbox is checked
            if not running: return
            if ultimate_var.get():
                gui_queue.put(('update_status', "Executing Ultimate..."))
                keyboard.press_and_release('r')

            # Create a new list with the last matched pattern at the top
            if last_matched_pattern:
                patterns_list = [last_matched_pattern] + [item for item in patterns.items() if item[0] != last_matched_pattern[0]]
            else:
                patterns_list = list(patterns.items())  # Convert to list to allow modifications

            if not running: return
            found_match = False

            # Search for patterns and store results
            gui_queue.put(('update_status', "Searching for quests..."))
            matches = []
            for pattern, (action, status_text) in patterns_list:
                if not running: return
                check_focus(window_title)
                
                match_percentage, max_loc = match_template(screenshot, templates[pattern])
                if DEBUG: print(f"Match for {pattern} is {match_percentage}% confidence at location {max_loc}")  
                
                if match_percentage is not None and match_percentage >= threshold:
                    matches.append((pattern, action, status_text, max_loc))

            # Find the most valuable quest
            if matches:
                best_match = max(matches, key=lambda x: x[3][1])  # x[3][1] is the y-coordinate of max_loc
                pattern, action, status_text, max_loc = best_match
                found_match = True

                if pattern in ['best-eggs-quest', 'rare-eggs-quest']:
                    gui_queue.put(('update_status', status_text))
                    hatch_eggs(60)
                elif action:
                    check_for_menus()
                    seconds = 10
                    if pattern == 'potion-quest':
                        seconds = 0
                    gui_queue.put(('update_status', status_text+"..."))
                    keyboard.press_and_release(action)  # Call the action
                    click_ok_button()  # Check for "There is already something in this area" window 
                    sleep(status_text, seconds)  # Allow time for action execution
                
                # Update the last matched pattern
                last_matched_pattern = (pattern, (action, status_text))
                no_match_count = 0

            if not found_match:
                no_match_count += 1

        gui_queue.put(('update_button',))

    except Exception as e:
        error_message = f"Error: {e}\n{traceback.format_exc()}"
        gui_queue.put(('status_label', "ERROR", "danger"))
        gui_queue.put(('show_error', error_message))
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
    if DEBUG: print("Stopped")
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
ttk.Label(table_frame, text="Auto Actions", font=("Helvetica", 11)).grid(row=0, column=0, padx=10, pady=1, sticky=tk.W)
ttk.Label(table_frame, text="Hotkeys", font=("Helvetica", 11), foreground="red").grid(row=0, column=1, padx=10, pady=1)

# Create hotkey entries in a table format
labels = ["Coin Jar", "Comet", "Lucky Block", "Pinata", "Potion", "Fruit", "Flag"]
hotkeys = {}

# Build hotkey table
for i, label in enumerate(labels):
    ttk.Label(table_frame, text=label).grid(row=i+1, column=0, padx=10, pady=1, sticky=tk.W)
    hotkey_entry = ttk.Entry(table_frame, width=2)
    hotkey_entry.grid(row=i+1, column=1, padx=10, pady=1)
    hotkeys[label.lower().replace(" ", "_") + "_hotkey"] = hotkey_entry # Convert letters to lowercase

# Set default values for the text fields
hotkeys["coin_jar_hotkey"].insert(0, "j")
hotkeys["comet_hotkey"].insert(0, "c")
hotkeys["lucky_block_hotkey"].insert(0, "l")
hotkeys["pinata_hotkey"].insert(0, "p")
hotkeys["potion_hotkey"].insert(0, "0")
hotkeys["fruit_hotkey"].insert(0, "1")
hotkeys["flag_hotkey"].insert(0, "m")

# Define hotkeys
coin_jar_hotkey = hotkeys["coin_jar_hotkey"]
comet_hotkey = hotkeys["comet_hotkey"]
lucky_block_hotkey = hotkeys["lucky_block_hotkey"]
pinata_hotkey = hotkeys["pinata_hotkey"]
potion_hotkey = hotkeys["potion_hotkey"]
fruit_hotkey = hotkeys["fruit_hotkey"]
flag_hotkey = hotkeys["flag_hotkey"]

# Add the "Ultimate" row with a checkbox
ultimate_var = tk.BooleanVar(value=True)  # Set the default value to True
ttk.Label(table_frame, text="Ultimate").grid(row=len(labels) + 2, column=0, padx=10, pady=1, sticky=tk.W)
ultimate_check = ttk.Checkbutton(table_frame, variable=ultimate_var)
ultimate_check.grid(row=len(labels) + 2, column=1, padx=10, pady=1)

# Create a status label
status_label = ttkb.Label(root, text="Not running", bootstyle="info", font=("Helvetica", 11))
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
