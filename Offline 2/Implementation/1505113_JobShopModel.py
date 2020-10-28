import heapq
import random
import math
import lcgrand as lg
import numpy as np

#global variables for different parameters
numOfStations=0
numOfMachinesPerStations =[]
interArrivalTimeforJobsMean=0.0
numOfJobTypes=0
jobProbabilities=[]
numOfStationForEachJob =[]
#dictionary for keeping each job's station routing and mean service time for each station
stationRouting ={}
meanServiceTimeForEachStation ={}


#total simulation time
simulationHour = 8
simulationIteration = 30


#expon function
def expon(mean):
    return  -mean * math.log(lg.lcgrand(1))

#erlang function
def erlang(mean):
    ex1 = expon(mean/2)
    ex2 = expon(mean/2)
    return ex1 + ex2


# States and statistical counters
class States:
    def __init__(self):
        #---------------------------------------------------------------------------------------------------------------
        #queue for every station. so it will be a 2D queue
        self.queue =[]
        for i in range(numOfStations+1):
            stationOwnqueue =[]
            self.queue.append(stationOwnqueue)

        #busy machine counter. this array counts the number of busy machines of a station.
        self.numOfBusyMachines =[]
        for i in range(numOfStations+1):
            self.numOfBusyMachines.append(0)

        #serving counter. It counts every station's completed work number
        self.everyStationServed=[]
        for i in range(numOfStations+1):
            self.everyStationServed.append(0)
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        # total delay of queues of every station
        self.totalDelayInQueue = []
        for i in range(numOfStations+1):
            self.totalDelayInQueue.append(0.0)

        # average delay of queues of every station
        self.avgDelayInQueue =[]
        for i in range(numOfStations+1):
            self.avgDelayInQueue.append(0.0)

        # area num of every station queue.It will help to determine average queue length.
        self.areaNumInQueue = []
        for i in range(numOfStations+1):
            self.areaNumInQueue.append(0.0)

        # average queue length of every station's queue
        self.avgQueueLength = []
        for i in range(numOfStations+1):
            self.avgQueueLength.append(0.0)

        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #cuurent jobs in the system. how many jobs are oning in the system right now.
        self.numOfOngoingJobsInTheSystem = 0

        #job counter. How many works have been done of each jobs
        self.jobCounter=[]
        for i in range(numOfJobTypes+1):
            self.jobCounter.append(0)

        #counting on average how many jobs were in the system
        self.avgNumOfJobsInSystem = 0.0

        #average delay of every job types
        self.avgDelayPerJob=[]
        for i in range(numOfJobTypes+1):
            self.avgDelayPerJob.append(0.0)

        # total average delay
        self.avgTotalJobDelay = 0.0

        #---------------------------------------------------------------------------------------------------------------

        # time of the last event
        self.time_last_event = 0.0

    def update(self, sim, event):
        #update the statistical values

        #Compute time since last event, and update last-event-time- marker
        time_since_last_event = event.eventTime - self.time_last_event
        self.time_last_event= event.eventTime

        #updating the average queue length
        for i in range(1 , numOfStations+1 , 1):
            self.areaNumInQueue[i] += len(self.queue[i]) * time_since_last_event

        self.avgNumOfJobsInSystem += self.numOfOngoingJobsInTheSystem* time_since_last_event


    def finish(self, sim):
        #---------------------------------------------------------------------------------------------------------------
        #calculating average delay in each queue
        for i in range(1, numOfStations+1 , 1):
            if(self.everyStationServed[i] != 0):
                self.avgDelayInQueue[i] = self.totalDelayInQueue[i]/self.everyStationServed[i]

        #calculating average length of queue
        for i in range(1, numOfStations+1 , 1):
            self.avgQueueLength[i] = self.areaNumInQueue[i] / sim.now()
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #average dealay for each of the jobs
        for i in range(1, numOfJobTypes+1 ,1):
            if (self.jobCounter[i] != 0):
                self.avgDelayPerJob[i] = self.avgDelayPerJob[i] / self.jobCounter[i]

        #calculating overall total delays
        for i in range(1, numOfJobTypes+1 , 1):
            self.avgTotalJobDelay += self.avgDelayPerJob[i] * jobProbabilities[i]

        #calculating average num of jobs done in the system
        self.avgNumOfJobsInSystem = self.avgNumOfJobsInSystem / sim.now()
        #---------------------------------------------------------------------------------------------------------------

        return self.avgDelayInQueue,self.avgQueueLength,self.avgDelayPerJob,self.avgTotalJobDelay,self.avgNumOfJobsInSystem


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        #schedule the 1st arrival in the job shop
        arrivalTime = self.eventTime + expon(interArrivalTimeforJobsMean)

        #now randomly choosing one job from job types array
        jobTypearray =[]
        for i in range(numOfJobTypes):
            jobTypearray.append(i+1)

        tempJobProb =[]
        for i in range(len(jobProbabilities)-1):
            tempJobProb.append(jobProbabilities[i+1])

        tempjobType = np.random.choice(jobTypearray, 1, tempJobProb)
        jobType = tempjobType[0]

        #find out the 1st station of that job type
        firstStationOfTheJob = stationRouting[jobType][1]

        #schedule the first arrival event
        self.sim.scheduleEvent(ArrivalEvent(arrivalTime, self.sim, jobType, firstStationOfTheJob))

        #schedule the Exit event here
        self.sim.scheduleEvent(ExitEvent(simulationHour,self.sim))

class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        #The exit event is processed in the arrival event
        print("The simulation is end")


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim, jobType, stationNo):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.jobType =jobType
        self.stationNo =stationNo

    def process(self, sim):
        #schedule the next arrival. The next arrival will happen when the current arrival is at
        #its 1st station
        if(self.stationNo == stationRouting[self.jobType][1]):
            arrivalTime = sim.now() + expon(interArrivalTimeforJobsMean)
            # now randomly choosing one job from job types array
            jobTypearray = []
            for i in range(numOfJobTypes):
                jobTypearray.append(i+1)

            tempJobProb = []
            for i in range(len(jobProbabilities) - 1):
                tempJobProb.append(jobProbabilities[i + 1])

            tempjobNo = np.random.choice(jobTypearray, 1, tempJobProb)
            jobType = tempjobNo[0]

            # find out the 1st station of that job type
            firstStationOfTheJob = stationRouting[jobType][1]

            # schedule the first arrival event
            sim.scheduleEvent(ArrivalEvent(arrivalTime, sim, jobType, firstStationOfTheJob))

            #now increase te job counter because of the current job
            sim.states.jobCounter[self.jobType] += 1
            sim.states.numOfOngoingJobsInTheSystem +=1

        #processing the current arrival event
        #checking if every machine of the station is busy or not. If every machine of
        #a station is busy then push the job in the queue of that station.
        if(sim.states.numOfBusyMachines[self.stationNo] == numOfMachinesPerStations[self.stationNo]):
            sim.states.queue[self.stationNo].append(self)
        else:
            #increase the number of busy machine
            sim.states.numOfBusyMachines[self.stationNo] += 1

            #schedule the departure of this job from this station
            #findout the station index number for the job routing
            jobRoutingStations = stationRouting[self.jobType]
            index =1
            for i in range(1, len(jobRoutingStations)+1 , 1):
                if(jobRoutingStations[i] == self.stationNo):
                    index = i
                    break

            temp = erlang(meanServiceTimeForEachStation[self.jobType][index])
            departureTime = sim.now() + temp
            sim.scheduleEvent(DepartureEvent(departureTime , sim , self.jobType , self.stationNo ))



class DepartureEvent(Event):
    def __init__(self, eventTime, sim , jobType , stationNo):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.jobType = jobType
        self.stationNo = stationNo


    def process(self, sim):
        #first increase the served counter for the station who is performing this event
        sim.states.everyStationServed[self.stationNo] += 1

        #now check is this the last station of the job. if it is not the last station, then
        #schedule for the next station
        lastStationOfTheJob = stationRouting[self.jobType][-1]

        if(lastStationOfTheJob != self.stationNo):
            #job is not finished. so schedule for the next station.
            #findout the next station index number for the job routing
            jobRoutingStations = stationRouting[self.jobType]
            index =1
            for i in range(1,len(jobRoutingStations)+1 , 1):
                if(jobRoutingStations[i] == self.stationNo):
                    index = i
                    break

            #finding the next station
            nextStation = stationRouting[self.jobType][index+1]

            #schedule the arrival event for the next station
            arrivalTime = sim.now()
            sim.scheduleEvent(ArrivalEvent(arrivalTime , sim , self.jobType , nextStation))
        else:
            #the job is done. so it can be patched out of the system
            sim.states.numOfOngoingJobsInTheSystem -= 1

        #now check the queue of the station.
        if(len(sim.states.queue[self.stationNo]) == 0):
            #no one is the queue. SO decreament 1 of the this station's busy counter.
            sim.states.numOfBusyMachines[self.stationNo] -= 1
        else:
            #someone is in the queue. so give that job a service and fix a departure schedule for that work.
            #the waiting arrival event in the queue
            waitingItem = sim.states.queue[self.stationNo].pop(0)

            #counting the dealay
            timeDelayed =  sim.now() - waitingItem.eventTime

            #add the dealay to the stations total delay array
            sim.states.totalDelayInQueue[self.stationNo] += timeDelayed

            #add the delay to the job delay array
            sim.states.avgDelayPerJob[waitingItem.jobType] += timeDelayed

            #now schedule a departure for this waiting item
            #findout the station index number for the job routing
            jobRoutingStations = stationRouting[waitingItem.jobType]
            index =1
            for i in range(1, len(jobRoutingStations)+1 ,1):
                if(jobRoutingStations[i] == self.stationNo):
                    index = i
                    break

            #schedule the departure
            temp = erlang(meanServiceTimeForEachStation[waitingItem.jobType][index])
            departureTime = sim.now() + temp
            sim.scheduleEvent(DepartureEvent(departureTime , sim , waitingItem.jobType , self.stationNo ))


class Simulator:
    def __init__(self):
        self.eventQ = []
        self.simclock = 0
        self.states = States()

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))
        lg.resetzrng()


    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'EXIT':
                #print(event.eventTime, 'Event', event)
                self.simclock = event.eventTime
                event.process(self)
                print()
                break

            if self.states != None:
                self.states.update(self, event)

            #print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)

        return self.states.finish(self)



def jobShopModel():
    global numOfStations,numOfMachinesPerStations,interArrivalTimeforJobsMean,numOfJobTypes,jobProbabilities
    global numOfStationForEachJob,stationRouting,meanServiceTimeForEachStation

    #-------------------------------------------------------------------------------------------------------------------
    # first read the input file and fillup different variables
    f= open("jobshop_input.txt","r")
    lines = f.readlines()
    f.close()

    #remove the "\n" from every line
    for i in range(len(lines)):
        if(lines[i].endswith("\n")):
            lines[i] = lines[i].rstrip("\n")

    #updating the values of various variables
    numOfStations = int (lines[0])

    numOfMachinesPerStations = lines[1].split()
    for i in range(numOfStations):
        numOfMachinesPerStations[i] = int(numOfMachinesPerStations[i])

    numOfMachinesPerStations.insert(0,0)

    interArrivalTimeforJobsMean = float(lines[2])

    numOfJobTypes = int (lines[3])

    jobProbabilities = lines[4].split()
    for i in range(numOfJobTypes):
        jobProbabilities[i] = float(jobProbabilities[i])
    jobProbabilities.insert(0,0)

    numOfStationForEachJob = lines[5].split()
    for i in range(numOfJobTypes):
        numOfStationForEachJob[i] = int (numOfStationForEachJob[i])
    numOfStationForEachJob.insert(0,0)

    lineNumber=6

    for i in range(1, numOfJobTypes+1 ,1):
        #working of station routing
        tempJobStationRouting = lines[lineNumber].split()

        for j in range(len(tempJobStationRouting)):
            tempJobStationRouting[j] = int(tempJobStationRouting[j])

        tempJobStationRouting.insert(0,0)
        stationRouting[i] = tempJobStationRouting

        #working of mean service time for each station
        tempMeanServiceTimeForStations = lines[lineNumber+1].split()

        for j in range(len(tempMeanServiceTimeForStations)):
            tempMeanServiceTimeForStations[j] = float(tempMeanServiceTimeForStations[j])
        tempMeanServiceTimeForStations.insert(0,0)
        meanServiceTimeForEachStation[i] = tempMeanServiceTimeForStations
        lineNumber = lineNumber + 2

    print('number of stations: ', numOfStations)
    print('number of machines per station: ',numOfMachinesPerStations)
    print('inter arrival time for jobs: ',interArrivalTimeforJobsMean)
    print('number of job types: ',numOfJobTypes)
    print('job probabilities: ', jobProbabilities)
    print('number of station for each job: ', numOfStationForEachJob)
    print('routing of the jobs: ',stationRouting)
    print('mean service time for each station: ', meanServiceTimeForEachStation)
    #-------------------------------------------------------------------------------------------------------------------

    #main calculation work of the simulation

    #-------------------------------------------------------------------------------------------------------------------
    #declaring the variables to hold the metrics from simulation
    avgDelayInQueue = []
    avgQueueLength = []
    for i in range(numOfStations):
        avgDelayInQueue.append(0.0)
        avgQueueLength.append(0.0)

    avgDelayPerJob = []
    for i in range(numOfJobTypes):
        avgDelayPerJob.append(0.0)

    avgTotalJobDelay = 0.0
    avgNumOfJobsInSystem = 0.0
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------
    #running the simulation

    sim = Simulator()
    avgDelayInQueue,avgQueueLength,avgDelayPerJob,avgTotalJobDelay,avgNumOfJobsInSystem = sim.run()

def main():
    jobShopModel()


if __name__ == "__main__":
    main()


