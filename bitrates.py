import os, shutil, ffmpeg, statistics

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
top = 3                                                                     #uses the top # of samples

tmpcheck()
tmpcheck('new')
gather()                                                                    #ls the directory
original = dirlist[:]                                                       #[:] Slice Operator
        
for file in original:                                                       #splits into copies of 60s slices
    segment = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -i "' + file + '" -map 0 -c copy -f segment -segment_time 60 -reset_timestamps 1 ".\\tmp\\%03d-' + file + '"'
    )
    os.system(segment)
    os.chdir('tmp')
    gather()

    for i in dirlist:
        eps.append( (i, bitrate(i)) )                                       #add em to working list for this loop
    delet = ( sorted(eps, key=lambda x: x[1]) [:-top] )                     #regx['S0xE0x'] = (file-name1.mp4, bitrate,   sorted(eps, by key x[1])
                                                                                              #file-name2.mp4, bitrate,   in this case x = ( i, bitrate(i) )
                                                                                              #file-name3.mp4, bitrate)   from above
                                                                                              #asc sorted by bitrate at [:-3]
    for i in delet:
        os.remove(i[0])                                                     #remove all but the top X segments
        eps.remove(i)

    gather()

    for ep in dirlist:
        infile = ffmpeg.input(ep)
        infile.video.output(
        '.\\tmp\\'+ep,                                                     #filename
        vcodec='libx265',
        preset='slow',
        crf='22'
        ).run(overwrite_output=True)

    os.chdir('.\\tmp\\')
    gather()

    for i in dirlist:
        eps.append( (i, bitrate(i)) )                                       #make a list of every S0XE0X episode temp' bitrate

    nicebitrate = str( int( statistics.mean( [b for e,b in eps] ) )+100 )   #avg bitrate for top 3 temp, for this episode

    os.chdir(pydir)

    pass1 = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -an -sn -i "' + file + '" -c:v libx265 -b:v ' + nicebitrate + 'K -x265-params pass=1 -f null NUL'
    )
    pass2 = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -i "' + file + '" -c:v libx265 -b:v ' + nicebitrate + 'K -x265-params pass=2 -c:a libopus -b:a 160k ".\\new\\' + file + '"'
    )
    print('\n\n\nBitrate for '+ i + ' is: ' + nicebitrate + 'K')
    print('\nRunning with command:\n'+pass1+'\n\n')
    os.system(pass1)
    print('\nRunning with command:\n'+pass2+'\n\n')
    os.system(pass2)        
    shutil.rmtree(pydir + '\\tmp')

os.system("pause")
