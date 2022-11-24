from picopath import PicoPath, invalid_path

class PicoHTTP:

    _hexdig = '0123456789ABCDEFabcdef'
    _hextobyte = None

    def __init__(self, ip, http_port):
        self._ip = ip
        self._http_port = http_port


    def urldecode(self, string):
        """urldecode('abc%20def') -> b'abc def'."""

        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.
        if not string:
            return b''

        if isinstance(string, str):
            string = string.encode('utf-8')

        bits = string.split(b'%')
        if len(bits) == 1:
            return string

        res = [bits[0]]
        append = res.append

        # Delay the initialization of the table to not waste memory
        # if the function is never called
        if self._hextobyte is None:
            self._hextobyte = {(a + b).encode(): bytes([int(a + b, 16)])
                          for a in self._hexdig for b in self._hexdig}

        for item in bits[1:]:
            try:
                append(self._hextobyte[item[:2]])
                append(item[2:])
            except KeyError:
                append(b'%')
                append(item)

        return b''.join(res)


    async def listener(self, reader, writer):
        print("HTTP client connected")
        request_line = await reader.readline()
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass
        
        request = request_line.decode().strip()
        print("Request:", request_line)

        if not request.startswith('GET'):
            error = "Only GET requests allowed"
            print(f"HTTP error: {error}")
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(error)
            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")

            return

        selector = self.urldecode(request.split()[1]).decode()
        print("Selector:", selector)

        if selector:
            if not selector.startswith('/'):
                selector = '/' + selector
            relative = selector[1:]
        else:
            relative = ""

        # this is a quick hack to fix Mac/IOS' requests
        # intercepted by the captive portal
        if relative == "hotspot-detect.html":
            relative = ""
            selector = "/"

        absolute_path = "/gopher/" + relative
        print("Absolute path: {}".format(absolute_path))
        
        if invalid_path(absolute_path):
            error = f"Invalid path: {absolute_path}"
            print(f"HTTP error: {error}")
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(error)
            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            return

        elif PicoPath(absolute_path).is_file():
            print('Success: file: {}'.format(absolute_path))
            
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
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
            
            response = '''
<html><head><title>gophermap</title></head>
<style type='text/css'> pre {display: inline;} </style>
<body>
<span style="font-family:Courier; white-space:pre">
'''            
            txt = gmap.splitlines()
            outln = []
            for line in txt:
                if line:
                    cols = line.split('\t')
                else:
                    cols = ['i']

                if len(cols) == 1:
                    # translate plain text rows
                    response_line = f"{line}"
                elif len(cols) == 2:
                    ### SUPER EARLY IMPLEMENTATION!
                    # - does not handle http URLs properly
                    # - does not work with links to external gopherholes
                    ident = cols[0][0]
                    text = cols[0][1:]
                    ref = cols[1]

                    print("***", ref)
                    # fix relative paths
                    if ref[0] != '/' and selector != "/":
                        ref = '{}/{}'.format(selector, ref)

                    response_line = f'<a href="{ref}">{text}</a>'

                else:
                    response_line = ""

                outln.append(response_line)
                
            outln.append("</span></body></html>")
            response = response + '\r\n'.join(outln)
            print(response)
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(response)
            writer.write('\r\n')
            await writer.drain()
            await writer.wait_closed()
            
        print("Client disconnected")
