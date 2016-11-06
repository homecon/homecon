class myobject(object):

    def __init__(self):
        self._a = {}

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self,val):
        self._a = val



inst = myobject()

print(inst.a)
inst.a = {'a':1,'b':2}


print(inst.a)

inst.a['test'] = 5

print(inst.a)

inst.a.update({'a':2,'b':10})

print(inst.a)
