"""
    Tiny, ad-hoc implementation of urllib.urlparse
    See https://github.com/micropython/micropython-lib/blob/master/unix-ffi/urllib.parse/urllib/parse.py#L438
"""
def splitnetloc(url, start=0):
    delim = len(url)  # position of end of domain part of url, default is end
    for c in "/?#":  # look for delimiters; the order is NOT important
        wdelim = url.find(c, start)  # find first of this delim
        if wdelim >= 0:  # if found
            delim = min(delim, wdelim)  # use earliest delim position
    return url[start:delim], url[delim:]  # return (domain, rest)


def urlparse(url):
    scheme_chars = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "0123456789" "+-."
    
    netloc = port = query = fragment = ""
    
    i = url.find(":")
    if i > 0:
        for c in url[:i]:
            if c not in scheme_chars:
                break

        rest = url[i + 1 :]
        if not rest or any(c not in "0123456789" for c in rest):
            scheme, url = url[:i].lower(), rest

    if url[:2] == "//":
        netloc, url = splitnetloc(url, 2)

    if ":" in netloc:
        hostname, port = netloc.split(":", 1)
    else:
        hostname = netloc

    # NOT dealing with fragments RN as Lagrange is removing them?
    # (need to understand whether they are supported or not despite
    # what gemini://geminiprotocol.net/docs/specification.gmi says)
    if "#" in url:
        url, fragment = url.split("#", 1)

    if "?" in url:
        url, query = url.split("?", 1)

    return({
        "scheme": scheme,
        "hostname": hostname,
        "port": port,
        # TODO: I know, this is terrible - I'll bring HTTP URLdecode here
        "path": url.replace("%20", " "),
        "query": query,
        "fragment": fragment,
    })
