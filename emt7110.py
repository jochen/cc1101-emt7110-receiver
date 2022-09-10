#!/usr/bin/env python3

from time import sleep
from binascii import hexlify
import bitstruct

from cc1101.config import RXConfig, Modulation
from cc1101 import CC1101

rx_config = RXConfig(frequency=868.28, modulation=Modulation.FSK_2, baud_rate=9.579, bandwidth=232, sync_word=0x2dd4, packet_length=12)
radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True)

# 0-3 	ID des Senders
# 4 Bit 7/6 	Bit6 = Geräte am Stromnetz, Bit7 = Paarungsmodus
# 4 Bit 5-0, 5 	Leistung in 0,5 W Schritten, 14 Bits (MSB first)
# 6-7 	Strom in mA, 16 Bits (MSB first)
# 8 	Spannung in 0,5 V Schritten – 128 V
# 9 Bit 7/6 	Unbekannt
# 9 Bit 5-0, 10 	Energieverbrauch, akkumuliert, in 10 Wh (0,01 kWh) Schritten, 14 Bits (MSB first)
# 11 	Prüfsumme, alle 12 Bytes aufsummiert müssen 0 ergeben

cf = bitstruct.compile('s32u6u1u1u16u8u16u8')

while True:
    packets = radio.receive()

    for packet in packets:
        lenght = len(packet)
        summe = sum(packet) & 0xFF
        print(f"Received - {hexlify(packet)}, {lenght} , {summe}")
        data = cf.unpack(packet)
        print(repr(data))
        
    
    sleep(0.1)
