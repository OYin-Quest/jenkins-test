#-------------------------------------------------------------------------------
# Author    :   oyin
#
# Created   :   May 8, 2015
# Modified  :   July 17, 2015
# Copyright :   (c) oyin 2018
#-------------------------------------------------------------------------------

import ast
import re
import os
import datetime
import shutil
import sys
import urllib

jenkinsTICURL = 'http://ticjenkins.skytapbuilddb.local:8080/tic/job/datahub.main/label=HubWin7x64/api/python?tree=allBuilds[number,url]'
jenkinsAdminConsoleUrl = 'http://ticjenkins.skytapbuilddb.local:8080/tic/job/adminconsole.main/api/python?tree=allBuilds[number,url]'
jenkinsWebServerUrl = 'http://ticjenkins.skytapbuilddb.local:8080/tic/job/webserver.main/api/python?tree=allBuilds[number,url]'
jenkinsBundleUrl = 'http://ticjenkins.skytapbuilddb.local:8080/tic/job/ticserverbundle.main/api/python?tree=allBuilds[number,url]'
jenkinsDecisionPointUrl = 'http://ticjenkins.skytapbuilddb.local:8080/tic/job/decisionpoint.main/api/python?tree=allBuilds[number,url]'
jenkinsKeptBuilds = []

ticPattern = '^Toad.*x64.*msi$'
adminConsolePattern = '^Toad.*AdminConsole.*msi$'
webServerPattern = '^Toad.*WebServer.*msi$'
decisionPointPattern = '^Toad.*Point.*msi$'
serverBundlePattern = '^Toad.*ServerInstaller.*exe$'
masterPattern = "^Toad.*-\d+\.\d+\.\d+\.\d+\.(msi|exe)$"

maxBuilds = None
maxDays = None
removeDays = 90

# Check file modify date
def isInRecentNDays(mDateTime, nDays):
    pastDays = (datetime.datetime.now() - mDateTime).days
    return pastDays <= nDays

# Is build being kept forever in Jenkins
def isJenkinsKeptBuild(buildInstallerName):
    return jenkinsKeptBuilds.__contains__(buildInstallerName)

# Get installer branch info
def getInstallerBranchInfo(installerName):
    pattern = 'Toad(.*)\.\d+\.(msi|exe)'
    m = re.match(pattern, installerName, re.IGNORECASE)
    if m is None:
        return "NULL"
    else:
        return m.group(1)

# Get artifacts by regex expression from those jobs which are kept by Jenkins    
def getJenkinsKeptBuilds(jenkinsUrl, artifactRegex):
    print("\r\n>>> Get kept builds from: " + jenkinsUrl)
    content = urllib.urlopen(jenkinsUrl).read().decode('utf-8')
    jenkinsBuilds = ast.literal_eval(content)
    
    for build in jenkinsBuilds['allBuilds']:
        try:
            buildObj = ast.literal_eval(urllib.urlopen(build['url'] + 'api/python').read().decode('utf-8'))
            if buildObj['result'] != 'FAILURE' and buildObj['keepLog']:
                for artifact in buildObj['artifacts']:
                    fileName = artifact['fileName']
                    m = re.match(artifactRegex, fileName, re.I)
                    if m is None:
                        continue
                    else:
                        jenkinsKeptBuilds.append(fileName)
        except Exception as e:
            print(e)

def removeOldBuilds(oldBuildLocation, installerPattern, mBuilds, nDays):
    print("\r\n>>> Check installers in: " + oldBuildLocation)
    installerDic = {}
    for file in os.listdir(oldBuildLocation):
        try:
            msiFile = None
            filePath = os.path.join(oldBuildLocation, file)
            if os.path.isfile(filePath):
                # If it is a file
                m = re.match(installerPattern, file, re.I)
                if m is not None:
                    mDate = datetime.datetime.fromtimestamp(os.path.getmtime(filePath))
                    installerDic[filePath] = [mDate, file]
                else:
                    print("  *****not an installer file, delete it: " + filePath)
                    os.remove(filePath)
                    continue
            else:
                # If it is a folder
                for subFile in os.listdir(filePath):
                    m = re.match(installerPattern, subFile, re.I)
                    if m is not None:
                        msiFile = subFile
                        break;
                
                if msiFile is None:
                    print("  *****delete folder since installer file doesn't exist in: " + filePath)
                    shutil.rmtree(filePath)
                    continue
                else:
                    mDate = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(filePath, msiFile)))
                    installerDic[filePath] = [mDate, msiFile]
        except Exception as e:
            print(e)
            pass
          
    # Sort files by modify date
    orderFiles = sorted(installerDic.items(), key=lambda x:x[1][0], reverse=True)
    
    filesToKeptDic = {}
    for itm in orderFiles:
        try:
            keyName = itm[0]
            installerName = itm[1][1]
            modifyDate = itm[1][0]
            branchInfo = getInstallerBranchInfo(installerName)
            
            if branchInfo not in filesToKeptDic:
                filesToKeptDic[branchInfo] = []
            
            # If build exists longer than removeDays
            if not isInRecentNDays(modifyDate, removeDays):
                m = re.match(masterPattern, installerName, re.I)
                # If build is not master build
                if m is None:
                    if os.path.isfile(keyName):
                        print("  ****Delete file by calling os.remove(keyName): " + keyName)
                        os.remove(keyName)
                    else:
                        print("  ****Delete folder by calling shutil.rmtree(keyName): " + keyName)
                        shutil.rmtree(keyName)
                    continue
			
            # mBuilds per branch to keep
            if mBuilds is not None:
                if len(filesToKeptDic[branchInfo]) < mBuilds:
                    filesToKeptDic[branchInfo].append(installerName)
                    continue
            
            # nDays to keep
            if nDays is not None:
                if isInRecentNDays(modifyDate, nDays):
                    filesToKeptDic[branchInfo].append(installerName)
                    continue 
            
            '''
            # build which was kept forever in Jenkins
            if jenkinsKeptBuilds.__contains__(installerName):
                filesToKeptDic[branchInfo].append(installerName)
                continue
            '''
			
            if os.path.isfile(keyName):
                print("  ****Delete file by calling os.remove(keyName): " + keyName)
                os.remove(keyName)
            else:
                print("  ****Delete folder by calling shutil.rmtree(keyName): " + keyName)
                shutil.rmtree(keyName)
        except Exception as e:
            print(e)
                    
if __name__ == '__main__':
    print(datetime.datetime.now())
    
    inputParams = sys.argv
    
    if len(inputParams) > 1:
        # No need to check whether build is marked as 'Keep forever' on Jenkins
        '''
        getJenkinsKeptBuilds(jenkinsTICURL, ticPattern)
        getJenkinsKeptBuilds(jenkinsAdminConsoleUrl, adminConsolePattern)
        getJenkinsKeptBuilds(jenkinsWebServerUrl, webServerPattern)
        getJenkinsKeptBuilds(jenkinsDecisionPointUrl, decisionPointPattern)
        getJenkinsKeptBuilds(jenkinsBundleUrl, serverBundlePattern)
        
        print("====================Builds kept in Jenkins====================")
        print(jenkinsKeptBuilds)
        '''
        try:
            maxBuilds = int(os.environ['NUMBER_OF_BUILDS'])
        except KeyError:
            pass
        
        try:  
            maxDays = int(os.environ['DAY_OF_BUILDS'])
        except KeyError:
            pass
		
        try:
            removeDays = int(os.environ['DAYS_TO_REMOVE'])
        except KeyError:
            pass
		
        print("\nNumber of builds to keep: " + str(maxBuilds))
        print("Days of builds to keep: " + str(maxDays))
        print("Days of builds to remove: " + str(removeDays))
        
        for i in range(1, len(inputParams)):
            ticLocation = inputParams[i] + r'\TIC'
            adminConsoleLocation = inputParams[i] + r'\AdminConsole'
            webServerLocation = inputParams[i] + r'\WebServer'
            bundleLocation = inputParams[i] + r'\ServerInstaller'
            decisionPointLocation = inputParams[i] + r'\DecisionPoint'
            
            removeOldBuilds(ticLocation, ticPattern, maxBuilds, maxDays)
            removeOldBuilds(adminConsoleLocation, adminConsolePattern, maxBuilds, maxDays)
            removeOldBuilds(webServerLocation, webServerPattern, maxBuilds, maxDays)
            removeOldBuilds(decisionPointLocation, decisionPointPattern, maxBuilds, maxDays)
            removeOldBuilds(bundleLocation, serverBundlePattern, maxBuilds, maxDays)
    
    print(datetime.datetime.now())
