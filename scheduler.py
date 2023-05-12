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
        

def match(tutors, students):
    matching = dict()
    tutor = findNextTutor(tutors, matching)
    while (tutor != None):
        i = tutor.prefList.pop()
        student = students[i]
        if (not student.matched):
            addToMatching(tutor, i, matching, students)
        tutor = findNextTutor(tutors, matching)
        # elif (betterFit(tutor, student, matching)):
        #     removeFromMatching(student, matching)
        #     addToMatching(tutor, student, matching)
    return matching

def res():
    tutors, students = createData()
    # for tutor in tutors:
    #     print(tutor, [students[i].name for i in tutor.prefList])
    matching = match(tutors, students)
    print("\n")
    for tutor in matching:
        print(tutor, ":", matching[tutor])
    unmatchedStudents = set()
    for student in students:
        if (not student.matched): unmatchedStudents.add(student)
    print(f"\nthere are {len(unmatchedStudents)} unmatched students:", unmatchedStudents)
    unmatchedTutors = set()
    for tutor in tutors:
        if (not tutor in matching): unmatchedTutors.add(tutor)
    print(f"\nthere are {len(unmatchedTutors)} unmatched tutors:", unmatchedTutors)

res()