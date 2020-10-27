import heapq
import random
import matplotlib.pyplot as plt
import math
import lcgrand as lg

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






#status of the server IDLE or BUSY
BUSY=1
IDLE=0

#total simulation time
total_simulation_time=10000


# States and statistical counters
class States:
    def __init__(self, k):
        # States
        self.queue = []
        #other variables
        self.time_last_event= 0.0
        self.k=k
        self.num_in_q = 0
        self.total_time_server_served = 0

        #an array of k servers and every server is IDLE initially
        self.server_array=[]
        self.area_server_status=[]
        for i in range(k):
            self.server_array.append(IDLE)
            self.area_server_status.append(0.0)

        self.total_time_of_delays =0.0
        self.area_num_in_q = 0.0


        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def update(self, sim, event):
        #update the statistical values

        #Compute time since last event, and update last-event-time- marker
        time_since_last_event = event.eventTime - self.time_last_event
        self.time_last_event= event.eventTime

        #Update area under number-in-queue function
        self.area_num_in_q += self.num_in_q * time_since_last_event

        #Update area under server-
        for i in range(self.k):
            self.area_server_status[i] += self.server_array[i] * time_since_last_event
            self.total_time_server_served += self.server_array[i] * time_since_last_event


    def finish(self, sim):
        if(self.served == 0):
            self.avgQdelay=0
        else:
            self.avgQdelay = self.total_time_of_delays / self.served

        self.avgQlength = self.area_num_in_q / sim.now()

        #util will be the mean of all servers util
        sum=0.0

        for i in range(self.k):
            self.area_server_status[i]=self.area_server_status[i] / sim.now()
            sum+=self.area_server_status[i]

        self.util = sum/self.k


    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('Experimental Results:')
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

# Write more functions if required

#expon function
def expon(rate):
    mean=float( 1 / rate )
    return  -mean * math.log(lg.lcgrand(1))


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
        #Beginning of the service. Server is waiting for an arrival
        l= sim.params.lambd
        first_arrival_time = self.eventTime + expon(l)

        #schedule the event in the simulator
        sim.scheduleEvent(ArrivalEvent(first_arrival_time, sim))

        #Scheduleing the exit event of the simulation
        sim.scheduleEvent(ExitEvent(total_simulation_time,sim))



class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        #exit event is scheduled in the start event already
        time_now= self.eventTime
        #print("This is the Exit Event at time: ", time_now)



class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim


    def process(self, sim):
        #schedule the next arrival
        time_next_event= sim.now() + expon(sim.params.lambd)
        sim.scheduleEvent(ArrivalEvent(time_next_event,sim))

        #check all the servers are busy or not.
        busy_check=0
        server_index=0

        for i in range(sim.params.k):
            if(sim.states.server_array[i] == BUSY):
                busy_check+=1
            else:
                busy_check=0
                server_index=i
                break

        #all servers are busy. So wait in the queue
        if(busy_check==sim.params.k):
            sim.states.num_in_q += 1
            sim.states.queue.append(sim.now())

        #got an IDLE server
        else:
            delay=0.0
            sim.states.total_time_of_delays+=delay

            #increment the number of customer served
            sim.states.served += 1
            sim.states.server_array[server_index]= BUSY

            #schedule a departure fot this arrival
            time= sim.now() + expon(sim.params.mu)
            sim.scheduleEvent(DepartureEvent(time,sim,server_index))


class DepartureEvent(Event):
    def __init__(self, eventTime, sim,server_no):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.server_no=server_no


    def process(self, sim):
        #check whether the queue is empty. If empty then make that particular server IDLE
        if(sim.states.num_in_q == 0):
            sim.states.server_array[self.server_no]=IDLE

        else:
            #decrease the number of people in queue
            sim.states.num_in_q -= 1

            #compute the delay
            delay= sim.now() - sim.states.queue[0]
            sim.states.total_time_of_delays += delay

            # remove the 1st customer from the waiting queue
            sim.states.queue.pop(0)

            #increment the num of customer served
            sim.states.served+=1

            #schedule the departure of the customer
            time=sim.now() + expon(sim.params.mu)
            sim.scheduleEvent(DepartureEvent(time,sim,self.server_no))


class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))
        lg.resetzrng()

    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
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

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)

    def printanalyticalResults(self):
        self.params.analyticalResults()



def jobShopModel():
    global numOfStations,numOfMachinesPerStations,interArrivalTimeforJobsMean,numOfJobTypes,jobProbabilities
    global numOfStationForEachJob,stationRouting,meanServiceTimeForEachStation

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

    interArrivalTimeforJobsMean = float(lines[2])

    numOfJobTypes = int (lines[3])
    jobProbabilities = lines[4].split()
    for i in range(numOfJobTypes):
        jobProbabilities[i] = float(jobProbabilities[i])

    numOfStationForEachJob = lines[5].split()
    for i in range(numOfJobTypes):
        numOfStationForEachJob[i] = int (numOfStationForEachJob[i])

    lineNumber=6

    for i in range(numOfJobTypes):
        #working of station routing
        tempJobStationRouting = lines[lineNumber].split()

        for j in range(numOfStationForEachJob[i]):
            tempJobStationRouting[j] = int(tempJobStationRouting[j])

        stationRouting[i] = tempJobStationRouting

        #working of mean service time for each station
        tempMeanServiceTimeForStations = lines[lineNumber+1].split()

        for j in range(numOfStationForEachJob[i]):
            tempMeanServiceTimeForStations[j] = float(tempMeanServiceTimeForStations[j])

        meanServiceTimeForEachStation[i] = tempMeanServiceTimeForStations
        lineNumber = lineNumber + 2

    print('number of stations: ', numOfStations)
    print('number of machines per station: ',numOfMachinesPerStations)
    print('inter arrival time for jobs: ',interArrivalTimeforJobsMean)
    print('number of job types: ',numOfJobTypes)
    print('job probabilities: ', jobProbabilities)
    print('number of station for each jon: ', numOfStationForEachJob)
    print('routing of the jobs: ',stationRouting)
    print('mean service time for each station: ', meanServiceTimeForEachStation)

def main():
    jobShopModel()


if __name__ == "__main__":
    main()


