
class memoize_on(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, size=None, argf=None):
      self.size = size
      self.argf = argf
      if self.argf is None:
         self.argf = lambda *args, **kwargs: args
      self.cache = {}
   def __call__(self, f):
      def wrapped_f(*args, **kwargs):
          try:
             return self.cache[self.argf(*args, **kwargs)]
          except KeyError:
             value = f(*args, **kwargs)
             if self.size is not None and len(self.cache) >= self.size:
                self.cache.popitem() # FIXME: Doesn't care how old it is.
             self.cache[self.argf(*args, **kwargs)] = value
             return value
          except TypeError:
             # uncachable -- for instance, passing a list as an argument.
             # Better to not cache than to blow up entirely.
             return f(*args, **kwargs)
      return wrapped_f
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__
   def __get__(self, obj, objtype):
      """Support instance methods."""
      return functools.partial(self.__call__, obj)