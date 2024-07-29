from picopath import PicoPath, invalid_path
import micropython
import gc
import time
import picourllib


class PicoGemini:
    """ MicroPython port of GeGoBi (more like GeBi for now...).

    See https://git.sr.ht/~solderpunk/gegobi/tree/master/item/gegobi.py
    """

    def __init__(self, ip, cfg):
        self._ip = ip
        self._cfg = cfg
        self._writer = None


    def parse_request(self, req):
        """
        Read a URL from the Gemini client and parse it up into parts,
        including separating out the Gopher item type.
        """
        requested_url = req.decode("UTF-8").strip()
        if "://" not in requested_url:
            requested_url = "gemini://" + requested_url
        self.request_url = requested_url

        parsed =  picourllib.urlparse(requested_url)
        self.request_scheme = parsed["scheme"]
        self.request_host = parsed["hostname"]
        self.request_port = parsed["port"] or 1965
        self.request_path = parsed["path"][1:] if parsed["path"].startswith("/") else parsed["path"]
        ### TODO: reimplement parse.unquote
# see https://github.com/micropython/micropython-lib/blob/master/unix-ffi/urllib.parse/urllib/parse.py
#         self.request_path = urllib.parse.unquote(self.request_path)
        self.request_query = parsed["query"]
        print(parsed)


    def _send(self, string):
        self._writer.write(string.encode("UTF-8"))


    def send_gemini_header(self, status, meta):
#         print("Sending {} {}\r\n".format(status, meta))
        self._send("{} {}\r\n".format(status, meta))


    async def close(self):
        await self._writer.drain()
        await self._writer.wait_closed()        
        print("Client disconnected")
        return


    def handle_geminimap(self, filename):
        self.send_gemini_header(20, "text/gemini")
        with open(filename,"r") as fp:
            self._send(fp.read())


    def _gopher_url(self, host, port, itemtype, path):
        path = itemtype + path
        if port == "70":
            netloc = host
        else:
            netloc = host + ":" + port

        return f"gopher://{netloc}/{path}"


    def handle_gophermap(self, filename):
        self.send_gemini_header(20, "text/gemini")
        with open(filename, "r") as fp:
            for line in fp:
                if "\t" in line:
                    itemtype = line[0]
                    parts = line[1:].strip().split("\t")
                    print(parts)
                    if itemtype == "i":
                        self._send(parts[0])
                    else:
                        if len(parts) == 2:
                            # Relative link to same server
                            name, link = parts
                            if itemtype == "h" and link.startswith("URL:"):
                                link = link[4:]
                        elif len(parts) == 4:
                            # External gopher link
                            name, path, host, port = parts
                            link = self._gopher_url(host, port, itemtype, path)
                        # TODO: do a proper urlencoding here!
                        self._send("=> %s %s\r\n" % (link.replace(" ","%20"), name))
                else:
                    self._send(line)


    def handle_file(self, filename):
        """
        """
#         # TODO: Guess/detect MIME type
#         mimetype, encoding = mimetypes.guess_type(filename)
#         if not mimetype:
#             out = subprocess.check_output(
#                 shlex.split("file --brief --mime-type %s" % filename)
#             )
#             mimetype = out.decode("UTF-8").strip()
        self.send_gemini_header(20, "text/plain")
        with open(filename,"r") as fp:
            self._send(fp.read())


    async def listener(self, reader, writer):
        print("Gemini client connected")
        self._writer = writer

        req = await reader.readline()
        self.parse_request(req)

        print(f"[i] Request details:")
        print(f"    scheme: {self.request_scheme}")
        print(f"    hostname: {self.request_host}")
        print(f"    port: {self.request_port}")
        print(f"    path: {self.request_path}")
        print(f"    query: {self.request_query}")

        # Resolve path to filesystem
        local_path = str(PicoPath(self._cfg.root_dir) / self.request_path)
        print("Absolute path: {}".format(local_path))

        # check for invalid paths
        if invalid_path(local_path):
            self.send_gemini_header(51, "Not found.")
            await self.close()
            return

        if PicoPath(local_path).is_dir():
            # Redirect to add trailing slash so relative URLs work
            if self.request_path and not self.request_path.endswith("/"):
                print(f"Request was: {self.request_url}")
                self.send_gemini_header(31, self.request_url +"/")
                await self.close()
                return
            # Check for gemini or gopher menus
            geminimap = local_path + "index.gmi"
            geminimap2 = local_path + "index.gemini"
            gophermap = local_path + "gophermap"
            indexgph = local_path + "index.gph"

            if PicoPath(geminimap).exists():
                self.handle_geminimap(geminimap)
#             elif os.path.exists(geminimap2):
#                 self.handle_geminimap(geminimap2)
            elif PicoPath(gophermap).exists():
                self.handle_gophermap(gophermap)
#             elif os.path.exists(indexgph):
#                 self.handle_gph(indexgph)
#             else:
#                 self.generate_directory_listing(local_path)
        #  Handle files
        else:
            self.handle_file(local_path)
        # Clean up
        await self.close()