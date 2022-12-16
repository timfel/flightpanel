RPi GPIO based flight panel

Uses the RPi as an HID keyboard, driven from GPIO inputs.

Setup of the Pi from https://randomnerdtutorials.com/raspberry-pi-zero-usb-keyboard-hid/
Roughly like this:
```
pi@raspberrypi:~ $ echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
pi@raspberrypi:~ $ echo "dwc2" | sudo tee -a /etc/modules
pi@raspberrypi:~ $ sudo echo "libcomposite" | sudo tee -a /etc/modules
pi@raspberrypi:~ $ sudo touch /usr/bin/isticktoit_usb
pi@raspberrypi:~ $ sudo chmod +x /usr/bin/isticktoit_usb
pi@raspberrypi:~ $ cat <<EOF | sudo tee -a /usr/bin/isticktoit_usb
#!/bin/bash
cd /sys/kernel/config/usb_gadget/
mkdir -p isticktoit
cd isticktoit
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2
mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Tobias Girstmair" > strings/0x409/manufacturer
echo "iSticktoit.net USB Device" > strings/0x409/product
mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
echo 500 > configs/c.1/MaxPower

# Add functions here
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc
ln -s functions/hid.usb0 configs/c.1/
# End functions

ls /sys/class/udc > UDC
EOF

pi@raspberrypi:~ $ sed -i 's/exit 0//' /etc/rc.local
pi@raspberrypi:~ $ echo "/usr/bin/isticktoit_usb # libcomposite configuration" | sudo tee -a /etc/rc.local
pi@raspberrypi:~ $ echo "exit 0" | sudo tee -a /etc/rc.local

pi@raspberrypi:~ $ cat <<EOF | sudo tee -a /etc/systemd/system/flightpanel.service
[Unit]
Description=Flightpanel
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
Restart=always
RestartSec=1
ExecStart=python3 /home/pi/flightpanel/panel.py /boot/flightpanel.ini

[Install]
WantedBy=multi-user.target
EOF

pi@raspberrypi:~ $ sudo systemctl enable flightpanel
```

Test, if working, make the root filesystem read-only using raspi-config -> Performance -> Overlay file system ..

Config can then be done by taking the SD card out and modifying the ini file on the boot partition.
