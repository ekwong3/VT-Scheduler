import gspread
import copy
import csv
from students_tutors_classes import *
from students_tutors_list import *

# serviceAccount = gspread.service_account(filename = "credentials.json")
# sheet = serviceAccount.open("Main 2023 Spring Tutoring Spreadsheet")

# tutors = sheet.worksheet("Tutor List").get_all_values()
# students = sheet.worksheet("Student List").get_all_values()

def mergePeople(left, right):
    res = []
    while (left != [] and right != []):
        pLeft = left[0]
        pRight = right[0]
        if (pLeft < pRight):
            res.append(left.pop(0))
        else:
            res.append(right.pop(0))
    if (left == []): res += right
    else: res += left
    return res
            
def sortOrder(people):
    length = len(people)
    if length > 1:
        middle = length//2
        left = sortOrder(people[:middle])
        right = sortOrder(people[middle:])
        return mergePeople(left, right)
    return people

# Returns a set of Tutors with the attributes corresponding to each tutor's inputs
def getTutors(tutors):
    allTutors = []
    # allTutors = set()
    for tutorInfo in tutors[1:]:
        training = tutorInfo[0]
        if training != "N":
            zoom, pwd, email, fName, lName = tutorInfo[1:6]
            numClasses, spc, whichClasses = tutorInfo[8:11]
            times = tutorInfo[11:16]
            #firstName, lastName, email, sessions, classes, times, zoom, password
            tutor = Tutor(fName, lName, email, numClasses, spc, whichClasses, times, zoom, pwd)
            allTutors.append(tutor)
            # allTutors.add(tutor)
    return sortOrder(allTutors)
    # return allTutors

# Returns a set of Students with the attributes corresponding to each student's inputs
def getStudents(students):
    # allStudents = []
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
        # allStudents.append(student)   
        allStudents.add(student)
    # return sortOrder(allStudents)
    return allStudents

# Matches up students with tutors
def matchMake(students, tutors):
    bestMatch = [dict()]
    numLeft = []
    # print(students, tutors)
    perfectMatch = matchMakeHelper(students, tutors, dict(), bestMatch, numLeft)
    return perfectMatch if perfectMatch != None else bestMatch[0]

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

def sessionFits(session, day, time, subject):
    return (day == session.day and time == session.time and 
            subject == session.subject and session.capacity > 0)

def timeOverlap(session, day, time):
    return (day == session.day) # change to be better!

def tutorAvailable(fullTime, student, tutor, pairings):
    day, time = fullTime
    pairings[tutor] = pairings.get(tutor, set())
    tutorSchedule = pairings[tutor]
    subject = student.prefClass
    for session in tutorSchedule: # add to an existing session
        if sessionFits(session, day, time, subject):
            session.students.add(student)
            session.capacity -= 1
            return True
        elif timeOverlap(session, day, time): 
            # time is in the schedule but class doesn't fit
            return False
    if (tutor.numClasses > 0): # know that the time doesn't overlap
        session = Session(student, tutor, subject, day, time)
        session.capacity -= 1
        tutorSchedule.add(session)
        tutor.numClasses -= 1
        return True
    return False

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

def mostlyDecreasing(L):
    prevNumber = None
    count = 0
    for n in L:
        if (prevNumber == None):
            prevNumber = n
        else:
            if (n >= prevNumber):
                count += 1
    return count <= (len(L) * 0.4)

def goodEnough(numLeft):
    if numLeft <= 25:
        return True
    return False
    # if len(numLeft) < 11:
    #     return False
    # startingNumber = numLeft[0]
    # lastTen = numLeft[-10:]
    # if not mostlyDecreasing(lastTen):
    #     return False
    # average = sum(lastTen) / 10
    # return average < 35 #(startingNumber / 4) # at least 80% students are matchedwr

# Finds a pairing using backtracking
def matchMakeHelper(students, tutors, pairings, bestMatch, numLeft):
    # numLeft.append(len(students))
    if betterPairing(pairings, bestMatch[0]):
        bestMatch.pop()
        bestMatch.append(pairings)
    print("students paired:", countStudents(bestMatch[0]), 
          "students left:", len(students))
    # print(pairings)
    if (students == set()):
        print("No unmatched students")
        return pairings
    elif goodEnough(len(students)):
        return bestMatch[0]
    else:
        # Finds the highest priority student
        for student in students:
            for tutor in tutors:
                if subjectFit(student, tutor):
                    times = timeFit(student, tutor) # set of times that work for both
                    for time in times:
                        # Legality check
                        newStudents = copy.deepcopy(students)
                        newPairings = copy.deepcopy(pairings)
                        if tutorAvailable(time, student, tutor, newPairings):
                            newStudents.remove(student)
                            possibleMatch = matchMakeHelper(newStudents, tutors, 
                                                            newPairings, bestMatch, 
                                                            numLeft)
                            if possibleMatch != None:
                                return possibleMatch
        return None

def createSchedules(schedule):
    studentSchedule, tutorSchedule = dict(), dict()
    for tutor in schedule:
        tutorSubjects = ", ".join(tutor.subjects)
        tutorInfo = [tutor.email, tutor.firstName, tutor.lastName, "", 
                     tutorSubjects, tutor.numClasses]
        for session in schedule[tutor]:
            studentNames = [s.name for s in session.students]
            tutorInfo.extend([' and '.join(studentNames), 
                              getDay(session.day) + " at " + session.time, 
                              session.subject])
            for student in session.students:
                tutor = session.tutor
                day, time = session.day, session.time
                subject = session.subject
                studentInfo = [student.email, student.parent, "", "", student.name, 
                               getDay(day) + " at " + time, subject, tutor.name, tutor.email, 
                               tutor.zoom, tutor.password]
                studentSchedule[student.name] = studentInfo
        tutorSchedule[tutor.name] = tutorInfo
    return studentSchedule, tutorSchedule

def writeSchedules(students, tutors):
    orderedStudents, orderedTutors = getStudents(students), getTutors(tutors)
    schedule = matchMake(orderedStudents, orderedTutors)
    # studentSchedule = sheet.worksheet("Student Schedule")
    # print(schedule)
    count = countStudents(schedule)
    print("total students:", count)

    studentDict, tutorDict = createSchedules(schedule)
    studentSchedule = []
    tutorSchedule = []
    for student in students:
        fullName = cleanup(' '.join(student[8:10]))
        if fullName in studentDict:
            studentSchedule.append(studentDict[fullName])
        else:
            parentName = cleanup(' '.join(student[5:7]))
            parentEmail = student[3]
            studentSchedule.append([parentEmail, parentName, "", "", fullName])
    for tutor in tutors:
        fullName = cleanup(' '.join(tutor[4:6]))
        if fullName in tutorDict:
            tutorSchedule.append(tutorDict[fullName])
        else:
            firstName = cleanup(tutor[4])
            lastName = cleanup(tutor[5])
            email = tutor[3]
            tutorSchedule.append([email, firstName, lastName])
    
    writeToFile = input("Write this to csv? y/n \n")
    if (writeToFile == "y"):
        writeToCsv(tutorSchedule, "tutor_schedule.csv")
        writeToCsv(studentSchedule, "student_schedule.csv")

def writeToCsv(schedule, fileName):
    with open(fileName, "w") as file:
        writer = csv.writer(file)
        for row in schedule:
            writer.writerow(row)