from zeroconf import ServiceBrowser, Zeroconf
import paho.mqtt.client as paho
import json
import time
import socket

class zeroconfListener:

    def __init__(self):
        self.mqtt_address = None
        self.mqtt_port = None

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        global mqtt_address, mqtt_port
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        for address in info.addresses:
            print("Address: %s %d" % (socket.inet_ntoa(address), info.port))
            self.mqtt_address = socket.inet_ntoa(address)
            self.mqtt_port = info.port

    def update_service(self, zeroconf, type, name):
        print ("update")

    def get_mqtt(self):
        return (self.mqtt_address, self.mqtt_port)

    def mqtt_exists(self):
        if self.mqtt_address == None or self.mqtt_port == 0:
            return False
        return True

class zeroconfMqtt:

    def __init__(self):
        self.zeroconf = Zeroconf()
        self.listener = zeroconfListener()
        self.browser = ServiceBrowser(self.zeroconf, "_mqtt._tcp.local.", self.listener)

    def get_mqtt_host(self):
        try:
            while not self.listener.mqtt_exists():
                print("no mqtt_address, mqtt_port")
                time.sleep(1)

            return self.listener.get_mqtt()
            #input("Press enter to exit...\n\n")
        finally:
            self.zeroconf.close()

class zeroconfMqttClient:

    def __init__(self, clientname, userdata):
        self.zcm = zeroconfMqtt()
        host, port = self.zcm.get_mqtt_host()
        print(host, port)
        self.mqtt_client = paho.Client(client_id=clientname, userdata=userdata)
        #mqtt_client.on_publish = on_publish
        self.mqtt_client.connect(host,port)
        self.mqtt_client.loop_start()

    def publish(self, topic, data):
        ret = self.mqtt_client.publish(topic,json.dumps(data))

    def subscribe(self, topic):
        self.mqtt_client.subscribe(topic)

    def message_callback(self, function):
        self.mqtt_client.on_message = function

