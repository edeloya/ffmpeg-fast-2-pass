import os, subprocess, re, collections, pprint, ffmpeg, statistics
from pymkv import MKVFile

def bitrate(X):                                             #parse file BITRATE
    return int(ffmpeg.probe(X)['format']['bit_rate']) // 1000

def gather(ext):                                            #checks for EXT, creates tmp directory for working files
    dirlist.clear()
    for i in os.listdir():
        if i.endswith(ext):
            dirlist.append(i)

def tmpcheck(x='tmp'):
    if os.path.isdir(x) == False:
        os.mkdir(x)

pydir = os.path.dirname(os.path.abspath(__name__))
os.chdir(pydir)
original, dirlist, eps = [], [], []
regx = {}
filetype = 'mkv'
top = 3                                                     #uses the top # of samples

tmpcheck()
gather(filetype)
original = dirlist[:]                                            #[:] Slice Operator
        
for every in dirlist:                                         #splits into copies of 60s slices 
    mkv = MKVFile(every)
    mkv.split_duration(60)
    mkv.mux( 'tmp\\' + mkv.tracks[0].file_path )

os.chdir('tmp')
gather(filetype)

for file in dirlist:
    if re.findall(r'(S\d{2}E\d{2})', file):
        regx[re.findall(r'(S\d{2}E\d{2})', file)[0]] = None #regx[file] = None

for x in regx:                                              #for every ep S0xE0x,
    for i in dirlist:                                          #for every shard '<filename>-0xx.ext',
        if x in i:                                          #if ep S0xE0x is found in any temp, 
            eps.append( (i, bitrate(i)) )                    #add em to working list for this loop
            with open('bit.s', 'a') as file:
                file.write(eps)
    regx[x] = ( sorted(eps, key=lambda x: x[1]) [:-top] )   #regx['S0xE0x'] = (file-name1.mp4, bitrate,   sorted(eps, by key x[1])
                                                                              #file-name2.mp4, bitrate,   in this case x = ( i, bitrate(i) )
                                                                              #file-name3.mp4, bitrate)   from above
                                                                              #asc sorted by bitrate at [:-3]
    for i in regx[x]:
        os.remove(i[0])    
    eps.clear()                                             #clear the eps of temp from ep x in regx

tmpcheck()
gather(filetype)

for ep in dirlist:
    infile = ffmpeg.input(ep)
    infile.video.output(
    'tmp\\'+ep,                                             #filename
    vcodec='libx265',
    preset='slow',
    crf='22'
    ).run(overwrite_output=True)

tmpcheck()
os.chdir('tmp')
gather(filetype)

for key in regx:                                            #go through unique episode list from original dir
    regx[key] = None                                          #reset values
    for file in dirlist:
        if key in file:
            eps.append( bitrate(file) )                    #make a list of every S0XE0X episode temp' bitrate
    regx[key] = int(statistics.mean(eps))+100               #avg bitrate for top 3 temp, for this episode
    eps.clear()

os.chdir(pydir)
gather(filetype)

tmpcheck('new')

for ep in regx:
    for i in original:
        if ep in i:
            s_bitrate = str(regx[ep])
            pass1 = str(
                'ffmpeg -hide_banner -loglevel quiet -stats -an -sn -y -i \"' + pydir + '\\' + i + '\" -c:v libx265 -b:v ' + s_bitrate + 'K -x265-params pass=1 -f null NUL'
            )
            pass2 = str(
                'ffmpeg -hide_banner -loglevel quiet -stats -y -i \"' + pydir + '\\' + i + '\" -c:v libx265 -b:v ' + s_bitrate + 'K -x265-params pass=2 -c:a libopus -b:a 192k \"' + pydir + '\\new\\' + i + '\"'
            )
            print('\n\n\nBitrate for '+ i + ' is: ' + s_bitrate)
            print('\nRunning with command:\n'+pass1+'\n\n')
            os.system(pass1)
            print('\nRunning with command:\n'+pass2+'\n\n')
            os.system(pass2)

os.system("pause")
os.system('rmdir /q /s tmp')
