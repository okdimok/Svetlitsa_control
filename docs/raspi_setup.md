# Raspberry Pi Config

I've been using these commands to set up raspberry as an AP. I think I've been following [the official docs](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point).

```
  714  2022-03-26 13:05:27 sudo apt install hostapd
  715  2022-03-26 13:05:48 sudo apt update
  716  2022-03-26 13:06:24 sudo apt upgrade
  717  2022-03-26 13:16:26 sudo systemctl unmask hostapd
  718  2022-03-26 13:16:33 sudo systemctl enable hostapd
  719  2022-03-26 13:16:45 sudo apt install dnsmasq
  720  2022-03-26 13:16:58 sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
  721  2022-03-26 13:17:34 sudo vim /etc/dhcpcd.conf
  722  2022-03-26 13:20:49 sudo vim /etc/sysctl.d/routed-ap.conf
  723  2022-03-26 13:21:43 sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  724  2022-03-26 13:22:09 sudo netfilter-persistent save
  (wled-env) BH pi@raspberrypi:~/Svetlitsa_control(master)$ sudo netfilter-persistent save
  run-parts: executing /usr/share/netfilter-persistent/plugins.d/15-ip4tables save
  run-parts: executing /usr/share/netfilter-persistent/plugins.d/25-ip6tables save
  725  2022-03-26 13:22:52 sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
  726  2022-03-26 13:23:01 sudo vim /etc/dnsmasq.conf
  727  2022-03-26 13:24:01 sudo nano /etc/dnsmasq.conf
  728  2022-03-26 13:24:51 sudo rfkill unblock wlan
  729  2022-03-26 13:24:58 sudo nano /etc/hostapd/hostapd.conf
  730  2022-03-26 13:26:24 sudo systemctl reboot
```

To reverse it
```bash
sudo systemctl disable hostapd
sudo systemctl mask hostapd
sudo mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bup
```

Comment out the following the lines in `/etc/dhcpcd.conf`
[see docs](https://www.raspberrypi.com/documentation/computers/configuration.html#running-the-new-wireless-ap:~:text=for%20dhcpcd%20with%3A-,sudo%20nano%20/etc/dhcpcd.conf,-Go%20to%)

After the reboot, the Network part of the `sudo raspi-config` starts working again.

I looked deeper into the eth0 dhcp client setup `sudo vim /etc/dhcpcd.conf` and uncommented the suggested code
```
profile static_eth0
static ip_address=192.168.137.23/24
static routers=192.168.137.1
static domain_name_servers=192.168.137.1

# fallback to static profile on eth0
interface eth0
fallback static_eth0
```
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.ap
sudo cp /etc/dnsmasq.conf.orig /etc/dnsmasq.conf
sudo systemctl disable --now dnsmasq
sudo systemctl mask dnsmasq
```

It turns out it is somehow important for getting UDP messages.

# Bluetooth audio doesn't work in 2024 yet
https://www.digikey.com/en/maker/blogs/raspberry-pi-wi-fi-bluetooth-setup-how-to-configure-your-pi-4-model-b-3-model-b

```
BH pi@raspberrypi:~$ bluetoothctl
[bluetooth]# power on
[bluetooth]# scan on
[bluetooth]# pair 5C:FB:7C:B3:EB:FF
[bluetooth]# trust 5C:FB:7C:B3:EB:FF
[bluetooth]# connect 5C:FB:7C:B3:EB:FF
```

Than following [ChatGPT](https://chat.openai.com/share/3a5cdd6b-2276-44fe-8672-a2eb474704a9)
```
pacmd list-sinks
pacmd set-default-sink bluez_sink.5C_FB_7C_B3_EB_FF
```
Following [some message on a forum](https://forums.raspberrypi.com/viewtopic.php?t=203756#p1265959) 

Edit /boot/config.txt and comment out the following line: "dtparam=audio=on" so that it looks like "#dtparam=audio=on" (without the quotes).
This means that the built-in audio is disabled and so the BT speaker becomes the default (only) choice for audio playback.

Now reboot the RPi.

Connect the BT speaker again (using bluetoothctl) : note, for reasons that are not clear to me I have to disconnect it first, then reconnect it.

And now the audio, such as mplayer, automatically uses the BT speaker.
