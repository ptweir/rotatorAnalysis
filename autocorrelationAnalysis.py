import numpy as np
import pylab
pylab.ion()

DOWNSAMPLE_RATE = 50
OFFSET = 120

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
        orientations = orientations*numpy.pi/180
        complexOrientations = np.exp(np.complex(0,1)*orientations)
        
        times = fly['times'].copy()
        times = times - times[0]
        times = times[::DOWNSAMPLE_RATE]
        
        if OFFSET > 0:
            timestep = np.median(np.diff(times))
            startInd = int(round(OFFSET/timestep))
            resultTimes = numpy.concatenate((-times[-startInd-1::-1],times[1:-startInd]))
            result = np.correlate(complexOrientations[startInd:], complexOrientations[:-startInd].conjugate(), mode='full')
        else:
            resultTimes = numpy.concatenate((-times[::-1],times[1:]))
            result = np.correlate(complexOrientations, complexOrientations.conjugate(), mode='full')
            
        lines = ax.plot(resultTimes,result)
        line = lines[0]
        line.set_label(fly['dirName'][-5:])
    ax.set_title(baseDir)
    for x in range(-720,720,120):
        ax.axvline(x)
    ax.legend()
