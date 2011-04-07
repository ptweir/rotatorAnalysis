import time, numpy, flypod, pylab
pylab.ion()
COLORS = dict({'U': 'm', 'R': 'c'})
PLOTCOLORS = ['m','k','c','r','g','b']
MAX_NUM_STOPS=0
MOD_180 = False
def circmean(alpha):
    mean_angle = numpy.arctan2(numpy.mean(numpy.sin(alpha)),numpy.mean(numpy.cos(alpha)))
    return mean_angle

def circvar(alpha):
    R = numpy.sqrt(numpy.sum(numpy.sin(alpha))**2 + numpy.sum(numpy.cos(alpha))**2)/len(alpha)
    V = 1-R
    return V
def angleDiffDegrees(alpha,beta):
    a, b = alpha*np.pi/180, beta*np.pi/180
    d = np.arctan2(np.sin(a-b), np.cos(a-b))
    D = d*180/np.pi
    return D

fig0 = pylab.figure()
ax0 = fig0.add_subplot(111)
mA, vA, nS = [[]]*len(flies),[[]]*len(flies),[[]]*len(flies)
for bd, baseDir in enumerate(flies.keys()):
    fig = pylab.figure()
    fig.suptitle(baseDir+str(bd))
    fig.set_facecolor('w')
    
    numFlies = len(flies[baseDir])
    meanAngle = numpy.ma.masked_all((numFlies,2))
    varAngle = numpy.ma.masked_all((numFlies,2))
    numStops = numpy.ma.masked_all((numFlies,1))

    for fNum in range(numFlies):
        totals = dict({'U':numpy.array([]),'R':numpy.array([])})
        
        fly = flies[baseDir][fNum].copy()
        sky = skies[baseDir][fNum].copy()
        
        orientations = fly['orientations'].copy()
        orientations = orientations + 180
        if MOD_180:
            orientations = mod(orientations,180)
        
        times = fly['times'].copy()
        
        if sky['rotatorState'][-1] == 'L':
            experiment_end_time = sky['changeTimes'][-1]
        else:
            experiment_end_time = experiment_start_time + 12*60
        
        if fly.has_key('stopTimes'):
            numStops[fNum] = sum([sT < experiment_end_time for sT in fly['stopTimes']])
            for i, sT in enumerate(fly['stopTimes']):
                inds = (times > sT) & (times < fly['startTimes'][i])
                orientations[inds] = numpy.nan
        else:
            numStops[fNum] = 0
            
        if numStops[fNum] <= MAX_NUM_STOPS:
            for i, cT in enumerate(sky['changeTimes'][:-1]):
                trialInds = (times > cT) & (times < sky['changeTimes'][i+1])
                ors = orientations[trialInds]
                ors = ors[~numpy.isnan(ors)]
                if len(ors)>0:
                    if mod(i, 2)==0:
                        rotatorStateForPlots = sky['rotatorState'][i]
                    else:
                        rotatorStateForPlots = 'R'
                    totals[rotatorStateForPlots] = numpy.concatenate((totals[rotatorStateForPlots],ors))
                    
            for i, d in enumerate(COLORS):
                ax = fig.add_subplot(i+1,numFlies,1+fNum,polar=True)
                if MOD_180:
                    m = (circmean(totals[d]*2.0*numpy.pi/180.0)*180.0/numpy.pi)/2.0
                else:
                    m = circmean(totals[d]*numpy.pi/180.0)*180.0/numpy.pi
                #m=circmean(totals[d]*numpy.pi/180.0)*180.0/numpy.pi
                v=circvar(totals[d]*numpy.pi/180)
                orw,n,b,bc,ax = flypod.rose(totals[d],360)
                pylab.polar([0,numpy.pi/2-m*numpy.pi/180],[0,ax.get_rmax()*(1-v)])
                ax.set_rmax(.15)
                ax.set_rgrids([1],'')
                ax.set_thetagrids([0,90,180,270],['','','',''])
                pylab.title(str(int(round(m))))
                ax.axesPatch.set_facecolor(COLORS[d])
                ax.axesPatch.set_alpha(0.2)
                meanAngle[fNum,i] = m.copy()
                varAngle[fNum,i] = v.copy()
    mA[bd] = meanAngle.copy()
    vA[bd] = varAngle.copy()
    nS[bd] = numStops.copy()
    
    asc = ax0.scatter(bd*numpy.ones(mA[bd][:,1].shape)+(pylab.rand(mA[bd][:,1].shape[0])-.5)/8.0,abs(angleDiffDegrees(mA[bd][:,1],mA[bd][:,0])),color=PLOTCOLORS[bd])
    asc.set_label(baseDir)
    
#asc = ax0.boxplot([abs(angleDiffDegrees(mmA[:,1],mmA[:,0])) for mmA in mA])
ax0.legend(loc='upper left')
ax0.set_ylabel('Difference in heading (pol unrotated - pol rotated) degrees')

