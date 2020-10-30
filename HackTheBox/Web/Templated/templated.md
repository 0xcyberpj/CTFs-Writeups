# Templated

By surfing the page we get the following and we notice the underlying **Flask/Jinja2** template engine

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/1.png" alt="1" />
</p>

and by requesting a random page the server replies outputting our input

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/2.png" alt="2" />
</p>

```html
<h1>Error 404</h1>
<p>The page '<str>aaaa</str>' could not be found</p>
```

As first shot we try to break the html context by XSS

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/3.png" alt="3" />
</p>

the page is vulnerable, but unfortunately nothing shows up.

We decide to switch our test on a Server Side template injection (SSTI) vulnerability.

As second shot we ask the server to solve an expression and we get

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/4.png" alt="4" />
</p>

and this confirms the vulnerability!

By searching within the [Flask doc](https://flask.palletsprojects.com/en/1.1.x/api/) we find the class **flask.Request** from which we can access methods, properties
and the [global namespace](https://stackoverflow.com/questions/37381341/globals-getting-merged-when-using-decorators#answer-37381475)

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/5.png" alt="5" />
</p>

From here, in order to obtain RCE we can [import](https://python-reference.readthedocs.io/en/latest/docs/functions/__import__.html) the built-in [os](https://docs.python.org/3/library/os.html) module
and [inject](https://docs.python.org/3/library/os.html#os.popen) commands

<p align="center">
  <img src="https://github.com/lorenzoinvidia/CTFs-Writeups/blob/master/HackTheBox/Web/Templated/src/6.png" alt="6" />
</p>

The **flag.txt** file is located within the root directory.  



If you liked this writeup, please leave a respect on my hackthebox

![htbbadge](https://www.hackthebox.eu/badge/image/77747)
