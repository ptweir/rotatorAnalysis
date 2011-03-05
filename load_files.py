import os, flypod, sky_times

def compare_dir_names(dn1, dn2):
    n1, n2 = int(dn1[3:]),int(dn2[3:])
    return cmp(n1,n2)

def load_flies_skies(rootDir, baseDirs):
    skies, flies = {}, {}
    for b, baseDir in enumerate(baseDirs):
        sks, fls = {}, {}
        dNames = os.listdir(os.path.join(rootDir,baseDir))
        flyDirNames = [D for D in dNames if D[:3] == 'fly']
        flyDirNames.sort(compare_dir_names)

        for dNum, dName in enumerate(flyDirNames):
            dirName=os.path.join(rootDir,baseDir,dName)
            print dirName
            fly = flypod.analyze_directory(dirName)
            fls[dNum] = fly.copy()
            sky = sky_times.analyze_directory(dirName)
            sks[dNum] = sky.copy()
            
        flies[baseDir] = fls
        skies[baseDir] = sks
    return flies, skies

rootDir = '/media/weir05/data/rotator'
baseDirs = ['12trials','indoor/12trials','indoor/gray/12trials','indoor/sham12trials','indoor/12trials/white','indoor/sham12trials/white']
flies, skies = load_flies_skies(rootDir, baseDirs)
