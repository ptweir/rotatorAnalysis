import numpy as np
import pylab
from scipy.stats import ttest_ind, ttest_1samp, mannwhitneyu
pylab.ion()
import matplotlib as mpl
mpl.rcParams['font.size'] = 8
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['svg.embed_char_paths'] = False
"""
import pickle
inPklFile = open('allRotatorFlies.pkl', 'rb')
flies = pickle.load(inPklFile)
inPklFile.close()
inPklFile = open('allRotatorSkies.pkl', 'rb')
skies = pickle.load(inPklFile)
inPklFile.close()
"""

MAX_NUM_STOPS = 4
MAX_TIME_STOPPED = 60
chunksPerTrial = 10
maxTimeStoppedChunk = 3
#chunksPerTrial = 5
#maxTimeStoppedChunk = 6
AXBUFFER = np.array((2,1,-2,-1))*.1
for baseDirsInd, baseDirs in enumerate([['diffuserPol/12trials','diffuserPol/sham12trials', 'polDiffuser/12trials'],['noFilter/12trials', 'noFilter/sham12trials','diffuser/12trials']]):
    NUM_SUBPLOT_ROWS = 5
    NUM_SUBPLOT_COLS = 4
    
    FIG_WIDTH_mm = 85 #188
    fig0 = pylab.figure(figsize=(FIG_WIDTH_mm/25.4,8))
    #fig0 = pylab.figure(figsize=(18,10))
    fig0.set_facecolor('w')
    ax0 = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,1)
    ax0.set_position(np.array((0,.8,1,.2))+AXBUFFER)
    arenaImg = pylab.imread('rotatorArena.png')
    ax0.imshow(arenaImg)
    ax0.set_aspect('equal')
    ax0.set_axis_off()
    
    ax1 = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,5)
    ax1.set_position(np.array((0,.6,1,.2))+AXBUFFER)
    
    # plot raw trace:
    import plotIndividual
    reload(plotIndividual)
    plotIndividual.plotIt(ax1,flies,skies,baseDirs)
    
    import autocorrelationAnalysis
    reload(autocorrelationAnalysis)
    ax2a = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,9)
    ax2a.set_position(np.array((0,.4,1,.2))+AXBUFFER)
    ax2b = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,13)
    ax2b.set_position(np.array((0,.2,1,.2))+AXBUFFER)
    autocorrelationAnalysis.plotIt(ax2b,ax2a,flies,skies,baseDirs, MAX_NUM_STOPS, MAX_TIME_STOPPED)
    
    ax3a = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,17)
    ax3b = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,18)
    ax3c = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,19)
    for axIndex, ax in enumerate([ax3a,ax3b,ax3c]):
        ax.set_position(np.array((0,0,.25,.2))+AXBUFFER+np.array((axIndex*.3,0,0,0)))
    ax3boxes = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,20)
    ax3boxes.set_position(np.array((.85,0,.25,.2))+AXBUFFER)
    axesList = [ax3a,ax3b,ax3c,ax3boxes]
    import plotSpeedAfterSwitch
    reload(plotSpeedAfterSwitch)
    allSpeedChanges = plotSpeedAfterSwitch.plotIt(axesList,flies,skies,baseDirs, MAX_NUM_STOPS, MAX_TIME_STOPPED)
    #import plotSaccadeRateAfterSwitch
    #reload(plotSaccadeRateAfterSwitch)
    #allSpeedChanges = plotSaccadeRateAfterSwitch.plotIt(axesList,flies,skies,baseDirs, MAX_NUM_STOPS, MAX_TIME_STOPPED)
    
    for baseDirInd, baseDir in enumerate(baseDirs):
        print baseDir, " speed N = ", len(allSpeedChanges[baseDirInd])
        t, p_val = ttest_1samp(allSpeedChanges[baseDirInd],0)
        print "p value speed changes = ", p_val
    u, p_val = mannwhitneyu(allSpeedChanges[0],allSpeedChanges[1])#t, p_val = ttest_ind(allSpeedChanges[0],allSpeedChanges[1])
    print "p value between speed changes in ", baseDirs[0], " and ", baseDirs[1], " = ", p_val
    u, p_val = mannwhitneyu(allSpeedChanges[0],allSpeedChanges[2])#t, p_val = ttest_ind(allSpeedChanges[0],allSpeedChanges[2])
    print "p value between speed changes in ", baseDirs[0], " and ", baseDirs[2], " = ", p_val
    u, p_val = mannwhitneyu(allSpeedChanges[1],allSpeedChanges[2])#t, p_val = ttest_ind(allSpeedChanges[0],allSpeedChanges[2])
    print "p value between speed changes in ", baseDirs[1], " and ", baseDirs[2], " = ", p_val
    
    ax0.set_position([0,.8,1,.2])

    ax1.set_position([.18,.65,.79,.13])

    ax2a.set_position([.18,.45,.79,.13])
    ax2b.set_position([.18,.3,.79,.13])
    
    for axIndex, ax in enumerate([ax3a,ax3b,ax3c]):
        ax.set_position(np.array((.17,.05,.18,.15))+np.array((axIndex*.22,0,0,0)))
    ax3boxes = fig0.add_subplot(NUM_SUBPLOT_ROWS,NUM_SUBPLOT_COLS,20)
    ax3boxes.set_position(np.array((.85,.05,.14,.15)))
    
    pylab.draw()
    fig0.savefig('Fig'+str(baseDirsInd+5)+'.svg', dpi=600)
    
    
