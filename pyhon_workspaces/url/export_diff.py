import xml.etree.ElementTree as ET
import pycurl
import cStringIO
import sys
import os

requirePublished = False
exportDir = 'd:/DIFF'
xmlActual = 'actual.xml'
xmlUser = 'user.xml'
xmlWorkspace = 'workspace.xml'

# Normal environment
#loginUrl = 'http://217.21.192.152:8080/catchplus/auth/signIn'
#apiUrl = 'http://217.21.192.152:8080/catchplus/api';

# Acceptance environment
loginUrl = 'http://workspaces.target-imedia.nl:8080/workspaces/auth/signIn'
apiUrl = 'http://workspaces.target-imedia.nl:8080/workspaces/api'


username = 'instituut01@admin.nl';
password = 'qwerty';

illegalFilenameCharacters = '\\/:*?"<>|'

if not os.path.isdir(exportDir):
    os.makedirs(exportDir)

# Authentication.
c = pycurl.Curl()
c.setopt(pycurl.COOKIEFILE, '')
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.URL, loginUrl)
c.setopt(pycurl.POSTFIELDS, 'username=' + username + '&password=' + password)
c.perform()

def userInput(question):
    rawInput = raw_input(question + " [Yes/No]: ").lower()
    if rawInput in {'y', 'yes'}:
        return True
    elif rawInput in {'n', 'no'}:
        return False
    else:
        userInput(question)

def makeUserXml():
    open(exportDir + '/' + xmlUser, 'wb').write(ET.tostring(etUser))
    print 'The difference XML is saved to: "' + exportDir + '/' + xmlUser + '".'
    print 'In difference XML change the attribute "download="true"" into "download="false"" if the download for this object is not required.'

def addUserCollection(collectionId, strDownload='true'):
    try:
        etUser.find('collection[@id="' + collectionId + '"]').attrib.get('id')
    except:
        etUser.append(ET.XML('<collection id="' + collectionId + '" download="' + strDownload + '" title="' + etWorkspace.find('collection[@id="' + collectionId + '"]/title').text + '" description="' + etWorkspace.find('collection[@id="' + collectionId + '"]/description').text + '" published="' + etWorkspace.find('collection[@id="' + collectionId + '"]/published').text + '"></collection>'))

def addUserBundle(collectionId, bundleId, strDownload='true'):
    addUserCollection(collectionId, 'false')
    try:
        etUser.find('collection[@id="' + collectionId + '"]/bundle[@id="' + bundleId + '"]').attrib.get('id')
    except:
        etUser.find('collection[@id="' + collectionId + '"]').append(ET.XML('<bundle id="' + bundleId + '" download="' + strDownload + '" title="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/title').text + '" description="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/description').text + '" published="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/published').text + '"></bundle>'))
    
def addUserBaseContent(collectionId, bundleId, baseContentId):
    addUserCollection(collectionId, 'false')
    addUserBundle(collectionId, bundleId, 'false')
    etUser.find('collection[@id="' + collectionId + '"]/bundle[@id="' + bundleId + '"]').append(ET.XML('<baseContent id="' + baseContentId + '" download="true" title="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/content/baseContent[@id="' + baseContentId + '"]/title').text + '" description="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/content/baseContent[@id="' + baseContentId + '"]/description').text + '" published="' + etWorkspace.find('collection[@id="' + collectionId + '"]/bundle/bundle[@id="' + bundleId + '"]/content/baseContent[@id="' + baseContentId + '"]/published').text + '"></baseContent>'))
    
def getWorkspace():
    # REST request all collections.
    c.setopt(pycurl.POST, 0)
    c.setopt(pycurl.URL, apiUrl + '/collection')
    response = cStringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, response.write)
    c.perform()
    etCollections = ET.XML(response.getvalue())
    etWorkspace = etCollections
    # Loop collections to get children bundles.
    for etCollection in etCollections.findall('collection'):
        collectionId = etCollection.attrib.get('id')
        collectionTitle = etCollection.find('title').text
        print 'Collection title: ' + collectionTitle + ', id: ' + collectionId + '.'
        for etBundleId in etCollection.findall('bundle/bundle'):
            bundleId = etBundleId.attrib.get('id')
            # Get child bundle.
            c.setopt(pycurl.POST, 0)
            c.setopt(pycurl.URL, apiUrl + '/bundle/' + bundleId)
            response = cStringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, response.write)
            c.perform()
            etBundle = ET.XML(response.getvalue())
            if etBundle.tag != 'error': # No permission results in error.
                bundleTitle = etBundle.find('title').text
                # Copy child bundle to 'etWorkspace'.
                etWorkspace.find('collection/bundle/bundle[@id="' + bundleId + '"]').extend(etBundle)
                print '\tBundle title: ' + bundleTitle + ', id: ' + bundleId + '.'
                # Loop bundle to get children baseContents
                for etBaseContentId in ET.XML(ET.tostring(etBundle)).findall('content/baseContent'):
                    baseContentId = etBaseContentId.attrib.get('id')
                    # Get child baseContent.
                    c.setopt(pycurl.POST, 0)
                    c.setopt(pycurl.URL, apiUrl + '/baseContent/' + baseContentId)
                    response = cStringIO.StringIO()
                    c.setopt(pycurl.WRITEFUNCTION, response.write)
                    c.perform()
                    etBaseContent = ET.XML(response.getvalue())
                    if etBaseContent.tag != 'error': # No permission results in error.
                        baseContentTitle = etBaseContent.find('title').text
                        # Copy child baseContent to 'etWorkspace'.
                        etWorkspace.find('collection/bundle/bundle/content/baseContent[@id="' + baseContentId + '"]').extend(etBaseContent)
                        print '\t\tBaseContent: ' + baseContentTitle + ', id: ' + baseContentId + '.'
    open(exportDir + '/' + xmlWorkspace, 'wb').write(ET.tostring(etWorkspace))
    print 'The Workspace XML is saved to: "' + exportDir + '/' + xmlWorkspace + '".'
    return etWorkspace

if os.path.isfile(exportDir + '/' + xmlWorkspace):
    if userInput('Use online Workspace API, and overwrite "' + xmlWorkspace + '"?'):
        etWorkspace = getWorkspace()
    else:
        etWorkspace = ET.XML(open(exportDir + '/' + xmlWorkspace, 'rb').read())
else:
    etWorkspace = getWorkspace()



if os.path.isfile(exportDir + '/' + xmlActual):
    etActual = ET.XML(open(exportDir + '/' + xmlActual, 'rb').read())
else:
    etActual = ET.XML('<list></list>')
etUser = ET.XML('<list></list>')

actualCollectionIds = []
actualBundleIds = []
actualBaseContentIds = []
for etActualCollection in etActual.findall('collection'):
    actualCollectionIds.append(etActualCollection.attrib.get('id'))
for etActualBundle in etActual.findall('collection/bundle/bundle'):
    actualBundleIds.append(etActualBundle.attrib.get('id'))
for etActualBaseContent in etActual.findall('collection/bundle/bundle/content/baseContent'):
    actualBaseContentIds.append(etActualBaseContent.attrib.get('id'))

for etWorkspaceCollection in etWorkspace.findall('collection'):
    try:
        if requirePublished == False or etWorkspaceCollection.find('published').text == 'true':
            collectionId = etWorkspaceCollection.attrib.get('id')
            if (collectionId not in actualCollectionIds):
                addUserCollection(collectionId)
    except:
        continue;        
for etWorkspaceBundle in etWorkspace.findall('collection/bundle/bundle'):
    try:
        if requirePublished == False or  etWorkspaceBundle.find('published').text == 'true':
            bundleId = etWorkspaceBundle.attrib.get('id')
            if (bundleId not in actualBundleIds):
                collectionId = etWorkspaceBundle.find('collection/collection').attrib.get('id')
                addUserBundle(collectionId, bundleId)        
    except:
        continue;
for etWorkspaceBaseContent in etWorkspace.findall('collection/bundle/bundle/content/baseContent'):
    try:
        if requirePublished == False or  etWorkspaceBaseContent.find('published').text == 'true':
            baseContentId = etWorkspaceBaseContent.attrib.get('id')
            if (baseContentId not in actualBaseContentIds):
                bundleId = etWorkspaceBaseContent.find('bundle/bundle').attrib.get('id')
                for etWorkspaceBundle in etWorkspace.findall('collection/bundle/bundle'):
                    if (etWorkspaceBundle.attrib.get('id') in bundleId):
                        collectionId = etWorkspaceBundle.find('collection/collection').attrib.get('id')
                        addUserBaseContent(collectionId, bundleId, baseContentId)
    except:
        continue;                

if os.path.isfile(exportDir + '/' + xmlUser):
    if userInput('Overwrite "' + xmlUser + '"?'):
        makeUserXml();
else:
    makeUserXml();
  
if not userInput(question="Continue download using: " + exportDir + '/' + xmlUser + "?"):
    sys.exit(0)
    
etWorkspace1 = ET.XML(open(exportDir + '/' + xmlWorkspace, 'rb').read())
etWorkspace2 = ET.XML(open(exportDir + '/' + xmlWorkspace, 'rb').read())

etUser = ET.XML(open(exportDir + '/' + xmlUser, 'rb').read())
for etUserCollection in etUser.findall('collection'):
    if etUserCollection.attrib.get('download') == 'true':
        print 'Collection title: ' + etUserCollection.attrib.get('title') + ', id: ' + etUserCollection.attrib.get('id') + '.'
        d = exportDir + '/' + etUserCollection.attrib.get('id')  + '_' +  etUserCollection.attrib.get('title')
        if not os.path.exists(d):
            os.makedirs(d)
        etWorkspaceCollection = etWorkspace1.find('collection[@id="' + etUserCollection.attrib.get('id') + '"]')    
        for children in etWorkspaceCollection:
            for childrenOfChildren in children:
                memory = childrenOfChildren.attrib.get('id')
                childrenOfChildren.clear()
                childrenOfChildren.attrib['id'] = memory
        etActual.append(etWorkspaceCollection)

    for etUserBundle in etUserCollection.findall('bundle'):
        if etUserBundle.attrib.get('download') == 'true':
            print '\tBundle title: ' + etUserBundle.attrib.get('title') + ', id: ' + etUserBundle.attrib.get('id') + '.'
            d = exportDir + '/' + etUserCollection.attrib.get('id')  + '_' +  etUserCollection.attrib.get('title') + '/' + etUserBundle.attrib.get('id')  + '_' +  etUserBundle.attrib.get('title')
            if not os.path.exists(d):
                os.makedirs(d)
            etWorkspaceBundle = etWorkspace2.find('collection/bundle/bundle[@id="' + etUserBundle.attrib.get('id') + '"]')
            for children in etWorkspaceBundle:
                for childrenOfChildren in children:
                    memory = childrenOfChildren.attrib.get('id')
                    childrenOfChildren.clear()
                    childrenOfChildren.attrib['id'] = memory
            try:
                etActual.find('collection/bundle/bundle[@id="' + etUserBundle.attrib.get('id') + '"]').extend(etWorkspaceBundle)
            except:
                etActual.find('collection[@id="' + etUserCollection.attrib.get('id') + '"]/bundle').append(etWorkspaceBundle)
            
        for etUserBaseContent in etUserBundle.findall('baseContent'):
            if etUserBaseContent.attrib.get('download') == 'true':
                print '\t\tBaseContent title: ' + etUserBaseContent.attrib.get('title') + ', id: ' + etUserBaseContent.attrib.get('id') + '.'
                d = exportDir + '/' + etUserCollection.attrib.get('id')  + '_' +  etUserCollection.attrib.get('title') + '/' + etUserBundle.attrib.get('id')  + '_' +  etUserBundle.attrib.get('title')
                if not os.path.exists(d):
                    os.makedirs(d)
                etWorkspaceBaseContent = etWorkspace.find('collection/bundle/bundle/content/baseContent[@id="' + etUserBaseContent.attrib.get('id') + '"]')
                try:
                    etActual.find('collection/bundle/bundle/content/baseContent[@id="' + etUserBaseContent.attrib.get('id') + '"]').extend(etWorkspaceBaseContent)
                except:
                    etActual.find('collection/bundle/bundle[@id="' + etUserBundle.attrib.get('id') + '"]/content').append(etWorkspaceBaseContent)

                # Try download attachment.
                try:
                    url = etActual.find('collection/bundle/bundle/content/baseContent[@id="' + etUserBaseContent.attrib.get('id') + '"]/url').text   
                    c.setopt(pycurl.POST, 0)
                    c.setopt(pycurl.URL, url)            
                    response = cStringIO.StringIO()
                    headers = cStringIO.StringIO()
                    retrievedHeaders = cStringIO.StringIO()
                    c.setopt(pycurl.WRITEFUNCTION, response.write)
                    c.setopt(pycurl.HEADERFUNCTION, headers.write)
                    c.perform()
                    filename = ''
                    for headerLine in headers.getvalue().splitlines():
                        if 'Content-disposition: filename=' in headerLine:
                            filename = headerLine.replace('Content-disposition: filename=', '')
                    open(d + '/' + etUserBaseContent.attrib.get('id') + '_' + filename, 'wb').write(response.getvalue())
                except: 
                    pass

open(exportDir + '/' + xmlActual, 'wb').write(ET.tostring(etActual))
print 'Saving "'+ xmlActual + '".'
print 'DONE'


