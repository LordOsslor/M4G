from genericpath import exists
import json
from json.encoder import JSONEncoder
import os
import requests
import math
import sys
import argparse


parser = argparse.ArgumentParser(
    description='Automatically update Curseforge mods.')
parser.add_argument(
    '-d', help='Delete all mods not in json.', action='store_true')
parser.add_argument('-y', help='Say yes to all prompts.', action='store_true')
parser.add_argument(
    '-p', '--purge', help='Delete all mods and download them fresh.', action='store_true')
args = parser.parse_args()


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


def getInstanceFiles(addons):
    addonFiles = []
    for addon in addons:
        if not type(addon['installedFile']) == type(None):
            list.append(addonFiles, addon['installedFile'])

    return addonFiles


def getInstalledMods(addonFiles, modFiles):
    installedAddonFiles = []
    missingAddonFiles = []
    excessFiles = list.copy(modFiles)
    for addonFile in addonFiles:
        if addonFile['fileName'] in modFiles:
            list.remove(excessFiles, addonFile['fileName'])
            list.append(installedAddonFiles, addonFile)
        else:
            list.append(missingAddonFiles, addonFile)
    return installedAddonFiles, missingAddonFiles, excessFiles


def getSize(AddonFiles):
    totalSize = 0
    for missingAddonFile in AddonFiles:
        totalSize += missingAddonFile['fileLength']
    return totalSize


def main():

    querySkip = args.y
    if not exists('minecraftinstance.json'):
        print(str.format(
            '"minecraftinstance.json" not found! Current working directory is "{}"', os.getcwd()))

    if not exists('mods'):
        if querySkip or query_yes_no('Mods folder not found. Should it be generated?'):
            os.mkdir('mods')
    if args.purge:
        print('Purging mods folder:')
        for modFile in os.listdir('mods'):
            os.remove(os.path.join('mods', modFile))
            print(str.format('Deleted {}', modFile))

    # globals:
    cwd = os.getcwd()
    modFiles = os.listdir('mods')
    instance = open('minecraftinstance.json', 'r+')
    instanceJson = json.load(instance)
    if not instanceJson['installPath'] == cwd:
        instanceJson['installPath'] = cwd
        print(str.format('Install path of the modpack set to: {}', cwd))
        nam = input('Enter Modpack Name!')
        instanceJson['name'] = nam
        json.dump(instanceJson, instance)

    addons = instanceJson['installedAddons']
    addonFiles = getInstanceFiles(addons)
    installedAddonFiles, missingAddonFiles, excessFiles = getInstalledMods(
        addonFiles, modFiles)

    totalAddonCount = len(addons)
    installedAddonCount = len(installedAddonFiles)
    missingAddonCount = len(missingAddonFiles)
    excessFileCount = len(excessFiles)
    totalDownloadSize = getSize(missingAddonFiles)
    totalReadableSize = convert_size(totalDownloadSize)

    if(totalDownloadSize > 0):
        print(str.format('Found {} of {} ({}%) mods in mods-folder, missing {} mods ({}).',
                         installedAddonCount, totalAddonCount, getPercent(installedAddonCount, totalAddonCount), missingAddonCount, totalReadableSize))

        if querySkip or query_yes_no((totalReadableSize + ' of mods will be downloaded. Continue? (Y/N)')):
            fileNameList = {}
            i = 0
            alreadyDownloaded = 0
            for installedFile in missingAddonFiles:
                displayName = installedFile['displayName']
                fileName = installedFile['fileName']
                downloadUrl = installedFile['downloadUrl']
                fileLength = installedFile['fileLength']
                fileNameList[i] = fileName
                if not fileName in modFiles:
                    print(str.format('{} of {} ({} of {}, {}%) Mods downloaded; Downloading mod: "{}" ({})...',
                                     i, missingAddonCount, convert_size(alreadyDownloaded), totalReadableSize, getPercent(alreadyDownloaded, totalDownloadSize), displayName, convert_size(fileLength)))
                    req = requests.get(downloadUrl)
                    with open(os.path.join('mods', fileName), 'wb') as modFile:
                        modFile.write(req.content)
                        modFile.close()
                    i += 1
                    alreadyDownloaded += fileLength

            print(str.format('{} of {} ({} of {}, {}%) Mods downloaded', i, missingAddonCount, convert_size(
                alreadyDownloaded), convert_size(totalDownloadSize), getPercent(alreadyDownloaded, totalDownloadSize)))
            print("Successfully downloaded all mods.")

    if args.d and excessFileCount > 0:
        print('Removing excess Files:')
        totalExcessSize = 0
        for excessFile in excessFiles:
            totalExcessSize += os.path.getsize(
                os.path.join('mods', excessFile))
            print(excessFile)
        if querySkip or query_yes_no(str.format('{} ({}) mods will be deleted. Continue?',
                                                excessFileCount, convert_size(totalExcessSize))) or querySkip:
            for excessFile in excessFiles:
                os.remove(os.path.join('mods', excessFile))

    modFiles2 = os.listdir('mods')
    installedAddonFiles2, missingAddonFiles2, excessFiles2 = getInstalledMods(
        addonFiles, modFiles2)
    totalInstall = len(installedAddonFiles2) - len(missingAddonFiles2)
    totalDownload = missingAddonCount - len(missingAddonFiles2)
    totalExcess = excessFileCount - len(excessFiles2)
    print(len(missingAddonFiles2))
    print(str.format('Mod update completed.\r\nDownloaded {} mods, missing {}. Excess files deleted: {}. Total mods: {}',
                     totalDownload, len(missingAddonFiles2), totalExcess, totalInstall))


print('Started mod update.')
main()
