import pyautogui
import keyboard
import time

macro_enabled = False
counter = 101

# Starting from nic2 — change this if needed

def toggle_macro():
    global macro_enabled
    macro_enabled = not macro_enabled
    print("[MACRO ENABLED]" if macro_enabled else "[MACRO DISABLED]")

def run_macro_step():
    global counter
    if macro_enabled:
        print(f"[EXPORTING] newtrainingdata{counter}")

        # Press CTRL+SHIFT+E to open export dialog
        pyautogui.hotkey('ctrl', 'shift', 'e')
        time.sleep(0.2)

        # Type the filename
        filename = f"newtrainingdata{counter}"
        pyautogui.typewrite(filename)
        time.sleep(0.2)

        # Press ENTER to save
        pyautogui.press('enter')
        time.sleep(1.0)

        # Press ENTER to confirm overwrite or accept defaults
        pyautogui.press('enter')
        time.sleep(0.2)

        # Press CTRL+Z to undo the last action
        pyautogui.hotkey('ctrl', 'z')

        # Increment the counter for next export
        counter += 1

# Set up hotkeys
keyboard.add_hotkey('F8', toggle_macro)   # Toggle macro on/off
keyboard.add_hotkey('F9', run_macro_step) # Run one macro export step

print("Press F8 to enable/disable macro.")
print("Press F9 after cropping to export and auto-increment filename.")

# Keep script running
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[EXITING]")
