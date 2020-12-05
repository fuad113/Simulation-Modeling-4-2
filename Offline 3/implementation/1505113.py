from scipy import  stats

seed= 1505113
alpha = 0.1



def uniformityTest(k, alpha , numOfRandomNumbers):

    print("Performing Uniformity Test")
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

def serialTest(k ,alpha ,d, numOfRandomNumbers):
    print("Perforing Serial Test")


def main():

   #uniformity testing. parameters are k,alpha & number of random numbers
   # uniformityTest(10,alpha,20)
   # uniformityTest(20,alpha,100)

   #serial testing. parameters are k,alpha ,d & number of random numbers
   serialTest(10,alpha,2,100)


if __name__ == "__main__":
    main()
