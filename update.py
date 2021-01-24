import json
import os
import requests


print('Started mod Update.')
instance = open('minecraftinstance.json', 'r')
instanceJson = json.load(instance)

modfiles = os.listdir('mods')
print(str.format('Found {} mods in mods-folder.', len(modfiles)))


installedAddons = instanceJson.installedAddons

for addon in installedAddons:
    displayName = addon.installedFile.displayName
    fileName = addon.installedFile.fileName
    downloadUrl = addon.installedFile.downloadUrl
    if not fileName in modfiles:
        print(str.format('Mod "{}" not found; Downloading from {}',
                         displayName, downloadUrl))
        req = requests.get(downloadUrl)
        with open(os.path.join('mods', fileName), 'wb') as f:
            f.write(req.content)
            f.close()
