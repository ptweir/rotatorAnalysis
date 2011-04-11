import numpy as np
import pylab
pylab.ion()

DOWNSAMPLE_RATE = 50
OFFSET = 0
UNBIASED = True

for b, baseDir in enumerate(flies.keys()):
    numFlies = len(flies[baseDir])
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    for fNum in range(numFlies):
        fly = flies[baseDir][fNum].copy()
        sky = skies[baseDir][fNum].copy()
        
        print fly['dirName']

        orientations = fly['orientations'].copy()
        orientations = orientations[::DOWNSAMPLE_RATE]
        orientations = orientations*numpy.pi/180.0
        complexOrientations = np.exp(np.complex(0,1)*orientations)
        if np.sum(np.isnan(complexOrientations)) != 0:
            print 'tracking failed ', np.sum(np.isnan(complexOrientations)), ' times'
            complexOrientations[np.isnan(complexOrientations)] = np.ma.masked #times when tracking failed CHECK should be 0?
            complexOrientations = complexOrientations - np.mean(complexOrientations)
        
        times = fly['times'].copy()
        times = times - times[0]
        times = times[::DOWNSAMPLE_RATE]
        
        if OFFSET > 0:
            timestep = np.median(np.diff(times))
            startInd = int(round(OFFSET/timestep))
            resultTimes = numpy.concatenate((-times[-startInd-1::-1],times[1:-startInd]))
            result = abs(np.correlate(complexOrientations[startInd:], complexOrientations[:-startInd].conjugate(), mode='full'))
        else:
            resultTimes = numpy.concatenate((-times[::-1],times[1:]))
            result = abs(np.correlate(complexOrientations, complexOrientations.conjugate(), mode='full'))
        
        if UNBIASED:
            N = (resultTimes.size+1)/2.0
            bias = 1.0/(N - abs(arange(-N+1,N)))
            result = result*bias
            
        lines = ax.plot(resultTimes,result)
        line = lines[0]
        line.set_label(fly['dirName'][-5:])
    #ax.set_ylim(( 0, int(round(90000.0/DOWNSAMPLE_RATE)) ))
    ax.set_title(baseDir)
    for x in range(-720,720,120):
        ax.axvline(x,color='k')
    ax.set_xticks(range(-720,720,120))
    ax.legend()
    ax.set_xlabel('time (sec)')
