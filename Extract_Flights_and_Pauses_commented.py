'''
@author: Ashley Kwon
'''
import math
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.misc import derivative
import scipy.integrate as integrate
from pynverse import inversefunc
import numpy as np
import random

class CoordAng:
    '''
    A CoordAng object contains the following.
        1. A list with 2 items, each representing an x-coordinate and a z-coordinate in floats
        2. A float that represents the azimuth angle in the range  [0, 360]
    '''
    def __init__(self, coord, ang):
        self.coord = coord
        self.ang = ang



def readData(fileName):
    '''
    *input: 
        the name of the file that contains data, which is composed of (x-coordinate, z-coordinate, azimuth angle in the range [0, 360]) recorded every 0.5 seconds
    *output: 
        a list with CoordAng objects, in which one object represents a line in the data stored in fileName
    '''
    filePath = '/Users/ashleykwon/Desktop/I3T Lab/Viking_Village_Trajectory_Generation/Assets/CameraPaths/' 
    #filePath needs to be modified according to your file directory
    f = open(filePath  + fileName)
    data = []
    for line in f:
        if line != 'Camera Path \n' and line != ' \n':
            line.strip('\n')
            coordinates = line.split(",")
            obj = CoordAng([float(coordinates[0]), float(coordinates[1])], float(coordinates[2]))
            data.append(obj)
    return data



def saveFlights(data, index):
    '''
    *inputs: 
        1. a list of CoordAng objects derived from readData
        2. index that will be used when saving flights and pauses from data
    *output:
        a call to the function getFlights
    '''
    textFile = open("Flights_And_Pauses_" + str(index) + ".txt", "w+")
    return getFlights(data, 0, 0, 0, 0, 0, 1, textFile, [])
    


def getFlights(data, flightTime, pauseTime, flightLength, start, prev, end, textFile, flightLengthList):
    '''
    *inputs:
        data: a list of CoordAng objects
        flightTime: the amount of time a flight took (initialized as 0)
        pauseTime: the amount of time the user paused (initialized as 0)
        flightLength: the length of a flight (initialized as 0)
        start, prev, end: indices that are needed to traverse through data (initialized as 0, 0, 1, respectively)
        textFile: a text file to save flight and pause data in
        flightLengthList: a list where each pause+flight data entry is appended as [flightLength, flightTime, pauseTime, angleChange] 
    *functionality: 
        tail recursively extracts flight data from data, while reading two consecutive lines of it
    *output:
        entries written to textFile
        a list with all flight lengths read from data
    '''
    if end == len(data): #the function stops calling itself after it reads the last line of the data
        textFile.close()
        return flightLengthList
    else:
        if data[prev].coord != data[end].coord and data[prev].ang == data[end].ang: 
            # The preceding line's coordinate is different the succeeding line's coordinate, but the angle didn't change.
            # This satisfies the definition of a flight. 
            # Therefore, add 0.5 to flightTime and the distance from coordinate 1 to 2 to flightLength
            flightTime  += 0.5
            flightLength += math.sqrt((data[end].coord[0] - data[prev].coord[0])**2 + (data[end].coord[1] - data[prev].coord[1])**2)
            prev = end
            end += 1 
            getFlights(data, flightTime, pauseTime, flightLength, start, prev, end, textFile, flightLengthList)

        elif data[prev].coord == data[end].coord: 
            # The preceding line's coordinate is the same as the succeeding line's coordinate. 
            # This means that the user paused. 
            # Therefore, add 0.5 to pauseTime
            prev = end
            end += 1
            pauseTime += 0.5
            getFlights(data, flightTime, pauseTime, flightLength, start, prev, end, textFile, flightLengthList)

        elif data[prev].coord != data[end].coord and data[prev].ang != data[end].ang:
            # The preceding line's coordinate is different from the succeeding line's coordinate, and the angle changed too
            # This means that the user did not pause, but started moving in a different direction. 
            # Therefore, write the folllowing to textFile and start calculating flight length, velocity, time  ... etc. from data[end]
            #   1. current flight length, time, velocity 
            #   2. pause time right before the current flight 
            #   3. azimuth angle change after the current flight 
            angleChange = data[end].ang - data[start].ang 
            if flightTime != 0 and flightLength  != 0:
                textFile.write(str(flightLength) + "," + str(angleChange) + "," + str(flightTime) + "," + str(pauseTime) + "," + str(flightLength/flightTime) + "\n")
            else:
                textFile.write(str(flightLength) + "," + str(angleChange) + "," + str(flightTime) + "," + str(pauseTime) + "," + str(0) + "\n")
            flightLengthList.append([flightLength, flightTime, pauseTime, angleChange])
            getFlights(data, 0.5, 0, math.sqrt((data[end].coord[0] - data[prev].coord[0])**2 + (data[end].coord[1] - data[prev].coord[1])**2), end, end, end + 1, textFile, flightLengthList)
        
        else:
            print("something is wrong")



def readFlights(flightFileName, flightList, flightTimes, flightLengthandTime, pauseTimes, angles, velocities):
    '''
    *inputs:
        flightFileName: the name of the file that contains flight/pause entries written from getFlights
        flightList: an empty list to contain flight lengths
        flightTimes: an empty list to contain flight times
        flightLengthandTime: an empty list to contain flight lengths and times
        pauseTimes: an empty list to contain pause times
        angles: an empty list to contain azimuth angle changes
        velocities: an empty list to contain velocities 
    *output: 
        the function doesn't return anything, but adds entries to flightList, flightTimes, flightLengthandTime, pauseTImes, angles, and velocities
    '''
    filePath = '/Users/ashleykwon/Desktop/Viking_Village_Flights_and_Pauses/'
    f = open(filePath  + flightFileName)
    for line in f:
        if line.strip() != 'Camera Path':
            line = line.strip()
            coordinates = line.split(",")
            if float(coordinates[0]) != 0.0:
                flightList.append(float(coordinates[0]))
                angles.append(float(coordinates[1]))
                flightTimes.append(float(coordinates[2]))
                pauseTimes.append(float(coordinates[3]))
                velocities.append(float(coordinates[4]))
                flightLengthandTime.append([round(float(coordinates[0]), 3), round(float(coordinates[2]), 3)])



def getCumulProb(flightLengths):
    '''
    *input: 
        flightLengths: a list of flight lengths
    *functionality: 
        plots cumulative probability distribution of the input data
    *output: 
        a list of cumulative probabilities, each corresponding to a flight length in flightLengths
    '''
    numFlights = len(flightLengths)
    cumulProbs= []
    #SortedFlightLengths = sorted(flightLengths)
    for length in flightLengths:
        cumulProbs.append(len([i for i in flightLengths if i <= length])/numFlights)
    plt.plot(sorted(flightLengths), sorted(cumulProbs))
    plt.title('Flight Length CDF')
    plt.show()
    return cumulProbs



def cumulDistFunc(lengths, lamb):
    '''
    *inputs: 
        lengths: a list of flight lengths 
        lamb: the lambda value to be used in fitting the original cumulative probabilty distribution of flight lengths 
            to the distribution derived from a cumulative probability distribution function
    *output: a list with outputs from the cumulative probability distribution function
    '''
    fittedLengths  = []
    for length in lengths:
        fittedLengths.append(1 - math.exp((-1)*lamb*math.pi*(length**2)))
    return fittedLengths


def optimizeLamb(flightLengths):
    '''
    *input: a list of flight lengths
    *output: the lambda value to be used in the function cumulDistFunc
    '''
    cumulProbs =  getCumulProb(flightLengths)
    flightLengths = sorted(flightLengths)
    popt, pcov = curve_fit(cumulDistFunc, flightLengths, cumulProbs)
    print(popt[0])
    return popt[0]


if __name__ == '__main__':
    filePath = '/Users/ashleykwon/Desktop/I3T Lab/Viking_Village_Trajectory_Generation/Assets/CameraPaths/' #needs to be modified to fit yours
    onlyfiles = [f for f in listdir(filePath) if isfile(join(filePath, f))]
    index = 0
    for f in onlyfiles:
        if '.meta' not in f and '.DS_Store' not in f:
            data = readData(f)
            saveFlights(data, index)
            index += 1


    filePath2 =  '/Users/ashleykwon/Desktop/Viking_Village_Flights_and_Pauses/' #needs to be modified to fit yours
    onlyfiles = [f for f in listdir(filePath2) if isfile(join(filePath2, f))]
    flightLengths = []
    flightTimes = []
    flightLengthandTime = []
    pauseTimes = []
    angles = []
    velocities = []

    for f in onlyfiles:
        if f[-4:] == '.txt':
            readFlights(f, flightLengths, flightTimes, flightLengthandTime, pauseTimes, angles, velocities)

    plt.hist(flightLengths)
    plt.title('Flight Lengths')
    plt.show()

    plt.hist(flightTimes)
    plt.title('Flight Times')
    plt.show()

    plt.hist(pauseTimes)
    plt.title('Pause Times')
    plt.show()

    plt.hist(angles)
    plt.title('Angle Changes')
    plt.show()

    plt.hist(velocities)
    plt.title('Velocities')
    plt.show()


    getCumulProb(flightLengths)
    print(optimizeLamb(flightLengths)) #returns 0.03678359207702214 for Fantasy Lite, 0.04953239167238745 for Viking Village
    fitted = sorted(cumulDistFunc(flightLengths, 0.04953239167238745))
    plt.plot(sorted(flightLengths),fitted)
    plt.title('CDF of Fitted Flight Lengths')
    plt.show()
