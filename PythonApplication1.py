from machine import Pin
import time, micropython, machine

LED_PIN = 47
KEY_PIN = 9

led = Pin(LED_PIN, Pin.OUT)
key_pin = Pin(KEY_PIN, Pin.IN, Pin.PULL_UP)

class KeyState:
    idle = 0
    filter_a = 1
    down_a = 2
    filter_b = 3
    wait = 4
    filter_c = 5
    longpress = 6
    down_b = 7
    filter_d = 8
    filter_e = 9

class KeyClass:
    __slots__ = ('_pin', 'state', 'cnt', 'key_flag', 'key_result')
    def __init__(self, pin):
        self._pin = pin
        self.state = KeyState.idle
        self.cnt = 0
        self.key_flag = 0
        self.key_result = 0
    def value(self):
        return self._pin.value()

def cycle_key(io: KeyClass):
    st = io.state
    if st == KeyState.idle:
        if io.value() == 0:
            io.state = KeyState.filter_a
    elif st == KeyState.filter_a:
        io.cnt += 1
        if io.cnt >=20:
            io.net = 0
            io.state = KeyState.down_a if io.value() == 0 else KeyState.idle
    elif st == KeyState.down_a:
        io.cnt += 1
        if io.cnt>= 2000:
            io.ket_result,io.keyflag,io.cnt = 3,1,0
            io.state = KeyState.longpress
        elif io.value():
            io.cnt = 0
            io.state = KeyState.filter_b
    elif st == KeyState.filter_b:
        io.cnt += 1
        if io.cnt >= 20:
            io.cnt = 0
            io.state = KeyState. down_a if io.value() == 0 else KeyState.wait #按钮松开后进入计时状态
    elif st == KeyState.wait:
        io.cnt += 1
        if io.cnt >= 400:
            io.key_result, io.key_flag, io.cnt = 1 , 1 , 0 #单击，计时归零
            io.state = KeyState.idle
        elif io.value() == 0:
            io.cnt = 0
            io.state = KeyState.filter_c
    elif st == KeyState.filter_c:
        io.cnt += 1
        if io.cnt >= 20:
            io.cnt = 0
            io.state = KeyState.down_b if io.value() == 0 else KeyState.wait
    elif st == KeyState.longpress:
        if io.value():
            io.state = KeyState.filter_e
        else:
            io.state = KeyState.idle
    elif st == KeyState.down_b:
        io.cnt += 1
        if io.cnt >= 2000:
            io.key_result, io.key_flag, io.cnt = 3 , 1 , 0 #长按,计时归零
            io.state = KeyState.longpress
        elif io.value():
            io.cnt = 0
            io.state = KeyState.filter_d
    elif st == KeyState.filter_d:
        io.cnt += 1
        if io.cnt >= 20:
            io.cnt = 0
            io.key_result,io.key_flag,io.cnt = 2 , 1 , 0 #双击，计时归零
            io.state = KeyState.idle
    elif st == KeyState.filter_e:
        io.cnt += 1
        if io.cnt >=20:
            io.cnt = 0
            io.state = KeyState. idle

mykey = KeyClass(key_pin)
print('start...')
last_tick = time.ticks_ms()
while True:
    now = time.ticks_ms()
    if time.ticks_diff(now,last_tick)>=1:
        cycle_key(mykey)
        last_tick =now
    if mykey.key_flag:
        res = mykey.key_result
        mykey.key_flag = 0
        print('key_result:',res)