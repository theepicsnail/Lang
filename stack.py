###
# Program stack
###
class Stack(list):
    def push(self, value):
        self.append(value)
    
    def push_many(self, value_list):
        self.extend(value_list[::-1])
        #print "pushmany", value_list
        #self.stack[self.pos:self.pos] = value_list

    def peek(self):
        #print "peek"
        return self[-1]

    def empty(self):
        return not self

    def __str__(self):
        return "Stack:[" + ", ".join(map(str, self)) + "]"
 
