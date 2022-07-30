# Simon Says game... repeat after me.
# Graham Kneen
# July 31, 2022
#
# Hardware: Raspberry Pi Pico
#           Pimoroni Pico Display PIM543
# Optional  Pimoroni Pico Omnibus (dual expander) PIM556
#           Passive piezeo buzzer
#           F-F jumper wires
#
# Software: Pimoroni Micropython version 1.19.1 (uf2 file)
#
# Thanks to Bill at dronebotworkshop.com for a similar project
# with discrete LEDs and coded in c/c++
#
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from machine import Pin, PWM
from pimoroni import Button
import time
import random

# We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM!
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)
# display set up and parameters

display.set_backlight(0.7)
display.set_font("bitmap8")
buzzer = PWM(Pin(3))  # (optional) hook up passive piezeo buzzer, + to pin 3, - to GND

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# colours tuple in order are Black, Yellow, Green, Red, Blue
colours = (
    display.create_pen(0, 0, 0), 
    display.create_pen(255, 255, 0),
    display.create_pen(0, 255, 100),
    display.create_pen(255, 0, 0),
    display.create_pen(0, 0, 255))

w,h = display.get_bounds()
centerX = int(w/2)               # x boundary in coloured frame
centerY = int(h/2)               # y boundary in coloured frame
thick = 15                       # frame thickness  
speed = 1                        # how long to show the dot
iconSize = 30                    # display size of icons

# parameters for Simon game
MAX_LEVEL = 50

# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(colours[0])
    display.clear()
    display.update()
    
def text(words, delay):
    display.set_pen(colours[3])
    display.text(words, 20, 30, 210, 3)
    display.update()
    time.sleep(delay)
    clear()

def frame(fx, fy, th):
    # Function to create the button frame
    # display polygon to define the frame for pin A YELLOW

    display.set_pen(colours[1])
    display.polygon([(0,0),(fx,0),(fx,th),(th,th), (th,fy),(0,fy)])

    # display polygon to define the frame for pin B RED

    display.set_pen(colours[3])
    display.polygon([(0,fy+1),(th,fy+1),(th,h-th),(fx,h-th),(fx,h),(0,h)])

    # display polygon to define the frame for pin Y GREEN

    display.set_pen(colours[2])
    display.polygon([(fx+1,h),(w,h),(w,fy+1),(w-th,fy+1),(w-th,h-th),(fx+1,h-th)])

    # display polygon to define the frame for pin X BLUE

    display.set_pen(colours[4])
    display.polygon([(w,fy),(w,0),(fx+1,0),(fx+1,th),(w-th,th),(w-th,fy)])
    display.update()

def playTone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)

def beQuiet():
    buzzer.duty_u16(0)

def showColourIcon(cx, cy, showColour, duration, iSize):
    display.set_pen(colours[showColour])
    if showColour == 1:     # Yellow
        display.circle(cx, cy, iSize)
        playTone(329)
    if showColour == 2:     # Green
        display.rectangle(cx-iSize, cy-iSize, 2*iSize, 2*iSize)
        playTone(261)
    if showColour == 3:     # Red
        display.triangle(cx-iSize, cy+iSize, cx, cy-iSize, cx+iSize, cy+iSize)
        playTone(293)
    if showColour == 4:     # Blue
        display.triangle(cx-iSize, cy-iSize, cx+iSize, cy-iSize, cx, cy+iSize)
        playTone(349)
        
    display.update()
    time.sleep(duration)
    beQuiet()

    display.set_pen(colours[0])    #Set to Black to erase
    if showColour == 1:
        display.circle(cx, cy, iSize)
    if showColour == 2:
        display.rectangle(cx-iSize, cy-iSize, 2*iSize, 2*iSize)
    if showColour == 3:
        display.triangle(cx-iSize, cy+iSize, cx, cy-iSize, cx+iSize, cy+iSize)
    if showColour == 4:
        display.triangle(cx-iSize, cy-iSize, cx+iSize, cy-iSize, cx, cy+iSize)
      
    display.update()
    time.sleep(duration/2)

def get_button():
    response = 0
    while response == 0:
        if button_a.read():
            response = 1
        if button_b.read():
            response = 3
        if button_x.read():
            response = 4
        if button_y.read():
            response = 2
        time.sleep(.2)
    return response

# ===Main ===
while True:
    
    display.set_pen(colours[3])

    display.text("SIMON says...", 0, 0, 240, 3)
    display.text("Press A to begin", 0, 50, 240, 3)
    display.text("Press B for HELP", 0, 100, 240, 3)
    display.update()


    if button_a.read():
        clear()
        # print("Start game")
        # generate random sequence of coloured icons up to MAX_Level
        level = 1
        velocity = 1
        random.seed()
        sequence = []
        for i in range(MAX_LEVEL):
            select_icon = random.randint(1,4)
            sequence.append(select_icon)
        
        # Show the sequence of icons to the player
        while level > 0:
            frame(centerX, centerY, thick)
            time.sleep(1)
            for i in range(level):
                showColourIcon(centerX, centerY,sequence[i],velocity, iconSize)
            clear()
            text("Use buttons to repeat sequence", 1)
            
            # Get player sequence of icons
            frame(centerX, centerY, thick)
            user_sequence = []
            for i in range(level):
                user_icon = get_button()
                user_sequence.append(user_icon)
                showColourIcon(centerX, centerY,user_sequence[i],1, iconSize)
            
            # compare user sequence to Simon's sequence
            status = 1
            for i in range(level):
                if user_sequence[i] != sequence[i]:
                    status = 0
            if status == 1:
                if level < MAX_LEVEL:
                    clear()
                    text("SUCCESS", .5)
                    levelStatus = "You have reached level " + str(level)
                    text(levelStatus, 1)
                    level = level +1
                    velocity = velocity - .005   # speed up the display of icons
                else:
                    clear()
                    text("Win! Win! Win!", 1)
                    levelStatus = "You have reached the maximum level of " + str(level)
                    text(levelStatus, 2)
                    level = 0
            else:
                clear()
                playTone(400)
                text("FAILURE - NO MATCH", 1)
                playTone(233)
                levelStatus = "You reached level " + str(level-1)
                text(levelStatus, 2)
                beQuiet()
                level = 0
                               
    if button_b.read():   # help screens
        clear()
        text("Here are the 4 icons", 2)
        frame(centerX, centerY, thick) # display the frame
        # Display the icon, colour and tone

        showColourIcon(centerX, centerY, 1, speed, iconSize)
        showColourIcon(centerX, centerY, 2, speed, iconSize)
        showColourIcon(centerX, centerY, 3, speed, iconSize)
        showColourIcon(centerX, centerY, 4, speed, iconSize)
        clear()
        
        text("Memorize the sequence of icons", 3)
        text("Use the coloured buttons to repeat the sequence", 3)
        
        # print("Showing icons")
