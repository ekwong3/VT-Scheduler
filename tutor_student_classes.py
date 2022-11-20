def splitTimes(listTimes):
    dictTimes = {'Monday': '', 'Tuesday': '', 'Wednesday': '', 
                'Thursday': '', 'Friday': '', 'Weekends': ''}
    index = 0
    for day in dictTimes.keys():
        times = listTimes[index].split(', ')
        dictTimes[day] = times
        index += 1
    return dictTimes

class Tutor(object):
    def __init__(self, email, name, numClasses, lSubjects, lTimes, zoomLink, password):
        self.email = email
        self.name = name
        self.numClasses = numClasses
        self.subjects = lSubjects.split(', ')
        self.times = [int(x) for x in lTimes.split(', ')]
        self.zoom = zoomLink
        self.password = password
        self.schedule = {}
        self.availability = self.numClasses + len(self.subjects) + len(self.times)

    def info(self):
        return f'[{self.email}, {self.name}, {self.numClasses}, {self.subjects}, {self.times}]'

    def __repr__(self):
        return self.name

class Student(object):
    def __init__(self, email, name, grade, subject, lTimes, parent):
        self.email = email
        self.name = name
        self.grade = grade
        self.subject = subject
        self.times = [int(x) for x in lTimes.split(', ')]
        self.parent = parent
        #schedule saved as: time, subject, tutor name, tutor email, zoom, password
        self.schedule = []
        self.availability = len(self.times)
        self.assigned = False
    
    def info(self):
        return f'[{self.email}, {self.name}, {self.subject}, {self.times}]'

    def __repr__(self):
        return self.name