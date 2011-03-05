import time, numpy, pylab
import flypod, sky_times
from scipy.stats.morestats import circmean, circvar	
pylab.ion()

#dirName = '/media/weir05/data/rotator/indoor/gray/12trials/fly10'
#dirName = '/media/weir05/data/rotator/indoor/12trials/fly17'
#dirName = '/media/weir05/data/rotator/indoor/sham12trials/fly09'
#dirName = '/media/weir05/data/rotator/12trials/fly92'
dirName = '/media/weir05/data/rotator/indoor/sham12trials/white/fly28'

fly = flypod.analyze_directory(dirName)
CHANGEBUFFER = 0
if fly is not None:
    sky = sky_times.analyze_directory(dirName)
    
    COLORS = dict({'U': 'm', 'R': 'c'})

    TOTAL_TIME = 12*3*60

    worldTotals=numpy.array([])
    totals = dict({'U':numpy.array([]),'R':numpy.array([])})

    orientations = numpy.copy(fly['orientations']) + 180
    times = numpy.copy(fly['times'])
    fig1 = pylab.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(times,orientations,'k')
    
    ax1.set_xticklabels([time.ctime(float(ti))[11:19] for ti in ax1.get_xticks()])
    ax1.set_yticks((0,90,180,270,360))
    for i, cT in enumerate(sky['changeTimes'][:-1]):
        ax1.text(cT,380,sky['rotatorState'][i])
        ax1.axvspan(cT-CHANGEBUFFER, sky['changeTimes'][i+1]-CHANGEBUFFER, facecolor=COLORS[sky['rotatorState'][i]], alpha=0.2)
    if sum(numpy.isnan(orientations)) > 0:
        for trackingErrorTime in times[numpy.isnan(orientations)]:
            ax1.axvline(trackingErrorTime,linewidth=2,color='k')
    if fly.has_key('stopTimes'):
        for i, sT in enumerate(fly['stopTimes']):
            ax1.axvspan(sT, fly['startTimes'][i], facecolor='r', alpha=0.5)
            inds = (times > sT) & (times < fly['startTimes'][i])
            ax1.plot(times[inds],orientations[inds],color='0.5')
            orientations[inds] = numpy.nan
    inds = (times > TOTAL_TIME + times[0])
    orientations[inds] = numpy.nan

    pylab.draw()
    fig2 = pylab.figure()
    fig2.set_facecolor('w')
    fig2.suptitle(fly['fileName'])
    for i, cT in enumerate(sky['changeTimes'][:-1]):
        ax2=fig2.add_subplot(int(numpy.ceil(numpy.sqrt(len(sky['changeTimes'])-1))),int(numpy.ceil(numpy.sqrt(len(sky['changeTimes'])-1))),1+i,polar=True)
        inds = (times > cT) & (times < sky['changeTimes'][i+1])
        ors = orientations[inds]
        ors = ors[~numpy.isnan(ors)]
        if len(ors)>0:
            orw,n,b,bc,ax = flypod.rose(ors,360)
            m=circmean(ors,high=180,low=-180)
            v=circvar(ors*numpy.pi/180,high=numpy.pi,low=-numpy.pi)
            #hold('on')
            pylab.polar([0,numpy.pi/2-m*numpy.pi/180],[0,ax.get_rmax()*(1-v)])
            ax2.set_rmax(.4)
            ax2.set_rgrids([1],'')
            ax2.set_thetagrids([0,90,180,270],['','','',''])
            ax2.set_title(sky['rotatorState'][i])
            #ax.set_axis_bgcolor(COLORS[sky['directions'][i]])
            ax2.axesPatch.set_facecolor(COLORS[sky['rotatorState'][i]])
            ax2.axesPatch.set_alpha(0.4)
            
            totals[sky['rotatorState'][i]] = numpy.concatenate((totals[sky['rotatorState'][i]],ors))
        
    pylab.draw()
        
    fig3 = pylab.figure()
    fig3.set_facecolor('w')
    fig3.suptitle(fly['dirName'])
    for i, d in enumerate(COLORS):
        #m=circmean(totals[d],high=180,low=-180)
        m=circmean(totals[d],high=180,low=-180)
        v=circvar(totals[d]*numpy.pi/180,high=numpy.pi,low=-numpy.pi)
        ax3 = fig3.add_subplot(2,2,i+1,polar=True)
        orw,n,b,bc,ax = flypod.rose(totals[d],360)
        #orw,n,b,bc,ax = flypod.rose(totals[d],360)
        #pylab.hold('on')
        pylab.polar([0,numpy.pi/2-m*numpy.pi/180],[0,ax.get_rmax()*(1-v)])
        ax3.set_rmax(.4)
        ax3.set_rgrids([1],'')
        ax3.set_thetagrids([0,90,180,270],['','','',''])
        ax3.set_title(d)
        ax3.axesPatch.set_facecolor(COLORS[d])
        ax3.axesPatch.set_alpha(0.2)

