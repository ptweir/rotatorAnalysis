"""sky_times

PTW
"""

import os, time, pickle


def read_rotator_file(filename):
    """ read notes from rotator_*.txt file
    example:
    changeTimes, rotatorState = sky_times.read_rotator_file('rotator_20100427_145334.txt')
    """
    ROTATOR_STATE=['U','R','L']
    fd = open(filename,'r')

    changeTimes=[]
    rotatorState=[]

    while 1:
        line = fd.readline()
        if line:
            sline = line.split()
            if sline[1] in ROTATOR_STATE:
                changeTimes.append(float(sline[0]))
                rotatorState.append(sline[1])

        if not line:  # 'readline()' returns None at end of file.
            break
		    
    return 	changeTimes, rotatorState
    
def read_stops_file(filename):
    """ read notes from stops_*.txt file
    example:
    stopStartTimes = sky_times.read_stops_file('stops_20100427_145334.txt')
    """
    INTERVENTIONS=['w','t']
    fd = open(filename,'r')

    stopStartTimes=[]

    while 1:
        line = fd.readline()
        if line:
            sline = line.split()
            if sline[1] in INTERVENTIONS:
                stopStartTimes.append(float(sline[0]))
        if not line:  # 'readline()' returns None at end of file.
            break
		    
    return 	stopStartTimes

def analyze_directory(dirName):
    """pixel mean analysis
    
    arguments:      
    dirName     directory path to analyze
    
    example:
    analyze_directory('/media/weir05/data/rotator/fly04/')
    """ 
    filenames = os.listdir(dirName)
    rotatorFileExists = False
    stopsFileExists = False
    for f, filename in enumerate(filenames):
        if filename[:7] == 'rotator' and filename[-4:] == '.txt':
            rotatorFileExists = True
            rotatorFilename = filename
        elif filename[:5] == 'stops' and filename[-4:] == '.txt':
            stopsFileExists = True
            stopsFilename = filename
        elif filename[:4] == 'aSky' and filename[-3:] == 'pkl': # not sure which will choose if >1 pkl file
            inPklFile = open(os.path.join(dirName,filename), 'rb')
            sky = pickle.load(inPklFile)
            inPklFile.close()
            break
    
    else:
        sky = {}
        if rotatorFileExists:
            changeTimes, rotatorState = read_rotator_file(os.path.join(dirName,rotatorFilename))
            sky['dirName'], sky['fileName'] = dirName, rotatorFilename
            sky['changeTimes']=changeTimes
            sky['rotatorState']=rotatorState
        if stopsFileExists:
            stopStartTimes = read_stops_file(os.path.join(dirName,stopsFilename))
            sky['stopStartTimes']=stopStartTimes

        date_time = time.strftime("%Y%m%d_%H%M%S")
        pklFilename = 'aSky'+ date_time +'.pkl'
        sky['pklFileName'] = pklFilename
        outPklFile = open(os.path.join(dirName,pklFilename), 'wb')
        pickle.dump(sky, outPklFile)
        outPklFile.close()
    return sky
    
    
