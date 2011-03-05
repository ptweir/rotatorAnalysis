pylab.ion()
def cumprobdist(ax,data,xmax=None,plotArgs={}):
    if xmax is None:
        xmax = numpy.max(data)
    elif xmax < numpy.max(data):
        warnings.warn('value of xmax lower than maximum of data')
        xmax = numpy.max(data)
    num_points = len(data)
    X = numpy.concatenate(([0.0],data,data,[xmax]))
    X.sort()
    X = X[-1::-1]
    Y = numpy.concatenate(([0.0],arange(num_points),arange(num_points)+1,[num_points]))/num_points
    Y.sort()
    line = ax.plot(X,Y,**plotArgs)
    return line[0]



PLOTCOLORS = ['m','k','c','r','g','b']

fig1 = pylab.figure()
ax1 = fig1.add_subplot(111)

fig2 = pylab.figure()
ax2 = fig2.add_subplot(111)

fig3 = pylab.figure()
ax3 = fig3.add_subplot(111)

meanAbsDiffAngles,meanVarianceAngles,numTrialsStopped = [[]]*len(flies),[[]]*len(flies),[[]]*len(flies)
for i, ad in enumerate(ada):
    ad[ds[i]>0] = numpy.ma.masked
    meanAbsDiffAngles[i] = ad.mean(axis=1)
    mva[i][ds[i]>0] = numpy.ma.masked
    meanVarianceAngles[i] = mva[i].mean(axis=1)
    
    numTrialsStopped[i] = sum(ds[i].data>0,axis=1) #CHECK
    meanAbsDiffAngles[i][numTrialsStopped[i]>2] = numpy.ma.masked
    meanVarianceAngles[i][numTrialsStopped[i]>2] = numpy.ma.masked
    
    asc = ax1.scatter(meanAbsDiffAngles[i],meanVarianceAngles[i],color=PLOTCOLORS[i])
    asc.set_label(labels[i])
    
    plotArgs = dict(color=PLOTCOLORS[i])
    line = cumprobdist(ax2,meanVarianceAngles[i].compressed(),1.4,plotArgs=plotArgs)
    line.set_label(labels[i])
    
    line = cumprobdist(ax3,meanAbsDiffAngles[i].compressed(),180,plotArgs=plotArgs)
    line.set_label(labels[i])
    
    
ax1.legend()
ax2.legend(loc='upper right')
ax2.set_ylim((-.1,1.1))
ax2.set_xlabel('average anglular variance')
ax2.set_ylabel('fraction of flies')
ax3.legend(loc='upper right')
ax3.set_ylim((-.1,1.1))
ax3.set_xlabel('average difference in heading (pol unrotated - pol rotated) degrees')
ax3.set_ylabel('fraction of flies')

fig4 = pylab.figure()
ax4 = fig4.add_subplot(111)
ax4.boxplot([mada.compressed() for mada in meanAbsDiffAngles])
ax4.set_xticklabels(labels)
ax4.set_ylabel('abs diff angle')

fig5 = pylab.figure()
ax5 = fig5.add_subplot(111)
ax5.boxplot([mVa.compressed() for mVa in meanVarianceAngles])
ax5.set_xticklabels(labels)
ax5.set_ylabel('var angle')
