import network
import socket
import time
import errno
import os

from machine import Pin

led = Pin("LED", Pin.OUT)

essid = 'JOIN ¯\_(ツ)_/¯ ME'

ap = network.WLAN(network.AP_IF)
ap.config(essid=essid, security=0)

print('waiting for connection...')
ap.active(True)
print('Connection successfull')
print(ap.ifconfig())

ip_address = ap.ifconfig()[0]
fqdn = ip_address
port = 70

# Open socket
addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

#led.value(1)

# -------------------------------------------------------------
class PicoPath:

    S_IFDIR  = 0o040000  # directory
    S_IFCHR  = 0o020000  # character device
    S_IFBLK  = 0o060000  # block device
    S_IFREG  = 0o100000  # regular file
    S_IFIFO  = 0o010000  # fifo (named pipe)
    S_IFLNK  = 0o120000  # symbolic link
    S_IFSOCK = 0o140000  # socket file
    
    def __init__(self, fname):
        self.fname = fname
        self.s = None        

    def stat(self):
        if self.s is None:
            try:
                self.s = os.stat(self.fname)
            except Exception as e:
                return None
        return self.s
    
    def S_IFMT(self, mode):
        """Return the portion of the file's mode that describes the
        file type.
        """
        return mode & 0o170000

    def S_ISDIR(self, mode):
        """Return True if mode is from a directory."""
        return self.S_IFMT(mode) == self.S_IFDIR

    def S_ISREG(self, mode):
        """Return True if mode is from a regular file."""
        return self.S_IFMT(mode) == self.S_IFREG

    def exists(self):
        return self.stat() is not None
    
    def is_file(self):
        return self.S_ISREG(self.stat()[0])

    def is_dir(self):
        return self.S_ISDIR(self.stat()[0])
# -------------------------------------------------------------


def invalid_path(absolute_path):
    if '..' in absolute_path:
        print('Error: attempt to access parent: {}'.format(absolute_path))
        return True

    path_abs = PicoPath(absolute_path)
    path_gmap = PicoPath(absolute_path + '/gophermap')
            
    if not path_abs.exists():
        print('Error: attempt to access nonpublic path: {}'.format(absolute_path))
        return True

    elif path_abs.is_file():
        return False
    elif (path_abs.is_dir() and path_gmap.exists() and path_gmap.is_file()):
        return False

    print('Error: attempt to access something weird: {}'.format(absolute_path))
    return True


# -------------------------------------------------------------

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)

        # return a file object associated with the socket
        cl_file = cl.makefile('rwb', 0)

        # use the file object to read the client request
        data = cl_file.readline()
        print(data)

        selector = data.decode().strip()
        if '\t' in selector:
            cl.send('3Gopher+ selectors unsupported {}.\t\terror.host\t1'.format(selector).encode('US-ASCII', 'replace'))
            cl.send('\r\n.\r\n'.encode('US-ASCII', 'replace'))
            cl.close()

        if selector:
            if not selector.startswith('/'):
                selector = '/' + selector
            relative = selector[1:]
        else:
            relative = ""
            
        absolute_path = "/gopher/" + relative
        print("Absolute path: {}".format(absolute_path))
        
        if invalid_path(absolute_path):
            print('Error result: {}'.format(absolute_path))
            cl.send('3Error accessing {}.\t\terror.host\t1'.format(selector).encode('US-ASCII', 'replace'))
            cl.send('\r\n.\r\n'.encode('US-ASCII', 'replace'))
            cl.close()

        elif PicoPath(absolute_path).is_file():
            print('Success: file: {}'.format(absolute_path))
            # I got some memory errors with 64KB blocks,
            # so I am keeping them tiny for now
            block_size = 4 * 1024
            with open(absolute_path, 'rb') as inf:
                data = inf.read(block_size)
                while len(data) > 0:
                    cl.write(data)
                    data = inf.read(block_size)
            cl.close()        

        else:
            absolute_path = absolute_path + "/gophermap"
            f = open(absolute_path)
            gmap = f.read()
            f.close()

            txt = gmap.splitlines()
            outln = []
            for line in txt:
                if line:
                    cols = line.split('\t')
                else:
                    cols = ['i', '/', '-', '0']

                if len(cols) == 1:
                    # translate plain text rows
                    cols = ['i'+line, '/', '-', '0']
                elif len(cols) == 2:
                    # these are regular tab-separated rows missing fqdn and port
                    cols.append(fqdn)
                    cols.append(str(port))
                elif len(cols) == 3:
                    # these are regular tab-separated rows just missing port
                    cols.append('70')
                elif len(cols) > 4:
                    # these rows should not have so many columns!
                    cols = cols[:4]

                # fix relative paths (if not HTTP URLs)
                if cols[0][0] != 'h' and cols[1] and cols[1][0] != '/':
                    if fqdn == cols[2]:
                        # if paths are within this domain
                        # they must be relative
                        cols[1] = '{}/{}'.format(selector, cols[1])
                    else:
                        # if paths point to an external domain
                        # they must be absolute
                        cols[1] = '/' + cols[1]
                outln.append('\t'.join(cols))
                
            response = '\r\n'.join(outln)
            print(response)
            cl.send(response)
            cl.send('\r\n.\r\n')
            cl.close()

    except OSError as e:
        print(e)
        cl.close()
        print('connection closed')


