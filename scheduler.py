import csv
from students_tutors_classes import *

def createData():
    tutors = []
    students = []
    with open("data/tutors.csv") as csvfile:
        tutorList = csv.reader(csvfile)
        for tutorInfo in tutorList:
            if tutorInfo[0] == 'Training': continue
            tutor = Tutor(*tutorInfo)
            if tutor in tutors:
                tutors.remove(tutor)
            tutors.append(tutor)
    with open("data/students.csv") as csvfile:
        studentList = csv.reader(csvfile)
        for studentInfo in studentList:
            if studentInfo[0] == "Email address": continue
            student = Student(*studentInfo)
            if student in students:
                students.remove(student)
            students.append(student)
    for tutor in tutors:
        tutor.makePrefs(students)
    return (tutors, students)

def findNextTutor(tutors, matching):
    for tutor in tutors:
        if (tutor.prefList != [] and not tutor.full): return tutor
    return None

def addToMatching(tutor, index, matching, students):
    student = students[index]
    times = (tutor.times & student.times)
    if (not tutor in matching):
        time = times.pop()
        session = Session(tutor, student.subject, tutor.numStudents, time)
        session.add(index, students)
        matching[tutor] = [session]
    else:
        teachingTimes = set()
        for session in matching[tutor]:
            teachingTimes.add(session.time)
            if session.canAdd(student):
                session.add(index, students)
                return
        time = None
        if (len(matching[tutor]) < tutor.numSessions):
            while (time in teachingTimes and times != set()):
                time = times.pop()
            if time != None:
                session = Session(tutor, student.subject, tutor.numStudents, time)
                session.add(index, students)
                matching[tutor].append(session)

def removeFromMatching(student, matching):
    for session in matching[student.tutor]:
        if student in session.students:
            session.remove(student)
            session.capacity += 1
            if (session.students == []):
                matching[student.tutor].remove(session)
            return

def betterFit(tutor, student, matching):
    oldTutor = student.tutor
    if (not tutor in matching and len(matching[oldTutor]) > 1): return True
    return False


def match(tutors, students):
    matching = dict()
    tutor = findNextTutor(tutors, matching)
    while (tutor != None):
        # print(tutor, tutor.prefList)
        i = tutor.prefList.pop()
        student = students[i]
        if (not student.matched):
            addToMatching(tutor, i, matching, students)
        elif (betterFit(tutor, student, matching)):
            removeFromMatching(student, matching)
            addToMatching(tutor, student, matching)
        tutor = findNextTutor(tutors, matching)
    return matching

def report(tutors, students, matching):
    print("")
    for tutor in matching:
        print(tutor, ":", matching[tutor])

    unmatchedStudents = []
    subjects = dict()
    for student in students:
        if (not student.matched):
            unmatchedStudents.append(student)
            subjects[student.subject] = subjects.get(student.subject, []) + [student]
    print(f"\nthere are {len(unmatchedStudents)} unmatched students:", unmatchedStudents)
    print("\nTheir subjects are", subjects)

    unmatchedTutors = []
    for tutor in tutors:
        if (not tutor in matching): unmatchedTutors.append(tutor)
    print(f"\nthere are {len(unmatchedTutors)} unmatched tutors:", unmatchedTutors)

def getTime(time):
    res = ""
    while (time[0].isdigit()):
        res += time[0]
        time = time[1:]
    res += "-" + str((int(res) + 1) % 12)
    res += time
    return res

def getRow(tutor, matching):
    first, last = tutor.name.split()[0], tutor.name.split()[-1]
    res = [tutor.email, first, last, "", tutor.subjects]
    if (not tutor in matching):
        return res + [str(tutor.numSessions)]
    else: 
        res += [str(tutor.numSessions - len(matching[tutor]))]
    for session in matching[tutor]:
        students = [student.name for student in session.students]
        time = getTime(session.time)
        res += [", ".join(students), time, session.subject]
    return res

def getSchedule():
    tutors, students = createData()
    # for tutor in tutors:
    #     print(tutor, [students[i].name for i in tutor.prefList], "\n")
    matching = match(tutors, students)
    # report(tutors, students, matching)
    
    with open("data/schedule.csv", "w") as csvfile:
        scheduleWriter = csv.writer(csvfile, delimiter = ",")
        scheduleWriter.writerow(["Email", "First Name", "Last Name", "Send Filter", "Subject", 
            "Classes Left", "Class 1", "Time 1", "Subject 1", "Class 2", "Time 2", "Subject 2"])
        for tutor in tutors:
            scheduleWriter.writerow(getRow(tutor, matching))

getSchedule()