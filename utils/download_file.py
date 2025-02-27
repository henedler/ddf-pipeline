#!/usr/bin/python
# Generic file download with retry and check for length

from __future__ import print_function
import requests
import os
from time import sleep,time

def download_file(url,filename,catch_codes=(),retry_interval=60):
    '''
    Download a file from URL url to file filename.  Optionally,
    specify a tuple of HTTP response codes where we will back off and
    retry rather than failing.
    '''
    
    downloaded=False
    while not downloaded:
        connected=False
        while not connected:
            try:
                print('Opening connection')
                response = requests.get(url, stream=True,verify=True,timeout=60)
                if response.status_code!=200:
                    print('Unexpected response code received!')
                    print(response.headers)
                    if response.status_code in catch_codes:
                        print('Retrying in %i seconds' % retry_interval)
                        sleep(retry_interval)
                        continue
                    else:
                        raise RuntimeError('Download failed, code was %i' % response.status_code)
                esize=int(response.headers['Content-Length'])
            except requests.exceptions.ConnectionError:
                print('Connection error! sleeping 30 seconds before retry...')
                sleep(30)
            except (requests.exceptions.Timeout,requests.exceptions.ReadTimeout):
                print('Timeout! sleeping 30 seconds before retry...')
                sleep(30)
            else:
                connected=True
        try:
            print('Downloading %i bytes' % esize)
            starttime=time()
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        fd.write(chunk)
            fsize=os.path.getsize(filename)
            if esize!=fsize:
                print('Download incomplete (expected %i, got %i)! Retrying' % (esize, fsize))
            else:
                endtime=time()
                dt=endtime-starttime
                print('Download successful, %i of %i bytes received in %.2f seconds (%.2f MB/s)' % (fsize, esize, dt, fsize/(dt*1024*1024)))
                downloaded=True

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,requests.exceptions.ChunkedEncodingError):
            print('Connection error! sleeping 30 seconds before retry...')
            sleep(30) # back to the connection

    del response
    return downloaded

if __name__=='__main__':
    import sys
    download_file(sys.argv[1],sys.argv[2])
    
