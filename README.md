# cc1101-emt7110-receiver
A very simple script that can serve as a food for thought and that already has the appropriate settings for the EMT7110.

# A very short description:
Set the appropriate configuration for the cc1101 to receive packets from an EMT7110, decode them, and forward them to my mqtt broker.
The mqtt-broker is recognized by zeroconf. 

# setup
* Installed the cc1101-driver for kms as described in setup-dev-cc1101.txt
* clone this code to a directory
* pip install -r requirements.txt
* python3 emt7110.py 

# Information sources
emt7110 description https://www.seegel-systeme.de/2015/09/07/das-funk-energiekosten-messgeraet-emt7110/
ev1101 driver installation https://github.com/28757B2/cc1101-driver

spezial thanks to Christoph (https://www.fablabs.io/users/baztuk) for the EMT7110 and https://fablab-rothenburg.de/
