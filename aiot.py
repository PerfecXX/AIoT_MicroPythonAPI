# Import Library
try :
    from machine import *
    from time import sleep
    from ssd1306 import SSD1306_I2C
    from simple import MQTTClient
    from network import WLAN,STA_IF
    from dht import DHT11
    from neopixel import NeoPixel
    from json import dumps
    
except ImportError:
    print("Error: Library Not Found")
    
class AIOT():
    """
    Create instance and setup all AIoT pin
    -----
    <Your instance name> = AIOT()
    """
    def __init__(self):
        self.__buzzFreq = 500
        self.__buzzDuty = 0
        self.__temperature = 0
        self.__humidity = 0
        self.__btn1State = 0
        self.__btn2State = 0
        self.__btn3State = 0
        self.__btn4State = 0
        self.__oledScreenWidth = 128
        self.__oledScreenHeight = 64
        
        self.__oledPin = SoftI2C(scl=Pin(22),sda=Pin(21))
        self.__oled = SSD1306_I2C(self.__oledScreenWidth,
                                 self.__oledScreenHeight,
                                 self.__oledPin)
        self.__relay1Pin = Pin(14,Pin.OUT)
        self.__relay2Pin = Pin(27,Pin.OUT)
        self.__buzzerPin = Pin(32,Pin.OUT)
        self.__neopixelPin = NeoPixel(Pin(23,Pin.OUT),2)
        self.__dhtPin = DHT11(Pin(13))
        
        self.__btn1Pin = Pin(15,Pin.IN,Pin.PULL_UP)
        self.__btn2Pin = Pin(2,Pin.IN,Pin.PULL_UP)
        self.__btn3Pin = Pin(0,Pin.IN,Pin.PULL_UP)
        self.__btn4Pin = Pin(4,Pin.IN,Pin.PULL_UP)
        self.__potPin = ADC(Pin(39))
        self.__ldrPin = ADC(Pin(36))
        self.__welcome()
        
    def rgb_setColor(self,index='all',color=(255,255,255)):
        """
        Set an RGB color to a specific position
        -----
        Parameter
        (int)index -> 0 or 1 => Position of RGB LED1 or LED2
        (str)index -> 'all' => Set both positions of the RGB LED
        (tuple)color -> (r,g,b) => color of RGB LED
        ---
        (int)r -> 0 to 255 => intensity of the red color
        (int)g -> 0 to 255 => intensity of the green color
        (int)b -> 0 to 255 => intensity of the blue color
        """
        if index == 'all':
            self.__neopixelPin[0] = (color[0],color[1],color[2])
            self.__neopixelPin[1] = (color[0],color[1],color[2])
        else:
            self.__neopixelPin[index] = (color[0],color[1],color[2])
        
    def rgb_show(self):
        """
        Write data and turn on all RGB LED
        """
        self.__neopixelPin.write()
        
    def rgb_off(self,index):
        """
        Set "Off" to a specific RGB LED position. 
        -----
        Parameter
        (int)index-> 0 or 1 => Position of RGB LED   
        (str)index-> 'all' => All of RGB LED
        """
        if index == 'all':
            self.__neopixelPin[0] = (0,0,0)
            self.__neopixelPin[1] = (0,0,0)
        else:
            self.__neopixelPin[index] = (0,0,0)
        self.rgb_show()
        
    def relay_on(self,index):
        """
        Set "On" to specific relay position
        -----
        Parameter
        (int)index-> 1 or 2 => Position of Relay
        (str)index-> 'all' => All of Relay
        """
        if index == 'all':
            self.__relay1Pin.value(1)
            self.__relay2Pin.value(1)
        elif index == 1:
            self.__relay1Pin.value(1)
        elif index == 2:
            self.__relay2Pin.value(1)
    
    def relay_off(self,index):
        """
        Set "Off" to specific relay position
        -----
        Parameter
        (int)index-> 1 or 2 => Position of Relay
        (str)index-> 'all' => All of Relay
        """
        if index == 'all':
            self.__relay1Pin.value(0)
            self.__relay2Pin.value(0)
        elif index == 1:
            self.__relay1Pin.value(0)
        elif index == 2:
            self.__relay2Pin.value(0)
    
    def relay_isOn(self,index):
        """
        Determines whether the specified relay is opened.
        -----
        Parameter
        (str)index -> "all" => any relay
        (int)index -> 1 or 2 => Name of the relay
        ---
        Return
        True-> if the specified relay is opened
        """
        
        self.__relay1State = self.__relay1Pin.value()
        self.__relay2State = self.__relay2Pin.value()
        
        if index == 1:
            if self.__relay1State == 1:
                return True
        elif index == 2:
            if self.__relay2State == 1:
                return True
        elif index == 'all':
            if self.__relay1State == 1 or self.__relay2State == 1:
                return True
        
    def button_isPressed(self,index):
        """
        Determines whether the specified button is pressed.
        -----
        Parameter
        (str)index -> "all" => any button 
        (int)index -> 1,2,3 or 4 => Name of the button
        ---
        Return
        True-> if the specified button is pressed
        """
        
        self.__btn1State = self.__btn1Pin.value()
        self.__btn2State = self.__btn2Pin.value()
        self.__btn3State = self.__btn3Pin.value()
        self.__btn4State = self.__btn4Pin.value()
        
        if index ==1:
            if self.__btn1State == 0:
                return True
        elif index ==2:
            if self.__btn2State == 0:
                return True
        elif index ==3:
            if self.__btn3State == 0:
                return True
        elif index ==4:
            if self.__btn4State == 0:
                return True
        elif index == 'all':
            if self.__btn1State == 0 or self.__btn2State == 0 or self.__btn3State == 0 or self.__btn4State == 0:
                return True
    
    def dht_measure(self,environment='all'):
        """
        Obtains the temperature(celsius) and humidity(%RH) measure by the DHT11 Sensor.
        -----
        Parameter
        (str)environment -> "temperature","humidity" or 'all' => type of measurement 
        ---
        Return
        (tuple)Temperature,Humdity -> if environment set to "all"
        (int)Temperature -> if environment set to "temperature"
        (int)Humidity -> if environment set to "humidity"
        """
        self.__dhtPin.measure()
        self.__temperature = self.__dhtPin.temperature()
        self.__humidity = self.__dhtPin.humidity()
        if environment == 'all':
            return self.__temperature,self.__humidity
        elif environment == 'temperature':
            return self.__temperature
        elif environment == 'humidity':
            return self.__humidity
        
    def display_setText(self,text='Test',xPostion=0,YPosition=0,color=1):
        """
        """
        self.__oled.text(str(text),int(xPostion),int(YPosition),int(color))
        
    def display_show(self):
        """
        """
        self.__oled.show()
        
    def __welcome(self):
        print('Welcome to KMITL AIoT Development Board Version 1')
        print('For more detail,please visit')
        print('https://github.com/PerfecXX/AIoT_MicroPythonAPI')
        
            
board = AIOT()
board.rgb_setColor('all',(255,0,0))
board.rgb_show()
sleep(1)
board.rgb_off('all')
board.display_setText()
board.display_show()
