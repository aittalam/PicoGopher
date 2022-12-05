from picopath import PicoPath, invalid_path
import micropython
import gc
import time

class PicoGopher:

    def __init__(self, ip, gopher_port):
        self._ip = ip
        self._gopher_port = gopher_port

    async def listener(self, reader, writer):
        print("Gopher client connected")
        request_line = await reader.readline()
        print("Request:", request_line)

        selector = request_line.decode().strip()
        if '\t' in selector:
            writer.write('3Gopher+ selectors unsupported {}.\t\terror.host\t1'.format(selector).encode('US-ASCII', 'replace'))
            writer.write('\r\n.\r\n'.encode('US-ASCII', 'replace'))
            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")

            return

        if selector:
            if not selector.startswith('/'):
                selector = '/' + selector
            relative = selector[1:]
        else:
            relative = ""
            
        absolute_path = "/gopher/" + relative
        print("Absolute path: {}".format(absolute_path))
        
        if invalid_path(absolute_path):
            writer.write('3Error accessing {}.\t\terror.host\t1'.format(selector).encode('US-ASCII', 'replace'))
            writer.write('\r\n.\r\n'.encode('US-ASCII', 'replace'))
            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            return

        elif PicoPath(absolute_path).is_file():
            print('Success: file: {}'.format(absolute_path))
            # I got some memory errors with 64KB blocks,
            # so I am keeping them tiny for now
            block_size = 1 * 1024
            
            # preallocate a buffer of block_size to load data into
            buf = bytearray(block_size)

            with open(absolute_path, 'rb') as inf:
                bytes_read = inf.readinto(buf)
                while bytes_read == block_size :
                    try:
                        writer.write(buf)
                    except MemoryError as e:
                        # happens (also) when out_buf gets too
                        # large, so let us drain and retry
                        print(f"[w] {e} => will drain and retry")
                        await writer.drain()
                        writer.write(buf)

                    # read next chunk into buf
                    bytes_read = inf.readinto(buf)

                # finally, write the remaining bytes
                # (note that there's a chance we'll get
                # a MemoryError here too...)
                writer.write(buf[:bytes_read])

            await writer.drain()
            await writer.wait_closed()

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
                    cols.append(self._ip)
                    cols.append(str(self._gopher_port))
                elif len(cols) == 3:
                    # these are regular tab-separated rows just missing port
                    cols.append(self._gopher_port)
                elif len(cols) > 4:
                    # these rows should not have so many columns!
                    cols = cols[:4]

                # fix relative paths (if not HTTP URLs)
                if cols[0][0] != 'h' and cols[1] and cols[1][0] != '/':
                    if self._ip == cols[2]:
                        # if paths are within this domain
                        # they must be relative
                        cols[1] = '{}/{}'.format(selector, cols[1])
                    else:
                        # if paths point to an external domain
                        # they must be absolute
                        cols[1] = '/' + cols[1]
                outln.append('\t'.join(cols))
                
            response = '\r\n'.join(outln)
#             print(response)
            writer.write(response)
            writer.write('\r\n.\r\n')
            await writer.drain()
            await writer.wait_closed()
            
        print("Client disconnected")
