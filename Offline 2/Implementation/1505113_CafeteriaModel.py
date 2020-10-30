import heapq
import random
import math
import lcgrand as lg
import numpy as np

#declaring variables
groupSizes = [1 , 2 , 3 , 4]
groupSizeProbabilities =[0.5 , 0.3 , 0.1 , 0.1]

#inter arrival time of the groups. this value is given in seconds.It is a mean.
interArrivalTimeBetweenGroups = 30
#simulation Duration is 90 Minutes. So it is converted into seconds
simulationDuration = 90*60

counters = ["hotfood" , "sandwich" , "drinks" ]
NoOfCustomerType =3
customerType = [1,2,3]
customerTypewiseRouting = {
    "1" : ["hotfood" , "drinks" , "cash"],
    "2" : ["sandwich" , "drinks" , "cash"],
    "3" : ["drinks" , "cash"]
}
cutomerTypeProbabilities = [0.80 , 0.15 , 0.05]


counterSTMap = {
    "hotfood" : [50 , 120],
    "sandwich" : [60 , 180],
    "drinks" : [5 , 20]
}

counterACTMap = {
    "hotfood" : [20 , 40],
    "sandwich" : [5 , 15],
    "drinks" : [5 , 10]
}

employeeCounter = {}

groupID = 0

#a map for controlling the new arrival in the arrival event
arrivalMap = {}

#expon function
def expon(mean):
    return  -mean * math.log(lg.lcgrand(1))


# States and statistical counters
class States:
    def __init__(self):
        #defining various parameters to calculating various metrics

        #---------------------------------------------------------------------------------------------------------------
        #queue for various counters
        #There will be only 1 queue for hot food and sandwich.
        #No queue for drinks
        #No. of queue for the cash counter depends on the num of cashier

        hotfoodQueue = []
        sandwichQueue =[]
        #taking drinks queue for avoiding complexity
        drinksQueue=[]
        #cash counter queue calculation
        cashCounterEmployeeNo = employeeCounter["cash"]
        cashQueue=[]

        for i in range(cashCounterEmployeeNo):
            tempQueue =[]
            cashQueue.append(tempQueue)

        #Now create a map for tracking various types of queue
        self.queue={
            "hotfood" : [hotfoodQueue],
            "sandwich" : [sandwichQueue],
            "drinks" : [drinksQueue],
            "cash" : [cashQueue]
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #How many servers/employee at each station available
        hotfoodServers = employeeCounter["hotfood"]
        sandwichServers = employeeCounter["sandwich"]
        drinksServers = np.inf
        cashServers = employeeCounter["cash"]

        self.serverAvailable = {
            "hotfood" : hotfoodServers,
            "sandwich" : sandwichServers,
            "drinks" : drinksServers,
            "cash" : cashServers
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #special work for the cash counter.
        #because there can be more than 1 queue in the cash counter
        self.cashServer =[]
        for i in range(cashServers):
            self.cashServer.append(0)
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #avg and maximum delay for each counter
        self.avgQDelay = {
            "hotfood" : 0.0,
            "sandwich" : 0.0,
            "cash" : 0.0
        }

        self.maxQDelay = {
            "hotfood": 0.0,
            "sandwich": 0.0,
            "cash": 0.0
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        self.overallAvgDelay =0.0
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #avg and maximum queue length for each counter
        self.avgQLength = {
            "hotfood" : 0.0,
            "sandwich" : 0.0,
            "cash" : 0.0
        }

        self.maxQLength = {
            "hotfood": 0.0,
            "sandwich": 0.0,
            "cash": 0.0
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #avg and maximum delay for various types(here 3) of customers
        self.avgCustomerTypewiseDelay ={
            "1" : 0.0,
            "2" : 0.0,
            "3" : 0.0
        }

        self.maxCustomerTypewiseDelay = {
            "1": 0.0,
            "2": 0.0,
            "3": 0.0
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #which counter served how many customers
        self.customerServed ={
            "hotfood" : 0,
            "sandwich" : 0,
            "drinks" : 0,
            "cash" : 0
        }

        #which counter served how many customers typewise
        self.customerServedTypeWise = {
            "1" : 0,
            "2" : 0,
            "3" : 0
        }
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        self.time_last_event = 0.0
        self.currentCustomersIntheSystem =0
        self.maxCustomerInTheSystem =0
        self.avgCustomerInTheSystem =0
        #---------------------------------------------------------------------------------------------------------------


    def update(self, sim, event):
        #update the statistical values

        #Compute time since last event, and update last-event-time- marker
        time_since_last_event = event.eventTime - self.time_last_event
        self.time_last_event= event.eventTime

        #update the value of average queue length

        for key in self.avgQLength:
            numOfQueues = len(self.queue[key])
            qCounter =0
            for i in range(len(self.queue[key])):
                currentQueueLength = len(self.queue[key][i])
                qCounter += currentQueueLength
                self.maxQLength[key] = max( self.maxQLength[key] , currentQueueLength )
            self.avgQLength[key] += (qCounter/numOfQueues) * time_since_last_event


        #update the customer numbers in the system
        self.avgCustomerInTheSystem += self.currentCustomersIntheSystem * time_since_last_event
        self.maxCustomerInTheSystem = max(self.maxCustomerInTheSystem , self.currentCustomersIntheSystem)


    def finish(self, sim):
        #---------------------------------------------------------------------------------------------------------------
        #Calculation for the Queues
        #calculation of average queue length

        for key in self.avgQLength:
            self.avgQLength[key] /= sim.now()

        #calculation for the avg queue delay
        for key in self.avgQDelay:
            #division by 60 is for conversion to per minutes
            if(self.customerServed[key] != 0):
                self.avgQDelay[key] =  (self.avgQDelay[key]/self.customerServed[key]) / 60

        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #calculation for the customer types

        for i in range (NoOfCustomerType):

            key = str(i+1)
            if(self.customerServedTypeWise[key] != 0):
                self.avgCustomerTypewiseDelay[key] /= self.customerServedTypeWise[key]
            # division by 60 is for conversion to per minutes
            self.avgCustomerTypewiseDelay[key] /= 60
            self.avgCustomerTypewiseDelay[key] = round(self.avgCustomerTypewiseDelay[key] , 3 )
            self.overallAvgDelay += self.avgCustomerTypewiseDelay[key] * cutomerTypeProbabilities[i]

        #---------------------------------------------------------------------------------------------------------------

        #average customer in the system
        self.avgCustomerInTheSystem = self.avgCustomerInTheSystem / sim.now()

        for key in self.maxCustomerTypewiseDelay:
            # division by 60 is for conversion to per minutes
            self.maxCustomerTypewiseDelay[key] /= 60

        #---------------------------------------------------------------------------------------------------------------
        #rounding each values to precision 3
        for key in self.avgQLength:
            self.avgQLength[key] = round(self.avgQLength[key], 3 )

        for key in self.avgQDelay:
            self.avgQDelay[key] = round(self.avgQDelay[key], 3)

        self.overallAvgDelay = round(self.overallAvgDelay, 3)

        self.avgCustomerInTheSystem = round( self.avgCustomerInTheSystem , 3)

        for key in self.maxCustomerTypewiseDelay:
            self.maxCustomerTypewiseDelay[key] = round(self.maxCustomerTypewiseDelay[key] , 3)

        for key in self.maxQLength:
            self.maxQLength[key] = round( self.maxQLength[key] , 3 )

        for key in self.maxQDelay:
            self.maxQDelay[key] = round(self.maxQDelay[key] , 3 )

        #---------------------------------------------------------------------------------------------------------------

    def results(self):
        #print all the results

        print("Average No. of Customers in the System: ", self.avgCustomerInTheSystem)

        print("Max No. of Customers in the System: ", self.maxCustomerInTheSystem)

        print("Total Customer served: ", self.customerServed["cash"])

        print("\n\n")

        print("Average Queue Length of Every Counter")
        print(self.avgQLength)

        print("Max Queue Length of Every Counter")
        print(self.maxQLength)

        print("\n")

        print("Average Delay in Oueue of Every Counter")
        print(self.avgQDelay)

        print("Max Delay in Oueue of Every Counter")
        print(self.maxQDelay)

        print("\n")

        print("Average Delay for Each Type of Customers")
        print(self.avgCustomerTypewiseDelay)
        print("\n")

        print("Max Delay for Each Type of Customers")
        print(self.maxCustomerTypewiseDelay)

        print("Overall Average Delay: " , self.overallAvgDelay)


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType

    #this is for the comparion on the heap.
    def __lt__(self, other):
        return True


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        global groupID

        #creating the first arrival
        arrivalTime = sim.now() + expon(interArrivalTimeBetweenGroups)
        #assigning this group a group ID
        groupID+=1
        #determining the group size of th customer
        groupSize = np.random.choice(groupSizes, p=groupSizeProbabilities)


        #now processing each customer of the group
        for i in range(groupSize):
            #findout which customer type he/she is
            tempCustomerType = np.random.choice(customerType , p=cutomerTypeProbabilities)
            #increase te counter of that type of customer by 1
            sim.states.customerServedTypeWise[str(tempCustomerType)] += 1
            #find the first counter name of this type of customer
            firstCounter = customerTypewiseRouting[str(tempCustomerType)][0]
            #now create an arrival event for this customer
            sim.scheduleEvent(ArrivalEvent( arrivalTime ,sim , groupID ,tempCustomerType ,firstCounter ,0))

        #schedule the exit event of the simulation
        sim.scheduleEvent(ExitEvent(simulationDuration,sim))


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        #The exit event is processed in the arrival event
        print("The simulation is end")


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim , groupID , customerType , currentCounter , queueNo):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.groupID = groupID
        self.customerType = customerType
        self.currentCounter = currentCounter
        self.queueNo = queueNo


    def process(self, sim):
        #---------------------------------------------------------------------------------------------------------------
        #if the customer is in the 1st counter of his/her route,then increament the Num of customers
        #in the system
        tempfirstcounter = customerTypewiseRouting[str(self.customerType)][0]
        firstCounterFlag = False

        if(tempfirstcounter == self.currentCounter):
            #then it is the first counter for the new customer.
            #increase the current number of people in the system
            sim.states.currentCustomersIntheSystem+=1
            firstCounterFlag =True

        #---------------------------------------------------------------------------------------------------------------


        #---------------------------------------------------------------------------------------------------------------
        #Schedule the arrival of the next group
        if( self.groupID not in arrivalMap and firstCounterFlag==True ):
            #mark on going processed group true to avoid too many arrival
            arrivalMap[self.groupID] = True

            #now create new arrival
            arrivalTime = self.eventTime + expon(interArrivalTimeBetweenGroups)
            # assigning this group a group ID
            newgroupID = self.groupID + 1
            # determining the group size of th customer
            groupSize = np.random.choice(groupSizes, p=groupSizeProbabilities)

            # now processing each customer of the group
            for i in range(groupSize):
                # findout which customer type he/she is
                tempCustomerType = np.random.choice(customerType, p=cutomerTypeProbabilities)
                # increase te counter of that type of customer by 1
                sim.states.customerServedTypeWise[str(tempCustomerType)] += 1
                # find the first counter name of this type of customer
                firstCounter = customerTypewiseRouting[str(tempCustomerType)][0]
                # now create an arrival event for this customer
                sim.scheduleEvent(ArrivalEvent(arrivalTime, sim, newgroupID, tempCustomerType, firstCounter, 0))
        #---------------------------------------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------------------------------------
        #Process the onging arrival event
        #counters are free. so customer will get the service. No standing in queue
        #the main target is to create the departure for this arrival
        if( sim.states.serverAvailable[self.currentCounter] > 0):
            #that is atleast 1 employee is available to serve the customer
            sim.states.serverAvailable[self.currentCounter] -=1

            #now figure out the service time of the counters
            #normal food counter, use ST
            #for cash counter use ACT
            serviceTime = 0

            if(self.currentCounter == "cash"):
                for key in counterACTMap:
                    if (key in customerTypewiseRouting[str(self.customerType)]):
                        temp = np.random.uniform( counterACTMap[key][0] , counterACTMap[key][1] )
                        serviceTime += temp
            else:
                serviceTime += np.random.uniform(counterSTMap[self.currentCounter][0] , counterSTMap[self.currentCounter][1])

            #schedule the departure time
            departtime = self.eventTime + serviceTime

            #now determine the queue
            #for food counters queue index will be always 0
            #but for cash counter there can be multiple queue
            queueNo =0

            noOfQueueInCashServer = len(sim.states.cashServer)

            if( self.currentCounter == "cash" ):
                for i in range(noOfQueueInCashServer):
                    if(sim.states.cashServer[i] == 0):
                        sim.states.cashServer[i] =1
                        queueNo = i

            #increament the no of customer served in the counter
            sim.states.customerServed[self.currentCounter] +=1

            #schedule the departure event
            sim.scheduleEvent(DepartureEvent(departtime , sim , self.groupID , self.customerType ,
                                             self.currentCounter , queueNo ))

        else:
            #counter is busy. so customer have to stand in queue
            #for the cash counter there will be multiple queues
            #find the shortest queue to stant

            queueNo = 0
            min =np.inf
            nofqueueInCounter = len(sim.states.queue[self.currentCounter])

            for i in range(nofqueueInCounter):
                queuelen = len(sim.states.queue[self.currentCounter][i])
                if(queuelen < min):
                    min = queuelen
                    queueNo = i

            self.queueNo = queueNo

            #append to the counter queue
            sim.states.queue[self.currentCounter][queueNo].append(self)

        #---------------------------------------------------------------------------------------------------------------



class DepartureEvent(Event):
    def __init__(self, eventTime, sim , groupID , customerType , currentCounter , queueNo ):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.groupID = groupID
        self.customerType = customerType
        self.currentCounter = currentCounter
        self.queueNo = queueNo


    def process(self, sim):
        None


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

        self.states.finish(self)
        self.states.results()




def cafeteriaModel(index):
    global employeeCounter , counterSTMap , counterACTMap
    #this is a list of employee variations.How many possible ways there will be employees in
    #each counter

    employeeVariations = {
        "0": [1 , 1 , 2],
        "1": [1 , 1 , 3],
        "2": [2 , 1 , 2],
        "3": [1 , 2 , 2],
        "4": [2 , 2 , 2],
        "5": [2 , 1 , 3],
        "6": [1 , 2 , 3],
        "7": [2 , 2 , 3]
    }

    hotfoodEmployeeNo = employeeVariations[str(index)][0]
    sandwichEmployeeNo = employeeVariations[str(index)][1]
    cashEmployeeNo = employeeVariations[str(index)][2]

    employeeCounter = {
        "hotfood" : hotfoodEmployeeNo ,
        "sandwich" : sandwichEmployeeNo,
        "cash" : cashEmployeeNo,
    }

    # -------------------------------------------------------------------------------------------------------------------
    # now update the ST map according to the employee counter
    # for hot food
    prevLowBoundST = counterSTMap["hotfood"][0]
    prevLowHigherST = counterSTMap["hotfood"][1]

    newLowBoundST = prevLowBoundST / hotfoodEmployeeNo
    newHighBoundST = prevLowHigherST / hotfoodEmployeeNo

    counterSTMap["hotfood"][0] = newLowBoundST
    counterSTMap["hotfood"][1] = newHighBoundST

    # for sandwich
    prevLowBoundST = counterSTMap["sandwich"][0]
    prevLowHigherST = counterSTMap["sandwich"][1]

    newLowBoundST = prevLowBoundST / sandwichEmployeeNo
    newHighBoundST = prevLowHigherST / sandwichEmployeeNo

    counterSTMap["sandwich"][0] = newLowBoundST
    counterSTMap["sandwich"][1] = newHighBoundST
    # -------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------------
    # now update the ACT map according to the employee counter
    # for hot food
    prevLowBoundST = counterACTMap["hotfood"][0]
    prevLowHigherST = counterACTMap["hotfood"][1]

    newLowBoundST = prevLowBoundST / hotfoodEmployeeNo
    newHighBoundST = prevLowHigherST / hotfoodEmployeeNo

    counterACTMap["hotfood"][0] = newLowBoundST
    counterACTMap["hotfood"][1] = newHighBoundST

    # for sandwich
    prevLowBoundST = counterACTMap["sandwich"][0]
    prevLowHigherST = counterACTMap["sandwich"][1]

    newLowBoundST = prevLowBoundST / sandwichEmployeeNo
    newHighBoundST = prevLowHigherST / sandwichEmployeeNo

    counterACTMap["sandwich"][0] = newLowBoundST
    counterACTMap["sandwich"][1] = newHighBoundST
    # -------------------------------------------------------------------------------------------------------------------

    print("Employee Counters:",employeeCounter)
    print("ST map: ", counterSTMap)
    print("ACT map: " ,counterACTMap)

    #-------------------------------------------------------------------------------------------------------------------
    seed = 1
    np.random.seed(seed)
    #run the simulator
    sim =Simulator()
    sim.run()


def main():
    #give the index of the employee variation map to get the employee counter
    cafeteriaModel(0)


if __name__ == "__main__":
    main()


