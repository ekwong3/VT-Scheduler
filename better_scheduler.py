import gspread
import copy
import csv
from students_tutors_classes import *
from students_tutors_list import *

# serviceAccount = gspread.service_account(filename = "credentials.json")
# sheet = serviceAccount.open("Test Tutoring Spreadsheet")

# tutors = sheet.worksheet("Tutor List").get_all_values()
# students = sheet.worksheet("Student List").get_all_values()

# Returns a set of Tutors with the attributes corresponding to each tutor's inputs
def getTutors(tutors):
    allTutors = set()
    for tutorInfo in tutors[1:]:
        training = tutorInfo[0]
        if training != "N":
            zoom, pwd, email, fName, lName = tutorInfo[1:6]
            numClasses, _, whichClasses = tutorInfo[8:11]
            times = tutorInfo[11:16]
            #firstName, lastName, email, sessions, classes, times, zoom, password
            tutor = Tutor(fName, lName, email, numClasses, whichClasses, times, zoom, pwd)
            allTutors.add(tutor)
    return allTutors

# Returns a set of Students with the attributes corresponding to each student's inputs
def getStudents(students):
    allStudents = set()
    for studentInfo in students[1:]:
        priorityL, priorityI, email = studentInfo[1:4]
        parent = ' '.join(studentInfo[5:7])
        fName, lName = studentInfo[8:10]
        prefClass, otherClass = studentInfo[12:14]
        times = studentInfo[14:19]
        #firstName, lastName, parent, email, class1, class2, times
        student = Student(fName, lName, parent, email, prefClass, 
                          otherClass, times, priorityL, priorityI)
        allStudents.add(student)   
    return allStudents

# Matches up students with tutors
def matchMake(students, tutors):
    bestMatch = [dict()]
    # print(students, tutors)
    perfectMatch = matchMakeHelper(students, tutors, dict(), bestMatch)
    return perfectMatch if perfectMatch != None else bestMatch[0]

def findHighestPrioStudent(students):
    booster = len(students)
    highestPrio = None
    bestScore = -5 * booster
    curOrder = booster + 1
    for student in students:
        pL = 2*booster if student.priorityLearning else 0
        pI = 2*booster if student.priorityIncome else 0
        score = pL + pI - student.placeInLine
        if (score > bestScore) or ((score == bestScore) and (student.placeInLine < curOrder)):
            highestPrio = student
            bestScore = score
            curOrder = student.placeInLine
    return highestPrio

def timeFit(student, tutor):
    times = set()
    for day in student.times:
        for time in student.times[day]:
            if (time != "") and (time in tutor.times[day]):
                times.add((day, time))
    return times

def subjectFit(student, tutor):
    subject = student.prefClass
    if subject == "Algebra 1":
        return subject in tutor.subjects
    else: 
        studentGrade = int(subject[0])
        if studentGrade in [1,2,3,4,5]:
            grade = "Elementary School "
        elif studentGrade in [6,7,8,9]:
            grade = "Middle School "
        fullSubject = grade + (subject.split()[-1])
        if fullSubject in tutor.subjects: 
            return True
    return False

def openTime(day, time, tutorSchedule):
    for session in tutorSchedule:
        if (day == session.day and session.time == time):
            return False
    return True

def tutorAvailable(fullTime, student, tutor, pairings):
    day, time = fullTime
    pairings[tutor] = pairings.get(tutor, set())
    tutorSchedule = pairings[tutor]
    if (tutor.numClasses == 0):
        # do check to see if the student can fit in with a current class
        for session in tutorSchedule:
            if ((student.prefClass == session.subject) and
                 (session.capacity > 0) and
                 (day == session.day and time == session.time)):
                session.students.add(student)
                session.capacity -= 1
                return True
        return False
    elif openTime(day, time, tutorSchedule):
        tutorSchedule.add(
            Session(student, tutor, student.prefClass, day, time, 1))
        tutor.numClasses -= 1
        return True
    return False

def canAdd(student, tutor, time, pairings):
    subjectFits = subjectFit(student, tutor)
    return subjectFits and tutorAvailable(time, student, tutor, pairings)

def betterPairing(pairings, bestMatch):
    oldCount = countStudents(bestMatch)
    newCount = countStudents(pairings)
    return newCount > oldCount

def countStudents(schedule):
    count = 0
    for tutor in schedule:
        for session in schedule[tutor]:
            count += len(session.students)
    return count

# Finds a pairing using backtracking
def matchMakeHelper(students, tutors, pairings, bestMatch):
    # print(len(bestMatch))
    if betterPairing(pairings, bestMatch[0]):
        bestMatch.pop()
        bestMatch.append(pairings)
    # print(countStudents(bestMatch[0]))
    if (students == set()):
        print("No unmatched students")
        return pairings
    else:
        # Finds the highest priority student
        student = findHighestPrioStudent(students)
        for tutor in tutors:
            times = timeFit(student, tutor)
            for time in times:
                # Legality check
                newStudents = copy.deepcopy(students)
                newPairings = copy.deepcopy(pairings)
                if canAdd(student, tutor, time, newPairings):
                    newStudents.remove(student)
                    possibleMatch = matchMakeHelper(newStudents, tutors, 
                                                    newPairings, bestMatch)
                    if possibleMatch != None:
                        return possibleMatch
        return None

def writeStudentSchedule(students, tutors):
    students, tutors = getStudents(students), getTutors(tutors)
    schedule = matchMake(students, tutors)
    curRow = 2
    # studentSchedule = sheet.worksheet("Student Schedule")
    # print(schedule)
    count = countStudents(schedule)
    print("total students:", count)

    masterSchedule = []
    for tutor in schedule:
        for session in schedule[tutor]:
            for student in session.students:
                tutor = session.tutor
                day, time = session.day, session.time
                subject = session.subject
                line = [student.email, student.parent, "", "", student.name, 
                        getDay(day) + " at " + time, subject, tutor.name, tutor.email, 
                        tutor.zoom, tutor.password]
                # studentSchedule.update(f'A{curRow}:K{curRow}', line)
                # line = (student.email + student.parent + "" + "" + student.name +
                #         day + " at " + time + subject + tutor.name + tutor.email + 
                #         tutor.zoom + tutor.password + "\n")
                masterSchedule.append(line)
                curRow += 1
    # with open("test_schedule.csv", "w") as file:
    #     writer = csv.writer(file)
    #     for row in masterSchedule:
    #         writer.writerow(row)