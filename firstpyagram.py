# first = dict.copy(globals())
import sys
default = sys._getframe().f_locals
import bdb, inspect, ast
import test

def stringtofile(str):
    f = open("userinput.py", "w")
    f.write(str)
    f.close()
    f = open("userinput.py", "r")
    return f


# class printvars(bdb.Bdb):
#     def user_call(self, frame, args):
#         print(globals())
#
#     def user_line(self, frame):
#         print(globals())
#
#     def user_return(self, frame, value):
#         print(globals())
#
#     def user_exception(self, frame, exception):
#         print(globals())

class Func():
    # TODO: finish this class as an easy way to store
    #       and print functions in the pyagram class
    def __init__(self, f):
        self.f = f

    def getparent(self):
        pass
    def getsig(self):
        pass



class Pyagram(bdb.Bdb):
    # natural = {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x107b1d080>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': 'firstpyagram.py', '__cached__': None}
    # glst = {}
    # diclen = 0
    # llst = {}

    def __init__(self):
        bdb.Bdb.__init__(self)
        self.framedict = {} # maps frame num the most recent instance of that frame
        self.idmap = {} # maps frame id to frame num
        self.returnvalues = {}
        self.framecount = 0
        self.curframe = 0 # key or the current frame
        self.prevframe = 0 # key of the frame that called the current frame
        self.funcs = {}
        self.lambdas = {}

    def linegetter(self, ln):
        import linecache
        fn = 'userinput.py'
        line = linecache.getline(fn, ln)
        return line

    def user_func(self, frame):
        # print(frame.f_locals)
        # print(frame.f_globals)
        # print(id(frame))
        self.updateframes(frame)
        import linecache
        # astnode = ast.parse(test.test1)
        self.printall()
        # self.printvars(frame)
        line = self.linegetter(frame.f_lineno)
        print("line {}:".format(frame.f_lineno), line)

    def funcID(self, function):
        # TODO: create a function that gives non built in functions IDs to be
        return id(function)

    # def updatefun()

    def updateframes(self, frame):
        # TODO: add in the return values in the frames
        #       this might need to be done inside of the user_return function
        # TODO: check if this function works for tests other than multframes
        #
        # DONE(6/23/19): update the framedict variable to have the frame number
        #   map to dictionaries of the defined variables in that specific frame
        if not self.framedict:
            self.framedict[0] = frame
            self.idmap[id(frame)] = 0
        elif self.framecount >= len(self.framedict):
            self.framedict[self.framecount] = frame
            self.idmap[id(frame)] = self.framecount
        else:
            # print(self.framecount, len(self.framedict))
            self.framedict[self.idmap[id(frame)]] = frame

    def printframe(self, frame):
        lcls = frame.f_locals
        for var, binding in lcls.items():
            print(var, binding)

    def printframes(self):
        for num, frame in self.framedict.items():
            qwer = {k: v for k, v in frame.f_locals.items() if k not in default}
            print(num, qwer, id(frame))

    def printall(self): # basicly just printframes but it also prints the return value
        for num, frame in self.framedict.items():
            qwer = {k: v for k, v in frame.f_locals.items() if k not in default}
            print(num, qwer, id(frame), repr(self.returnvalues[num]) if num in self.returnvalues.keys() else "") # , "" if not num else repr(self.returnvalues[num])     #.get(num, False)

    def printvars(self, frame):
        # TODO: update to print variables within their corresponding frames

        d = dict.copy(frame.f_locals)
        for key, val in d.items():
            if key == "__" + key[2:-2] + "__":
                continue
            elif inspect.isfunction(val):
                print(key, val.__name__, repr(val))
                # funcname = val.__name__
                # parent =
                # args = inspect.
                # flag = [funcname, ]
            else:
                print(key, repr(val))

    def printfunction(self, function):
        pass

    def user_call(self, frame, args):
        self.framecount += 1
        # self.curframe =
        print("user_call")
        self.user_func(frame)

    def user_line(self, frame):
        print("user_line")
        # print("\n-----------------", frame.f_globals, "\n\n")
        self.user_func(frame)

    def user_return(self, frame, value):
        # TODO: coordinate with updateframes function the addition of
        #       return values in frames storred ad __return__
        #
        #       maybe could do this by simply adding the R.V. on to the
        #       variable bindings in framedict (but how?) A: just do it

        # self.curframe =
        if self.framedict[0] != frame: # might have to do frame.f_back or something
            # print(id(frame) in self.idmap.keys())
            self.returnvalues[self.idmap[id(frame)]] = value
            # self.framedict[self.idmap[id(frame)]].RV = value # add in the frame number
            # need to change the key where 'self.idmap[frame]' is to make it not error!

        print("user_return", repr(value)) #, frame.f_back in self.framedict
        self.user_func(frame)

    def user_exception(self, frame, exception):
        print("user_exception")
        self.user_func(frame)

# print(first)
temp = {'__name__': '__main__', '__doc__': None, '__package__': None, '__spec__': None, '__annotations__': {}, '__cached__': None}
t = Pyagram()
inputfile = stringtofile(test.testrepr)
string = inputfile.read()

t.run(string, {}, {})




"""
#Tdb example class from bdb.py
class Tdb(Bdb):
    def user_call(self, frame, args):
        name = frame.f_code.co_name
        if not name: name = '???'
        print('+++ call', name, args, sys.__dict__)
    def user_line(self, frame):
        import linecache
        name = frame.f_code.co_name
        if not name: name = '???'
        fn = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        print('+++', fn, frame.f_lineno, name, ':', line.strip())
    def user_return(self, frame, retval):
        print('+++ return', retval)
    def user_exception(self, frame, exc_stuff):
        print('+++ exception', exc_stuff)
        self.set_continue()
"""

# print(frame.f_locals) # taken from user_call
# print(frame.f_globals)
# import linecache
# line = linegetter(frame)
# astnode = ast.parse(test.test1)
# # print(fn, frame.f_lineno, frame.f_globals)
# print("user_call: \n", line)
# print('locals:', frame.f_locals)
# print('\nframe info:', inspect.getframeinfo(frame))
#print('\narg spec:', inspect.formatargspec(*inspect.getfullargspec(f)))
# don't have a function to call formateargspec on

#
# def dicchange(self, curframe1234):
#     if curframe1234.f_globals == curframe1234.f_locals: # we are in the global frame
#         if not glst:
#             glst = curframe1234.f_globals
#         print(curframe1234.f_globals.items() - glst.items())
#         glst = curframe1234.f_globals.items()
#     else: # we are in some function call
#         if not llst:
#             llst = curframe1234.f_locals
#         print(curframe1234.f_locals.items() - llst.items())
# elif:
#
# else:
#     var = frame.f_locals
#     if var.items() - llst.items() == var.items():
#         print(var.items() - glst.items())
#     else:
#         print(var.items() - llst.items())

# # will return the last created variable
# def dicchange(self, frame):
#     if diclen = 0:
#         diclen = len(frame.f_globals)
#     elif diclen != len(frame.f_globals):




#
