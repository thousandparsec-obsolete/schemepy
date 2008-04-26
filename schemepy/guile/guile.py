from ctypes.util import find_library
from ctypes import *

lib = find_library("guile")
if lib is None:
    raise RuntimeError("Can't find a guile library to use.")
guile = cdll.LoadLibrary(lib)


class SCM(c_void_p):
    def __init__(self, value=None):
        c_void_p.__init__(self)
        self.value = value
        
    def value_set(self, value):
        oldv = getattr(self, 'value', None)
        if oldv is not None:
            guile.scm_gc_unprotect_object(oldv)
        if value is not None:
            guile.scm_gc_protect_object(value)
        return c_void_p.value.__set__(self, v)

    def value_get(self):
        return c_void_p.value.__get__(self)
    scm = property(value_get, value_set)
    
    def __del__(self):
        self.value = None

    def __str__(self):
        return "<SCM %s>" % self.value
    
    def __repr__(self):
        return self.__str__()

    def type(self):
        if guile.scm_is_bool(self):
            return bool
        if guile.scm_is_number(self):
            if guile.scm_is_true(guile.scm_exact_p(self)):
                return int
            if guile.scm_c_imag_part(self) != 0:
                return complex
            return float
        return type(None)

    def topython(self):
        "Return a Python value corresponding to this SCM"
        if guile.scm_is_bool(self):
            if guile.scm_to_bool(self):
                return True
            return False
        if guile.scm_is_number(self):
            if guile.scm_is_true(guile.scm_exact_p(self)):
                return guile.scm_to_int32(self)
            if guile.scm_c_imag_part(self) != 0:
                return complex(guile.scm_c_real_part(self),
                               guile.scm_c_imag_part(self))
            return guile.scm_to_double(self)
        return None

    def toscm(val):
        "Convert the Python value to a SCM"
        if type(val) is bool:
            if val:             # FIXME: are those constants portable?
                return SCM(260)
            return SCM(4)
        if type(val) is int:
            return guile.scm_from_int32(val)
        if type(val) is complex:
            return guile.scm_make_complex(val.real, val.imag)
        if type(val) is float:
            return guile.scm_from_double(val)
        return SCM(None)
    toscm = staticmethod(toscm)

SCM.constants = dict([[v, SCM.toscm(v)] for v in \
                          [True, False]])

class Compiler(object):
    """Compiler for guile. Guile doesn't support bytecode yet. So the
    compiler just do nothing."""
    def __call__(self, code):
        return code


def exception_body(src):
    return guile.scm_c_eval_string(src).value
exception_body_t = CFUNCTYPE(SCM, c_char_p)
exception_body = exception_body_t(exception_body)

exception_handler_t = CFUNCTYPE(SCM, c_void_p, c_void_p, c_void_p)
def make_exception_handler(exceptions):
    """\
    * error-signal: thrown after receiving an unhandled fatal
      signal such as SIGSEGV, SIGBUS, SIGFPE etc. The rest
      argument in the throw contains the coded signal number (at
      present this is not the same as the usual Unix signal
      number).
    
    * system-error: thrown after the operating system indicates an
      error condition. The rest argument in the throw contains the
      errno value.
    
    * numerical-overflow: numerical overflow.
    
    * out-of-range: the arguments to a procedure do not fall
      within the accepted domain.
    
    * wrong-type-arg: an argument to a procedure has the wrong
      type.
    
    * wrong-number-of-args: a procedure was called with the wrong
      number of arguments.
    
    * memory-allocation-error: memory allocation error.
    
    * stack-overflow: stack overflow error.
    
    * regular-expression-syntax: errors generated by the regular
      expression library.
    
    * misc-error: other errors. 
    """
    def exception_handle(trash, key, args):
        key = SCM(key)
        args = SCM(args)
        exceptions.append(Exception(key.topython(), args.topython()))
        return SCM.constants[True].value
    
    return exception_handler_t(exception_handle)
        

guile.scm_internal_catch.argtypes = [SCM, exception_body_t, c_char_p, exception_handler_t, c_void_p]
guile.scm_internal_catch.restype = SCM
guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype  = SCM

class VM(object):
    """VM for guile.
    """

    def __init__(self):
        self.exception = None
   
    def eval(self, src):
        exceptions = []
        r = guile.scm_internal_catch(SCM.constants[True], exception_body, src,
                                     make_exception_handler(exceptions), None)
        if len(exceptions) != 0:
            raise exceptions[0]
        return r

    def toscheme(val):
        return SCM.toscm(val)
    toscheme = staticmethod(toscheme)

# Initialize guile
guile.scm_init_guile()

# Predict functions
guile.scm_exact_p.argtypes = [SCM]
guile.scm_exact_p.restype = SCM

# Conversion functions
guile.scm_from_int32.argtype = [c_int]
guile.scm_from_int32.restype = SCM
guile.scm_make_complex.argtype = [c_double, c_double]
guile.scm_make_complex.restype = SCM
guile.scm_from_double.argtypes = [c_double]
guile.scm_from_double.restype = SCM

guile.scm_is_true = lambda b: b.value == SCM.constants[True].value
