import gspread
import copy
from tutor_student_classes import *

serviceAccount = gspread.service_account(filename = "credentials.json")
sheet = serviceAccount.open("Copy of Main Summer 2022 Spreadsheet")

tutors = sheet.worksheet("Tutor List").get_all_values()
students = sheet.worksheet("Student List").get_all_values()
maxStudents = 5

#indicies:
#tutors: email: 4, name: 5-6, #classes: 9, subjects: 12, zoom + password: 1-2
#students: email: 2, student's name: 4-5, subject: 8, parent's name: 3-4

def combineFirstLastNames(first,last):
    if first[-1] != ' ':
        first += ' '
    if last[-1] == ' ':
        last = last[:-1]
    return first + last

def shortenTutor(t):
    tutor = [t[4]] + [combineFirstLastNames(*t[5:7])] + [int(t[9])] + [t[12]] + [t[10]] + t[1:3]
    return tutor

def shortenStudent(s):
    #email, student name, grade, subject, lTimes, parent
    student = [s[2]] + [combineFirstLastNames(*s[4:6])] + [int(s[7][0])] + [s[8]] + [s[9]] + [combineFirstLastNames(*s[2:4])]
    return student

def cleanupTutors(t):
    emailIndex = 4
    newList = []
    tutors = t[1:]
    for tutor in tutors:
        if tutor[emailIndex] != '':
            newList.append(Tutor(*shortenTutor(tutor)))
    return newList

def cleanupStudents(s):
    emailIndex = 2
    newList = []
    students = s[1:]
    for student in students:
        if student[emailIndex] != '':
            newList.append(Student(*shortenStudent(student)))
    return newList

def dictTutors(tDict):
    dTutors = {}
    for group in tDict:
        for tutor in tDict[group]:
            dTutors[tutor.name] = tutor
    return dTutors

def dictStudents(sDict):
    dStudents = {}
    for group in sDict:
        for student in sDict[group]:
            dStudents[student.name] = student
    return dStudents

def sortListByAvailability(plist):
    newList = []
    while plist != []:
        leastAvailability = min([p.availability for p in plist])
        for p in plist:
            if p.availability == leastAvailability:
                newList.append(p)
                plist.remove(p)
    return newList

def sortPeopleByAvailability(pdict):
    for c in pdict:
        pdict[c] = sortListByAvailability(pdict[c])
    return pdict

# Sorted by least optioned classes to most
def createTutorsDict(t):
    t = cleanupTutors(t)
    tDict = {}
    for tutor in t:
        for subject in tutor.subjects:
            if subject not in tDict:
                tDict[subject] = [tutor]
            else: 
                tDict[subject].append(tutor)
    return sortPeopleByAvailability(tDict)

# Sorted by most demanded classes to least
def createStudentsDict(s):
    s = cleanupStudents(s)
    sDict = {}
    for student in s:
        if student.subject not in sDict:
            sDict[student.subject] = [student]
        else: 
            sDict[student.subject].append(student) 
    return sortPeopleByAvailability(sDict)

def sortClassesByDemand(studentDict):
    sDict = copy.deepcopy(studentDict)
    classes = []
    numClasses = len(sDict)
    biggest = -1 
    curClass = ""
    for i in range(numClasses):
        for c in sDict:
            curLen = len(sDict[c])
            if curLen > biggest:
                biggest = curLen
                curClass = c
        classes.append(curClass)
        sDict.pop(curClass)
        biggest = -1
    return classes

def sortTimesByDemand(sDict, subject):
    times = {}
    for student in sDict[subject]:
        for t in student.times:
            if t in times:
                times[t]+=[1]
            else:
                times[t] = [1]
    return [int(x) for x in sortClassesByDemand(times)]

def matchSubject(subject):
    if subject == "Algebra 1": 
        return "Algebra 1"
    sGrade = int(subject[0])
    # Math, English
    subjectName = subject.split(' ')[-1]
    if sGrade in [1,2,3,4,5]:
        grade = "Elementary School "
    elif sGrade in [6,7,8,9]:
        grade = "Middle School "
    return grade + subjectName

def timeFit(tutor, student):
    tTimes, sTimes = tutor.times, student.times
    for time in sTimes:
      if (time in tTimes):
        return True
    return False

def hasRoom(tutor, time, subject):
    if (time not in tutor.schedule) and (len(tutor.schedule) >= tutor.numClasses):
        return False
    elif (time not in tutor.schedule) and (len(tutor.schedule) < tutor.numClasses):
        return True
    else:
        #tutor schedule is {time:[subject, [students]]}
        curSubject, students = tutor.schedule[time]
        return (curSubject == subject) and (len(students) < maxStudents)

def findTutorwTime(tDict, subject, times):
    subject = matchSubject(subject)
    for time in times:
        for tutor in tDict[subject]:
            if time in tutor.times and hasRoom(tutor, time, subject):
                return tutor, time
    return None, None

def addStudentToTutor(student, tutor, time, subject):
    student.schedule = [time, subject, tutor.name, 
                        tutor.email, tutor.zoom, tutor.password]
    if time not in tutor.schedule:
        tutor.schedule[time] = [subject, [student.name]]
    else:
        tutor.schedule[time][1].append(student.name)
        if len(tutor.schedule[time][1]) >= maxStudents:
            tutor.times.remove(time)
    tutor.availability-=1
    return tutor, student

def loopPair(tDict, sDict):
    # Organize by most demanded classes
    classesOrder = sortClassesByDemand(sDict)
    for c in classesOrder:
        bestTimes = sortTimesByDemand(sDict, c)
        tutor, time = findTutorwTime(tDict, c, bestTimes)
        for student in sDict[c]:
            if (tutor == None or not hasRoom(tutor, time, c)):
                continue
            if (timeFit(tutor, student) and not(student.assigned)):
                student.assigned = True
                tutor, student = addStudentToTutor(student, tutor, time, c)
    return tDict, sDict

def updateWaitlist(sDict):
    updatedWaitlist = set()
    for c in sDict:
        for student in sDict[c]:
            if not(student.assigned):
                updatedWaitlist.add(student)
    return updatedWaitlist

def schedule(tutors,students):
    tDict = createTutorsDict(tutors)
    sDict = createStudentsDict(students)
    tDict, sDict = loopPair(tDict, sDict)
    unassignedTutors = set()
    waitlist = set()
    runs = 0
    while True:
        updatedWaitlist = updateWaitlist(sDict)
        tDict, sDict = loopPair(tDict, sDict)
        runs+=1
        if updatedWaitlist == waitlist:
            break
        waitlist = updatedWaitlist
    for group in tDict.keys():
        for tutor in tDict[group]:
            if tutor.schedule == {}:
                unassignedTutors.add(tutor)
    tPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/tutors.txt'
    writeTxtDicts(tPath, stringifyTutors(tDict))
    sPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/students.txt'
    writeTxtDicts(sPath, stringifyStudents(sDict))
    return len(waitlist), waitlist, unassignedTutors, runs

def stringifyTutors(tDict):
    newTutorDict = {}
    for group in tDict:
        for t in tDict[group]:
            firstName, lastName = t.name.split(' ')
            newTutorDict[t.name] = [t.email, firstName, lastName, '', t.numClasses, t.schedule]
    return str(newTutorDict)

def stringifyStudents(sDict):
    newStudentDict = {}
    for group in sDict:
        for s in sDict[group]:
            newStudentDict[s.name] = [s.email, s.parent, '', s.name, s.schedule]
    return str(newStudentDict)

def writeTxtDicts(path, stringDict):
    text_file = open(path, 'w')
    text_file.write(stringDict)
    text_file.close()

import ast

def readDicts(path):
    txtDict = open(path, 'r')
    content = txtDict.read()
    return ast.literal_eval(content)

def addSchedule(tutorStartRow = 0, studentStartRow = 0):
    tOrder = [tutor.name for tutor in cleanupTutors(tutors)]
    sOrder = [student.name for student in cleanupStudents(students)]
    stuScheduleSheet = sheet.worksheet("Student Schedule")
    tutScheduleSheet = sheet.worksheet("Tutor Schedule")
    tPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/tutors.txt'
    sPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/students.txt'
    tDict, sDict = readDicts(tPath), readDicts(sPath)
    for row in range(tutorStartRow, len(tOrder)):
        curTutor = tDict[tOrder[row]]
        row += 2
        regInfo = curTutor[:-1]
        tutScheduleSheet.update(f'A{row}:E{row}', [regInfo])
        classStartEndCols = [('F','H'),('I','K'),('L','N')]
        classNum = 0
        curSchedule = curTutor[-1]
        if curSchedule != {}:
            for time in curSchedule.keys():
                curStudents = ' and '.join(curSchedule[time][1])
                subject = curSchedule[time][0]
                classInfo = [curStudents, time, subject]
                start, end = classStartEndCols[classNum]
                tutScheduleSheet.update(f'{start}{row}:{end}{row}', [classInfo])
                classNum += 1
    for row in range(studentStartRow, len(sOrder)):
        curStudent = sDict[sOrder[row]]
        row += 2
        regInfo = curStudent[:-1]
        stuScheduleSheet.update(f'A{row}:D{row}', [regInfo])
        curSchedule = curStudent[-1]
        if curSchedule != []:
            stuScheduleSheet.update(f'E{row}:J{row}', [curSchedule])

def studentsAssigned(tDict):
    count = 0
    for c in tDict:
        for tutor in tDict[c]:
            for session in tutor.schedule:
                for student in tutor.schedule[session][1]:
                    print(tutor.name, student)
                    count+=1
    return count

    # Aren't necessary
# def lookForOpening(tDict, student):
#     times = student.times
#     tutor, time = findTutorwTime(tDict, student.subject, times)
#     if tutor != None:
#         tutor, student = addStudentToTutor(student, tutor, time, student.subject)
#     return tDict, student

# def fillIn(tDict, sDict):
#     for c in sDict:
#         for student in sDict[c]:
#             if not student.assigned:
#                 tDict, student = lookForOpening(tDict, student)
#     return tDict, sDict