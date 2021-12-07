import os, subprocess, re, collections, pprint, ffmpeg, statistics
from pymkv import MKVFile

def bitrate(X):                                             #parse file BITRATE
    return int(ffmpeg.probe(X)['format']['bit_rate']) // 1000

def gather(ext):                                            #checks for EXT, creates tmp directory for working files
    shards.clear()
    for i in os.listdir():
        if i.endswith(ext):
            shards.append(i)
    if os.path.isdir('tmp') == False:
        os.mkdir('tmp')

os.chdir('D:\\lol\\x265') # os.chdir(os.path.dirname(os.path.abspath(__file__)))
shards, eps = [], []
regx = {}
gather('mkv')

for every in shards:                                      #splits into copies of 60s slices 
    mkv = MKVFile(every)
    mkv.split_duration(60)
    mkv.mux( 'tmp\\' + mkv.tracks[0].file_path )

os.chdir('tmp')

for file in shards:
    if re.findall(r'(S\d{2}E\d{2})', file):
        regx[re.findall(r'(S\d{2}E\d{2})', file)[0]] = None #regx[file] = None

gather('mkv')
for x in regx:                                              #for every ep S0xE0x,
    for i in shards:                                        #for every shard '<filename>-0xx.ext',
        if x in i:                                          #if ep S0xE0x is found in any shards, 
            eps.append( (i,bitrate(i)) )                    #add em to working list for this loop
    regx[x] = ( sorted(eps, key=lambda x: x[1]) [:-3] )     #regx['S0xE0x'] = (file-name1.mp4, bitrate,
                                                                              #file-name2.mp4, bitrate,
                                                                              #file-name3.mp4, bitrate)
                                                                              #sorted by bitrate
    for i in regx[x]:
        os.remove(i[0])    
    eps.clear()                                             #clear the eps of shards from ep x in regx

gather('mkv')
for ep in shards:
    infile = ffmpeg.input(ep)
    infile.video.output(
    'tmp\\'+ep,                                            #filename
    vcodec='libx265',
    preset='slow',
    crf='22'
    ).run(overwrite_output=True)

os.chdir('tmp')
gather('mkv')

for key in regx:                                              #go through unique episode list from original dir
    regx[key] = None                                          #reset values
    for shard in shards:
        if key in shard:
            eps.append( bitrate(shard) )                      #make a list of every S0XE0X episode shards' bitrate
    regx[key] = statistics.mean(eps) // 1 + 100               #avg bitrate for top 3 shards, for this episode
    eps.clear()

os.chdir('..\\')
gather('mkv')


for i,file in enumerate(shards):
    subprocess.call('ffmpeg -hide_banner -loglevel quiet -stats -an -y -i \"'+file+'\" -c:v libx265 -x265-params pass=1 -f null NUL ')
    subprocess.call('ffmpeg -hide_banner -loglevel quiet -stats -i \"'+file+'\" -c:v libx265 -b:v '+regx[i]+' -x265-params pass=2 -c:a aac -b:a 128k \"new_'+file+'\"')
