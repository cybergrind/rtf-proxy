Setup iptables:

```
iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2050 -j REDIRECT --to-port 9995
iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2051 -j DNAT --to 192.223.31.195:2050
```

Remove iptables rules:
```
iptables -t nat -D OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2050 -j REDIRECT --to 9995
iptables -t nat -D OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2051 -j DNAT --to 192.223.31.195:2050
```


Compiling structs:

```
make structs
```

Run proxy:

```
make venv
./venb/bin/python rtf_proxy/run.py
```

Swf decompress:

```
swfdecompress client.swf
abcexport client.swf
rabcdasm client-1.abc
```

Packets analysis with https://ide.kaitai.io/
