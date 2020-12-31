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
        2. A float that represents the angle around the y axis () in the range  [0, 360]
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



def correlateFlightsAndAngles(fileName):
    '''
    * input: 
        fileName: the name of the text file that contains (x-coordinate, z-coordinate, aximuth angle) in each line
    '''

    data = readData(fileName)
    flightDirections  = [] 
    angles = []
    start = 0
    prev = 0
    end = 1

    while end < len(data): 
        if data[prev].coord != data[end].coord and data[prev].ang == data[end].ang: 
            #is a part of a flight (please reference the description of the same line in getFlights)
            prev = end
            end += 1 
        elif data[prev].coord == data[end].coord: 
            # is a pause (please reference the description of the same line in getFlights)
            prev = end
            end += 1 
        elif data[prev].coord != data[end].coord and data[prev].ang != data[end].ang:
            #is the end of a flight (please reference the description of the same line in getFlights)
            #data[end].coord is where the angle changes and is where a new flight starts
            trans = np.array(data[end].coord) - np.array(data[start].coord) 
                #trans is a 2-dimensional vector representing the transformation from data[start].coord to data[end].coord
            
            directionChange = math.degrees(math.acos(trans.dot(np.array([0,1]))/np.linalg.norm(trans)))
                #directionChange is the angle between trans and the vector [0 1] normalized to fall into the range [0, 180]

            angles.append(data[start].ang) #is the azimuth angle of a particular flight, which doesn't change during the flight
            flightDirections.append(directionChange)
            start = end
            prev = end
            end += 1
    return flightDirections, angles
    

if __name__ == '__main__':
    filePath = '/Users/ashleykwon/Desktop/I3T Lab/Viking_Village_Trajectory_Generation/Assets/CameraPaths/' #needs to be modified to fit yours
    onlyfiles = [f for f in listdir(filePath) if isfile(join(filePath, f))]
    
    ###This part derives the differences between flight directions and azimuth angles############################
    flightDirections  = []
    angles = []
    diff = []
    for f in onlyfiles:
        if '.meta' not in f and '.DS_Store' not in f:
            data = readData(f)
            res = correlateFlightsAndAngles(f)
            flightDirections += res[0]
            angles += res[1]
    
    for i in range(len(flightDirections)):
        diff.append(abs(flightDirections[i] - angles[i]))

    plt.hist(diff)
    plt.title('Absolute values of differences between flight directions and azimuth angles')
    plt.show()
    ##############################################################################################################

