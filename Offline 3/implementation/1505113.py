from scipy import  stats

seed= 1505113
alpha = 0.1



def uniformityTest(k, alpha , numOfRandomNumbers):

    print("Performing Uniformity Test")
    print("k =",k,"alpha =",alpha,"n =",numOfRandomNumbers)
    #first generate random numbers
    randomNumbers=[]

    u0= seed / pow(2,31)
    randomNumbers.append(u0)

    prevZ= seed
    for i in range(1, numOfRandomNumbers):
        zi = (65539 * prevZ) % pow(2,31)
        ui = zi / pow(2,31)
        prevZ = zi
        randomNumbers.append(ui)

    print("Random Numbers: " , randomNumbers)
    #work for uniformity test
    #first we need to create k intervals between 0 and 1
    intervalDuration = 1.0/k

    #working of frequency counter
    frequencyCounter =[]

    for i in range(k):
        frequencyCounter.append(0)

    prevHighestValue = 0.0

    for i in range(k):
        lowerValue = prevHighestValue
        highestValue = lowerValue+intervalDuration

        for j in range(numOfRandomNumbers):
            if( randomNumbers[j]>= lowerValue and randomNumbers[j]<=highestValue ):
                frequencyCounter[i]+=1

        prevHighestValue = highestValue

    #chi square testing
    n= numOfRandomNumbers
    chiSquared = 0.0

    for i in range(k):
        temp = (frequencyCounter[i] - (n/k))
        chiSquared += pow(temp,2)

    chiSquared = chiSquared * (k/n)

    #checking rejected or not
    X_square = stats.chi2.ppf(q = 1-alpha, df = k-1)

    if( chiSquared > X_square):
        print("Rejected")
    else:
        print("Not Rejected")

    print()

def serialTest(k ,alpha ,d, numOfRandomNumbers):
    print("Perforing Serial Test")
    print("k =",k , "alpha =",alpha , "d =" ,d , "n =" ,numOfRandomNumbers)

    #first generate random numbers
    randomNumbers=[]

    u0= seed / pow(2,31)
    randomNumbers.append(u0)

    prevZ= seed
    for i in range(1, numOfRandomNumbers):
        zi = (65539 * prevZ) % pow(2,31)
        ui = zi / pow(2,31)
        prevZ = zi
        randomNumbers.append(ui)

    print("Random Numbers: " , randomNumbers)

    #main work of the serial test
    n= numOfRandomNumbers
    totalNumsTaken = (n // d)*d

    tupleArray =[]

    for i in range(0,totalNumsTaken,d):
        tempArray = []

        for j in range(i,i+d,1):
            tempArray.append(randomNumbers[j])

        tupleArray.append(tempArray)

    frequencyDictionary={}

    print("Tuple: ",tupleArray)

    intervalDuration = 1.0 / k

    for i in range(len(tupleArray)):
        segment=[]
        for j in range(d):
            num = tupleArray[i][j]

            prevHighestValue = 0.0
            for l in range(k):
                lowerValue = prevHighestValue
                highestValue = lowerValue + intervalDuration

                if (num >= lowerValue and num <= highestValue):
                    segment.append(str(l))

                prevHighestValue = highestValue

        tempKey="-"
        tempKey=tempKey.join(segment)

        if(tempKey in frequencyDictionary):
            frequencyDictionary[tempKey]+=1
        else:
            frequencyDictionary[tempKey]=1


    print("Frequency Dictionary: ",frequencyDictionary)



def main():

   #uniformity testing. parameters are k,alpha & number of random numbers
   # uniformityTest(10,alpha,20)
   # uniformityTest(20,alpha,100)

   #serial testing. parameters are k,alpha ,d & number of random numbers
   serialTest(3,alpha,2,5)


if __name__ == "__main__":
    main()
