webroot='http://yourmusicsync.local/' # MusicSync Server Root URL
token='' # access token for view protected MusicSync Server installations, get it from browser cookies
destdir='music' # Download destination dir
playlist_prefix='playlist' # prefix for playlists files names
lyricsDir='lyrics' # lyrics files save dir
genAlbums=True # generate playlist from albums
deleteExcess=True # delete files in music dir, that not indexed by program
saveLyrics=True # save audios lyrics if present
# -*- coding: utf-8 -*-
print('MusicSync Saver')
import sys, os, json, urllib2, urllib,re,codecs
reload(sys)  
sys.setdefaultencoding('utf8')

def getAudios(album=''):
	try:
			req = urllib2.Request(url=os.path.join(webroot, 'api/playlist'),data=urllib.urlencode({'token': token, 'album' : album}))
			return json.loads(urllib2.urlopen(req).read())
	except urllib2.HTTPError: return False 

def getAlbums():
	try: 
		return json.loads(urllib2.urlopen(urllib2.Request(url=os.path.join(webroot, 'api/albums'),data=urllib.urlencode({'token': token}))).read())
	except urllib2.HTTPError: return False

def diff(a, b):
	b = set(b)
	return [aa for aa in a if aa not in b]

destdir=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), destdir)
if not os.path.exists(destdir):
	print('Notice: Download destination dir is not exists, attempting to create..')
	os.makedirs(destdir)

print('Loading audios list..')
audios=getAudios()
if audios==False:
	print('Fatal: unable to connect')
	raise NameError, 'See above'

flist=[f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]
rlist=[]

if saveLyrics==True:
	lyricsDir=os.path.join(destdir, lyricsDir) # auto generate absolute path for lyrics dir
	if not os.path.exists(lyricsDir):
		print('Notice: Lyrics dir is not exists, attempting to create..')
		os.makedirs(lyricsDir)
	fllist=[f for f in os.listdir(lyricsDir) if os.path.isfile(os.path.join(lyricsDir, f))]
	rllist=[]

print('Starting '+str(len(audios))+' audios download..')
la=len(audios)
fp=codecs.open(destdir+"/"+playlist_prefix+'.m3u8', 'w', 'utf-8')
fp.write("#EXTM3U\n")

aeac=0
rtec=0
sadc=0
dnac=0

for audio in range(len(audios)):
	# converting artist & title to proper runtime
	artist = re.sub(' +', ' ', (str(audios[audio]['artist'].encode('utf8')).strip())).replace('&amp', '&').replace('&;', '&')
	title = re.sub(' +', ' ', (str(audios[audio]['title'].encode('utf8')).strip())).replace('&amp', '&').replace('&;', '&')
	if (artist=="" or artist.isspace()) and (title=="" or title.isspace()):
		fname=aid
	elif (artist=="" or artist.isspace()) and not (title=="" or title.isspace()):
		fname = re.sub(' +', ' ', ("Unknown - "+title).translate(None, ':*?!@%$<>|+\\\"').replace('/', '-'))
	else: fname = re.sub(' +', ' ', (artist+" - "+title).translate(None, ':*?!@%$<>|+\\\"').replace('/', '-'))

	sys.stdout.write("["+str(int(((audio+1)*1.0/len(audios)*1.0)*100))+"%] "+"Processing \"%s\" (#%s of %s).. " % (fname, audio+1, len(audios)))
	filepath = os.path.join(destdir, "%s.mp3" % (fname))
	fp.write("#EXTINF:,%s\n" % (artist+" - "+title))
	fp.write("%s.mp3\n" % (fname))
	if os.path.isfile(filepath)==False:
		try:
			try:
				urllib.urlretrieve(os.path.join(webroot, 'getAudio/', audios[audio]['filename']), filepath)
				rlist.append("%s.mp3" % (fname))
				sadc+=1
				print('Complete')
			except IndexError as e:
				print('Download unavailable')
				dnac+=1
		except:
			rtec+=1
			print('Error')
	else:
		aeac+=1
		print('Already exists.')
		rlist.append("%s.mp3" % (fname))
	if saveLyrics==True:
		lyr=0
		try: lyr=audios[audio]['lyrics']
		except KeyError: pass
		if lyr<>0 and lyr<>'':
			if not os.path.exists(lyricsDir+fname+'.txt'):
				lf=codecs.open(os.path.join(lyricsDir, "%s.txt" % (fname)), 'w', 'utf-8')
				lf.write(lyr)
				lf.close()
				rllist.append("%s.txt" % (fname))
			rllist.append("%s.txt" % (fname))
fp.close()
rlist.append(playlist_prefix+'.m3u8')
rlist.append(playlist_prefix+'_deprecated.m3u8')
print('Download complete!')
if saveLyrics==True:
	for f in diff(fllist, rllist):
		os.remove(os.path.join(lyricsDir,f))

if genAlbums==True:
	print('Generating playlists from your web albums..')
	albums=getAlbums()
	if albums==False: print('Albums list fetch failed!')
	else:
		for album in albums:
			print('Processing album "'+album+'"..')
			audios=getAudios(album)
			plf=codecs.open(os.path.join(destdir, playlist_prefix+'_'+album+'.m3u8'), 'w', 'utf-8')
			rlist.append(playlist_prefix+'_'+album+'.m3u8')
			plf.write("#EXTM3U\n")
			for audio in audios:

				artist = re.sub(' +', ' ', (str(audio['artist'].encode('utf8')).strip())).replace('&amp', '&').replace('&;', '&')
				title = re.sub(' +', ' ', (str(audio['title'].encode('utf8')).strip())).replace('&amp', '&').replace('&;', '&')
				if (artist=="" or artist.isspace()) and (title=="" or title.isspace()):
					fname=aid
				elif (artist=="" or artist.isspace()) and not (title=="" or title.isspace()):
					fname = re.sub(' +', ' ', ("Unknown - "+title).translate(None, ':*?!@%$<>|+\\\"').replace('/', '-'))
				else: fname = re.sub(' +', ' ', (artist+" - "+title).translate(None, ':*?!@%$<>|+\\\"').replace('/', '-'))

				filepath = os.path.join(destdir, "%s.mp3" % (fname))
				if os.path.isfile(filepath)==True:
					plf.write("#EXTINF:,%s\n" % (artist+" - "+title))
					plf.write("%s.mp3\n" % (fname))
				else: print('Warning: "'+fname+'" was not found at download dest dir, skipping from adding')


print('Displaying runtime stat..')
print('Total '+str(la)+' audios detected')
if dnac>0: print('And server not gived download URL for '+str(dnac)+' audios.')
if sadc>0: print('Total successful downloads: '+str(sadc))
if aeac>0: print('Total already downloaded audios: '+str(aeac))
if rtec>0: print('Total terminated by error downloads: '+str(rtec))

diffr=diff(flist, rlist)

if len(diffr)>0:
	diffm=[]
	difff=[]
	for name in diffr:
		if ".mp3" in name:
			diffm.append(name)
		else:
			difff.append(name)
	if len(diffm)>0:
		print "Notice: Script found %s (maybe) excess audio files:" %(len(diffm))
		if deleteExcess==False:
			fp=codecs.open(destdir+"/"+playlist_prefix+"_deprecated.m3u8", 'w', 'utf-8')
			fp.write("#EXTM3U\n")
		for name in diffm:
				print name
				if deleteExcess==False: fp.write(name+"\n")
				else:
					os.remove(destdir+'/'+name)
		if deleteExcess==False: fp.close()
		if deleteExcess==False: print "It was deleted by server administrator. Saved to playlist deprecated."
		else:
			print "Excess deletion is enabled in config, it all were wiped"

	if len(difff)>0:
		print "Notice: Script found %s (maybe) excess files:" % len(difff)
		for name in difff:
			print name
			if deleteExcess==True: os.remove(destdir+'/'+name)
		if deleteExcess==True: print "Excess deletion is enabled in config, it all were wiped"
