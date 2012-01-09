#make_enhanced_movie.py
#PTW 10/12/2011 based on make_movie.py
# to make movie, run at command prompt:
# ffmpeg -b 8000000 -r 20 -i frame%05d.png supplementalMovie3Weir.mpeg
# this will result in movie 10x actual speed

#import flypod, sky_times
import motmot.FlyMovieFormat.FlyMovieFormat as FMF
import numpy as np
from os.path import join
import pylab, time, imp
from PIL import Image
import matplotlib as mpl
mpl.rcParams['font.size'] = 12
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['svg.embed_char_paths'] = False
pylab.ion()

flypod = imp.load_source('flypod','/home/peter/src/rotatorAnalysis/flypod.py')
sky_times = imp.load_source('sky_times','/home/peter/src/rotatorAnalysis/sky_times.py')

#inDirName = '/media/weir09/data/diffuserPol/12trials/fly05'
inDirName = '/media/weir09/data/noFilter/12trials/fly02'
outDirName = './frames'

def circle_fit(dataX,dataY):
    """fit a circle to data, returns x,y,radius
    
    arguments:      
    dataX       numpy array containing x data
    dataY       numpy array containing y data (must be same size as dataX)
    
    example:
    cx, cy, r = circle_fit(x,y)
    """ 
    n = sum(~np.isnan(dataX))
    a = np.ones((n,3))
    a[:,0] = dataX[~np.isnan(dataX)]
    a[:,1] = dataY[~np.isnan(dataY)]
    b = -dataX[~np.isnan(dataX)]**2 - dataY[~np.isnan(dataY)]**2
    ai = np.linalg.pinv(a)
    out = np.dot(ai,b)
    circCenterX = -.5*out[0]
    circCenterY = -.5*out[1]
    circR  =  ((out[0]**2+out[1]**2)/4-out[2])**.5;
    return circCenterX, circCenterY, circR
def rose(ax,data,line_color,fill_color):
    """makes polar histogram plot, returns wrapped data, n, bins, binCenters, axes
    
    arguments:
    ax              axes to plot in 
    data            numpy array containing data, must be in radians
    plotArgs        dict of plot arguments (color, etc.)
    
    example:
    orw,n,b,bc,ax = rose(orientations)
    """ 
    NUMBINS = 36

    n, bins, patches = pylab.hist(data,NUMBINS,range=(-np.pi,np.pi),normed=True,visible=False)
    #n = n*2*np.pi/sum(n)
    binCenters = bins[:-1] + (bins[1:] - bins[:-1])/2
    n = np.append(n,n[0])
    binCenters = np.append(binCenters,binCenters[0])
    lineHandle = ax.plot(binCenters,n,color=line_color)
    fillHandle = ax.fill(binCenters,n,color=fill_color)
    ax.set_rmax(.25*NUMBINS/(2*np.pi))
    ax.set_rgrids([2],'')
    ax.set_thetagrids([0,90,180,270],['','','',''])
    return lineHandle, fillHandle

def make_frames(inDirName,outDirName):
    """saves frames in movie with orientation superimposed
    
    arguments:      
    inDirName       directory with fly, sky, and .fmf files
    outDirName      directory to save frames to
    
    example:
    make_frames('/media/weir05/data/rotator/white/diffuserPol/12trials/fly08','./frames/')
    """ 
    fly = flypod.analyze_directory(inDirName)
    sky = sky_times.analyze_directory(inDirName)
    
    startTime = sky['changeTimes'][0]
    
    OFFSET = np.pi/2
    orientationInFrame = fly['orientations'].copy() + 180
    #posToPlot = np.mod(-fly['orientations'].copy()*np.pi/180.0 + np.pi/2 - 3*np.pi/4 + OFFSET,2*np.pi) - np.pi
    posToPlot = np.mod(-fly['orientations'].copy()*np.pi/180.0 + np.pi/2,2*np.pi) - np.pi
    times = fly['times'].copy() - startTime
    
    rotatorStateEachFrame = -np.ones(times.shape) # we will store frame-based rotator state in here
    
    #COLORS = dict({'U': 'm', 'R': 'c'})
    COLORS = dict(U=[1,1,1],R=[.8,.8,.8])
    ROTATOR_CODE = dict({'U': 0, 'R': 1})
    FRAMESTEP = 65 #130#9360
    
    circleCenterX, circleCenterY, circleRadius = circle_fit(fly['x'],fly['y']) #NOTE:should have been saving this info from start.
    
    fmf = FMF.FlyMovie(join(inDirName,fly['fileName']))

    nFrames = fmf.get_n_frames()
    timestamps = np.ma.masked_all(len(range(0,int(nFrames),FRAMESTEP)))
    
    fig = pylab.figure(figsize=(5.5,5.5))
    fig.set_facecolor('w')
    fig.text(.05,.96,'10x normal speed, natural sky polarization')
    fig.text(.65,.96,'Polarization un-switched')
    fig.text(.65,.66,'Polarization switched')
    fig.text(.55,.375,'Polarization axis',color='r')
    fig.text(.3,.355,'Stopped flying',color='g')
    frameAxes = fig.add_axes([0.05, 0.4, 0.54, 0.54])
    timePlotAxes = fig.add_axes([0.17, 0.1, 0.8, 0.25])
    polarTopAxes = fig.add_axes([0.58, 0.7, 0.4, 0.25],polar=True)
    polarBottomAxes = fig.add_axes([0.58, 0.4, 0.4, 0.25],polar=True)
    polarTopAxes.set_rmax(.25*36/(2*np.pi))
    polarBottomAxes.set_rmax(.25*36/(2*np.pi))
    #timePlotAxes.text(12*60+30,.2,'Un-switched \npolarization axis',color='r')
    #timePlotAxes.text(12*60+30,-np.pi/2-.2,'Switched \npolarization axis',color='r')
    
    posToPlotWithoutJumps = posToPlot.copy()
    posToPlotWithoutJumps[abs(np.diff(posToPlotWithoutJumps))>np.pi] = np.nan
    timePlotAxes.plot(times,posToPlotWithoutJumps,'k',linewidth=.5,zorder=10)
    for i, cT in enumerate(np.array(sky['changeTimes'][:-1])-startTime):
        bgpatches = timePlotAxes.axvspan(cT, sky['changeTimes'][i+1]-startTime, facecolor=COLORS[sky['rotatorState'][i]],edgecolor='none')
        timePlotAxes.plot([cT, sky['changeTimes'][i+1]-startTime],np.pi/4 - (np.pi/2)*ROTATOR_CODE[sky['rotatorState'][i]]*np.ones(2),'r')
        startInd = np.argmin(abs(times-cT))
        endInd = np.argmin(abs(times-(sky['changeTimes'][i+1]-startTime)))
        rotatorStateEachFrame[startInd:endInd] = ROTATOR_CODE[sky['rotatorState'][i]]
    unrotatedPosToPlot = np.ma.masked_where(rotatorStateEachFrame != 0,posToPlot,copy=True)
    rotatedPosToPlot = np.ma.masked_where(rotatorStateEachFrame != 1,posToPlot,copy=True)
    if sum(np.isnan(orientationInFrame)) > 0:
        for trackingErrorTime in times[np.isnan(orientationInFrame)]:
            timePlotAxes.axvline(trackingErrorTime,linewidth=2,color='g')
    if fly.has_key('stopTimes'):
        for i, sT in enumerate(np.array(fly['stopTimes'])-startTime):
            timePlotAxes.axvspan(sT, fly['startTimes'][i]-startTime, facecolor='g')
    #timePlotAxes.set_axis_off()
    #timePlotAxes.axhline(np.pi/4,color='r',zorder=5)
    #timePlotAxes.axhline(-np.pi/4,color='r',zorder=5)
    timePlotAxes.set_ylim((-np.pi,np.pi))
    timePlotAxes.set_xlabel('time')
    timePlotAxes.spines['left'].set_position(('outward',8))
    timePlotAxes.spines['bottom'].set_position(('outward',8))
    timePlotAxes.spines['top'].set_visible(False)
    timePlotAxes.spines['right'].set_visible(False)
    timePlotAxes.spines['bottom'].set_bounds(0,12*60)
    timePlotAxes.yaxis.set_ticks_position('left')
    timePlotAxes.xaxis.set_ticks_position('bottom')
    timePlotAxes.set_yticks(np.linspace(-np.pi,np.pi,5))
    timePlotAxes.set_yticklabels([str(int(round(yt*180/np.pi)))+u'\u00b0' for yt in timePlotAxes.get_yticks()]) # don't subtract offset, so 0 is parallel to pol
    timePlotAxes.set_xticks(np.linspace(0,12*60,7))
    timePlotAxes.set_xticklabels([str(int(round(xt/60))) for xt in timePlotAxes.get_xticks()])
    timePlotAxes.set_ylabel('Heading in arena')
    for tickLine in timePlotAxes.get_xticklines() + timePlotAxes.get_yticklines():
        tickLine.set_markeredgewidth(1)
    timePlotAxes.set_xlabel('Time (min)')
    
    for fn,frameNumber in enumerate(range(0,int(nFrames),FRAMESTEP)):
        frame,timestamps[fn] = fmf.get_frame(frameNumber)
        frameAxes.imshow(frame,cmap='gray',origin='lower')

        lineX = [circleCenterX+fly['ROI'][2], 2*(circleCenterX+fly['ROI'][2])-(fly['x'][frameNumber]+fly['ROI'][2])]
        lineY = [circleCenterY+fly['ROI'][1], 2*(circleCenterY+fly['ROI'][1])-(fly['y'][frameNumber]+fly['ROI'][1])]

        frameAxes.plot(lineX,lineY,'b', linewidth=2)
        frameAxes.set_ylim((0,200))
        frameAxes.set_xlim((0,200))
        frameAxes.set_axis_off()
        
        movingDotList = timePlotAxes.plot(times[frameNumber],posToPlot[frameNumber],'ob',zorder=20)
        movingDot = movingDotList[0]
        
        lineHandle, fillHandle = rose(polarTopAxes,unrotatedPosToPlot[:frameNumber].compressed(),'k',COLORS['U'])
        lineHandle[0].set_zorder(20)
        fillHandle[0].set_zorder(20)
        polarTopAxes.plot([-3*np.pi/4, np.pi/4],polarTopAxes.get_rmax()*np.ones(2),'r',zorder=5)
        polarTopAxes.set_rmax(.25*36/(2*np.pi))
        
        lineHandle, fillHandle = rose(polarBottomAxes,rotatedPosToPlot[:frameNumber].compressed(),'k',COLORS['R'])
        lineHandle[0].set_zorder(20)
        fillHandle[0].set_zorder(20)
        polarBottomAxes.plot([3*np.pi/4, -np.pi/4],polarBottomAxes.get_rmax()*np.ones(2),'r',zorder=5)
        polarBottomAxes.set_rmax(.25*36/(2*np.pi))
        
        if rotatorStateEachFrame[frameNumber] == 0: # un-switched
            arrowHandle = frameAxes.plot([175,200],[0,25],'r')
        else:
            arrowHandle = frameAxes.plot([175,200],[25,0],'r')
        #pylab.draw()
        fig.savefig(join(outDirName,'frame')+("%05d" %(fn+1))+'.png')
        polarTopAxes.cla()
        polarBottomAxes.cla()
        frameAxes.cla()
        movingDot.remove()
    print 'frame rate = ' + str(1/np.mean(np.diff(timestamps)))
    
make_frames(inDirName,outDirName)

