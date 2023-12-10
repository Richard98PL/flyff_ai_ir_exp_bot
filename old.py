import tkinter as tk
import pyautogui
import pygetwindow as gw
import time
import easyocr
import numpy as np
import pytesseract
import cv2

def find_and_open_tab(tab_name):
    browser_tabs = gw.getWindowsWithTitle(tab_name)
    if browser_tabs:
        browser_tab = browser_tabs[0]
        browser_tab.activate()
        return True
    else:
        return False

def get_screen_resolution():
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    pyautogui.moveTo(center_x, center_y)
    print(center_x)
    print(center_y)
    return pyautogui.size()

def calculate_relative_coordinates(text_coordinates):
    # Get screen resolution dynamically
    screen_width, screen_height = get_screen_resolution()

    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    # Calculate coordinates relative to the center of the display
    center_x = center_x + text_coordinates['center_x']
    center_y = center_y + text_coordinates['center_y']

    return  center_x, center_y


def search_text_in_screenshot(search_text, screenshot):
   # Set the path to the Tesseract executable (change this to your Tesseract installation path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Read the image using OpenCV
    image = screenshot

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use a threshold to convert the image to binary
    _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

    # Use pytesseract to perform OCR on the binary image
    custom_config = r'--oem 3 --psm 6'  # Adjust OCR Engine Mode (OEM) and Page Segmentation Mode (PSM) as needed
    result = pytesseract.image_to_string(binary_image, config=custom_config)
    
    text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    print(text_data)
    for i in range(len(text_data['text'])):
        if search_text.lower() in text_data['text'][i].lower() and int(text_data['conf'][i]) > 0:
            print(text_data['text'][i])
            x, y, w, h = (
                text_data['left'][i],
                text_data['top'][i],
                text_data['width'][i],
                text_data['height'][i]
            )
            print(x)
            print(y)
            print(w)
            print(h)
            return [(x+(w/2)),(y+(h/2)) - 15]

    # Return None if no match is found
    return None


    # Find the bounding box coordinates of the search text
    print(result)
    for entry in result.splitlines():
        if search_text in entry:
            box = pytesseract.image_to_boxes(binary_image, config=custom_config)
            x_min = int(box.split()[1])
            y_min = int(box.split()[2])
            x_max = int(box.split()[3])
            y_max = int(box.split()[4])

            print('wtf')
            print( (x_max + x_min) / 2 )
            print( (y_max + y_min) / 2)
            
            return (x_max + x_min) / 2, (y_max + y_min) / 2

    return None

def calculate_click_position(text_coordinates):
   return text_coordinates['center_x'], text_coordinates['center_y']


def on_button_click():
    input_text = entry.get()
    if find_and_open_tab("Flyff Universe"):
        time.sleep(2)  # Wait for the tab to fully load (adjust if needed)

        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2


        # Capture the screenshot of the middle region
        # screenshot = pyautogui.screenshot(region=(center_x - 200, center_y - 200, 600, 600))
        result = None
        while result == None:
            screenshot = pyautogui.screenshot()
            screenshot.save("test.png")

            screenshot_np_array = np.array(screenshot)

            # Search for the text and get the position
            result = search_text_in_screenshot(input_text, screenshot_np_array)
            
        x = result[0]
        y = result[1]
        
        if x and y:
            result_label.config(text="Text found in the screenshot!")
            pyautogui.click(x, y, button='left')
            pyautogui.moveTo(x, y)
        else:
            result_label.config(text="Text not found in the screenshot.")
    else:
        result_label.config(text="Flyff Universe tab not found.")

# Create the UI window
window = tk.Tk()
window.title("Browser Automation")

# Set window size
window.geometry("400x300")

# Create input entry
entry_label = tk.Label(window, text="Enter text:")
entry_label.pack(pady=10)
entry = tk.Entry(window, width=30)
entry.pack(pady=10)

# Create search button
search_button = tk.Button(window, text="Search", command=on_button_click)
search_button.pack(pady=10)

# Display result label
result_label = tk.Label(window, text="")
result_label.pack(pady=10)

# Run the GUI
window.mainloop()
