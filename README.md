swfdecompress client.swf
abcexport client.swf
rabcdasm client-1.abc


base string
```
49417661305a78324a4d31367a4e5a583033782f5855305a4d5956326963386f42454e4f466836715a6b56795a6236517953773351526176664d79653730455348704d41352f6a64757174374c79713264664e323165355048386a68484467354c736a7954704f357936674d336236754e627468526d556b42794775726d2f6f726b797247496a4853666679694e42304d714c5a53394859657239663454667039794b38766d6a655a646b3d
```


```
.......X3.52.......IAva0Zx2JM16zNZX03x/XU0ZMYV2ic8oBENOFh6qZkVyZb6QySw3QRavfMye70ESHpMA5/jduqt7Lyq2dfN21e5PH8jhHDg5LsjyTpO5y6gM3b6uNbthRmUkByGurm/orkyrGIjHSffyiNB0MqLZS9HYer9f4Tfp9yK8vmjeZdk=..bohlpsI4OZ5BmbEncje7rp1k6skLRfQrg3xvdHEAZqOXITR9OMfIDQTvlmhads/Vcqa6ctzev2lQeU++Bgyg8TyQYWoKy6ECY/xaT86UtTQMQaFonucUoXzni6azLCwESeTOM0xMVhwdum48Sko6n/WrzyVO0UwfbP9MnAsj5iE=....https://rotf.io/assets/swf/client.swf?build=release/[[DYNAMIC]]/1QWERTYCODEUNODOS...7S..........Nexus..NexusU.
```


```
iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2050 -j REDIRECT --to 9995
iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2050 -j REDIRECT --to-port 9995
iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2051 -j REDIRECT --to-port 2050 --to-destination 192.223.31.195

iptables -t nat -A OUTPUT -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2051 -j DNAT --to 192.223.31.195:2050
```

```
iptables -D OUTPUT  -s 192.168.88.34 -d 192.223.31.195 -p tcp --dport 2050 -j REDIRECT --to 9995
```
