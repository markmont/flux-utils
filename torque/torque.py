
import re
from collections import defaultdict

# Load the standard system-wide version of the torque library:
from ctypes import *
_libtorque = cdll.LoadLibrary( "/usr/local/lib/libtorque.so.2.0.0" )


# Given a string of the form nnnn[ kmgt][ bw]
# return number of kb
def get_memory( mem_str ):
    mem_str = mem_str.lower()
    mem_str = mem_str.replace(' ', '')
    m = re.search( r'(\d+)([kmgt]?)([bw]?)', mem_str )
    if not m: return -1
    mem = int( m.group(1) )
    if m.group(2) == 'w' or m.group(3) == 'w': mem *= 8
    if m.group(2) == 'k': mem *= 1
    elif m.group(2) == 'm': mem *= 1024
    elif m.group(2) == 'g': mem *= 1024 * 1024
    elif m.group(2) == 't': mem *= 1024 * 1024 * 1024
    else:
        # memory was expressed in bytes, round up to next kilobyte:
        mem = int( (mem + 1023) / 1024 )
        if mem < 1: mem = 1
    return mem


# Given the amount of memory in KB, return a human-readable string
def show_memory( mem ):
    if mem < 0: return '???'
    if mem < 10 * 1024: return "%d KB" % mem
    if mem < 10 * 1024 * 1024:
        mem = int( (mem + (1 << 9)) / 1024 )   # round to nearest
        return "%d MB" % mem
    if mem < 10 * 1024 * 1024 * 1024:
        mem = int( (mem + (1 << 19)) / (1024 * 1024) )   # round to nearest
        return "%d GB" % mem
    mem = int( (mem + (1 << 29)) / (1024 * 1024 * 1024) )   # round to nearest
    return "%d TB" % mem


# Given a walltime in seconds, return a human-readable string
def show_walltime( walltime ):
    return "%d:%02d:%02d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:], [(walltime,),60,60])


class ATTRL(Structure):
    pass

ATTRL._fields_ = [
    ( "next", POINTER(ATTRL) ),
    ( "name", c_char_p ),
    ( "resource", c_char_p ),
    ( "value", c_char_p )
    ]

class BATCH_STATUS(Structure):
    pass

BATCH_STATUS._fields_ = [
    ( "next", POINTER(BATCH_STATUS) ),
    ( "name", c_char_p ),
    ( "attribs", POINTER(ATTRL) ),
    ( "text", c_char_p )
    ]

class ATTROPL(Structure):
    pass

ATTROPL._fields_ = [
    ( "next", POINTER(ATTROPL) ),
    ( "name", c_char_p ),
    ( "resource", c_char_p ),
    ( "value", c_char_p ),
    ( "op", c_int )
    ]

class BATCH_OP():
    SET = 0
    UNSET = 1
    INCR = 2
    DECR = 3
    EQ = 4
    NE = 5
    GE = 6
    GT = 7
    LE = 8
    LT = 9
    DFLT = 10
    MERGE = 11
    INCR_OLD = 12
 

_libtorque.pbs_errno = c_int
_libtorque.pbs_default.restype = c_char_p
_libtorque.pbs_statjob.argtypes = [ c_int, c_char_p, c_void_p, c_char_p ]
_libtorque.pbs_statjob.restype = POINTER(BATCH_STATUS)
_libtorque.pbs_selstat.argtypes = [ c_int, POINTER(ATTROPL), c_char_p ]
_libtorque.pbs_selstat.restype = POINTER(BATCH_STATUS)
_libtorque.pbs_statfree.argtypes = [ POINTER(BATCH_STATUS) ]  # return type is void


class PBS:

    class JobList:
        def __init__( self, list ):
            self.job_list = self.current_job = list
        def __del__( self ):
            if self.job_list:
                _libtorque.pbs_statfree( self.job_list )
        def __iter__( self ):
            return self
        def next( self ):
            if not self.current_job:
                raise StopIteration
            name = self.current_job.contents.name
            text = self.current_job.contents.text
            attrib = defaultdict(dict)
            a = self.current_job.contents.attribs
            while a:
                if a.contents.resource:
                    k = a.contents.resource
                    attrib[a.contents.name][k] = a.contents.value
                else:
                    attrib[a.contents.name] = a.contents.value
                a = a.contents.next
            self.current_job = self.current_job.contents.next
            return { 'name': name, 'attrib': attrib, 'text': text }


    def default( self ):
        pbs_server = _libtorque.pbs_default()
        if not pbs_server:
            raise EnvironmentError( 1, "No default server PBS server configured" )
        return pbs_server

    def connect( self, server ):
        self.con = _libtorque.pbs_connect( server )
        # pbs_connect appears to terminate the program if there is an error
        # so the following code is not reached
        if not self.con:
            raise EnvironmentError( 2, "unable to connect to pbs server %s (PBS error code %d)" % (server, _libtorque.pbs_errno ) )

    def statjob( self, id, attrib, extend ):
        if not self.con:
            raise RuntimeError( "not connected to pbs server" )
        job_info = _libtorque.pbs_statjob( self.con, id, attrib, extend )
        return PBS.JobList( job_info )

    def selstat( self, sel_list, extend ):
        if not self.con:
            raise RuntimeError( "not connected to pbs server" )
        job_info = _libtorque.pbs_selstat( self.con, sel_list, extend )
        return PBS.JobList( job_info )


