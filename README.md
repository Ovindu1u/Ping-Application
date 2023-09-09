# Ping Application in Python

A Ping tool that can be run through the command line, uses raw sockets

Features

* extremely simlpe
* supports variable ttl, count, payload size and timeout

### Usage 


```
python Ping.py <destination> <options...>
```
### Options
```
-t or --timeout     amount of seconds we listen before 
                    considering the packet dropped
                    (default 5)

-l or --live        ttl, amount of hops
                    (default 128)

-c or --count       amount of pings to do
                    (default 4)

-s or --size        size of icmp payload, not including header information 
                    (default 64)
```

### Examlpe

```
python Ping.py google.com --size 128

output:
Pinging google.com with 128 bytes:
Reply from 74.125.130.101: seq=0 bytes=68 time=181ms TTL=108
Reply from 74.125.130.101: seq=1 bytes=68 time=93ms TTL=108
Reply from 74.125.130.101: seq=2 bytes=68 time=93ms TTL=108
Reply from 74.125.130.101: seq=3 bytes=68 time=109ms TTL=108

Sent = 4, Received = 4, Lost = 0 (100% success)

Minimum = 93ms, Maximum = 181ms, Average = 119ms
```
