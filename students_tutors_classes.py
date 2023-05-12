import copy

def parseTimes(times):
    res = set()
    if times == "": return res
    for time in times.split(", "):
        if time[0].isdigit():
            res.add(time[:3])
    return res

def cleanup(name):
    name = name.strip()
    res = ""
    for n in name.split():
        n = n.lower()
        n = n[0].upper() + n[1:]
        res += n + " "
    return res[:-1]

def getTimes(times):
    res = ""
    for time in times:
        res += str(time) + ", "
    if res == set():
        res = "no times"
    else:
        res = res[:-2]
    return res

class Tutor:
    def __init__(self, t, link, email, fName, lName, school, grade, sessions, numStudents, subjects, times, *garbage):
        self.training = True if t == 'Y' else False
        self.link = link
        self.email = email
        self.name = cleanup(fName + " " + lName)
        self.info = (school, grade)
        self.numSessions = int(sessions)
        self.numStudents = int(numStudents)
        self.subjects = subjects
        self.times = parseTimes(times)
        self.prefList = []
        self.full = False

    def __repr__(self):
        times = getTimes(self.times)
        return f'{self.name}'# can tutor {self.numStudents} students in {self.numSessions} classes at {times}\n'
    
    def __eq__(self, other):
        return isinstance(other, Student) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def subjectMatch(self, subject):
        if (subject == "Algebra 1"):
            return (subject in self.subjects)
        (grade, _, subj) = subject.split()
        fullSubject = ""
        grade = int(grade[0])
        if (1 <= grade <= 5):
            fullSubject += "Elementary School " + subj
        else:
            fullSubject += "Middle School " + subj
        return (fullSubject in self.subjects)
    
    def makePrefs(self, students):
        for i in range(len(students)):
            student = students[i]
            if (student.times & self.times != set()) and self.subjectMatch(student.subject):
                self.prefList.append(i)
        # self.prefList.sort()
        # self.prefList = [students.index(student) for student in self.prefList]

class Student:
    def __init__(self, email, pfirst, plast, phone, firstName, lastName, school, grade, subject, times, other, pr, u, *garbage):
        self.email = email
        self.parent = cleanup(pfirst + " " + plast)
        self.phone = phone
        self.name = cleanup(firstName + " " + lastName)
        self.info = (school, grade)
        self.subject = subject
        self.times = parseTimes(times)
        self.prio = True if pr == "Yes" else False
        self.understanding = int(u)
        self.matched = False
        self.tutor = None

    def __repr__(self):
        times = getTimes(self.times)
        return f'{self.name}' # wanting to take {self.subject} at {times}\n'
    
    def __eq__(self, other):
        return isinstance(other, Student) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __lt__(self, other):
        return (not self.prio and other.prio) or (self.info[1] > other.info[1]) or (self.understanding > other.understanding)
        
    
class Session:
    def __init__(self, tutor, subject, capacity, time):
        self.tutor = tutor
        self.students = []
        self.capacity = capacity
        self.time = time
        self.subject = subject
    
    def add(self, index, students):
        student = students[index]
        # print(student)
        assert(self.canAdd(student))
        times = copy.copy(student.times)
        for otherStudent in self.students:
            times &= otherStudent.times
        self.time = times.pop()
        self.students.append(student)
        self.capacity -= 1
        students[index].tutor = self.tutor
        students[index].matched = True
    
    def canAdd(self, student):
        times = copy.copy(student.times)
        for otherStudent in self.students:
            times &= otherStudent.times
        return (self.capacity > 0) and (self.subject == student.subject) and (times != set())
    
    def __repr__(self):
        return f"{self.subject} being taught to {[student.name for student in self.students]} at {self.time}"