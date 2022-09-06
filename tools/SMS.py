import serial
import time
import math


class SMS:
    def __init__(self, ser):
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
            print('SMS is not ready')
            return 'ERROR'

    def send_sms(self, phone_number, text_message):
        # print("Setting SMS mode...")
        self.send_at("AT+CMGF=1", "OK", 1)
        # print("Sending Short Message")
        answer = self.send_at("AT+CMGS=\"" + phone_number + "\"", ">", 2)
        if 'ERROR' not in answer:
            self.serial.write(text_message.encode())
            self.serial.write(b'\x1A')
            answer = self.send_at('', 'OK', 20)
            if 'ERROR' not in answer:
                # print('send successfully')
                return True
            else:
                # print('error')
                return False
        else:
            return False

    def del_all_msg(self):
        self.send_at('AT+CMGF=1', 'OK', 1)
        self.send_at('AT+CMGD=,4', 'OK', 1)

    def rcv_live_sms(self):
        self.send_at('AT+CNMI=2,2,0,0,0', 'OK', 1)

    def rcv_sms(self):
        rec_buff = ''
        self.send_at('AT+CMGF=1', 'OK', 1)
        # self.send_at('AT+CMGD=,4', 'OK', 1)
        self.send_at('AT+CPMS=\"SM\",\"SM\",\"SM\"', 'OK', 1)
        answer = self.send_at('AT+CMGR=1', '+CMGR:', 2)
        if 'ERROR' not in answer:
            if 'OK' in answer:
                return answer
            else:
                return False
        else:
            return False
        return answer


