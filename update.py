import json
import os
import requests
import math
import sys


def convert_size(size_bytes):
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def getPercent(p, q):
    if q == 0:
        return 100
    return round((p / q) * 100)


print('Started mod Update.')
instance = open('minecraftinstance.json', 'r')
instanceJson = json.load(instance)
installedAddons = instanceJson['installedAddons']
totalModCount = len(installedAddons)

modfiles = os.listdir('mods')
installedModCount = len(modfiles)
print(str.format('Found {} of {} ({}%) mods in mods-folder.',
                 installedModCount, totalModCount, getPercent(installedModCount, totalModCount)))
downloadCount = totalModCount - installedModCount

totalLength = 0
for addon in installedAddons:
    fileName = addon['installedFile']['fileName']
    if not fileName in modfiles:
        totalLength += addon['installedFile']['fileLength']
totalSize = convert_size(totalLength)
if not query_yes_no((totalSize + ' of mods will be downloaded. Continue? (Y/N)')):
    os.abort()

i = 0
alreadyDownloaded = 0
for addon in installedAddons:
    installedFile = addon['installedFile']
    displayName = installedFile['displayName']
    fileName = installedFile['fileName']
    downloadUrl = installedFile['downloadUrl']
    fileLength = installedFile['fileLength']
    if not fileName in modfiles:
        print(str.format('{} of {} ({}% of {}) Mods downloaded; Downloading mod: "{}" ({})...',
                         i, downloadCount, getPercent(alreadyDownloaded, totalLength), convert_size(totalLength), displayName, convert_size(fileLength)))
        req = requests.get(downloadUrl)
        with open(os.path.join('mods', fileName), 'wb') as f:
            f.write(req.content)
            f.close()
        i += 1
        alreadyDownloaded += fileLength
