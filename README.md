piui
==============

Add a UI to your standalone Raspberry Pi project using your Android or iOS phone

Demo
====

[Watch Demo Video](http://www.youtube.com/watch?v=DV2i6T6mAgI)

![Demo Video Screengrab](http://blog.davidsingleton.org/static/ytpiui.png)


Install PiUi
============
```
pip install piui
```

Setup Instructions (to prepare your Raspberry Pi)
=================================================

The easy way (using a pre-prepared SD card image)
-------------------------------------------------

Download the `piui_plus_examples.zip` file from [github.com/dps/piui-sdcards](https://github.com/dps/piui-sdcards/blob/master/piui_plus_examples.zip?raw=true).  Unzip it and you'll find a 4Gb sd card image named `piui_plus_examples.img`.  Write it to an SD card by following the [usual Raspberry Pi instructions](http://elinux.org/RPi_Easy_SD_Card_Setup).  At present, this image is based on Occidentalis 0.2.

Assuming you have the same wifi adapter I do, this will work out of the box.  If not, read the [Pi-Point](http://www.pi-point.co.uk/) docs to configure for your own hardware.

On first boot, you can sync the latest piui source with:
```
cd piui
git pull origin
```
and start the demo app with:
```
python piui_demo.py
```

The do-it-yourself way
----------------------

Start with the latest release of [Raspbian](http://www.raspberrypi.org/downloads) or (better as it's ready for hardware projects) [Occidentalis](http://learn.adafruit.com/adafruit-raspberry-pi-educational-linux-distro/occidentalis-v0-dot-2).

Follow the [Pi-Point documentation](http://www.pi-point.co.uk/) to turn your Pi into a wifi access point.  Note that if you use the [Adafruit wifi adapter](https://www.adafruit.com/products/814), these instructions do not work in full as the `nl80211` driver does not support that device (which uses a Realtek chipset).  [This blog post](http://blog.sip2serve.com/post/38010690418/raspberry-pi-access-point-using-rtl8192cu) explains how to make it work - thanks Paul!

Add an entry to `/etc/hosts` mapping the DNS name `piui` to the address you configured for the Pi in the step above.  Assuming it's `192.168.1.1`, then you should add the following to `/etc/hosts`
```
192.168.1.1     piui
```

Install `nginx` - nginx is an HTTP server and reverse proxy, we use it to multiplex requests to your app and the `piui-supervisor`.

```
sudo apt-get install nginx
```

Configure nginx using the [config file](https://github.com/dps/piui/blob/master/nginx-conf/nginx.conf) in the PiUi github repo - copy this to `/etc/nginx/nginx.conf` and restart nginx.
```
sudo /etc/init.d/nginx restart
```

Get the piui source code from github
```
cd /home/pi
git clone https://github.com/dps/piui.git
```

Arrange for the `piui-supervisor` to run on boot.
```
sudo cp /home/pi/piui/supervisor/piui-supervisor /etc/init.d
sudo update-rc.d piui-supervisor defaults
```

Done!  Run the demo app:
```
cd piui
python piui_demo.py
```

Connect your phone to the wifi AP and navigate to 'http://piui/'.


Copyright and License (BSD 2-clause)
====================================

Copyright (c) 2013, David Singleton
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.