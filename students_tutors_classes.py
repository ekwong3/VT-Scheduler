def parseTimes(times):
    res = {0:"", 1:"", 2:"", 3:"", 4:""}
    for time in range(len(times)):
        res[time] = set(times[time].split(", "))
    return res

def clearSpaces(name):
    while (name[0] == ' '):
        name = name[1:]
    while (name[-1] == ' '):
        name = name[:-1]
    return name

class Student():
    order = 0

    def __init__(self, firstName, lastName, parent, email, prefClass, 
                 otherClass, times, priorityL, priorityI):
        self.firstName = clearSpaces(firstName)
        self.lastName = clearSpaces(lastName)
        self.name = self.firstName + " " + self.lastName
        self.parent = parent
        self.email = email
        self.prefClass = prefClass
        self.otherClass = otherClass
        self.times = parseTimes(times)
        self.priorityLearning = True if priorityL == "Yes" else False
        self.priorityIncome = True if priorityI == "Yes" else False
        self.matched = False
        self.placeInLine = Student.order
        Student.order += 1
    
    def __repr__(self):
        return (self.name)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)

class Tutor():
    def __init__(self, firstName, lastName, email, numClasses, whichClasses, 
                 times, zoom, password):
        self.firstName = clearSpaces(firstName)
        self.lastName = clearSpaces(lastName)
        self.name = self.firstName + " " + self.lastName
        self.email = email
        self.numClasses = int(numClasses)
        self.subjects = set(whichClasses.split(", "))
        self.times = parseTimes(times)
        self.zoom = zoom
        self.password = password
        self.matched = False

    def __repr__(self):
        return (self.name)
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)

def getDay(n):
    if (n == 0):
        return "Monday"
    elif (n == 1):
        return "Tuesday"
    elif (n == 2):
        return "Wednesday"
    elif (n == 3):
        return "Thursday"
    elif (n == 4):
        return "Friday"
    else:
        return ""

class Session():
    def __init__(self, student, tutor, subject, day, time, capacity):
        self.students = set([student])
        self.tutor = tutor
        self.subject = subject
        self.day = day
        self.time = time
        self.capacity = capacity
    
    def __repr__(self):
        return (self.tutor.name + " teaching " + 
                ", ".join([student.name for student in self.students]) + " " +
                self.subject + " at " + self.time + " on " + getDay(self.day))
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)