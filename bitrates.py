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

tmpcheck()
tmpcheck('new')
gather()                                                                    #ls the directory
original = dirlist[:]                                                       #[:] Slice Operator
        
for file in original:                                                       #splits into copies of 60s slices
    segment = str(
        'ffmpeg -n -hide_banner -loglevel quiet -stats -i \"{}\" -map 0 -c copy -f segment -segment_time 60 -reset_timestamps 1 \".\\tmp\\%03d-{}\"'.format(file,file)
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
        os.remove(i[0])                                                     #remove all EXCEPT the top X segments
        eps.remove(i)
        
    gather()
    tmpcheck()
    
    for ep in dirlist:
        infile = ffmpeg.input(ep)
        infile.video.output(
            '.\\tmp\\'+ep, 
            vcodec='libx265', 
            preset='slow', 
            crf='24'
        ).run(overwrite_output=True)

    os.chdir('.\\tmp\\')
    eps.clear()
    gather()
    
    for i in dirlist:
        eps.append( (i, bitrate(i)) )                                       #make a list of every S0XE0X episode temp' bitrate
    
    avgbitrate = str( int( statistics.mean( [b for e,b in eps] ) )+100 )   #avg bitrate for top x temp, for this episode
    maxrate = ( sorted(eps, key=lambda x: x[1]) [top:] )[-1][1]
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
