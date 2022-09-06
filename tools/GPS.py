import serial
import time
import math


class GPS:
    def __init__(self, ser=None):
        self.serial = ser

    def send_at(self, command, back, timeout):
        rec_buff = ''
        self.serial.write((command + '\r\n').encode())
        time.sleep(timeout)
        if self.serial.inWaiting():
            time.sleep(0.01)
            rec_buff = self.serial.read(self.serial.inWaiting())
        if rec_buff != '':
            if back not in rec_buff.decode():
                print(command + ' ERROR')
                print(command + ' back:\t' + rec_buff.decode())
                return 'ERROR'
            else:
                return rec_buff.decode()
        else:
            print('GPS is not ready')
            return 'ERROR'

    def init_gps(self):
        print('Start GPS session...')
        out = self.send_at('AT+CGPS=1,1', 'OK', 1)
        time.sleep(2)

    def get_gps_position(self):
        out = self.send_at('AT+CGPSINFO', '+CGPSINFO: ', 1)
        if 'ERROR' not in out:
            if ',,,,,,' in out:
                print('GPS is not ready')
                time.sleep(1)
                return False
            else:
                mod_out = out.strip().replace('+CGPSINFO: ', '').split('\n')[1].split(',')
                coord = self.get_lat_long(mod_out)
                return coord
        else:
            print('error')
            out = self.send_at('AT+CGPS=0', 'OK', 1)
            return False

    @staticmethod
    def truncate(number, digits):
        nb_decimals = len(str(number).split('.')[1])
        if nb_decimals <= digits:
            return number
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper

    def get_lat_long(self, gps_data):
        lat_deg = gps_data[0].split('.')[0][:-2]
        lat_min = gps_data[0].replace(lat_deg, '')
        long_deg = gps_data[2].split('.')[0][:-2]
        long_min = gps_data[2].replace(long_deg, '')
        lat = float(lat_deg) + float(lat_min)/60
        long = float(long_deg) + float(long_min)/60
        lat_t = f'{self.truncate(lat, 7)}{gps_data[1]}'
        long_t = f'{self.truncate(long, 7)}{gps_data[3]}'
        return [lat_t, long_t]


if __name__ == '__main__':
    from SMS import SMS
    ser_ = serial.Serial('COM5', 115200)
    ser_.flushInput()
    sms_c = SMS(ser=ser_)
    print("Waiting...")
    sms_rcv = sms_c.rcv_sms()
    print("Resume...")
    print(sms_rcv)
    gps_c = GPS(ser=ser_)
    gps_c.init_gps()
    gps_pos = gps_c.get_gps_position()
    phone_number = '+8801760440736'
    if gps_pos:
        stat = sms_c.send_sms(
            phone_number=phone_number,
            text_message=f"latitude: {gps_pos[0]}, longitude: {gps_pos[1]}"
        )
        if stat:
            print("sms sent")
        else:
            print("sms failed")

