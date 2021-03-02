import pydirectinput
import time
import pyautogui
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"D:\0Armand\Installations\Tesseract\tesseract.exe"

""" === Slot tuples Creation === """


def all_inventory_slots(pos_slot1, pos_slot9, offhand_pos):
    """
    Returns an int with the slot size and tuple of tuples with coordinates 
    to all 41 inventory slots (inventory + off-hand + armor). 
    Slot 1 is the bottom left, slot 36 top right
    Slot 1-36 : inventory, 37 : off-hdand, 38-41 : armor

    :param pos_slot1: <tuple> Slot 1 coordinates; Expected format (X, Y)
    :param pos_slot9: <tuple> Slot 9 coordinates; Expected format (X, Y)
    :param offhand_pos: <tuple> Offhand Slot coordinates; Expected format (X, Y)   
    """

    slot_size = (pos_slot9[0] - pos_slot1[0])/8
    all_inv = (None, )#Index 0 is nothing to match indexes and slot numbers

    #--- Inventory ---#
    for row in range(4):
        for column in range(9):
            new_size = slot_size
            if row != 0: #Extra padding between hotbarslots and inventory
                new_size += 4

            slot_pos = (pos_slot1[0] + column*slot_size, pos_slot1[1] - row*new_size)
            slot_pos = int(slot_pos[0]), int(slot_pos[1])#pydirectinput only accepts int coords

            all_inv += (slot_pos,)
    
    #--- OffHand slot ---#
    offhand_pos =int(offhand_pos[0]), int(offhand_pos[1])
    all_inv += (offhand_pos,)

    #--- Armor Slots ---#
    for row in range(1, 5):
        armor_pos = (pos_slot1[0], all_inv[28][1] - row*slot_size + 10)
        # +5 accounts for extra padding between inventory and armor slots
        armor_pos =int(armor_pos[0]), int(armor_pos[1])
        all_inv += (armor_pos,)
    
    return int(slot_size), all_inv


def all_hotbar_slots(pos_slot1, pos_slot9):
    """
    Returns an int with the slot size and tuple of tuples with coordinates 
    to all 9 hotbar slots
    Slot 1 is the farthest on the left, Slot 9 on the right

    :param pos_slot1: <tuple> Slot 1 coordinates; Expected format (X, Y)
    :param pos_slot9: <tuple> Slot 9 coordinates; Expected format (X, Y)
    :param offhand_pos: <tuple> Offhand Slot coordinates; Expected format (X, Y)   
    """
    slot_size = (pos_slot9[0] - pos_slot1[0])/8
    all_htbar = (None, )#Index 0 is nothing to match indexes and slot numbers

    #--- Hotbar ---#
    for column in range(9):
        htbar_slot = (pos_slot1[0] + column*slot_size, pos_slot1[1])
        all_htbar += (int(htbar_slot[0]), int(htbar_slot[1])), 

    return int(slot_size), all_htbar


""" === Actual Data retreivers === """


def item_amount(slot_pos, slot_size, filename, ss_path, hotbar=False):
    """
    Returns an int with the item amount on the slot, if nothing is found
    in the inventory 1 is the default amount (because not shown in minecraft)

    If working with the hotbar, the check for an item or not happens in this
    function (hotbar = True), and will return 0 if no item found (still 1 by default)

    :param slot_pos: <tuple> Expected format (X, Y)
    :param filename: <str> Filename with extension excluded
    :param slot_size: <int> Slot sizes
    :param ss_path: <str> Filepath where file has to be saved
    :param hotbar: <bool> Hotbar item_amount has an extra step
    to verify if there is an item 
    """
    
    posX, posY = int(slot_pos[0]), int(slot_pos[1])

    #--- Screenshot manipulations ---#

    item_screen = pyautogui.screenshot(f"{ss_path}{filename}.png",\
         region=(posX, posY, slot_size, slot_size)) #Takes screenshot
    

    item_screen = cv2.imread(f"{ss_path}{filename}.png") #cv2 needs a different format

    if hotbar:
        empty_slot = cv2.imread('empty_slot.png') #empty slot screen to compare to screenshot
        result = cv2.matchTemplate(item_screen, empty_slot, cv2.TM_CCOEFF_NORMED)
        max_val = cv2.minMaxLoc(result)[1]#We only need the max_val

        empty_slot_selected = cv2.imread('empty_slot_selected.png')
        result2 = cv2.matchTemplate(item_screen, empty_slot_selected, cv2.TM_CCOEFF_NORMED)
        max_val2= cv2.minMaxLoc(result2)[1]#We only need the max_val

        if max_val >= 0.999 or max_val2 >= 0.999: #Near perfect or perfect match with empty slot
            return 0 # 0 items then

    _, item_screen = cv2.threshold(
        item_screen, 251, 255, cv2.THRESH_BINARY) #Binarization for better OCR

    # Note : the cv2.treshold returns the screenshot but also the treshhold used (251 here)
    # We don't need it so it goes in the throwaway _ variable

    #--- OCR ---#
    amount = pytesseract.image_to_string(item_screen,\
         config='--psm 8 -c tessedit_char_whitelist=0123456789')
    # --psm 8 means 'Treat the image as a single word.'
    # other modes can be found here https://github.com/tesseract-ocr/tesseract/issues/434

    # the whitelist option removes all other characters than numbers
    # as we know those are errors since we are looking for a number

    if len(amount) == 1: #Nothing detected
        amount = '1\n♀'
    
    amount = amount.split('\n')#There is always a "♀" character at the end

    return amount[0]


def inventory_item_full_info(slot_i, slot_pos, slot_size, ss_path):
    """
    Returns a tuple follow this format : (slot_i, item_name, amount) (int, str, int)
    It uses the item_amount function

    :param slot_i: <int> Slot index
    :param slot_pos: <tuple> Format (X, Y)
    :param slot_size: <int> Slot size (needed for item_amount screenshots)
    :param ss_path: <str> Path to save screenshots (it spams them) Example : "./screenshots/"
    """
    max_length = 400
    slot_info = (slot_i, "null", "null")#Won't be changed if no items detected

    pydirectinput.moveTo(slot_pos[0], slot_pos[1])
    screenshot = pyautogui.screenshot(f"{ss_path}slot_{slot_i}.png",\
         region=(slot_pos[0]+17,slot_pos[1]-30, max_length, 24))#Takes Screenshot


    pixel = screenshot.getpixel((1, 0))#First top left pixel indicates if we found an item
    # item names are surrounded in a pink/black box, that we use to detect if one found


    if (25 <= pixel[0] <= 45) and (0 <= pixel[1] <= 15) and (80 <= pixel[2] <= 100): 
        # More or less close to (35, 0, 90) that we're looking for
        # If entered here, an item has been detected

        width = max_length - 1
        while width >= 0:
            new_px = screenshot.getpixel((width, 0))
            if (25 <= new_px[0] <= 45) and (0 <= new_px[1] <= 15) and (80 <= new_px[2] <= 100):
                # Means we reached the box around item name, no extra space on the right anymore
                break
            width -= 10
        print(width)

        screenshot = pyautogui.screenshot(f"{ss_path}slot_{slot_i}.png",\
             region=(slot_pos[0]+17,slot_pos[1]-30, width, 24))#New updated screenshot
            # Better OCR as a result of cropping the image

        content = pytesseract.image_to_data(screenshot)
        # image_to_data separates all text found in words

        item_name = ''

        for x, bx in enumerate(content.splitlines()): # Each line holds different data

            if x != 0: # First line is a different format and holds no data we need 
                bx = bx.split()
                
                if len(bx) == 12: # len is 12 when a word is found

                    item_name += f'{bx[11]} ' # word held at index 11 (last one)
        
        pyautogui.moveTo(64, 103)#Outside of inventory to not block item screenshot

        
        amount = item_amount(slot_pos, slot_size, f'slot_{slot_i}_amount.png', ss_path=ss_path)
        # Calls item_amount to get the amount on this slot

        slot_info = (slot_i, item_name, amount)

    return slot_info


def get_inv_tuple(slot_size, slots, ss_path, starting_i=1):
    """
    Calls the inventory_item_full_info() on all items within the tuple slots
    Warning : Inventory must be opened before executing this function
    Returns tuples of tuples in the following format : ((slot_i, item_name, amount),)

    :param slot_size: <int> Slot size (needed for item_amount screenshots)
    :param slots: <tuple> Tuple witht the pos to all the inv slots to scan  Format : ((X, Y),)
    :param ss_path: <str> Path to save screenshots (it spams them) Example : "./screenshots/"
    :param starting_i: <int> Used to debug screenshots 
    (to understand link between ss name and slot scanned)
    """
    
    all_slots_info = ()

    for slot_i, slot_pos in enumerate(slots): #gives us an index and an element

        slot_info = inventory_item_full_info(slot_i+starting_i, slot_pos, slot_size, ss_path=ss_path)
        all_slots_info += (slot_info),
    
    return all_slots_info


def get_bar_tuple(slot_size, slots, ss_path, starting_i=1):

    """
    Calls the item_amount() on all items within the tuple slots
    Warning : Player has to be outside of any menu, including chat
    in order to work properly
    This function can be ran in a thread
    Returns tuples of tuples in the following format : (amount,)

    :param slot_size: <int> Slot size (needed for item_amount screenshots)
    :param slots: <tuple> Tuple witht the pos to all the inv slots to scan  Format : ((X, Y),)
    :param ss_path: <str> Path to save screenshots (it spams them) Example : "./screenshots/"
    :param starting_i: <int> Used to debug screenshots 
    (to understand link between ss name and slot scanned)
    """

    all_slots_info = ()

    for slot_i, slot_pos in enumerate(slots): #gives us an index and an element

        slot_info = item_amount(slot_pos, slot_size,f'hotbar_slot_{slot_i+starting_i}', ss_path=ss_path, hotbar=True)
        all_slots_info += (slot_info),
    
    return all_slots_info


if __name__ == '__main__':
    
    #My values with Gui Scale 2, 1920*1080 resolution and not full screen
    slot_1 = 956, 652
    slot_9 = 1240, 649
    offhand = 1093, 487

    htbar_s1 = 784, 1003
    htbar_s9 = 1106, 1003


    inv_slot_size, inventory_slots = all_inventory_slots(slot_1, slot_9, offhand)
    htbar_slot_size, htbar_slots = all_hotbar_slots(htbar_s1, htbar_s9)


    print(get_bar_tuple(htbar_slot_size, htbar_slots[1:], './screenshots/'))
    # for slot in inventory_slots[1:]:
    #     slot_info = inventory_item_full_info(inventory_slots.index(slot), slot, inv_slot_size, "./screenshots/")
    
    pydirectinput.click()

    # for slot in htbar_slots[1:]:
    #     htbar_info = item_amount(slot, htbar_slot_size, f"htbar_slot_{htbar_slots.index(slot)}", "./screenshots/")