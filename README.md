# RouteSelectively
Python script designed to help route specific websites/domains/CDNs to various ZeroTier endpoints, while allowing everything else go through your internet as normal.

## How it works
Using a combination of iptables and ip routes, you can add the IPs of domains/cdns/websites/etc to route through a specific ZeroTier endpoint. The flexibility allows you to have the option of have multiple endpoints, while leaving the rest of your internet traffic as normal.

## Why ZeroTier?

From my experiences, I always found ZeroTier more flexible and versatile. Plus with ZeroTier, you don't have to worry about port forwarding, or dynamic IP headaches. ZeroTier has that plug-in-play, and pretty good performance.

## Why use this over just having a traditional VPN?

The advantage of using this script is the ability to allow ALL your devices in your house to be able to access the blocked or restricted websites and services without having to turn on/off a VPN. Some devices don't even have VPN support at all.
Some websites, like banks, also do not like VPNs and will be annoying whenever you use one. Split tunneling isn't supported by all devices either.
So with this, you can keep all your traffic going through your internet like normal, but have specific websites and platforms through ZeroTier. The best of both worlds.

## Example use-cases

* Bypassing Netflix's password sharing crackdown and blocks, by redirecting netflix CDNs and domains to a different ZeroTier endpoint.
* Bypass adult content restrictions imposed in several US states (which is requiring your ID to view content).
* Future proofing when other streaming service follows Netflix's strategy on password sharing crackdown.

## Limitations

* Requires a linux box for ip routing.
* Some basic knowledge on linux networking.
* Most routers do not support this unfortunantly.
* ZeroTier may have network speed bottlenecks, which isn't really a problem if you are just using it to stream content.

## Requirements

Terminology (For those that are confused): Client side = Your house or location; The machine that will be intercepting your home traffic.

* For the client side, you will need a linux machine running ZeroTier. The hardware doesn't need to be anything fancy, just needs to be capable of atleast outputting and sustaining gigabit internet speeds.
* An endpoint the ZeroTier client (with the ip routes set) will connect to send the traffic over to. Could be a VPS, or another linux box at a different location, etc. Weaker systems like RPi 3b (or newer) can work too if all you are doing is streaming and don't care about the fastest possible speeds.
* A ZeroTier network already set up and running.

## How-to setup

This has been battle tested on Ubuntu 24.04(.1), which is what I use for literally everything, so whether it works on other distros or older Ubuntu versions has not been verified by me.

**DISCLAIMER: I AM NOT RESPONSIBLE IF YOU SCREW UP YOUR FIREWALL, IPTABLES, IP ROUTING CONFIGURATION, OR REALLY ANYTHING NOT MENTIONED, IF IT HAPPENS TO GO WRONG. MAKE SURE YOU UNDERSTAND WHAT YOU ARE DOING, WHAT YOU ARE RUNNING, MADE BACKUPS OF YOUR IPTABLES, ETC. YOU HAVE BEEN WARNED.**

1. Make sure you have installed [ZeroTier](https://www.ZeroTier.com/download/) onto the client, and on to the endpoint you will be using.
2. Make sure you already have a [ZeroTier Network](https://my.ZeroTier.com/) created and configured.
(Further instructions regarding ZeroTier can be found [on their documentation page](https://docs.ZeroTier.com/))

Assuming you got ZeroTier on both ends connected to the network you created and its all ready to go, we will now begin with the instructions below.

I do recommend using iptables-persistent to save your iptables configuration, otherwise your MASQUERADE rules will be lost upon boot.

### Exit node instructions
1. Find your WAN interface and run the following command (replace <public-interface> with your WAN interface name):
``sudo iptables -t nat -A POSTROUTING -o <public-interface> -j MASQUERADE``

2. open ``/etc/sysctl.conf`` and add the following lines:
```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```
3. (Optional) I always have a habit of enable TCP BBR to take advantage better throughput and latency. To do so, in the same ``/etc/sysctl.conf`` file, add:
```
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
```
That's pretty much it for the exit node, it's actually the easiest part.

### Client side instructions

Now, we are going to create a new routing table, this will be used to store all the IPs that the script will run. Note: By default, these routes do not persist between boots, so you will need to run the python script each time.
To do so:

(Make sure you already have git installed)
1. ``git clone https://github.com/nolsen42/RouteSelectively.git ; cd ~/RouteSelectively``
1. run ``sudo nano /etc/iproute2/rt_tables``
2. We want to add a new table at the end of the file, so we are going to add ``1001    ZeroTier``
3. (Optional) If the client side is also routing traffic for multiple devices, like a router for example, add the following iptables line:
```sudo iptables -t nat -A POSTROUTING -o ztly5x7b3u -j MASQUERADE``` (Replace ztly5x7b3u with your ZeroTier interface)
If you are using it like a router (or as a default gateway for your devices), make sure you have set the ip_forward rules found in the Exit node instructions.

### Additional set-up tips

If you want to redirect ALL your lan traffic to go through the client to send specific traffic to your endpoint, but don't want to make it into a router, what you can do is make the client linux box as a default gateway, then change your DHCP settings to tell all your devices that "this is the new gateway, connect to it". On the client side, you would keep the gateway the same.

The end result: Your devices -> Router -> Client box -> Router -> WAN.


## How to run script

1. Discover the domains and CDNs you want to redirect. Inspect element networking tab is a helpful tool to find the CDNs you need. Another helpful tool is if you have a method to view DNS requests on your network like pi-hole.
2. Add such domains and CDNs to the domains.txt file.
3. Test if the routing is working using the tracert command.

Make sure to run the python script with elevated privileges (sudo), which is required to modify ip routes.

## Additional notes

1. There can be around 52 or more netflix domains and CDNs.
2. It is recommended that you make a separate domains.txt and setroutes.py for every website or category you want to redirect. See examples below on what I mean.

### Examples

* Have one setroutes.py called ``setroutes_netflix.py``, and ``domains_netflix.txt`` for domain file, then populate it with all the netflix CDNs and domains.
* Have one setroutes.py called ``setroutes_adult.py``, and ``domains_adult.txt`` for domain file, then populate it with all the domains, CDNs, etc, regarding adult websites (as a category basically rather than an individual website).
* Have either one of those above (or in general) but with a separate ZeroTier endpoint. Netflix goes to one ZeroTier endpoint, adult goes to a different endpoint, etc.

## Will you be providing a list of CDNs and domains to make it easier for us?

As much as I would like to, I am not sure if Github, netflix, adult websites, hulu, disney+, etc, will throw a fit and try to shutdown this repo (or send me an angry letter)

## Doesn't this violate Netflix's ToS?

Most likely, yes. Do I care? No. Should you care? That's up to you to decide, while I cannot assure you with a 100% guarantee, the likelihood of being banned for this is low (but not zero). This can be said with any other website out there. **Use this at your own risk. I am not responsible if you get spanked by the streaming platforms for this.**
