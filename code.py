# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Modified: Aaron Krawczyk ()
# Assistance: Cursor and Claud AI
# April 2025
# Fixes issue with webserver not writing new file
# or writing file after editing.
# Wirtes to file but overloads webserver on Pico W 2022.
# PICO 1, 2 and W board support

import time
import digitalio
from board import *
import board
from duckyinpython import *
import supervisor
import socketpool
import asyncio

if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    import wifi
    
    # Modification AK
    from webapp import init_web_app, startWebService

# Modification AK
# Global variable to store the socket pool
global_pool = None

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

# Modification AK
def startWiFi():
    """--------------------------------------------------------------------------------------"""
    ssid = "Pico WIFI DUCK"
    password = "pico123456"
    """--------------------------------------------------------------------------------------"""
    print("Creating access point", ssid)
    wifi.radio.stop_station()
    wifi.radio.start_ap(ssid, password)
    print("Access point created!")
    global global_pool
    global_pool = socketpool.SocketPool(wifi.radio)
    # Initialize the web app with the pool
    init_web_app(global_pool)
    return global_pool

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()


progStatus = False
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if(progStatus == False):
    print("Finding payload")
    # Run the payload script
    # not in setup mode, inject the payload
    payload = selectPayload()
    print("Running ", payload)
    runScript(payload)

    print("Done")
else:
    print("Update your payload")

led_state = False

async def main_loop():
    global led,button1

    button_task = asyncio.create_task(monitor_buttons(button1))
    if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, button_task, webservice_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, button_task)

asyncio.run(main_loop())


