#-------------------------------------------------------------------------------
# Author    :   oyin
#
# Created   :   24/03/2018
# Copyright :   (c) oyin 2018
#-------------------------------------------------------------------------------

import ast
import datetime
import os
import re
import sys
import urllib
import urllib2


baseurl = 'https://artifactory.labs.quest.com/artifactory'
username = 'ticbuild'
password = 'AP2m78TmyafgRZs3VNowfAv8Jj7'

ticPath      = 'toad-intelligence-central/tic'
webPath      = 'toad-intelligence-central/webserver'
bundlePath   = 'toad-intelligence-central/bundle'


def buildListUrl(folderPath):
    return '{0}/api/storage/{1}?list&deep=1&listFolders=1'.format(baseurl, folderPath)


def set_artifactory_authentication():

    manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, baseurl, username, password)
    auth = urllib2.HTTPBasicAuthHandler(manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)


def quote_url(requestUrl):
    return urllib.quote(requestUrl, safe="%/:=&?~#+!$,;'@()*[]")


def getBranchName(uri):
    m = re.search('^/([^/]*)(/.*)*', uri, re.IGNORECASE)
    if m is not None:
        return m.group(1)
    else:
        return None


def getBranchAndVersion(uri):
    m = re.search(r'^/([^/]*?/\d+\.\d+\.\d+\.\d+)(/.*)*', uri, re.IGNORECASE)
    if m is not None:
        return m.group(1)
    else:
        return None


def getBranchAndRelease(uri):
    m = re.search(r'^/([^/]*?/\d+\.\d+)\.\d+\.\d+(/.*)*', uri, re.IGNORECASE)
    if m is not None:
        return m.group(1)
    else:
        return None


def initialBranchInstallerCount(branchName):
    if branchName is not None:
        if not branchInstallerCountDic.has_key(branchName):
            branchInstallerCountDic[branchName] = 0


def increaseBranchInstallerCount(branchName):
    if branchName is not None:
        initialBranchInstallerCount(branchName)
        branchInstallerCountDic[branchName] += 1


def decreaseBranchInstallerCount(branchName):
    if branchName is not None:
        initialBranchInstallerCount(branchName)
        branchInstallerCountDic[branchName] -= 1


def mockDeleteInstaller(uri, branch, branchAndVersion):
    requestUri = '{0}/{1}{2}'.format(baseurl, productPath, uri)
    # print 'Mark artifactory for deletion: {0}'.format(requestUri)
    decreaseBranchInstallerCount(branch)
    decreaseBranchInstallerCount(branchAndVersion)


def deleteArtifactory():
    for itm in branchInstallerCountDic:
        if branchInstallerCountDic[itm] == 0:
            requestUri = '{0}/{1}/{2}'.format(baseurl, productPath, itm)
            request = urllib2.Request(requestUri)
            request.get_method = lambda : 'DELETE'
            try:
                print 'Delete path {0}'.format(requestUri)
                response = urllib2.urlopen(request)
                if response.code != 204:
                    print 'Failed to delete {0} with code {1}'.format(itm, str(response.code))
            except urllib2.HTTPError as ex:
                print 'Throw exception: {0}'.format(ex)
                if ex.code == 401:
                    set_artifactory_authentication()


# Keep maximum <mBuildsToKeep> builds within <nDaysToKeep> days
def removeOldBuilds(artifactoryUrl, mBuildsToKeep, nDaysToKeep):
    print '\r\n>>> Remove build from {0}/{1}:\n'.format(baseurl, productPath)
    set_artifactory_authentication()
    response = urllib2.urlopen(quote_url(artifactoryUrl))
    responseStr = response.read().decode('utf-8').replace('"folder" : true', '"folder" : True').replace('"folder" : false', '"folder" : False')
    responseObj = ast.literal_eval(responseStr)

    for file in responseObj['files']:
        if file['uri'] == '/master/4.5.0.85':
            print file
        uri = file['uri']
        branchName = getBranchName(uri)
        branchAndVersion = getBranchAndVersion(uri)

        if file['folder']:
            initialBranchInstallerCount(branchName)
            initialBranchInstallerCount(branchAndVersion)
        else:
            increaseBranchInstallerCount(branchName)
            increaseBranchInstallerCount(branchAndVersion)
            lastModifiedDt = datetime.datetime.strptime(file['lastModified'], "%Y-%m-%dT%H:%M:%S.%fZ")
            installerDic[uri] = [uri, lastModifiedDt, branchName]

    orderedInstallerDic = sorted(installerDic.items(), key=lambda x: x[1][1], reverse=True)

    filesToKeepDic = {}

    for itm in orderedInstallerDic:
        try:
            uri = itm[0]
            lastModifiedDt = itm[1][1]
            branchName = itm[1][2]
            branchAndVersion = getBranchAndVersion(uri)

            if branchName == 'master':
                branchKey = getBranchAndRelease(uri)
                if branchKey not in filesToKeepDic:
                    filesToKeepDic[branchKey] = []
            else:
                branchKey = branchName
                if branchKey not in filesToKeepDic:
                    filesToKeepDic[branchKey] = []

                if (currentDt - lastModifiedDt).days > nDaysToKeep:
                    # delete
                    mockDeleteInstaller(uri, branchName, branchAndVersion)
                    continue

            if branchAndVersion in filesToKeepDic:
                filesToKeepDic[branchAndVersion].append(uri)
                continue
            elif len(filesToKeepDic[branchKey]) < mBuildsToKeep:
                filesToKeepDic[branchAndVersion] = [uri]
                filesToKeepDic[branchKey].append(branchAndVersion)
                continue

            # delete installer
            mockDeleteInstaller(uri, branchName, branchAndVersion)
        except Exception as ex:
            print ex

    deleteArtifactory()


if __name__ == '__main__':
    currentDt = datetime.datetime.now()

    if len(sys.argv) > 1:
        try:
            mBuildsToKeep = int(os.environ['NUMBER_TO_KEEP'])
        except KeyError:
            pass

        try:
            nDaysToKeep = int(os.environ['DAYS_TO_KEEP'])
        except KeyError:
            pass
    else:
        mBuildsToKeep = 2
        nDaysToKeep = 60


    print("\n")
    print("Number of builds to keep: " + str(mBuildsToKeep))
    print("Days of builds to keep: " + str(nDaysToKeep))

    productPath = ticPath
    installerDic = {}
    branchInstallerCountDic = {}
    removeOldBuilds(buildListUrl(productPath), mBuildsToKeep, nDaysToKeep)

    productPath = webPath
    installerDic = {}
    branchInstallerCountDic = {}
    removeOldBuilds(buildListUrl(productPath), mBuildsToKeep, nDaysToKeep)

    productPath = bundlePath
    installerDic = {}
    branchInstallerCountDic = {}
    removeOldBuilds(buildListUrl(productPath), mBuildsToKeep, nDaysToKeep)





