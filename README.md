# RouteSelectively
Python script (with instructions) on bypassing specific websites/domains to various zerotier endpoints.

## How it works
Using a combination of iptables and ip routes, you can add the IPs of domains/cdns/websites/etc to route through a specific zerotier endpoint. The flexibility allows you to have the option of have multiple endpoints, while leaving the rest of your internet traffic as normal.

## Example use-cases

* Bypassing Netflix's password sharing crackdown and blocks, by redirecting netflix CDNs and domains to a different zerotier endpoint.
* Bypass adult content restrictions imposed in several US states (which is requiring your ID to view content).
* Future proofing when other streaming service follows Netflix's strategy on password sharing crackdown.

## Limitations

* Requires a linux box for ip routing.
* Some basic knowledge on linux networking.
* Most routers do not support this unfortunantly.
* ZeroTier may have network speed bottlenecks, which isn't really a problem if you are just using it to stream content.

## Requirements

* A linux box running Zerotier. The hardware doesn't need to be anything fancy, just needs to be capable of atleast outputting and sustaining gigabit internet speeds.
* A zerotier network already set up and running.
* An endpoint the Zerotier client (with the ip routes set) will connect to send the traffic over to. Could be VPSes, another linux box at a different location, etc.

## How-to setup

**DISCLAIMER: I AM NOT RESPONSIBLE IF YOU SCREW UP YOUR FIREWALL, IPTABLES, IP ROUTING CONFIGURATION, OR REALLY ANYTHING NOT MENTIONED, IF IT HAPPENS TO GO WRONG. MAKE SURE YOU UNDERSTAND WHAT YOU ARE DOING, WHAT YOU ARE RUNNING, MADE BACKUPS OF YOUR IPTABLES, ETC. YOU HAVE BEEN WARNED.**

1. Make sure you have installed [Zerotier](https://www.zerotier.com/download/) onto the client, and on to the endpoint you will be using.
2. Make sure you already have a [Zerotier Network](https://my.zerotier.com/) created and configured.
(Further instructions regarding Zerotier can be found [on their documentation page](https://docs.zerotier.com/))
Assuming you got Zerotier on both ends connected to the network you created and its all ready to go, we will now make changes on the client side first.

### Exit node instructions
1. Find your WAN interface and run the following command:
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

1. run ``sudo nano /etc/iproute2/rt_tables``
2. We want to add a new table at the end of the file, so we are going to add ``1001    zerotier``
3. (Optional) If the client side is also routing traffic for multiple devices, like a router for example, add the following iptables line:
```sudo iptables -t nat -A POSTROUTING -o ztly5x7b3u -j MASQUERADE``` (Replace ztly5x7b3u with your zerotier interface)
If you are using it like a router (or as a default gateway for your devices), make sure you have set the ip_forward rules found in the Exit node instructions.

### Additional set-up tips

If you want to redirect ALL your lan traffic to go through the client to send specific traffic to your endpoint, but don't want to make it into a router, what you can do is make the client linux box as a default gateway, then change your DHCP settings to tell all your devices that "this is the new gateway, connect to it". On the client side, you would keep the gateway the same.

The end result: Your devices -> Router -> Client box -> Router -> WAN.
