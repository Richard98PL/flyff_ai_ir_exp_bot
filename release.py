import cv2 as cv
import numpy as np
import os
import pyautogui
import pytesseract
import time
from PIL import Image, ImageTk
import tkinter as tk

import itertools
import os
import shutil
import threading
import time
import sys
from pynput.keyboard import Key, Controller as kb
from pynput.mouse import Button, Controller as mousy
import pygetwindow as gw
import random
import math
from playsound import playsound


import win32gui, win32ui, win32con

hwnd = None
class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

   
    # constructor
    def __init__(self, window_name=None):
        global hwnd

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            if hwnd == None:
                windows = []
                def callback(hwnd, windows):
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    if window_name in window_text or window_name in class_name:
                        windows.append((hwnd, window_text, class_name))

                win32gui.EnumWindows(callback, windows)
                for hwnd, window_text, class_name in windows:
                    print("Window Handle:", hwnd)
                    print("Window Title:", window_text)
                    print("Class Name:", class_name)
                    print()
                    self.hwnd = hwnd

                print(self.hwnd)

                if not self.hwnd:
                    raise Exception('Window not found: {}'.format(window_name))
            else:
                self.hwnd = hwnd

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        if not window_name is None:
            # account for the window border and titlebar and cut them off
            border_pixels = 8
            titlebar_pixels = 30
            self.w = self.w - (border_pixels * 2)
            self.h = self.h - titlebar_pixels - border_pixels
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels

            # set the cropped coordinates offset so we can translate screenshot
            # images into actual screen positions
            self.offset_x = window_rect[0] + self.cropped_x
            self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)    

keyboard = kb()
mouse = mousy()
db_window = None
def sendHotkey(hotkey):
    global db_window
    if db_window == None:
        db_window = gw.getWindowsWithTitle('Opera')[0]
    withSpin = False
    if hotkey == 'spin':
        withSpin = True

    if db_window:
        if hotkey == 'F3':
             hotkey = Key.f3
        elif hotkey == 'F5':
             hotkey = Key.f5
        elif hotkey == 'F11':
             hotkey = Key.f11
        elif hotkey =='F1':
             hotkey = Key.f1
        elif hotkey == 'F2':
             hotkey = Key.f2
        elif hotkey == 'F10':
             hotkey = Key.f10
        elif hotkey == 'q':
             hotkey = 'q'
        elif hotkey == 'stop':
             stop_keys = [Key.down, Key.up, Key.right, Key.left]
             hotkey = random.choice(stop_keys)
        elif hotkey == '1':
             hotkey = '1'
        elif hotkey == '3':
             hotkey = '3'
        elif hotkey == '4':
             hotkey = '4'
        elif hotkey == '5':
             hotkey = '5'
        elif hotkey == 'space':
             hotkey = Key.space
        elif hotkey == 'right':
             hotkey = Key.right
        

        #db_window.restore()
        try:
            db_window.show()
            #print('show')
            db_window.activate()
            if withSpin:

                keyboard.press(Key.ctrl_l)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated

                keyboard.press(Key.up)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(Key.up)

                delay = random.uniform(15, 25)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated

                keyboard.press(Key.down)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(Key.down)

                keyboard.release(Key.ctrl_l)

            else:
                keyboard.press(hotkey)
                delay = random.uniform(15, 45)  # Generate a random number between 0 and 10
                time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                keyboard.release(hotkey)
        except Exception as err:
            print(err)
            pass

  
def is_within_range(location, maxDistance):
    center_x = 960
    center_y = 416

    x, y = location  # Unpack the tuple into x and y coordinates

    distance = max(abs(center_x - x), abs(center_y - y))
    print('distance is ->: ' + str(distance))

    return distance <= maxDistance
import psutil

lastMobTimestamp = None
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
lastClickTimestamp = None
howManyMobs = 0

def distance_to_average(coord, coordinates, target=(1460, 560)):
    avg_x = sum(x for x, y in coordinates) / len(coordinates)
    avg_y = sum(y for x, y in coordinates) / len(coordinates)
    
    x, y = coord
    return math.sqrt((x - avg_x)**2 + (y - avg_y)**2)

def sort_by_distance_to_average(coordinates, target=(1460, 560)):
    return sorted(coordinates, key=lambda coord: distance_to_average(coord, coordinates))

def sort_by_center(point, target=(1460,560)):
    x1, y1 = point
    x2, y2 = target
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
def recognize(image_path, screenshot_image, screenshot_image_gray, thread_name, message_queue):
    # if 'mobs' in image_path:
    #     print(image_path)
    global mouse
    global keyboard
    global howManyMobs
    global current_index
    global lastClickTimestamp
    global lastMobTimestamp

    differenceBetweenLastMobFound = None
    wasSalka = False
    wasMouseClick = False
    current_mouse_position = mouse.position
    
    #print(image_path)
    # object = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    object = imagesByImagePath[image_path]

    result = cv.matchTemplate(screenshot_image, object, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    image_name = image_path.split('/')[-1]
    
    if 'waypoint' in image_path:
        #print(image_path)
        #print(max_val)
        pass

    if 'mob' in image_path:
        print('Best match: %s' % str(max_val))
        pass
    

    threshold = 0.5
    if 'battle' in image_path:
        threshold = 0.80
        
    if 'full' in image_path:
         threshold = 0.98

    if 'missing' in image_path:
         threshold = 0.99
         return

    if 'missing_mana' in image_path:
        threshold = 0.92
        return
    
    if 'mobs' in image_path:
        threshold = 0.82
        if 'red' in image_path:
            threshold = 0.68

    if 'map_center' in image_path:
        threshold = 0.95

    if '_waypoint' in image_path:
        threshold = 0.85
        #print(image_path)
        #print('before retry')
        #print(max_val)

    if 'msgcheck' in image_path:
        threshold = 0.72

    
    
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    #random.shuffle(locations)
    
    locations = sorted(locations, key=lambda point: sort_by_center(point))


    #print(locations)
    # if '_waypoint' in image_path and not locations and (lastClickTimestamp == None or time.time() - lastClickTimestamp >= 15):
    #     for x in range(3):
    #         #print('retry')
    #         screenshot_image = screenshot(thread_name)
    #         result = cv.matchTemplate(screenshot_image, object, cv.TM_CCOEFF_NORMED)
    #         min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    #         #print('after retry -> ' + str(max_val))
    #         if max_val > threshold:
    #             print('success retry!!!')
    #             locations = np.where(result >= threshold)
    #             locations = list(zip(*locations[::-1]))
    #             random.shuffle(locations)q
    #             break

    # if '_waypoint' in image_path and not locations:
    #     if str(current_index) + '_' in image_path:
    #         current_index = current_index + 1

    #     if current_index >= len(waypoints_reference):
    #         current_index = 1
    if thread_name == 'battle':
        if locations:
            print('IN BATTLE!')
            if not message_queue.empty():
                message_queue.get()
            time.sleep(1)
        else:
            print('NO BATTLE')
            #time.sleep(1.5)
            if message_queue.empty():
                message_queue.put(time.time())
            # sendHotkey('3')
            # time.sleep(1)
            # sendHotkey('3')
            # time.sleep(1)
            # sendHotkey('3')
            # time.sleep(1)
            
        #sendHotkey('1')
        #sendHotkey('space')
        
            
            
    if locations:
        if thread_name == 'msgcheck':
            print(max_val)
            print('MSG CHECK!!!')
        
        needle_w = object.shape[1]
        needle_h = object.shape[0]
        line_color = (0, 255, 0)  # Green color for lines
        line_type = cv.LINE_4

        folder_name = os.path.dirname(image_path)  # Extract the folder name
        folder_name = os.path.basename(folder_name)
        if 'mob' in folder_name:
           #print('mob found!')
           pass

        existing_text_points = []

        for loc in locations:
            #print(locations)

            if 'msgcheck' in image_path:
                #playsound('alarm.wav')
                os.startfile('alarm.wav')
                sendHotkey('q')

            if 'waypoint' in image_path and (lastClickTimestamp == None or time.time() - lastClickTimestamp >= 10):

                #awaiting_no_battle = message_queue.get()
                
                if 'map_center' in image_name:
                    sendHotkey('stop')
                    
                    top_left = loc
                    middle_x = top_left[0] + needle_w // 2
                    middle_y = top_left[1] + needle_h // 2

                    middle_y = middle_y + 23

                    middle_point = (middle_x, middle_y)

                    delay = random.uniform(200, 225)  # Generate a random number between 0 and 10

                    mouse.position = middle_point
                    time.sleep(delay/1000) 
                    mouse.press(Button.left )
                    
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    
                    time.sleep(delay/1000)

                    middle_point = (middle_x + 23, middle_y + 24)
                    mouse.position = middle_point

                    time.sleep(delay/1000)
                    mouse.press(Button.left)
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    time.sleep(delay/1000)

                    mouse.press(Button.left)
                    time.sleep(delay/1000)
                    mouse.release(Button.left)
                    time.sleep(delay/1000)

                    #mouse.position = current_mouse_position
                    #wasMouseClick = True

                #if 'waypoint' in image_name and str(current_index) + '_' in image_path:
                if 'waypoint' in image_name and random.choice([False, True, False]):
                    print(image_name)
                    print(max_val)

                    # current_index = current_index + 1
                    # if current_index >= len(waypoints_reference):
                    #     current_index = 1

                    if not wasMouseClick:
                        lastClickTimestamp = time.time()
                        top_left = loc
                        middle_x = top_left[0] + needle_w // 2
                        middle_y = top_left[1] + needle_h // 2

                        middle_y = middle_y + 21

                        middle_point = (middle_x, middle_y)
                        
                        mouse.position = middle_point

                        delay = random.uniform(125, 255)  # Generate a random number between 0 and 10
                        time.sleep(delay/1000)  # Sleep for the amount of seconds generated
        
                        mouse.press(Button.left)
                        delay = random.uniform(125, 255)  # Generate a random number between 0 and 10
                        time.sleep(delay/1000)  # Sleep for the amount of seconds generated
                        mouse.release(Button.left)
                        wasMouseClick = True

                        #mouse.position = current_mouse_position
                        
                    else:
                        pass



                    #print('clicking waypoint!')

                    #print(image_name)
                    #if not wasMouseClick and random.choice([True, False]):
                    
            # Determine the box positions
            top_left = loc
            bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
            
           
            
            # Draw the box with green color
            cv.rectangle(screenshot_image, top_left, bottom_right, line_color, line_type)

            middle_x = top_left[0] + needle_w // 2
            middle_y = top_left[1] + needle_h // 2

            middle_point = (middle_x, middle_y)
            #print(middle_point)


            if any(abs(middle_x - existing_x) <= 20 and abs(middle_y - existing_y) <= 20 for existing_x, existing_y in existing_text_points):
                continue  # Skip this middle point

            existing_text_points.append((middle_x, middle_y))  # Add the current middle point to existing text points

            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            font_color = (0, 255, 0)  # White color
            hotkey = ''


            if 'mobs' in folder_name:
                 #awaiting_no_battle = message_queue.get()
                 if is_within_range(middle_point, 1500):
                     #print('that ^ was hit')
                     wasSalka = True

                 hotkey = 'F1'
                 folder_name = folder_name.split('/')[-1] + ' (' + str(max_val) +')'
                 howManyMobs = len(existing_text_points)
                 #print('howManyMobs? ' + str(howManyMobs))

            elif 'furie' in folder_name:
                 hotkey = 'F11'
                 folder_name = folder_name.split('/')[-1] + ' (' + hotkey +')'

            text_size, _ = cv.getTextSize(folder_name, font, font_scale, font_thickness)

            x = middle_point[0]
            y = middle_point[1] - 10

            # Calculate the position to place the text
            text_x = x - int(text_size[0] / 2) + 75
            text_y = y + int(text_size[1] / 2) - 50
            # Draw the text with green color
            cv.putText(screenshot_image, folder_name, (text_x, text_y), font, font_scale, font_color, font_thickness)
            cv.putText(screenshot_image, folder_name, (text_x + 2, text_y - 2), font, font_scale, (0,0,0), font_thickness)
            update_tkinker('update_' + str(thread_name), screenshot_image)

            if wasSalka:
                 if wasSalka:
                    
                    lastMobTimestamp = time.time()


                    #sendHotkey('F1')
                    
                    y = y + 12
                    x = x
                    # #x = x + 5
                    # if 'captain' in image_name:
                    #     x = x + 20
                        
                    # if 'small' in image_name:
                    #     x = x + 20
                        
                    #pyautogui.click(x, y, button='left')
                    
                    sword = cv.imread('assets/sword.png', cv.IMREAD_UNCHANGED)
                    k = 0
                    y = y + 15
                    y_base = y
                    y_random = list(range(-12, 12 + 1, 4))

                    pyautogui.moveTo(x, y)
                    for k in list(range(-32, 32 + 1, 4)):
                        print('finding sword with k =' + str(k))
                        new_x = x + k
                        new_y = y + k
                        print(new_x)
                        print(new_y)
                        
                        y = y_base + random.choice(y_random)
                        pyautogui.moveTo(new_x,y)
                        screenshot_near_mouse = get_cursor_image(x, y, 200)
                        near_mouse_result = cv.matchTemplate(np.array(screenshot_near_mouse), sword, cv.TM_CCOEFF_NORMED)
                        locations_of_sword = np.where(near_mouse_result >= 0.65)
                        locations_of_sword = list(zip(*locations_of_sword[::-1]))
                        print('locations')
                        print(locations_of_sword)

                        if locations_of_sword:
                            pyautogui.click(new_x, y, button='left')
                            #time.sleep(3)
                            break

                    #sendHotkey('1')
                    #sendHotkey('3')
                    
                    delay = random.uniform(100, 215)  # Generate a random number between 0 and 10
                    time.sleep((555+delay) / 1000)  # Sleep for the amount of seconds generated
                    
                    return

                    #time.sleep(0.8 + (delay/1000))

                    # time.sleep(0.4)
                    # sendHotkey('F1')
            else:
               pass

            if wasSalka or wasMouseClick:
                #print('returning....')
                return True
    else:
        if 'mobs' in image_path:
            if lastMobTimestamp == None:
                if message_queue.empty():
                    message_queue.put(time.time())
            else:
                differenceBetweenLastMobFound = time.time() - lastMobTimestamp
                print('difference is : ' + str(differenceBetweenLastMobFound))

            if message_queue.empty() and differenceBetweenLastMobFound != None and differenceBetweenLastMobFound > 3:
                print('sending to queue!')
                #sendHotkey('F10')
                message_queue.put(time.time())
        pass
        #print('Needle not found.')

   
        


window_width = 1200
window_height = 600
def on_close():
    print('on close function')
    global root
    global threads
    # global instance
    # if player is not None:
    #     player.stop()
    #     player.get_media().release()
    #     player.release()
    #     player.get_instance().release()
    print(threads)
    for speech_thread in threads:
        if speech_thread.is_alive():
            speech_thread.terminate()
    #root.destroy()
    sys.exit(1)

import os

folder_path = 'assets'
folder_files_dict = {}
imagesByImagePath = {}

for root, dirs, files in os.walk(folder_path):
    if root != folder_path:  # Exclude the 'assets' folder itself
        folder_name = os.path.relpath(root, folder_path)
        folder_files_dict[folder_name] = []
        for file in files:
            if 'xd_map_center' not in file:
                image_path = os.path.join(root, file).replace('\\', '/')
                folder_files_dict[folder_name].append(image_path)
                imagesByImagePath[image_path] = cv.imread(image_path, cv.IMREAD_UNCHANGED)
                
#print(folder_files_dict)
import cv2
from PIL import ImageGrab, ImageOps
import ctypes

def get_cursor():
    hcursor = win32gui.GetCursorInfo()[1]
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 36, 36)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0,0), hcursor)
    
    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    cursor = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1).convert("RGBA")
    
    #win32gui.DestroyIcon(hcursor)    
    #win32gui.DeleteObject(hbmp.GetHandle())
    #hdc.DeleteDC()


    pixdata = cursor.load()


    width, height = cursor.size
    for y in range(height):
        for x in range(width):

            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = (0, 0, 0, 0)


    hotspot = win32gui.GetIconInfo(hcursor)[1:3]

    return (cursor, hotspot)

from io import BytesIO
def get_cursor_image(center_x, center_y, diameter):
    # Calculate the coordinates of the square
    left = center_x - diameter // 2
    top = center_y - diameter // 2
    right = left + diameter
    bottom = top + diameter

    # Take a screenshot using PIL
    cursor, (hotspotx, hotspoty) = get_cursor()
    return cursor


    # ratio = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    # screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    
    # pos_win = win32gui.GetCursorPos()
    # pos = (round(pos_win[0]*ratio - hotspotx), round(pos_win[1]*ratio - hotspoty))


    # screenshot.paste(cursor, pos, cursor)
    # # Save the screenshot
    # screenshot.save("square_screenshot.png")
    # return screenshot
    
def capture_rectangle(left, upper, right, lower):
    # Capture the screen region within the specified rectangle
    image = None
    try:
        image = ImageGrab.grab(bbox=(left, upper, right, lower))
        image = ImageOps.invert(image)
        
        image = image.convert("RGB")

        pixels = image.load()

        target_color = (14, 68, 68)
        # Iterate through each pixel
        for i in range(image.width):
            for j in range(image.height):
        # Check if the pixel is not black and not a shade of gray
                r, g, b = pixels[i, j]
                if r != 0 or g != 0 or b != 0:
                    gray_value = 0.299 * r + 0.587 * g + 0.114 * b  # Convert to grayscale
                    if gray_value > 55:
                        pixels[i, j] = (255, 255, 255)
                        # Check color similarity to the target color
                    color_difference = sum(abs(x - y) for x, y in zip((r, g, b), target_color))
                    if color_difference < 55:
                        # Set the pixel to white
                        pixels[i, j] = (255, 255, 255)

        #image.save('xd.png')
        # image = np.array(image)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # _, image =  cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        #image.save('xd.png')
    except Exception as e:
        print(e)
        pass
    
    return image

import re

def remove_non_numbers(text):
    pattern = r'\D'  # Regular expression pattern to match non-numeric characters
    result = re.sub(pattern, '', text)
    return result

def get_value_by_cooridantes(left, upper, right, lower):
    hp_screenshot = capture_rectangle(left, upper, right, lower)
    # if hp_screenshot == None:
    #     return 100
    
    image_array = np.array(hp_screenshot)

    # Count the number of white pixels
    white_pixels = np.sum(image_array == 255)

    # Calculate the total number of pixels
    total_pixels = image_array.size

    # Calculate the percentage of white pixels
    percentage_white = (white_pixels / total_pixels) * 100

    print(f"Percentage of white pixels: {percentage_white:.2f}%")
    
    text = percentage_white

    return text
    
energyRoom = False
iteration = 0
def heal():
    global energyRoom, iteration
    #time.sleep(0.5)q
    if energyRoom is False:
        hp = get_value_by_cooridantes(1115,141,1178,156)
        if hp:
            time.sleep(1)
            #print(hp)
            if hp < 42:
                sendHotkey('5')
    else:
        time.sleep(0.17)
    #print('hp: ' + str(hp))
    # if energyRoom is False:
    #     if (energyRoom == False and hp != 10 and hp != 100) or (energyRoom and hp != 10 and hp < 70):
    #             print('hp!')
    #             sendHotkey('F3')
    #             if energyRoom == False:
    #                 sendHotkey('F5')


    #         #time.sleep(0.1)
    #         # if energyRoom is False:
    #         #     sendHotkey('F3')

    # if energyRoom:
    #     iteration = iteration + 1
        
    #     print('iteration ->' + str(iteration))
    #     if iteration >= 75:
    #         sendHotkey('F3')
    #         iteration = 0
    #         sendHotkey('spin')
    #         time.sleep(1.5)
    #         sendHotkey('F2')

                
    # if energyRoom is False:
    #     mana = get_value_by_cooridantes(1804,107,1826,116)
    #     print(mana)
    #     if (mana != 10 and mana != 100 and mana < 60):
    #             sendHotkey('F5')
    #             print('mana!')

def screenshot(thread_name):
    wincap = WindowCapture(None)
    screenshot = wincap.get_screenshot()
    #print(screenshot)
    #screenshot = pyautogui.screenshot()
    #print(screenshot)
    screenshot_image = screenshot
    if 'mob' in thread_name:
        #cv.imwrite('debug.png', screenshot_image)
        #screenshot.save('debug2.png')
        pass
    screenshot_image_gray = screenshot
    update_tkinker('update_' + str(thread_name), screenshot_image)
    return screenshot_image

from msvcrt import getch
import os
import signal

def custom_sort(item):
    if any(char.isdigit() for char in item):
        return (1, item)
    else:
        return (0, item)
    


def replace_color(image_path, target_color, replacement_color, tolerance=50):
    img = Image.open(image_path)

    # Convert the image to a NumPy array
    img_array = np.array(img)

    # Define the target color and replacement color
    target_rgb = np.array([int(target_color[i:i+2], 16) for i in (0, 2, 4)])
    replacement_rgb = np.array([int(replacement_color[i:i+2], 16) for i in (0, 2, 4)])

    # Define a tolerance level for color replacement
    tolerance_range = np.array([tolerance, tolerance, tolerance])

    # Create a mask for pixels close to the target color
    mask = np.all(np.abs(img_array - target_rgb) < tolerance_range, axis=-1)

    # Replace pixels in the mask with the replacement color
    img_array[mask] = replacement_rgb

    # Save the modified image with specified quality
    modified_img = Image.fromarray(img_array)
    modified_img.save('modified_image.jpg', quality=95)
    return modified_img

    
def combine_arrays_in_dict(dictionary):
    result = []
    for key in dictionary:
        result.extend(dictionary[key])
    return result

filtered_dict = None
waypoints_reference = []
current_index = 1
def listen(thread_name, message_queue):
    #time.sleep(2)
    global db_window
    if db_window == None:
        db_window = gw.getWindowsWithTitle('Flyff Universe')[0]
    global folder_files_dict
    global img
    global canvas
    global loopFiles
    global filtered_dict
    global waypoints_reference

    if filtered_dict == None:
        #filtered_dict = {key: value for key, value in folder_files_dict.items() if thread_name in key}
        filtered_dict = {key: sorted(value, key=custom_sort) for key, value in folder_files_dict.items() if thread_name in key}
        print('filtered dict:')
        print(filtered_dict)
        if 'waypoint' in thread_name:
            #total_length = sum(len(value) for value in filtered_dict.values())
            waypoints_reference = combine_arrays_in_dict(filtered_dict)
        
        print('thread name -> ' + thread_name)

    while True:

        if thread_name == 'hotkey':
            sendHotkey('1')
            continue
        
        if thread_name == 'space':
            sendHotkey('space')
            time.sleep(1)
            sendHotkey('1')
            time.sleep(15)
            continue
        
        if thread_name == 'smooth':
            screenshot(thread_name)
            continue

        if 'heal' in thread_name:
            #print('heal check...')
            heal()
        else:    
            for folder, files in filtered_dict.items():
                #print('current folder ' + str(folder))
                for image_path in files:
                    #print('current image ' + str(image_path))
                    
                    if 'mob' in thread_name:
                        awaiting_no_battle = message_queue.get()
                        sendHotkey('4')
                        sendHotkey('4')
                        time.sleep(1)
                        sendHotkey('4')
                    
                    if 'battle' in thread_name:
                        #time.sleep(1)
                        pass
                        
                    screenshot_image = screenshot(thread_name)
                    image_name = image_path.split('/')[-1]
                    if 'waypoint' in image_name:
                        screenshot_image = screenshot(thread_name)

                    #print(image_path)

                    if 'battle' in thread_name:
                        screenshot_image = ImageGrab.grab(bbox=(1546, 140, 1563, 155))
                        screenshot_image = np.array(screenshot_image)

                    if 'mob' in thread_name:    
                        # response = recognize(image_path,   
                        #                      np.array(replace_color(image_path, 
                        #                                    'D6D5A2', 
                        #                                    'E50808', 
                        #                                    80)), None, thread_name, message_queue)
                        # if response == True:
                        #     break
                        
                        response = recognize(image_path, screenshot_image, None, thread_name, message_queue)
                    else:
                        response = recognize(image_path, screenshot_image, None, thread_name, message_queue)
                        

                    if response == True:
                        break
                        #heal()
                    else:
                        if 'mob' in thread_name:
                            for i in range(7):
                                sendHotkey('right')
                            

                    global howManyMobs
                    howManyMobs = 0


       
def update_tkinker(file_name, screenshot_image):
    global img
    global canvas
    global loopFiles
    file_name = file_name + '.jpg'
    if not 'mob' in file_name:
        return

    # cv.imwrite(file_name, screenshot_image)
    # tk_image  = Image.open(file_name)
    # tk_image = tk_image.resize((window_width, window_height), Image.ANTIALIAS)
    # render = ImageTk.PhotoImage(tk_image)

    pil_image = Image.fromarray(cv.cvtColor(screenshot_image, cv.COLOR_BGR2RGB))

    # Resize the PIL Image
    resized_image = pil_image.resize((window_width, window_height), Image.LANCZOS)

    # Convert PIL Image to Tkinter ImageTk format
    render = ImageTk.PhotoImage(resized_image)

    canvas.create_image(0, 0, anchor=tk.NW, image=render)
    canvas.update()

root = tk.Tk()
root.attributes("-topmost", False) 
root.title("PROJECT DICK LAURENT IS DEAD")
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
x = (ws/2) - (window_width/2)
y = (hs/2) - (window_height/2)
x = -x - 1000
y = -y + 250

root.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

root.protocol("WM_DELETE_WINDOW", on_close)
canvas = tk.Canvas(root, width=window_width, height=window_height, highlightthickness=0)
canvas.pack()
threads = []



from multiprocessing import Process, Event, Queue
if __name__ == '__main__':

    #WindowCapture.list_window_names()
    message_queue = Queue()

    event = Event()

    heal_thread = Process(target=listen, args=('heal', message_queue, ))
   
    mob_thread = Process(target=listen, args=('mob', message_queue, ))
    battle_thread = Process(target=listen, args=('battle', message_queue, ))


    cavebot_thread = Process(target=listen, args=('waypoint', message_queue, ))

    alarm_thread = Process(target=listen, args=('msgcheck', message_queue, ))
    
    hotkey_thread = Process(target=listen, args=('hotkey', message_queue, ))
    space_thread = Process(target=listen, args=('space', message_queue, ))


    threads.append(heal_thread)
    threads.append(battle_thread)
    threads.append(mob_thread)
    #threads.append(hotkey_thread)
    threads.append(space_thread)
    
    #threads.append(cavebot_thread)
    #threads.append(alarm_thread)

    for thread in threads:
        thread.start()

    from pynput.keyboard import Listener

    def on_press(key):
        #print("Key pressed: {0}".format(key))
        key = str(key).replace("'", '')
        if str(key) == 'q':
            print('terminating')
            on_close()

    def on_release(key):
        pass

    with Listener(on_press=on_press, on_release=on_release) as listener:
        print('click q to exit(1)')
        listener.join()

    #root.mainloop()
