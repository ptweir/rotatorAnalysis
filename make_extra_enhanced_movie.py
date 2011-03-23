#make_enhanced_movie.py
#PTW 3/18/2011 based on make_movie.py
# to make movie, run at command prompt:
# ffmpeg -b 8000000 -r 20 -i frame%05d.png movie.mpeg
# this will result in movie 10x actual speed

import flypod, sky_times
import motmot.FlyMovieFormat.FlyMovieFormat as FMF
import numpy as np
from os.path import join
import pylab, time

inDirName = '/media/weir05/data/rotator/white/diffuserPol/12trials/fly05'
outDirName = './movies/images'

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
    
    orientations = fly['orientations'].copy() + 180
    times = fly['times'].copy()
    
    rotatorStateEachFrame = -np.ones(times.shape) # we will store frame-based rotator state in here
    
    COLORS = dict({'U': 'm', 'R': 'c'})
    ROTATOR_CODE = dict({'U': 0, 'R': 1})
    FRAMESTEP = 65 #130
    
    circleCenterX, circleCenterY, circleRadius = circle_fit(fly['x'],fly['y']) #NOTE:should have been saving this info from start.
    
    fmf = FMF.FlyMovie(join(inDirName,fly['fileName']))

    nFrames = fmf.get_n_frames()
    timestamps = np.ma.masked_all(len(range(0,int(nFrames),FRAMESTEP)))
    
    fig = pylab.figure()
    frameAxes = fig.add_axes([0.1, 0.3, 0.5, 0.6])
    timePlotAxes = fig.add_axes([0.1, 0.1, 0.8, 0.15])
    polarTopAxes = fig.add_axes([0.55, 0.6, 0.4, 0.25],polar=True)
    polarBottomAxes = fig.add_axes([0.55, 0.3, 0.4, 0.25],polar=True)
    
    timePlotAxes.plot(times,orientations,'k')
    for i, cT in enumerate(sky['changeTimes'][:-1]):
        timePlotAxes.axvspan(cT, sky['changeTimes'][i+1], facecolor=COLORS[sky['rotatorState'][i]], alpha=0.2)
        startInd = np.argmin(abs(times-cT))
        endInd = np.argmin(abs(times-sky['changeTimes'][i+1]))
        rotatorStateEachFrame[startInd:endInd] = ROTATOR_CODE[sky['rotatorState'][i]]
    unrotatedOrientations = np.ma.masked_where(rotatorStateEachFrame != 0,orientations)
    rotatedOrientations = np.ma.masked_where(rotatorStateEachFrame != 1,orientations)
    if sum(np.isnan(orientations)) > 0:
        for trackingErrorTime in times[np.isnan(orientations)]:
            timePlotAxes.axvline(trackingErrorTime,linewidth=2,color='k')
    if fly.has_key('stopTimes'):
        for i, sT in enumerate(fly['stopTimes']):
            timePlotAxes.axvspan(sT, fly['startTimes'][i], facecolor='r', alpha=0.5)
    timePlotAxes.set_axis_off()
    for fn,frameNumber in enumerate(range(0,int(nFrames),FRAMESTEP)):
        frame,timestamps[fn] = fmf.get_frame(frameNumber)

        frameAxes.imshow(frame,cmap='gray',origin='lower')
        lineX = [circleCenterX+fly['ROI'][2], 2*(circleCenterX+fly['ROI'][2])-(fly['x'][frameNumber]+fly['ROI'][2])]
        lineY = [circleCenterY+fly['ROI'][1], 2*(circleCenterY+fly['ROI'][1])-(fly['y'][frameNumber]+fly['ROI'][1])]
        frameAxes.plot(lineX,lineY,'b', linewidth=2)
        frameAxes.set_axis_off()
        
        movingDot = timePlotAxes.scatter(times[frameNumber],orientations[frameNumber])
        timePlotAxes.set_ylim((-10,370))
        
        orw,n,b,bc,ax = flypod.rose(unrotatedOrientations[:frameNumber].compressed(),360,ax=polarTopAxes,plotArgs = dict(color=COLORS['U']))
        polarTopAxes.set_rmax(.25)
        polarTopAxes.set_rgrids([1],'')
        polarTopAxes.set_thetagrids([0,90,180,270],['','','',''])
        
        orw,n,b,bc,ax = flypod.rose(rotatedOrientations[:frameNumber].compressed(),360,ax=polarBottomAxes,plotArgs = dict(color=COLORS['R']))
        polarBottomAxes.set_rmax(.25)
        polarBottomAxes.set_rgrids([1],'')
        polarBottomAxes.set_thetagrids([0,90,180,270],['','','',''])
        
        fig.savefig(join(outDirName,'frame')+("%05d" %(fn+1))+'.png')
        polarTopAxes.cla()
        polarBottomAxes.cla()
        frameAxes.cla()
        movingDot.remove()
    print 'frame rate = ' + str(1/np.mean(np.diff(timestamps)))
    
make_frames(inDirName,outDirName)

