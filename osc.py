"""
OSC client
"""
import argparse
import random
import time
from pythonosc import osc_message_builder
from pythonosc import udp_client


class OSC:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
        self.parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")
        self.args = parser.parse_args()
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

    def init_sc(self):
        self.client.send_message("/root/init", 'osc communication has started!')
        print('osc communication has started!')

    def play(self):
        self.client.send_message("/root/play", 1)
        print('osc play')

    def set_parameter(self, x, y):
        osc_msg = [x, y]
        self.client.send_message("/root/msg", osc_msg)
        #print(osc_msg)
        #time.sleep(1)

    def stop(self):
        self.client.send_message("/root/play", 0)
        print('osc stop')
