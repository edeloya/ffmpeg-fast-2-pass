import os, subprocess, re, collections, pprint, ffmpeg, statistics
from pymkv import MKVFile

def bitrate(X):                                             #parse file BITRATE
    return int(ffmpeg.probe(X)['format']['bit_rate'])

def gather(ext):                                            #checks for EXT, creates tmp directory for working files
    shards.clear()
    for i in os.listdir():
        if i.endswith(ext):
            shards.append(i)
    if os.path.isdir('tmp') == False:
        os.mkdir('tmp')

pydir = os.path.dirname(os.path.abspath(__name__))
os.chdir(pydir)
shards, eps = [], []
regx = {}
filetype = 'mkv'
top = 3                                                     #uses the top # of samples

gather(filetype)
for every in shards:                                        #splits into copies of 60s slices 
    mkv = MKVFile(every)
    mkv.split_duration(60)
    mkv.mux( 'tmp\\' + mkv.tracks[0].file_path )

os.chdir('tmp')

for file in shards:
    if re.findall(r'(S\d{2}E\d{2})', file):
        regx[re.findall(r'(S\d{2}E\d{2})', file)[0]] = None #regx[file] = None

gather(filetype)
for x in regx:                                              #for every ep S0xE0x,
    for i in shards:                                        #for every shard '<filename>-0xx.ext',
        if x in i:                                          #if ep S0xE0x is found in any shards, 
            eps.append( (i,bitrate(i)) )                    #add em to working list for this loop
    regx[x] = ( sorted(eps, key=lambda x: x[1]) [:-top] )   #regx['S0xE0x'] = (file-name1.mp4, bitrate,
                                                                              #file-name2.mp4, bitrate,
                                                                              #file-name3.mp4, bitrate)
                                                                              #asc sorted by bitrate at [:-3]
    for i in regx[x]:
        os.remove(i[0])    
    eps.clear()                                             #clear the eps of shards from ep x in regx

gather(filetype)
for ep in shards:
    infile = ffmpeg.input(ep)
    infile.video.output(
    'tmp\\'+ep,                                            #filename
    vcodec='libx265',
    preset='slow',
    crf='22'
    ).run(overwrite_output=True)

os.chdir('tmp')
gather(filetype)

for key in regx:                                              #go through unique episode list from original dir
    regx[key] = None                                          #reset values
    for shard in shards:
        if key in shard:
            eps.append( bitrate(shard) )                      #make a list of every S0XE0X episode shards' bitrate
    regx[key] = int(statistics.mean(eps))+100                 #avg bitrate for top 3 shards, for this episode
    eps.clear()

os.chdir('..\\..\\')
gather(filetype)


for ep in regx:
    for i in shards:
        if ep in i:
            s_bitrate = str(regx[ep])
            pass1 = 'ffmpeg -hide_banner -loglevel quiet -stats -an -sn -y -i \"' + os.path.abspath(i) + '\" -c:v libx265 -b:v ' + s_bitrate + ' -x265-params pass=1 -f null NUL'
            pass2 = str(
                'ffmpeg -hide_banner -loglevel quiet -stats -y -i "' + os.path.abspath(i) + '" -c:v libx265 -b:v ' + s_bitrate + ' -x265-params pass=2 -c:a aac -b:a 128k \"' + pydir + '\\new_' + i + '\"')
            print('\n\nBitrate for '+ i + ' is: ' + s_bitrate)
            print('Running with command:\n'+pass1+'\n\n')
            os.system(pass1)
            print('Running with command:\n'+pass2+'\n\n')
            os.system(pass2)

os.system("pause")
