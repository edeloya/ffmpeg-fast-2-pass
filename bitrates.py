import os, shutil, ffmpeg, statistics, numpy, pprint, datetime

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

def log(string=''):
    with open('{}\\{}'.format(pydir,'.log'), 'a') as logfile:
        logfile.write('[{}]    {}\n\n'.format(datetime.datetime.now(),string))
    return

pydir = os.path.dirname(os.path.abspath(__name__))
original, dirlist, eps = [], [], []
os.chdir(pydir)
top = 4                                                                     #uses the top # of samples

gather()                                                                    #ls the directory
tmpcheck()     
tmpcheck('new')
original = dirlist[:]                                                       #[:] Slice Operator

for file in original:
    if file not in os.listdir('new'):
        segment = (
            'ffmpeg -n -hide_banner -loglevel quiet -stats -i \"{}\" -map 0 -c copy -f segment -segment_time 60 -reset_timestamps 1 \".\\tmp\\%03d-{}\"'.format(file,file)
        )
        log('Splitting {}..'.format(file))
        os.system(segment)
        os.chdir('tmp')
        tmpcheck()
        gather()

        for i in dirlist:
            eps.append( (i, bitrate(i)) )                                       #add em to working list for this loop

        eps = sorted(eps, key=lambda x: x[1])
        log(pprint.pformat(eps, indent=2))

        for i in eps[:-top]:
            os.remove(i[0])                                                     #remove all EXCEPT the top X segments
            eps.remove(i)

        for ep in eps:
            mojostop__= str(
            'ffmpeg -n -hide_banner -loglevel quiet -stats -an -sn -i \"{}\" -c:v libx265 -crf 24 -preset slow \".\\tmp\\{}\"'.format(ep[0],ep[0])
        )
            log('Running with command:\n{}'.format(mojostop__))
            os.system(mojostop__)

        os.chdir('.\\tmp\\')
        eps.clear()
        gather()

        for i in dirlist:
            eps.append( (i, bitrate(i)) )                                       #make a list of every S0XE0X episode temp' bitrate

        eps = sorted(eps, key=lambda x: x[1])
        bits = [b for a,b in eps]
        log(pprint.pformat(eps, indent=2))

        minrate = bits[0]
        maxrate = bits[-1]
        bufsize = round( maxrate / 500, 2 )
        avgbitrate = statistics.mean( bits )   #avg bitrate for top x temp, for this episode

        os.chdir(pydir)

        pass1 = str(
            'ffmpeg -n -hide_banner -loglevel quiet -stats -an -sn -i \"{}" -c:v libx265 -b:v {}K -minrate {}K -maxrate {}K -bufsize {}M -x265-params pass=1 -f null NUL'.format(file, avgbitrate, minrate, maxrate, bufsize)
        )
        pass2 = str(
            'ffmpeg -n -hide_banner -loglevel quiet -stats -i \"{}" -c:v libx265 -b:v {}K -minrate {}K -maxrate {}K -bufsize {}M -x265-params pass=2 -c:a libopus -b:a 160k ".\\new\\{}"'.format(file, avgbitrate, minrate, maxrate, bufsize, file)
        )

        log('Bitrate for {} is: {}K'.format(file, avgbitrate))

        log('Running with command:\n{}'.format(pass1))
        os.system(pass1)

        log('Running with command:\n{}'.format(pass2))
        os.system(pass2)

        eps.clear()
        bits.clear()
        shutil.rmtree(pydir + '\\tmp\\.')

os.system("pause")
