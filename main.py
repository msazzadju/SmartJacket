from tools.SMS import SMS
from tools.GPS import GPS
import serial
import time
from tqdm import tqdm
import os

match_str_start = "**start_gps_camera**"
match_str_stop = "**stop_gps_camera**"
phone_number = '+8801521380560'
wait_time = 60000

camera_start_cmd = ""
camera_stop_cmd = ""

ser_ = serial.Serial('COM5', 115200)
ser_.flushInput()

print("Initializing...")
time.sleep(60)

while True:
    sms_c = SMS(ser=ser_)
    print("Waiting...")
    sms_c.rcv_live_sms()
    while True:
        if ser_.inWaiting():
            time.sleep(0.01)
            rec_buff = ser_.read(ser_.inWaiting())
            if rec_buff != '':
                if match_str_start in rec_buff.decode():
                    # os.system(camera_start_cmd)
                    break
    print("Resume...")

    sms_c.rcv_live_sms()
    cont = True
    gps_c = GPS(ser=ser_)
    gps_c.init_gps()
    while cont:
        gps_pos = gps_c.get_gps_position()
        time.sleep(0.5)
        while not gps_pos:
            gps_pos = gps_c.get_gps_position()
            print("Retrying to fetch GPS info...")
            time.sleep(1.0)
        if gps_pos:
            stat = sms_c.send_sms(
                phone_number=phone_number,
                text_message=f"{gps_pos[0]}, {gps_pos[1]}"
            )
            if stat:
                print("sms sent")
            else:
                print("sms failed")
        print("Waiting a few minutes......")
        for w in tqdm(range(wait_time)):
            if ser_.inWaiting():
                time.sleep(0.01)
                rec_buff = ser_.read(ser_.inWaiting())
                if rec_buff != '':
                    if match_str_stop in rec_buff.decode():
                        cont = False
                        # os.system(camera_stop_cmd)
                        break
            time.sleep(0.001)
