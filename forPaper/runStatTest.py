MAX_NUM_STOPS = 4
MAX_TIME_STOPPED = 60
chunksPerTrial = 10
maxTimeStoppedChunk = 3
#chunksPerTrial = 5
#maxTimeStoppedChunk = 6

PVAL = .05

for baseDirsInd, baseDirs in enumerate([['diffuserPol/12trials','diffuserPol/sham12trials', 'polDiffuser/12trials'],['noFilter/12trials', 'noFilter/sham12trials','diffuser/12trials']]):
    
    import newStatTestChunks
    reload(newStatTestChunks)
    fig=pylab.figure()
    ax = fig.add_subplot(111)
    testStatistics, p_values = newStatTestChunks.plotIt(ax,flies,skies,baseDirs,'fisher', MAX_NUM_STOPS, MAX_TIME_STOPPED,chunksPerTrial,maxTimeStoppedChunk)
    for baseDirInd, baseDir in enumerate(baseDirs):
        print baseDir, np.sum(p_values[baseDirInd]<PVAL), " sig shift (p<", PVAL, ") out of N = ", len(testStatistics[baseDirInd])

