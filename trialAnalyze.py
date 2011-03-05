import numpy as np
    
def circmean(alpha):
    mean_angle = np.arctan2(np.mean(np.sin(alpha)),np.mean(np.cos(alpha)))
    return mean_angle

def circvar(alpha):
    if np.ma.isMaskedArray(alpha):
        N = alpha.count()
    else:
        N = len(alpha)
    R = np.sqrt(np.sum(np.sin(alpha))**2 + np.sum(np.cos(alpha))**2)/N
    V = 1-R
    return V
    
def angleDiffDegrees(alpha,beta):
    a, b = alpha*np.pi/180, beta*np.pi/180
    d = np.arctan2(np.sin(a-b), np.cos(a-b))
    D = d*180/np.pi
    return D


NUM_TRIALS = 12
ROTATOR_STATE = dict({'U': 0, 'R': 1})
STOPBUFFER = 0
ada = [[]]*len(flies)
ds = [[]]*len(flies)
mva = [[]]*len(flies)
labels=[[]]*len(flies)
for b, baseDir in enumerate(flies.keys()):
    numFlies = len(flies[baseDir])
    meanAngleTrials = np.ma.masked_all((numFlies,NUM_TRIALS)) #all initially masked. Unmasked automatically when assigned a value
    varAngleTrials = np.ma.masked_all((numFlies,NUM_TRIALS))
    rotatorStateTrials = np.ma.masked_all((numFlies,NUM_TRIALS))
    didStopTrials = np.ma.masked_all((numFlies,NUM_TRIALS))

    for fNum in range(numFlies):
        fly = flies[baseDir][fNum].copy()
        sky = skies[baseDir][fNum].copy()
        
        print fly['dirName']

        orientations = np.ma.masked_invalid(fly['orientations'],copy=True) #mask in case of nans (missed tracking) COPY
        orientations = orientations + 180
        orientations = mod(orientations,180)*2.0
        
        times = fly['times'].copy() #not sure if we should mask this array, also
        
        experiment_start_time = sky['changeTimes'][0]
        
        if sky['rotatorState'][-1] == 'L':
            experiment_end_time = sky['changeTimes'][-1]
        else:
            experiment_end_time = experiment_start_time + 12*60
            
        if fly.has_key('stopTimes'):
            total_num_stops = sum([sT < experiment_end_time for sT in fly['stopTimes']])
            for i, sT in enumerate(fly['stopTimes']):
                inds = (times > sT - STOPBUFFER) & (times < fly['startTimes'][i]+STOPBUFFER)
                orientations[inds] = np.ma.masked
                #times[inds] = np.ma.masked
        else:
            total_num_stops = 0
        
        print 'total_num stops = ', total_num_stops
            
        if (baseDir[-8:] == '12trials') or (baseDir[-5:] == 'white'):
            changeTimesForPlots = sky['changeTimes']
            rotatorStateForPlots = sky['rotatorState']
        else:
            ERROR
            #changeTimesForPlots = [fct + sky['changeTimes'][0] for fct in fictiveChangeTimes[b]]+sky['changeTimes']
            #changeTimesForPlots.sort()
            #rotatorStateForPlots = fictiveLabels[b]
            
        #for i, cT in enumerate(sky['changeTimes'][:-1]):
        for i, cT in enumerate(changeTimesForPlots[:-1]):
            startTime = cT
            startInd = np.argmin(abs(times-startTime))
            
            endTime = changeTimesForPlots[i+1]
            endInd = np.argmin(abs(times-endTime))
                
            #trialInds = (times > startTime) & (times <= endTime)
            
            meanAngleTrials[fNum,i] = (circmean(orientations[startInd:endInd]*np.pi/180.0)*180.0/np.pi)/2.0
            varAngleTrials[fNum,i] = circvar(orientations[startInd:endInd]*np.pi/180.0)
            rotatorStateTrials[fNum,i] = ROTATOR_STATE[rotatorStateForPlots[i]]
            
            if fly.has_key('stopTimes'):
                didStopTrials[fNum,i] = np.sign(sum([(sT > startTime) & (sT <= endTime) for sT in fly['stopTimes']]) + sum([(sT > startTime) & (sT <= endTime) for sT in fly['startTimes']]))
            else:
                didStopTrials[fNum,i] = 0
                
    #unrotatedSlice = (slice(None), slice(None,None,2))
    #rotatedSlice = (slice(None), slice(1,None,2))
    absDiffAngles = abs(angleDiffDegrees(meanAngleTrials[:,::2],meanAngleTrials[:,1::2]))
    ada[b] = absDiffAngles.copy()
    didStop = np.sign(didStopTrials[:,::2] + didStopTrials[:,1::2])
    ds[b] = didStop.copy()
    meanVarAngles = (varAngleTrials[:,::2] + varAngleTrials[:,1::2])/2
    mva[b] = meanVarAngles.copy()
    labels[b] = baseDir


