import os

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

    def __truediv__(self, other):
        if other.startswith("/"):
            other = other[1:]
        if self.fname.endswith("/"):
            return PicoPath(self.fname + other)
        else:
            return PicoPath(self.fname + "/" + other)

    def __str__(self):
        return self.fname


def invalid_path(absolute_path):
    '''
        Returns True if the provided absolute path is NOT valid.
        Rules for validity:
        
        - must not contain ".."
        - must match an existing file/dir
        - if a dir, it has to contain a gopherfile
        
        Note that while strongly biased towards gopher, this is
        currently used also for the HTTP server (as it currently
        only works with the very same gopherhole contents)
        
    '''
    if '..' in absolute_path:
        print('Error: attempt to access parent: {}'.format(absolute_path))
        return True

    path_abs = PicoPath(absolute_path)
    path_gmap = path_abs / 'gophermap'
    path_gmi = path_abs / 'index.gmi'
    path_gmi2 = path_abs / 'index.gemini'

    if not path_abs.exists():
        print('Error: attempt to access nonpublic path: {}'.format(absolute_path))
        return True
    elif path_abs.is_file():
        return False
    elif (path_abs.is_dir() and
          (path_gmap.exists() and path_gmap.is_file()) or
          (path_gmi.exists() and path_gmi.is_file()) or
          (path_gmi2.exists() and path_gmi2.is_file())
          ):
        return False

    print('Error: attempt to access something weird: {}'.format(absolute_path))
    return True
