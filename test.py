#!/usr/bin/python3

class Tag(object):

    def __init__(self):
        self.value = None
    
    def getValue(self):
        return self.value
    
    def setValue(self, value):
        self.value = value


t1 = Tag()
t2 = Tag()
t3 = Tag()

t1.setValue(20)
t2.setValue(3)
t3.setValue(t1.getValue() - t2.getValue())

print(t1.getValue(), t2.getValue(), t3.getValue())