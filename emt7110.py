#!/usr/bin/env python3

from time import sleep
from binascii import hexlify
import bitstruct
import platform
import json

from cc1101.config import RXConfig, Modulation
from cc1101 import CC1101

from mqtt_zeroconf import zeroconfMqttClient

MQTT_MODULE_TOPIC_PREFIX = "emt7110"

# 0-3 	ID des Senders
# 4 Bit 7/6 	Bit6 = Geräte am Stromnetz, Bit7 = Paarungsmodus
# 4 Bit 5-0, 5 	Leistung in 0,5 W Schritten, 14 Bits (MSB first)
# 6-7 	Strom in mA, 16 Bits (MSB first)
# 8 	Spannung in 0,5 V Schritten – 128 V
# 9 Bit 7/6 	Unbekannt
# 9 Bit 5-0, 10 	Energieverbrauch, akkumuliert, in 10 Wh (0,01 kWh) Schritten, 14 Bits (MSB first)
# 11 	Prüfsumme, alle 12 Bytes aufsummiert müssen 0 ergeben

def process_msg(client, userdata, message):
    print(client, userdata, message)
    print("Received message '" + str(message.payload) + "' on topic '"
                    + message.topic + "' with QoS " + str(message.qos) + " Userdata: " + repr(userdata) )
    if message.topic in userdata:
        try:
            config = json.loads(message.payload)
            if "topic" in config:
                userdata[message.topic]["topic"] = config["topic"]
        except Exception as e:
             print("config not parsable", e)
 


if __name__ == "__main__":

    hostname = platform.node()
    sensors = {}
    
    mqttclient = zeroconfMqttClient("emt7110-%s" % hostname, sensors)
    mqttclient.message_callback(process_msg)

    rx_config = RXConfig(frequency=868.28, modulation=Modulation.FSK_2, baud_rate=9.579, bandwidth=232, sync_word=0x2dd4, packet_length=12)
    radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True)
    
    cf = bitstruct.compile('s32u1u1u14u16u8u2u14u8')
    
    while True:
        packets = radio.receive()
    
        for packet in packets:
            lenght = len(packet)
            summe = sum(packet) & 0xFF
            print(f"Received - {hexlify(packet)}, {lenght} , {summe}")
            if summe != 0:
                continue
            data = cf.unpack(packet)
            print(repr(data))
            sensorid, pairing, plugged, power, current, voltage, unknown, energy, checksum = data
            sensorid_hex = "%0.4X" % sensorid
            print (sensorid_hex, pairing, plugged, power * 0.5, current, voltage * 0.5 + 128, unknown, energy * 10.0 )
            dict_data = {
                "sensorid": sensorid_hex,
                "pairing":  pairing,
                "plugged":  plugged,
                "power":    power * 0.5,
                "current":  current,
                "voltage":  voltage * 0.5 + 128,
                "unknown":  unknown,
                "energy":   energy * 10.0,
            }
            print(repr(dict_data))
            
    
            mqttclient.publish(f"{MQTT_MODULE_TOPIC_PREFIX}/hostname/{sensorid_hex}/status", dict_data)
            config_topic = f"{MQTT_MODULE_TOPIC_PREFIX}/hostname/{sensorid_hex}/config"
            if config_topic in sensors:
                print(repr(sensors[config_topic]))
                if "topic" in sensors[config_topic]:
                    mqttclient.publish(sensors[config_topic]["topic"], dict_data)
            else:
                sensors[config_topic] = { "sensorid": sensorid_hex }
                mqttclient.subscribe(config_topic)
                
        
        sleep(0.1)
