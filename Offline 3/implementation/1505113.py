from scipy import  stats
import math

seed= 1505113
alpha = 0.1


def uniformityTest(k, alpha , numOfRandomNumbers):

    print("Performing Uniformity Test")
    print("n =",numOfRandomNumbers,"k =",k,"alpha =",alpha)
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

    #print("Random Numbers: " , randomNumbers)

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

    print("ChiSquared:",chiSquared)

    #checking rejected or not
    X_square = stats.chi2.ppf(q = 1-alpha, df = k-1)
    print("Chisquared(k-1,1-alpha):",X_square)

    if( chiSquared > X_square):
        print("Rejected")
    else:
        print("Not Rejected")

    print()

def serialTest(k ,alpha ,d, numOfRandomNumbers):
    print("Perforing Serial Test")
    print("n =" ,numOfRandomNumbers, "d =" ,d ,"k =",k , "alpha =",alpha )

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

    #print("Random Numbers: " , randomNumbers)

    #main work of the serial test
    n= numOfRandomNumbers
    totalNumsTaken = (n // d)*d

    #creating the tuple array. taking d elements of tuples
    tupleArray =[]

    for i in range(0,totalNumsTaken,d):
        tempArray = []

        for j in range(i,i+d,1):
            tempArray.append(randomNumbers[j])

        tupleArray.append(tempArray)

    #print("Tuple: ", tupleArray)

    #working of frequency dictionary

    frequencyDictionary={}

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


    #print(frequencyDictionary)

    #calculation of the chi-square testing
    chiSquared =0.0

    constantTerm = n / pow(k,d)

    for key in frequencyDictionary:
        chiSquared+= pow( (frequencyDictionary[key]-constantTerm) , 2)

    #No of frequency patterns not present in the dictionary is (k^d - dictionar_size). Those patterns have frequency 0.

    temp = pow(k,d) - len(frequencyDictionary)

    for i in range(temp):
        chiSquared += pow( (0 - constantTerm) , 2)


    chiSquared =  chiSquared * ( pow(k,d) / n )
    print("ChiSquared:", chiSquared)

    #checking rejected or not
    X_square = stats.chi2.ppf(q = 1-alpha, df = pow(k,d)-1)
    print("Chisquared(k^d-1,1-alpha):", X_square)

    if( chiSquared > X_square):
        print("Rejected")
    else:
        print("Not Rejected")

    print()

def runsTest(alpha , numOfRandomNumbers):

    print("Performing Runs Test")
    print("alpha =",alpha,"n =",numOfRandomNumbers)

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

    #print("Random Numbers: " , randomNumbers)

    n= numOfRandomNumbers

    #defining a matrix and b matrix

    a = [[4529.4, 9044.9, 13568, 18091, 22615, 27892],
         [9044.9, 18097, 27139, 36187, 45234, 55789],
         [13568, 27139, 40721, 54281, 67852, 83685],
         [18091, 36187, 54281, 72414, 90470, 111580],
         [22615, 45234, 67852, 90470, 113262, 139476],
         [27892, 55789, 83685, 111580, 139476, 172860]]

    b = [1 / 6, 5 / 24, 11 / 120, 19 / 720, 29 / 5040, 1 / 840]

    #now calculate the runs of size 1,2,3,4,5, >=6

    runDictionary ={}
    counter =1

    for i in range(1,n,1):
        if(randomNumbers[i] > randomNumbers[i-1]):
            counter+=1

        else:
            counter = min(counter , 6)
            key =counter

            if(key not in runDictionary):
                runDictionary[key]=1

            else:
                runDictionary[key]+=1
            counter = 1

        if( i == n-1):
            counter = min(counter , 6)
            key = counter

            if (key not in runDictionary):
                runDictionary[key] = 1

            else:
                runDictionary[key] += 1

    for i in range(1,6+1,1):
        key = i
        if(key not in runDictionary):
            runDictionary[key]=0

    #print(runDictionary)

    #calculation of R

    R=0

    for i in range(6):
        for j in range(6):
            #r_i - n.b_i
            temp1 = runDictionary[i + 1] - ( n * b[i])
            # r_i - n.b_i
            temp2 = runDictionary[j + 1] - ( n * b[j])

            R+= a[i][j] * temp1 * temp2

    R= R/n

    print("R=" ,R)

    #checking rejected or not
    X_square = stats.chi2.ppf(q = 1-alpha, df = 6)
    print("Chisquared(6,1-alpha):", X_square)

    if( R > X_square):
        print("Rejected")
    else:
        print("Not Rejected")

    print()

def correlationTest(j, alpha , numOfRandomNumbers):

    print("Performing Correlation Test")
    print( "n =",numOfRandomNumbers , "j =",j,"alpha =",alpha)

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

    #print("Random Numbers: " , randomNumbers)

    n= numOfRandomNumbers

    h= int(((n-1)/j) - 1)

    rho = 0

    for k in range(h+1):
        u1 = randomNumbers[k * j]
        u2 = randomNumbers[(k+1) * j]

        rho+= u1*u2

    rho = ( (12 / (h+1)) * rho ) - 3

    var_rho = ((13*h)+7) / (pow((h+1) , 2))

    aj= rho / math.sqrt(var_rho)

    aj= abs(aj)
    print("Aj=",aj)

    #checking rejected or not
    z = stats.norm.ppf(q = 1-alpha/2)
    print("Z(1-alpha/2):" , z)

    if( aj > z):
        print("Rejected")
    else:
        print("Not Rejected")

    print()


def main():
    nArray = [20,500,4000,10000]

    # #uniformity testing. parameters are k,alpha & n
    # kArray= [10,20]
    # for n in range(len(nArray)):
    #     for k in range(len(kArray)):
    #         uniformityTest(kArray[k],alpha,nArray[n])


    #serial testing. parameters are k,alpha ,d & number of random numbers
    # dArray = [2,3]
    # kArray = [4,8]
    #
    # for n in range(len(nArray)):
    #     for d in range(len(dArray)):
    #         for k in range(len(kArray)):
    #             serialTest(kArray[k] , alpha , dArray[d] , nArray[n])



    #runs testing. parameters are alpha & number of random numbers
    # for n in range(len(nArray)):
    #     runsTest(alpha,nArray[n])


    #correlation testing. parameters are j,alpha & num of random numbers
    jArray = [1,3,5]

    for n in range(len(nArray)):
        for j in range(len(jArray)):
            correlationTest(jArray[j],alpha,nArray[n])


if __name__ == "__main__":
    main()
