from summer_scheduler import *

def schedule2(tutors,students):
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
            tDict, sDict = fillIn(tDict, sDict)
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
    return tDict, sDict
  
t, s = schedule2(tutors, students)
c = '5th Grade Math'
b = sortTimesByDemand(s, c)

