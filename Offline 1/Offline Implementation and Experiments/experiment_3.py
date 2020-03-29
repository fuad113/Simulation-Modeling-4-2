"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
import matplotlib.pyplot as plt
import math
import lcgrand as lg


#status of the server IDLE or BUSY
BUSY=1
IDLE=0

#total simulation time
total_simulation_time=10000

# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k


    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

    def analyticalResults(self):

        l= self.lambd
        m= self.mu

        L= (l*l) / (m * (m-l))
        D= l / (m * (m-l))
        U= l/m

        print()
        print('Analytical Results:')
        print('MMk Average queue length: %lf' % (L))
        print('MMk Average customer delay in queue: %lf' % (D))
        print('MMk Time-average server utility: %lf' % (U))



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
        time_since_last_event = sim.now() - self.time_last_event
        self.time_last_event= sim.now()

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



def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k

    seed = 110
    mu = 8.0 / 60
    lambd= 5.0 / 60

    #k_max is th
    k_servers=4
    k_arr = [i for i in range(1, k_servers+1)]

    avglength = []
    avgdelay = []
    util = []


    for k in k_arr:

        sim = Simulator(seed)
        sim.configure(Params(lambd ,mu, k), States(k))
        sim.run()

        length, delay, utl = sim.getResults()
        sim.printResults()
        print()

        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)


    plt.figure(1)
    plt.subplot(311)
    plt.plot(k_arr, avglength)
    plt.xlabel('K')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(k_arr, avgdelay)
    plt.xlabel('K')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(k_arr, util)
    plt.xlabel('K')
    plt.ylabel('Util')

    plt.show()



def main():
    experiment3()


if __name__ == "__main__":
    main()