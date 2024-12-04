import network
import socket
import select
import time

# SSID = 'HW_QA_STAND_1_2G'
# WIFI_KEY = '86057684429590'
SSID = 'TP_Link_W1F117'
WIFI_KEY = '96506592608183006536'
PORT = 4932


class TCPLogger:
    def __init__(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, WIFI_KEY)

        while not wlan.isconnected():
            time.sleep(1)
            print('Waiting until wifi connects')

        print("Connected to Wi-Fi: {}".format(wlan.ifconfig()))
        print("IP address: {}".format(wlan.ifconfig()[0]))

        addr = socket.getaddrinfo(
            wlan.ifconfig()[0], PORT)[0][-1]
        self.s = socket.socket()
        self.s.bind(addr)
        self.s.listen(1)
        self.s.setblocking(False)
        print("Start listening on", addr)

        self.conn = None

    def print(self, msg):
        # 0 - means select won't wait at all
        if not self.conn:
            print("Check if someone is waiting")
            readable, _, _ = select.select([self.s], [], [], 0)
            print(readable)
            if readable:
                self.conn, addr = self.s.accept()
                print("Client connected. Addr: {}".format(addr))
        else:
            try:
                self.conn.send((msg + "\n").encode())
            except Exception as e:
                print("Error:", e)
                if self.conn:
                    self.conn.close()
                self.conn = None
