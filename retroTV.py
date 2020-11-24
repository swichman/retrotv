#!/usr/bin/python3

from time import sleep
import subprocess
from sys import argv, stdout
import pyfiglet
from os import system

from gpiozero import Button


class Station:
    def __init__(self):
        self.channel = 0
        self.name = ''
        self.address = ''
        self.process = ''

class Television:
    def __init__(self, filename):
        self.current_channel = 0
        self.channel_list = []
        self.build_channel_list(filename)
        
        with open('/home/pi/retrotv/last_channel', 'r') as last:
            for line in last:
                #print(line)
                self.current_channel = int(line)
        
        self.start_channel()

    def build_channel_list(self, filename):
        with open(filename, 'r') as m3u:
            i = 0
            for line in m3u:
                if line.startswith('#EXTINF'):
                    this = Station()
                    this.name = line.split(',')[1]
                    line = next(m3u)
                    this.address = line.strip()
                    this.channel = i
                    self.channel_list.append(this)
                    i = i + 1

    def channel_up(self):
        print('channel UP')
        self.current_channel = self.current_channel + 1
        if self.current_channel > len(self.channel_list):
            self.current_channel = len(self.channel_list)
        self.start_channel()

    def channel_down(self):
        print('channel DOWN')
        self.current_channel = self.current_channel - 1
        if self.current_channel < 0:
            self.current_channel = 0
        self.start_channel()

    def start_channel(self):
        with open('/home/pi/retrotv/last_channel', 'w') as last:
            last.write(str(self.current_channel))
        try:
            self.process.kill()
        except:
            pass
        #subprocess.Popen(["setsid", "sh", "-c", "'exec clear <> /dev/tty1 >&0 2>&1'"]) 
        system("setsid sh -c 'exec clear <> /dev/tty1 >&0 2>&1'")
        channel_ascii = pyfiglet.figlet_format('channel\n' + str(self.current_channel), font='/home/pi/retrotv/poison', justify='center')
        with open('/dev/tty1', 'w') as ttyOutput:
            ttyOutput.write(channel_ascii)
            
        self.process = subprocess.Popen(['vlc', '-q', '--loop', '--intf', 'dummy', '--fullscreen', self.channel_list[self.current_channel].address])

this = Television('/home/pi/retrotv/us-m3uplaylist-2020-11-23-1.m3u')
channel_UP = Button(18)
channel_DN = Button(23)
while True:
    channel_UP.when_pressed = this.channel_up
    channel_DN.when_pressed = this.channel_down
