# make_movie.py
# PTW 3/18/2011 based on old make_bigmovie2.py
# to make movie, run at command prompt:
# ffmpeg -b 8000000 -r 20 -i frame%05d.png movie.mpeg
# this will result in movie 10x actual speed

import flypod, sky_times
import motmot.FlyMovieFormat.FlyMovieFormat as FMF
import numpy as np
from os.path import join
import pylab

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
    
    FRAMESTEP = 65 #130
    
    circleCenterX, circleCenterY, circleRadius = circle_fit(fly['x'],fly['y']) #NOTE:should have been saving this info from start.
    
    fmf = FMF.FlyMovie(join(inDirName,fly['fileName']))

    nFrames = fmf.get_n_frames()
    timestamps = np.ma.masked_all(len(range(0,int(nFrames),FRAMESTEP)))
    
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    for fn,frameNumber in enumerate(range(0,int(nFrames),FRAMESTEP)):
        frame,timestamps[fn] = fmf.get_frame(frameNumber)

        #pylab.imsave(join(outDirName,'frame')+("%05d" %(fn+1))+'.png',frame,format='png',cmap='gray')
        ax.imshow(frame,cmap='gray')
        lineX = [fly['x'][frameNumber]+fly['ROI'][2], circleCenterX+fly['ROI'][2]]
        lineY = [fly['y'][frameNumber]+fly['ROI'][1], circleCenterY+fly['ROI'][1]]
        ax.plot(lineX,lineY,'b-', linewidth=2)
        ax.set_axis_off()
        fig.savefig(join(outDirName,'frame')+("%05d" %(fn+1))+'.png')
        ax.cla()
    print 'frame rate = ' + str(1/np.mean(np.diff(timestamps)))
    
make_frames(inDirName,outDirName)

