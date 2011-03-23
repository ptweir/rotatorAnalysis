pylab.ion()
import numpy as np
import time

COLORS = dict({'U': 'm', 'R': 'c'})
MOD_180 = False

fig = pylab.figure()
ax = fig.add_subplot(111)

for b, baseDir in enumerate(flies.keys()):
    numFlies = len(flies[baseDir])
    for fNum in range(numFlies):
        ax.cla()
        fly = flies[baseDir][fNum].copy()
        sky = skies[baseDir][fNum].copy()

        orientations = np.copy(fly['orientations']) + 180 + 180
        if MOD_180:
            orientations = mod(orientations,180)
        orientations = mod(orientations,360)
            
        times = np.copy(fly['times'])

        ax.plot(times,orientations,'k')
        
        ax.set_xticklabels([time.ctime(float(ti))[11:19] for ti in ax.get_xticks()])
        if MOD_180:
            ax.set_yticks((0,45,90,135))
        else:
            ax.set_yticks((0,90,180,270,360))
        for i, cT in enumerate(sky['changeTimes'][:-1]):
            if MOD_180:
                ax.text(cT,190,sky['rotatorState'][i])
            else:
                ax.text(cT,380,sky['rotatorState'][i])
            ax.axvspan(cT, sky['changeTimes'][i+1], facecolor=COLORS[sky['rotatorState'][i]], alpha=0.2)
        if sum(np.isnan(orientations)) > 0:
            for trackingErrorTime in times[numpy.isnan(orientations)]:
                ax.axvline(trackingErrorTime,linewidth=2,color='k')
        if fly.has_key('stopTimes'):
            for i, sT in enumerate(fly['stopTimes']):
                ax.axvspan(sT, fly['startTimes'][i], facecolor='r', alpha=0.5)

        ax.set_title(fly['dirName'])
        pylab.draw()
        pt = pylab.ginput(1,0)
        #fig.savefig('./'+baseDir+'/'+fly['fileName'][:-3]+'pdf')
