import numpy as np
import pylab

OFFSET = np.pi/2
COMPASSDIRECTIONS = {0:'E',90:'N',180:'W',270:'S'}
def plotIt(ax,flies,skies,baseDirs):
    if 'noFilter/12trials' in baseDirs:
        flyToPlot = flies['noFilter/12trials'][1].copy() #'/media/weir10/data/noFilter/12trials/fly02' or 2 is good
        skyToPlot = skies['noFilter/12trials'][1].copy()
    else:
        flyToPlot = flies['diffuserPol/12trials'][4].copy() # '/media/weir05/data/rotator/white/diffuserPol/fly05' or 2 is good
        skyToPlot = skies['diffuserPol/12trials'][4].copy()
        
    COLORS = dict(U=[1,1,1],R=[.8,.8,.8])
    startTime = skyToPlot['changeTimes'][0]
    for changeTimeInd, changeTime in enumerate(skyToPlot['changeTimes'][:-1]):
        patchHandle = ax.axvspan((changeTime-startTime)/60.0, (skyToPlot['changeTimes'][changeTimeInd+1]-startTime)/60.0)
        patchHandle.set_facecolor(COLORS[skyToPlot['rotatorState'][changeTimeInd]])
        patchHandle.set_edgecolor('none')
    
    posToPlot = np.mod(np.ma.masked_invalid(-flyToPlot['orientations']*np.pi/180.0 + np.pi/2 - 3*np.pi/4 + OFFSET,copy=True),2*np.pi) - np.pi
    timesToPlot = np.ma.masked_invalid((flyToPlot['times']-startTime)/60.0,copy=True)

    posToPlot[abs(np.diff(posToPlot))>np.pi] = np.nan
    ax.plot(timesToPlot,posToPlot,'k',linewidth=.5)
    ax.set_xlim((-.5,12.5))
    ax.set_ylim((-np.pi, np.pi))
    ax.spines['left'].set_position(('outward',8))
    ax.spines['bottom'].set_position(('outward',8))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    try:
        ax.spines['bottom'].set_bounds(0,12)
    except AttributeError:
        print "running old matplotlib version"
        ax.set_xlim((-1,13))
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_yticks(np.linspace(-np.pi,np.pi,5))
    #ax.set_yticklabels(np.array(ax.get_yticks()*180/np.pi+180,dtype=int))
    #ax.set_yticklabels([str(int(round(yt*180/np.pi)))+u'\u00b0' for yt in ax.get_yticks()])
    if 'noFilter/12trials' in baseDirs:
        ax.set_yticklabels([COMPASSDIRECTIONS[np.mod(int(round((yt-OFFSET)*180/np.pi)),360)] for yt in ax.get_yticks()])
        ax.set_ylabel('Compass heading')
    else:
        ax.set_yticklabels([str(int(round(yt*180/np.pi)))+u'\u00b0' for yt in ax.get_yticks()]) # don't subtract offset, so 0 is parallel to pol
        ax.set_ylabel('Heading in arena')
    #ax.set_xticks(np.arange(0,24,3))
    for tickLine in ax.get_xticklines() + ax.get_yticklines():
        tickLine.set_markeredgewidth(1)
    ax.set_xlabel('Time (min)')
