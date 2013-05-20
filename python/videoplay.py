#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""

++++++++++++++++++++++++

    To Do:

++++++++++++++++++++++++    

1. Interface Design

2. What happens if a conversion fails?? 

    - It keeps trying to convert it... 

++++++++++++++++++++++++

    Completed:
    
++++++++++++++++++++++++

+ Convert videos so that they have AUDIO in VLC ... ffmpeg? (convertVideo)

+ Video Quality Sucks!!! Is this just the camera??? ( HARDWARE??? )

+ First video not showing up 

    - This is happening because the videos haven't been finished, so when VLC goes to try and get them, they can't be opened and it skips to the next openNewPlayList

    - Solution: Have 3 directoryes tmp / Unprocesseds / Videos ... 

    1. Max/MSP creates the video and changes it's direcotry (or Name)... 

    2. Python over on computer #1, scans for files and if it finds any, it converts them to MOV and then, after conversion, moves them

    - The trick with this one is figuring out when FFMPEG has finished with the file... 

+  Add the videos the the playlist in random order (makeXspfPlaylistFromList)

+ Work on Web Part.... 

    - PHP recognize videos...

    - Add an object when it does... 

    - 2 PHP Scripts 1 to see if file has been modified 2 upload JSON

    -  Add Object Automatically...

+ Accepted/Rejected Videos -  MAX/MSP

+ Play Sound on New Video (playNewVideoSound)

    - Audio on VLC is disabled when we do this :(

    - Just Add a Freaking Video!!!

Impossible:

+ Send an email every hour, to make sure this is working... (There won't be any internet in the installation)

DEBUG ANNOTATIOn

* Function Is Being Called - Name of the Function

^ Function Specific Applications

$ Function Speciifc Variable

! Error

# Outisde Command

"""
# Import Standard Libraries
import os
import sys
import signal
import subprocess
import shlex
import time
from time import gmtime, strftime
from os import listdir
from os.path import isfile, join
import shutil
import optparse # Deprecated
import datetime 
import random
import json
import re
from threading import Timer

# Import Other LIbraries
import xspf     # https://github.com/alastair/xspf -- Makes Playlist File
import pyglet   # http://www.pyglet.org/download.html -- Plays Sound
import pexpect  # http://www.noah.org/wiki/Pexpect#Download_and_Installation
# Also requires FFMPEG to be installed

VIDEOS_NAME             = "videos.tsv"
RECORDED_VIDEOS_NAME    = "recorded_videos.tsv"
THUMBS_NAME             = "thumbnails_videos.tsv"
UNPROCESSED_VIDEOS_NAME = "unprocessed_videos.tsv"
VIDEOS_JSON             = "videos.json"
PLAYLIST_NAME           = "playlist.xspf"
SOUND_NAME              = "beep.wav"

MAIN_LOCATION           = ["",""]
POSSIBLE_LOCATION_1     = os.path.join("/Volumes", "user","Sites","aws-exhibition","generatedVideos")
POSSIBLE_LOCATION_2     = os.path.join("/Volumes", "Machintosh HD", "Users", "user","Sites","aws-exhibition","generatedVideos")

if  (os.path.exists(POSSIBLE_LOCATION_1)):
    MAIN_LOCATION[0]       = POSSIBLE_LOCATION_1;
elif(os.path.exists(POSSIBLE_LOCATION_2)):
    MAIN_LOCATION[0]       = POSSIBLE_LOCATION_2;
else:
    print POSSIBLE_LOCATION_1
    print POSSIBLE_LOCATION_2
    raise Exception("Couldn't Find Main Location")

MAIN_LOCATION[1]       = os.path.join("/generatedVideos")

VIDEOS_LOCATION         = ["",""]
THUMBS_LOCATION         = ["",""]
UNCONVERTED_VIDS        = ["",""]
CONVERTED_VIDS          = ["",""]
RECORDED_VIDS           = ["",""]
WEB_VIDS                = ["",""]
ASSETS_LOCATION         = ["",""]
LOGS_LOCATION           = ["",""]
DEFAULT_MAIN            = ["",""]
DEFAULT_THUMBS          = ["",""]
DEFAULT_PROCESSED       = ["",""]

for i,location in enumerate(MAIN_LOCATION):
    VIDEOS_LOCATION[i]         = os.path.join(MAIN_LOCATION[i],"videos-main")
    THUMBS_LOCATION[i]         = os.path.join(MAIN_LOCATION[i],"videos-thumbnails")
    UNCONVERTED_VIDS[i]        = os.path.join(MAIN_LOCATION[i],"videos-unprocessed")
    CONVERTED_VIDS[i]          = os.path.join(MAIN_LOCATION[i],"videos-processed")
    RECORDED_VIDS[i]           = os.path.join(MAIN_LOCATION[i],"videos-recording")
    WEB_VIDS[i]                = os.path.join(MAIN_LOCATION[i],"videos-web")
    ASSETS_LOCATION[i]         = os.path.join(MAIN_LOCATION[i],"assets")
    LOGS_LOCATION[i]           = os.path.join(MAIN_LOCATION[i],"assets", "logs")
    DEFAULT_MAIN[i]            = os.path.join(MAIN_LOCATION[i],"assets", "videos-main")
    DEFAULT_THUMBS[i]          = os.path.join(MAIN_LOCATION[i],"assets", "videos-thumbnails")
    DEFAULT_PROCESSED[i]     = os.path.join(MAIN_LOCATION[i],"assets", "videos-processed")

PLAYLIST_LOCATION       = os.path.join(ASSETS_LOCATION[0],PLAYLIST_NAME)
VLC_LOCATION            = os.path.join("/Applications", "VLC.app","Contents","MacOS","VLC")

filetypes               = ["mov","m4v","mp4"]
currentlyLooping        = True
fileList                = []
unprocessed_fileList    = []
modified_time           = 0
mountains               = 0
mountainsDirection      = True

d = False

##########################
#
#       Level #1
#
##########################\

def printCurrentTime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

logTime = str("l" + printCurrentTime());

def convertVideo(FileName, destinationFormat):
    print "* convertVideo: ", destinationFormat
    newFilename          = "_p_" + FileName[:-3] + destinationFormat
    completeFileName     = os.path.join(UNCONVERTED_VIDS[0], FileName).replace(" ", "\ ")
    completeNewFileName  = os.path.join(UNCONVERTED_VIDS[0], newFilename).replace(" ", "\ ")
    completeDestination  = os.path.join(VIDEOS_LOCATION[0], newFilename).replace(" ", "\ ")
    convertedDestination = os.path.join(CONVERTED_VIDS[0], FileName).replace(" ", "\ ")
    time.sleep(1)
    if(os.path.exists(completeDestination)):
        print " ^^ File Already Exists - ",completeDestination
        return True
    else:
        
        if(destinationFormat == "mp4"):
            video_duration = findVideoDuration(completeFileName)[1]
            #  cmd = "ffmpeg -i "+completeFileName+" -b 1500k -vcodec libx264 -preset slow -preset baseline -g 30 "+completeNewFileName
            if(video_duration > 0):
                print "^ video_duration: ",video_duration
                #cmd = "ffmpeg -i "+completeFileName+" -vcodec libx264 -preset fast -maxrate 500k -bufsize 1000k -threads 0 -acodec libfdk_aac -b:a 128k -t "+ str(video_duration-1)+" "+completeNewFileName
                cmd = "ffmpeg -i "+completeFileName+" -threads 0  -t "+ str(video_duration-1)+" "+completeNewFileName
                #cmd = "ffmpeg -i "+completeFileName+" -vcodec libx264 -preset fast -threads 0 -acodec libfdk_aac -t "+ str(video_duration-1)+" -vf scale=480:ih*480/iw -strict -2 -r 30 -pix_fmt yuv420p  "+completeNewFileName
                #cmd = "ffmpeg -i "+completeFileName+" -b 1500k -vcodec libx264 -preset slow -g 30 -t "+ str(video_duration-1)+" "+completeNewFileName
            else:
                cmd = "ffmpeg -i "+completeFileName+" -threads 0 "+completeNewFileName
                #cmd = "ffmpeg -i "+completeFileName+" -vcodec libx264 -preset fast -threads 0 -acodec libfdk_aac -vf scale=480:ih*480/iw -strict -2 -r 30 -pix_fmt yuv420p "+completeNewFileName
                #cmd = "ffmpeg -i "+completeFileName+" -vcodec libx264 -preset fast -maxrate 500k -bufsize 1000k -threads 0 -acodec libfdk_aac -b:a 128k "+completeNewFileName
                #cmd = "ffmpeg -i "+completeFileName+" -b 1500k -vcodec libx264 -preset slow -g 30 "+completeNewFileName
        if(destinationFormat == "webm"):
            video_duration = findVideoDuration(convertedDestination)[1]
            # fmpeg -i Video-2013_4_29_23_8_13.mov -b 1500k -vcodec libvpx -ab 160000 -strict -2 -f webm -g 30 _p_Video-2013_4_29_23_8_13.webm
            if(video_duration):
                print "^ video_duration: ",video_duration
                #cmd = "ffmpeg -i "+convertedDestination+" -vcodec libvpx -ab 160000 -strict -2 -f webm -t "+ str(video_duration-1)+" "+completeNewFileName
                #cmd = "ffmpeg -i "+convertedDestination+" -vcodec libvpx -ab 160000 -strict -2 -f webm -g 0 -t "+ str(video_duration-1)+" "+completeNewFileName
                cmd = "ffmpeg -i "+convertedDestination+" -codec:v libvpx -quality good -cpu-used 0 -b:v 500k -qmin 10 -qmax 42 -maxrate 500k -bufsize 1000k -threads 4 -t "+ str(video_duration-1)+" -vf scale=-1:480 -codec:a libvorbis -b:a 128k -r 30  "+completeNewFileName
            else:
                cmd = "ffmpeg -i "+convertedDestination+" -codec:v libvpx -quality good -cpu-used 0 -b:v 500k -qmin 10 -qmax 42 -maxrate 500k -bufsize 1000k -threads 4 -vf scale=-1:480 -codec:a libvorbis -b:a 128k -r 30 "+completeNewFileName
                #cmd = "ffmpeg -i "+convertedDestination+" -vcodec libvpx -ab 160000 -strict -2 -f webm -g 0 "+completeNewFileName
        print "     # ConvertVideo: ",cmd
        ## pp = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        if(destinationFormat == "mp4"): 
            checkDestination = completeFileName
        if(destinationFormat == "webm"):
            checkDestination = convertedDestination
        if(os.path.exists(checkDestination)):
            try:
                #p = pexpect.spawn(cmd)
                #indexes = ['Overwrite ?', 'No such file or directory', pexpect.EOF, pexpect.TIMEOUT]
                #index = p.expect(indexes)
                #print "^ Exit Status: ",p.exitstatus
                if(os.path.exists(completeNewFileName) is False):
                    # Let's make sure this file doesn't exist to prevent an overwirte message...
                    args = shlex.split(cmd)
                    pp = subprocess.call(args)
                else:
                    print " ! File Already Exists..."
                os.rename(completeNewFileName,completeDestination)
                if(destinationFormat == "mp4"):
                    os.rename(completeFileName,convertedDestination)
                writeToLogFile(str(FileName + " - Video conversion succsesful"))
                print " ^ video conversion done"
                return True
            except:
                writeToLogFile(str("ERROR: " + FileName + " - Couldn't convert video"))
                print " ^ video conversion failed"
                print "     Failed: Filename: ",Filename
                return False
        else: 
            print "^ video file doesn't exists"
            return False
    # Query all processes to see if FFMPEG is running
    # http://stackoverflow.com/questions/160245/which-is-the-best-way-to-get-a-list-of-running-processes-in-unix-with-python

def findVideoDuration(completeFileName):
    time.sleep(1)
    try:
            cmd = "ffprobe " + completeFileName
            print "     # findVideoDuration: ",cmd
            p = pexpect.spawn(cmd)
            indexes = ['Duration', pexpect.EOF, pexpect.TIMEOUT]
            stdout = p.read()
            index = p.expect(indexes)
            stdout += p.read()
            if(index == 0 or "Duration" in stdout):
                pattern = re.compile("[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{2}")
                m = pattern.search(stdout)
                if(m.group(0)):
                    video_duration = m.group(0).replace("Duration: ", "").replace(" ","")# String
                    total_seconds = 0
                    for i,v in enumerate(video_duration.replace(".",":").split(":")):
                        if(i == 0): # Hours
                            total_seconds = total_seconds + (int(v) * 60 *60)
                        if(i == 1): # Minutes
                            total_seconds = total_seconds + (int(v) * 60)
                        if(i == 2): # Seconds
                            total_seconds = total_seconds + int(v)
                        if(i == 3): # Miliseconds
                            total_seconds = total_seconds + (int(v)/60) 
                    return video_duration, total_seconds
                    # Run a regular expressionto find the time...
                print "^ Couldn't find pattern for duration"
                return False
            else:
                print "^ Stdout couldn't find duration"
                print stdout
                return False
    except:
        print " ^ Failed To get duration"
        return False

def createThumbnail(Filename, direcotryName):
    """
        -i = Inputfile name
        -vframes 1 = Output one frame
        -an = Disable audio
        -s 400x222 = Output size
        -ss 30 = Grab the frame from 30 seconds into the video

        cmd = "ffmpeg -i "+completeFileName+" "+completeNewFileName
        cmd = "ffmpeg -i "+completeFileName+" -vf  'thumbnail,scale=1280:720' -frames:v 1 thumb.png"
        cmd = "ffmpeg -i "+completeFileName+" -vf fps=fps=1/10 -s 1280x720 " + completeNewFileName

    """
    print " * createThumbnail"
    durationFileName    = ["","","",""]
    durationFileName[0] = os.path.join(CONVERTED_VIDS[0], Filename[3:-4] + ".mov")
    durationFileName[1] = os.path.join(VIDEOS_LOCATION[0], Filename)
    durationFileName[2] = os.path.join(CONVERTED_VIDS[0], Filename[3:-4] + ".mp4")
    if(os.path.exists(durationFileName[0])):
        # See if the .mov exists
        completeFileName = durationFileName[0]
        video_duration, total_seconds = findVideoDuration(durationFileName[0])
        if(total_seconds == None or total_seconds == 0):
            video_duration, total_seconds = findVideoDuration(durationFileName[1])
            if(total_seconds == None or total_seconds == 0):
                print " ^ Failed to get Video Duration"
    elif(os.path.exists(durationFileName[2])):
        # See if the MP4 equivalent exits
        completeFileName = durationFileName[2]
        video_duration, total_seconds = findVideoDuration(durationFileName[2])
        if(total_seconds == None or total_seconds == 0):
            video_duration, total_seconds = findVideoDuration(durationFileName[1])
            if(total_seconds == None or total_seconds == 0):
                print " ^ Failed to get Video Duration"
    else:
        print " !!! Error - File Not Found: ", durationFileName
    newFileName = Filename.replace(".mp4", "_1.png")
    completeNewFileName = os.path.join(direcotryName, newFileName)
    # See if File Exists..
    if(os.path.exists(completeNewFileName)):
        print "     ^ File ALready Exists: ",completeNewFileName
        return newFileName
    else:
        # Let's try go get duraction
        print "     ^ total_seconds: ", total_seconds
        if(total_seconds != None and total_seconds > 0):
            cmd = "ffmpeg -y -ss " + str(int(total_seconds) / 2) + " -i "+completeFileName+" -vframes 1 -s 1280x720 " + completeNewFileName
            cmd_num = 0
        else:
            # Almost Exactly the Same, but video looks into it 10 seconds...
            cmd = "ffmpeg -y -ss 1 -i "+completeFileName+" -vframes 1  -s 1280x720 " + completeNewFileName
            cmd_num = 1
        print "         # createThumbnail: ",cmd
        # Try it!
        try:
            p = pexpect.spawn(cmd)
            indexes = ['Overwrite ?', 'No such file or directory', 'Weighted P-Frames',pexpect.EOF, pexpect.TIMEOUT]
            index = p.expect(indexes)
            time.sleep(1)
            if(os.path.exists(completeNewFileName)):
                print "     ^ thumbnail creation done: ", indexes[index], " - ",cmd_num
                writeToLogFile(str(Filename + " -- thumbnail creation succsesful"))
                return newFileName
            else:
                print "     ^ Video Thumbnail Creation Failed - File Doesn't Exist - ", indexes[index], " - ",cmd_num
                print "     ^ File - ", completeNewFileName
                return False
        except:
            writeToLogFile(str("ERROR: " + Filename + " -- thumbnail creation FAILED"))
            print "     ^ video thumbnail creation failed(2) - File DID NOT Exist"
            return False

def openNewPlayList(PLAYLIST_LOCATION):
    if(d):
        print "* openNewPlayList"
    SAVED_PATH = os.getcwd()
    os.chdir("/")
    # Output Files
    killAll("VLC")
    p = callVideo(PLAYLIST_LOCATION[0], VLC_LOCATION)
    # Kill all Processes by VLC Media Player
    # Yes my dear reader, this is ugly and unefficient but, 
    #   1. The alternative was complicated
    #   2. It might help solve anything that has been left behind
    os.chdir(SAVED_PATH)

def listFilesInDirecotry(DIRECTORY, filetypes):
    if(d):
        print "* listFilesInDirecotry"
    allfiles = [ f for f in listdir(DIRECTORY) if isfile(join(DIRECTORY,f)) ]
    returnedFiles = []
    for f in allfiles:
        for filetype in filetypes:
            if f.endswith(filetype):
                returnedFiles.append([f, os.path.getmtime(os.path.join(DIRECTORY,f))])
    # Sort the files by Modified Time, reverse (MOST RECENT FIRST), and return...
    returnedFiles = sorted(returnedFiles, key=lambda Key: Key[1],reverse=True)
    if(d):
        print " * END listFilesInDirecotry"
    return returnedFiles

def makeTSVfromList(array,FileName,TSV_Location):
    if(d):
        print "* makeTSVfromList"
    tsv_file = open(os.path.join(TSV_Location,FileName),"w")
    for l in array:
        for f in l:
            tsv_file.write(str(f) + "\t")
        tsv_file.write("\n")
    tsv_file.close()

def makeJSONfromLIst(array,FileName,JSON_Locastion):
    if(d):
        print "*    makeJSONfromLIst"
    json_file = open(os.path.join(JSON_Locastion, FileName), "w")
    json_data = json.dumps(array)
    json_file.write(json_data)
    json_file.close()
    print " ^^^ New Json Filed Created"
    
def readTSVandReturnList(FileName,TSV_Location):
    if(d):
        print "* readTSVandReturnList"
    returnList = []
    tsv_file = open(os.path.join(TSV_Location,FileName),"r")
    for line in tsv_file:
        splt = line.rstrip('\n').split("\t")
        returnList.append([splt[0], splt[1]])
    return returnList

def moveRecordedVideosToUnprocessed(FileName,TSV_Location, time):
    # These are the videos created by MAX. 
    # Max creates a TEXT file with all these videos... 
    # When a video file is in this text file, it means it has been already recorded....
    if(d):
        print "^ moveRecordedVideosToUnprocessed()"
    recorded_videos = readTSVandReturnList(FileName,TSV_Location)
    if(d):
        print "^ Recorded Videos: ", recorded_videos
    modified_time = os.path.getmtime(os.path.join(TSV_Location, FileName))
    if(d):
        print "^ Modified Time: ",modified_time
    for video in recorded_videos:
        oldFileName = os.path.join(RECORDED_VIDS[0], video[0])

        if(video[1] == "1"):
            newFileName = os.path.join(UNCONVERTED_VIDS[0], str(video[0][:-4] + "_r_" + video[0][-4:]))
            futureFileName = os.path.join(CONVERTED_VIDS[0], str(video[0][:-4] + "_r_" + video[0][-4:]))
        else:
            newFileName = os.path.join(UNCONVERTED_VIDS[0], str(video[0]))
            futureFileName = os.path.join(CONVERTED_VIDS[0], str(video[0]))
        # See if it exists
        if(os.path.exists(newFileName)):
            if(d):
                print "^ File Already Has been Moved"
        elif(os.path.exists(futureFileName)):
            if(d):
                print "^ File has Already Been Converted"
        elif(os.path.exists(oldFileName)):
            os.rename(oldFileName,newFileName)
            writeToLogFile(str(video[0] + " Moved To Unprocessed"))
        else:
            writeToLogFile(str("ERROR: " + video[0] + " - Couln't Find File to move"))
        if(d):
            print " ^ File Moved: ", video[0]
    return modified_time


def makeXspfPlaylistFromList(array,FileName,PLAYLIST_DIRECTORY,VIDEOS_LOCATION):
    if(d):
        print "* makeXspfPlaylistFromList"
    x = xspf.Xspf(title="AWS", creator="thejsj")

        # Add First Track
    tr1 = xspf.Track()
    tr1.location = "file://" + os.path.join(VIDEOS_LOCATION, array[0][0])
    x.add_track(tr1)

    # Mix up the array
    shuffleArray = [ i+1 for i,a in enumerate(array[1:])]
    random.shuffle(shuffleArray)

    for i,t in enumerate(array[1:]):
        tr1 = xspf.Track()
        tr1.location = "file://" + os.path.join(VIDEOS_LOCATION, array[shuffleArray[i]][0])
        x.add_track(tr1)

    playlist_file = open(os.path.join(PLAYLIST_DIRECTORY,FileName),"w")
    playlist_file.write(x.toXml().replace("ns0:",""))
    playlist_file.close()


def playNewVideoSound(FileName,DIRECTORY):
    if(d):
        print "* playNewVideoSound"
    SAVED_PATH = os.getcwd()
    os.chdir(DIRECTORY)
    def playSound():
        pyglet.resource.path = ['.']
        pyglet.resource.reindex()
        sound = pyglet.resource.media(FileName)
        sound.play()
        pyglet.app.run()
        time.sleep(1)
    try:
        playSound()
    except:
        try:
            playSound()
        except:
            try:
                playSound()
            except:
                pass
    os.chdir(SAVED_PATH)

def updateMountains():
    global mountainsDirection
    global mountains
    if(mountainsDirection is True):
        mountains += 1
    else:
        mountains = mountains - 1
    if(mountainsDirection is True and mountains >= 20):
        mountainsDirection = False
    if(mountainsDirection is False and mountains <= 0):
        mountainsDirection = True
    for i in range(mountains):
        print "-",
    print ""

def writeToLogFile(message):
    global logTime
    with open(os.path.join(LOGS_LOCATION[0],str(logTime + ".log")), "a") as f:
        writeString = str(printCurrentTime()) + "\t" + message + "\n"
        f.write(writeString)
        f.close()

def clearAll():
    files = [VIDEOS_NAME ,RECORDED_VIDEOS_NAME,THUMBS_NAME,UNPROCESSED_VIDEOS_NAME,VIDEOS_JSON]
    for f in files: 
        open(os.path.join(ASSETS_LOCATION[0], f), 'w').close()

    locations = [VIDEOS_LOCATION, UNCONVERTED_VIDS, CONVERTED_VIDS, RECORDED_VIDS,THUMBS_LOCATION]
    for path in locations:
        for (dirpath, dirname, filenames) in os.walk(path[0]):
            for f in filenames:
                try:
                    if(os.path.exists(os.path.join(path[0], f))):
                        os.remove(os.path.join(path[0], f))
                    else:
                        print "File Already Deleted: ",f
                except:
                    print "Couldn't Erase File: ", f
            for d in dirname:
                directory = os.path.join(path[0],d)
                try:
                    if(d):
                        print directory
                    if(os.path.exists(directory)):
                        shutil.rmtree(directory)
                    else:
                        if(d):
                            print "File Already Deleted - Level 2: ",f
                except:
                    print "Couldn't Erase File - Level 2: ", f

def restoreDefault(option, opt, value, parser):
    default_locations = [
        [DEFAULT_MAIN[0],VIDEOS_LOCATION],
        [DEFAULT_PROCESSED[0],CONVERTED_VIDS],
        [DEFAULT_THUMBS[0],THUMBS_LOCATION]
    ]
    for d in default_locations:
        shutil.copytree(d[0],d[1])
            

##########################
#
#       Level #2
#
##########################


def searchVideosMakePlayList(VIDEOS_LOCATION, ASSETS_LOCATION, PLAYLIST_LOCATION, VIDEOS_NAME, PLAYLIST_NAME, videoFiles, filetypes):

    # Second, generate a TSV with all those videos
    makeTSVfromList(videoFiles,VIDEOS_NAME ,ASSETS_LOCATION)

    # Read that TSV file and turn it into an array
    fileList = readTSVandReturnList(VIDEOS_NAME ,ASSETS_LOCATION)

    # Generate an .xspf from those videos and play it
    #makeXspfPlaylistFromList(fileList, PLAYLIST_NAME, ASSETS_LOCATION, VIDEOS_LOCATION)

    # Play Sound
    #playNewVideoSound(SOUND_NAME,ASSETS_LOCATION)

    # Play these videos
    #time.sleep(1) #Let's make sure the video file is actually created...
    #openNewPlayList(PLAYLIST_LOCATION)

    return fileList


def startSniffingForNewVideos(fileList, modified_time):
    if(d):
        print "* startSniffingForNewVideos"

    # Move recorded videos to Unprocessed
    modified_time = moveRecordedVideosToUnprocessed(RECORDED_VIDEOS_NAME, ASSETS_LOCATION[0], modified_time)

    # From now on, ad infinitum, you will check VIDEOS_LOCATION for new VIDEOS_LOCATION
    newVideoFiles = listFilesInDirecotry(VIDEOS_LOCATION[0],filetypes)

    analyzeNVF = []
    for f in newVideoFiles:
        analyzeNVF.append(f[0])

    analyzeFL = []
    for f in fileList:
        analyzeFL.append(f[0])

    comparrision = [i for i, j in zip(analyzeNVF, analyzeFL) if i == j]
    if(d):
        print "^ newVideoFiles:",newVideoFiles
        print "^ fileList:",fileList
        print "^ comparrision:",comparrision
        for f in fileList:
            print "^^    file:",f[0]," - ",f[1]
    if len(comparrision) == len(analyzeNVF) and len(comparrision) == len(analyzeFL):
        print "^    No Change to Video Direcotry - ", printCurrentTime(), " - ",len(fileList)
    # IF you find a new video
    else:
        if(d):
            print "^ len-comparrision:",len(comparrision)
            print "^ len-newVideoFiles:",len(newVideoFiles)
            print "^ len-fileList:",len(fileList)
        print
        print "+++ Videos Added +++ - ", printCurrentTime()
        print 

        # Search Videos, make a TSV, Make Playlist and Open the Playlist...
        fileList = searchVideosMakePlayList(VIDEOS_LOCATION[0], ASSETS_LOCATION[0], PLAYLIST_LOCATION[0], VIDEOS_NAME, PLAYLIST_NAME, newVideoFiles, filetypes)
    return fileList, modified_time
    # Look Every 10 Seconds

##########################
#
#       Level #3
#
##########################

def startRegistring(fileList, modified_time):

    # Move recorded videos to Unprocessed
    modified_time = moveRecordedVideosToUnprocessed(RECORDED_VIDEOS_NAME, ASSETS_LOCATION[0], modified_time)

    # First of all, grab a list of all videos avalialble in VIDEOS_LOCATION
    videoFiles = listFilesInDirecotry(VIDEOS_LOCATION[0],filetypes)

    # Search Videos, make a TSV, Make Playlist and Open the Playlist...
    fileList = searchVideosMakePlayList(VIDEOS_LOCATION[0], ASSETS_LOCATION[0], PLAYLIST_LOCATION[0], VIDEOS_NAME, PLAYLIST_NAME, videoFiles, filetypes)

    # Be on the Look out for videos
    return fileList, modified_time
    #startSniffingForNewVideos(fileList)

def convertVideos():
    # First of all, grab a list of all videos avalialble in VIDEOS_LOCATION
    unprocessedVideoFiles = listFilesInDirecotry(UNCONVERTED_VIDS[0],filetypes)

    # Second, generate a TSV with all those videos
    makeTSVfromList(unprocessedVideoFiles,UNPROCESSED_VIDEOS_NAME,ASSETS_LOCATION[0])

    # Read that TSV file and turn it into an array
    unprocessed_fileList = readTSVandReturnList(UNPROCESSED_VIDEOS_NAME,ASSETS_LOCATION[0])

    failedFiles = []

    # Get all the videos in unprocessed_fileList and convert them
    if(d):
        print "^    unprocessed_fileList: ",unprocessed_fileList
    if(len(unprocessed_fileList) > 0):
        for video in unprocessed_fileList:
            if(video[0].find("_p_")):
                print "^ VIDEO TO BE CONVERTED:", video[0]
                videoConverted = convertVideo(video[0],"mp4")
                if(videoConverted):
                    print " ^^^ Video Conversion to MP4 succsesful"
                #videoConvertedWebm = convertVideo(video[0],"webm")
                #if(videoConvertedWebm):
                #    print " ^^^ Video Conversion to WebM succsesful"
    else:
        print "^    No Videos To Convert - ", printCurrentTime(), " - ",len(fileList)

def convertToWeb(failedList):
    # THIS NEEDS to recognize if these thumbnails have already been done....


    # First of all, grab all the videos that have already been thumnailed...
    thumbsList = readTSVandReturnList(THUMBS_NAME, ASSETS_LOCATION[0])
    newThumbsList = thumbsList;

    # Seconnd, grab a TSV with videos avialable in VIDEOS_LOCATION that don't have the "REJECTED Tag"
    fileList = readTSVandReturnList(VIDEOS_NAME, ASSETS_LOCATION[0])

    noThumbnailsCreated = filter( lambda x: (not(x in thumbsList)), fileList)
    if(d):
        print "^    noThumbnailsCreated for: ", len(noThumbnailsCreated);
        print "^    ",noThumbnailsCreated;

    # Compare them and for all the videos that do not have thumnails, create them...
    if(len(noThumbnailsCreated) != 0):
        for File in noThumbnailsCreated: 
            inFailedFiles = False
            for i,ff in enumerate(failedList): 
                if(ff[0] == File[0]):
                    inFailedFiles = True
                    break
            if(inFailedFiles and int(random.uniform(1, 10)) != 1):
                thumb_filename = os.path.join(THUMBS_LOCATION[0], File[0].replace(".mp4", "_1.png"))
                if(os.path.exists(thumb_filename)):
                    print " ^ File failed but now Exists: ", File[0]
                    File.append(newFileName)
                    newThumbsList.append(File)
                    try:
                        index = failedList.index(File)
                        failedList.pop(index)
                    except:
                        try:
                            for i,ff in enumerate(failedList): 
                                if(ff[0] == File[0]):
                                    failedList.pop(i)
                                    break
                        except:
                            print "Coudln't Remove File"
                else:
                    print " ^ This File has Previously Failed: ", File[0]
            else:
                if(inFailedFiles):
                    print "Trying Again: ", File[0], " / ", File[0].replace(".mp4", "_1.png")
                # Create a Directory...
                """
                direcotryName = os.path.join(THUMBS_LOCATION[0], File[0][:-4])
                if not os.path.exists(direcotryName):
                    os.makedirs(direcotryName)
                """
                print "     -- Create thumnbnails : ",File[0]
                try:
                    newFileName = createThumbnail(File[0], THUMBS_LOCATION[0]);
                    if(newFileName != False):
                        File.append(newFileName)
                        newThumbsList.append(File)
                        print " ^ File Added To List"
                    else:
                        failedList.append(File)
                except:
                    print " ^ Failed to TRY to create a thumbnail for file"
        if(d):
            for dirname, dirnames, filenames in os.walk(THUMBS_LOCATION[0]):
                # print path to all subdirectories first.
                for subdirname in dirnames:
                        print subdirname
        # Write a New TSV FIle
        makeTSVfromList(newThumbsList,THUMBS_NAME, ASSETS_LOCATION[0])
        if(d):
            print "newThumbsList"
            print newThumbsList
        # Build Dictionary
        newFileList = []
        if(len(newThumbsList) > 0):
            for i,File in enumerate(newThumbsList):
                newDictionary = {};
                newDictionary["id"] = str(i)
                newDictionary["videoLocation"] = str(os.path.join(VIDEOS_LOCATION[1], File[0]))
                webmLocation = os.path.join(VIDEOS_LOCATION[0], str(File[0][:-3] + "webm"))
                print webmLocation
                if(os.path.exists(webmLocation)):
                    newDictionary["webmLocation"] = os.path.join(VIDEOS_LOCATION[1], str(File[0][:-3] + "webm"))
                try:
                    newDictionary["thumbLocation"] = str(os.path.join(THUMBS_LOCATION[1], File[2]))
                except:
                    newDictionary["thumbLocation"] = str(os.path.join(THUMBS_LOCATION[1], str(File[0][:-4] + "_1.png")))
                newDictionary["lastModified"]  = str(os.path.join(File[1]))
                newDictionary["accepted"]      = "1" if "_r_" in File[0] else "0" # 0 = Accepted / 1 = Rejected
                newFileList.append(newDictionary)
        # Second, Make a JSON with all the videos with thumbnails and put them in our ASSETS...
        # There should now be an array with all thumbnailedVideos...
        # Also, make a TSV with all these videos in order to read it later...
        makeJSONfromLIst(newFileList, VIDEOS_JSON, ASSETS_LOCATION[0])

##########################
#
#       Level #4 
#
##########################

def main(fileList):

    # OPTIONS PARSER
    def startRegistringParse(option, opt, value, parser):
        global fileList, modified_time
        print "* startRegistring()"
        # This will be the function running on our first computer
        # Register New Entries and play them when you have them... 
        # Also, create a new playlist
        fileList,modified_time = startRegistring(fileList, modified_time)
        while True:
            try: 
                fileList = startSniffingForNewVideos(fileList, modified_time)
                time.sleep(1)
            except:
                print "ERROR: Couldn't startRegistring()"
                time.sleep(2)

    def convertVideosParse(option, opt, value, parser): 
        print "* convertVideos()"
        while True:
            try: 
                convertVideos()
                time.sleep(1)
            except:
                print "ERROR: Couldn't convertVideos()"
                time.sleep(2)

    def convertToWebParse(option, opt, value, parser):
        print "* convertToWeb()"
        failedList = []
        while True:
            try: 
                convertToWeb(failedList)
                time.sleep(1)
            except:
                print "ERROR: Couldn't ConverToWeb()"
                time.sleep(2)

    def runAllThreeProcesses(option, opt, value, parser):
        global fileList, modified_time
        print "* runAllThreeProcesses()"
        fileList, modified_time = startRegistring(fileList, modified_time)
        failedList = []
        while True:
            try:
                updateMountains()
                fileList, modified_time = startSniffingForNewVideos(fileList, modified_time)
                convertVideos()
                convertToWeb(failedList)
                time.sleep(1)
            except:
                print "ERROR: Couldn't runAllThreeProcesses()"
                print "Unexpected error:", sys.exc_info()[0]
                time.sleep(2)
    def clearAllParse(option, opt, value, parser):
        print "* clearAll()"
        clearAll()

    def runInQuietMode(option, opt, value, parser):
        if(d):
            print "^ Running in Quiet Mode"
        d = False

    def runInVerboseMode(option, opt, value, parser):
        if(d):
            print "^ Running in Verbose"
        d = True

    parser = optparse.OptionParser()
    parser.add_option("-r","--register", action="callback", callback=startRegistringParse, help="Runs on Computer #1 - Plays videos in VIDEOS_LOCATIOn and Sniffs out for new videos. Generates and plays a new playlist when it finds one.")
    parser.add_option("-c","--convert",  action="callback", callback=convertVideosParse, help="Runs on Computer #2 - Sniffs out for unprocessed videos, converts them and moves them.")
    parser.add_option("-k","--clear",  action="callback", callback=clearAllParse, help="Delete All Files")
    parser.add_option("-d","--default",  action="callback", callback=restoreDefault, help="Restore Default Files")
    parser.add_option("-w","--convertToWeb",  action="callback", callback=convertToWebParse, help="Runs on Computer #3  - Sniffs out for new processed videos, converts them to a web format and moves them.")
    parser.add_option("-a","--all",  action="callback", callback=runAllThreeProcesses, help="Runs all Processes, leaving one second in between")
    parser.add_option("-q","--quiet",  action="callback", callback=runInQuietMode, help="No Debugging Messages")
    parser.add_option("-v","--verbose",  action="callback", callback=runInVerboseMode, help="Includes Debugging messages.")
    (options, arguments) = parser.parse_args()

    if options is None:
        print "A mandatory option is missing"
        parser.print_help()
        print "Options Provided:"
        print options
    exit(-1)


if __name__ == "__main__":
    main(fileList)