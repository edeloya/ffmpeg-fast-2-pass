import os, shutil, ffmpeg, statistics, numpy, pprint

def bitrate(X):                                                             #parse file BITRATE
    return int(ffmpeg.probe(X)['format']['bit_rate']) // 1000

def gather(ext='mkv'):                                                      #checks for EXT, creates tmp directory for working files
    dirlist.clear()
    for file in os.listdir():
        if file.endswith(ext):
            dirlist.append(file)

def tmpcheck(x='tmp'):
    if os.path.isdir(x) == False:
        os.mkdir(x)

pydir = os.path.dirname(os.path.abspath(__name__))
os.chdir(pydir)
original, dirlist, eps = [], [], []
top = 5                                                                     #uses the top # of samples

gather()                                                                    #ls the directory
original = dirlist[:]                                                       #[:] Slice Operator
        
for file in original:                                                       #splits into copies of 60s slices
    tmpcheck()
    tmpcheck('new')
    segment = str(
        'ffmpeg -n -hide_banner -stats -i \"{}\" -map 0 -c copy -f segment -segment_time 60 -reset_timestamps 1 \".\\tmp\\%03d-{}\"'.format(file,file)
    )
    os.system(segment)
    os.chdir('tmp')
    gather()

    for i in dirlist:
        eps.append( (i, bitrate(i)) )                                       #add em to working list for this loop

    tmp_sorted = [ x[1] for x in eps]
    minrate = numpy.quantile( tmp_sorted, 0.25 )                                                                                           #file-name2.mp4, bitrate,   in this case x = ( i, bitrate(i) )
                                                                                           #file-name3.mp4, bitrate)   from above
                                                                                           #asc sorted by bitrate at [:-3]
    for i in eps[:-top]:
        os.remove(i[0])                                                     #remove all EXCEPT the top X segments
        eps.remove(i)

    eps.clear()
    tmpcheck()
    gather()

    #Here you're in the first "./tmp"
    for ep in dirlist:
        mojostop__= str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -an -sn -i \"{}\" -c:v libx265 -crf 24 -preset slow \".\\tmp\\{}\"'.format(ep,ep)
    )
        print('\nRunning with command:\n{}\n\n'.format(mojostop__))
        os.system(mojostop__)

    os.chdir('.\\tmp\\')
    eps.clear()
    gather()
    
    for i in dirlist:
        eps.append( (i, bitrate(i)) )                                       #make a list of every S0XE0X episode temp' bitrate

    avgbitrate = numpy.quantile( [b for e,b in eps] , 0.5 )   #avg bitrate for top x temp, for this episode
    maxrate = sorted(eps, key=lambda x: x[1])[-1][1]
    bufsize = round( maxrate / 500, 2 )

    os.chdir(pydir)

    pass1 = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -an -sn -i \"{}" -c:v libx265 -b:v {}K -maxrate {}K -bufsize {}M -x265-params pass=1 -f null NUL'.format(file, avgbitrate, maxrate, bufsize)
    )
    pass2 = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -i \"{}" -c:v libx265 -b:v {}K -maxrate {}K -bufsize {}M -x265-params pass=2 -c:a libopus -b:a 160k ".\\new\\{}"'.format(file, avgbitrate, maxrate, bufsize, file)
    )

    print('\n\n\nBitrate for {} is: {}K'.format(file, avgbitrate))
    
    print('\nRunning with command:\n{}\n\n'.format(pass1))
    os.system(pass1)

    print('\nRunning with command:\n{}\n\n'.format(pass2))
    os.system(pass2)        

    shutil.rmtree(pydir + '\\tmp')

os.system("pause")
