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
counterRouting = {
    "1" : ["hotfood" , "drinks" , "cash"],
    "2" : ["sandwich" , "drinks" , "cash"],
    "3" : ["drinks" , "cash"]
}

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



#expon function
def expon(mean):
    return  -mean * math.log(lg.lcgrand(1))


# States and statistical counters
class States:
    def __init__(self):
        None

    def update(self, sim, event):
        None


    def finish(self, sim):
        None


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
        None

class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        #The exit event is processed in the arrival event
        print("The simulation is end")


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim


    def process(self, sim):
        None



class DepartureEvent(Event):
    def __init__(self, eventTime, sim ):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim


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

        return self.states.finish(self)



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


def main():
    #give the index of the employee variation map to get the employee counter
    cafeteriaModel(0)


if __name__ == "__main__":
    main()


