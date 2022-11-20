import gspread
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

def findTimes(times):
    numTimes = 0
    for time in times:
        if time == '':
            continue
        numTimes += len(time.split(','))
    return numTimes

def createTutorsDict(t):
    t = cleanupTutors(t)
    tDict = {}
    for tutor in t:
        if tutor.availability not in tDict:
            tDict[tutor.availability] = [tutor]
        else: 
            tDict[tutor.availability].append(tutor)
    return tDict

def createStudentsDict(s):
    s = cleanupStudents(s)
    sDict = {}
    for student in s:
        if student.availability not in sDict:
            sDict[student.availability] = [student]
        else: 
            sDict[student.availability].append(student) 
    return sDict

def subjectFit(tutor,student):
    tSubjects, sSubject = tutor.subjects, student.subject
    sGrade = student.grade
    if sSubject == "Algebra 1":
        if sSubject in tSubjects:
            return True, "Algebra 1"
        else: return False, None
    else: 
        subject = sSubject.split(' ')[-1]
        if sGrade in [1,2,3,4,5]:
            grade = "Elementary School "
        elif sGrade in [6,7,8,9]:
            grade = "Middle School "
        if sSubject == "Algebra 1": 
            fullSubject = "Algebra 1 "
        else: 
            # print(sGrade)
            fullSubject = grade + subject
        if fullSubject in tSubjects: 
            return True, sSubject
    return False, None

#added into the tutor schedule dictionary as: 
def timeFit(tutor, student):
    tTimes, sTimes = tutor.times, student.times
    for day in sTimes:
        for time in sTimes[day]:
            if (time in tTimes[day]) and (time != ''):
                return True, day + ' at ' + time
    return False, None

def timeFitSummer(tutor, student):
    tTimes, sTimes = tutor.times, student.times
    for time in sTimes:
      if (time in tTimes):
        return True, time
    return False, None

def hasRoom(tutor,time,subject):
    if (time not in tutor.schedule) and (len(tutor.schedule) >= tutor.numClasses):
        return False
    elif (time not in tutor.schedule) and (len(tutor.schedule) < tutor.numClasses):
        return True
    else:
        #tutor schedule is {time:[subject, [students]]}
        curSubject, students = tutor.schedule[time]
        # print((curSubject == subject) and (len(students) > 2))t'
        return (curSubject == subject) and (len(students) < 5)

def studentFit(tutor,student):
    #if it works we return True, subject, time
    timeOK, subjOK = timeFitSummer(tutor,student), subjectFit(tutor,student) 
    # print(tutor.name, student.name, timeOK, subjOK)
    if not(timeOK[0] and subjOK[0]):
        return False, None, None
    else:
        time, subject = timeOK[1], subjOK[1]
        return hasRoom(tutor,time,subject), time, subject
    
def stillAvailable(tutor):
    if len(tutor.schedule) < tutor.numClasses:
        return True
    else:
        print(tutor.schedule)
        for session in tutor.schedule:
            print(session)
            # USE FOR FALL/SPRING
            # students = session[1]
            # USE FOR SUMMER
            students = tutor.schedule[session][1]
            if len(students) < maxStudents:
                return True
    return False

def loopPair(tDict, sDict, assignedStudents = set()):
    possibleMoreStudents = {}
    assignedTutors = set()
    tOrder = sorted(tDict.keys())[::-1]
    sOrder = sorted(sDict.keys())[::-1]
    for flexRank in tOrder:
        for tutor in tDict[flexRank]:
            for flexTime in sOrder:
                for student in sDict[flexTime]:
                    fit, time, subject = studentFit(tutor,student)
                    if (fit and (student not in assignedStudents) 
                            and (tutor.name not in assignedTutors)):
                        assignedStudents.add(student)
                        assignedTutors.add(tutor)
                        student.schedule = [time, subject, tutor.name, 
                            tutor.email, tutor.zoom, tutor.password]
                        if time not in tutor.schedule:
                            tutor.schedule[time] = [subject, [student.name]]
                        else:
                            tutor.schedule[time][1].append(student.name)
                            day, specificTime = time.split(' at ')
                            tutor.times[day].remove(specificTime)
                            tutor.availability -= 1
            if stillAvailable(tutor):
                if tutor.availability not in possibleMoreStudents:
                    possibleMoreStudents[tutor.availability] = [tutor]
                else: 
                    possibleMoreStudents[tutor.availability].append(tutor)
    return possibleMoreStudents, assignedStudents

def schedule(tutors,students):
    tDict = createTutorsDict(tutors)
    sDict = createStudentsDict(students)
    newTDict, assignedStudents = loopPair(tDict,sDict)
    unassignedTutors = set()
    waitlist = set()
    while True:
        unassignedStudents = {}
        for group in sDict.keys():
            for student in sDict[group]:
                if student not in assignedStudents:
                    if group not in unassignedStudents:
                        unassignedStudents[group] = [student]
                    else:
                        unassignedStudents[group].append(student)
        possibleMoreStudents, assignedStudents = loopPair(newTDict, unassignedStudents, assignedStudents)
        if newTDict == possibleMoreStudents:
            break
        newTDict = possibleMoreStudents
    for group in tDict.keys():
        for tutor in tDict[group]:
            if tutor.schedule == {}:
                unassignedTutors.add(tutor)
    for group in sDict.keys():
        for student in sDict[group]:
            if student.schedule == []:
                waitlist.add(student)
    tPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/tutors.txt'
    writeTxtDicts(tPath, stringifyTutors(tDict))
    sPath = '/Users/ekwong/Desktop/Virtual_Tutoring/tSchedulerFinal/students.txt'
    writeTxtDicts(sPath, stringifyStudents(sDict))
    return len(waitlist), waitlist, unassignedTutors, #tDict, sDict

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
        

#only if google apis didnt have a quota on them...

# def addSchedule(tutors, students, tutorStartRow = 0, studentStartRow = 0):
#     tOrder = [tutor.name for tutor in cleanupTutors(tutors)]
#     sOrder = [student.name for student in cleanupStudents(students)]
#     tDict, sDict = schedule(tutors,students)[3:]
#     tuts, stus = dictTutors(tDict), dictStudents(sDict)
#     stuScheduleSheet = sheet.worksheet("Student Schedule")
#     tutScheduleSheet = sheet.worksheet("Tutor Schedule")
#     for row in range(tutorStartRow, len(tOrder)):
#         curTutor = tuts[tOrder[row]]
#         row += 2
#         firstName, lastName = curTutor.name.split(' ')
#         curRow = [curTutor.email, firstName, lastName, '', curTutor.numClasses]
#         tutScheduleSheet.update(f'A{row}:E{row}', [curRow])
#         classStartEndCols = [('F','H'),('I','K'),('L','N')]
#         classNum = 0
#         if curTutor.schedule != {}:
#             for time in curTutor.schedule.keys():
#                 curStudents = ' and '.join(curTutor.schedule[time][1])
#                 subject = curTutor.schedule[time][0]
#                 classInfo = [curStudents, time, subject]
#                 start, end = classStartEndCols[classNum]
#                 tutScheduleSheet.update(f'{start}{row}:{end}{row}', [classInfo])
#                 classNum += 1
#     for row in range(studentStartRow, len(sOrder)):
#         curStudent = stus[sOrder[row]]
#         row += 
#         curRow = [curStudent.email, curStudent.parent, '', curStudent.name]
#         stuScheduleSheet.update(f'A{row}:D{row}', [curRow])
#         if curStudent.schedule != []:
#             curRow = curStudent.schedule
#             stuScheduleSheet.update(f'E{row}:J{row}', [curRow])


    