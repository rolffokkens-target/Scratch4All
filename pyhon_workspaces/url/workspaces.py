import os
import sys
import xml.etree.ElementTree as ET
import pycurl
import cStringIO

loginUrl = 'http://workspaces2a.target-imedia.nl:8080/workspaces/auth/signIn'
apiUrl = 'http://workspaces2a.target-imedia.nl:8080/workspaces/api'
username = 'instituut01@admin.nl'
password = 'qwerty'
baseDir = 'd:/workspace'
localRepository = 'local.xml'

# Make export directory.
if not os.path.exists(baseDir):
    os.makedirs(baseDir)
# Open local repository.
etLocalRepository = ET.XML('<list></list>')
if os.path.isfile(baseDir + '/' + localRepository):
    etLocalRepository = ET.XML(open(baseDir + '/' + localRepository, 'rb').read())
# Authentication.
c = pycurl.Curl()
c.setopt(pycurl.COOKIEFILE, '')
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.URL, loginUrl)
c.setopt(pycurl.POSTFIELDS, 'username=' + username + '&password=' + password)
c.perform()

if 'help' in sys.argv[1:] or '--help' in sys.argv[1:]:
    print (
           'ls [inclucde_non_published_bundles] [inclucde_non_published_content] \n\n'
           '  Output bundle(s) with new item(s).\n\n'
           '<bundle_id> [download] [inclucde_non_published_bundles] [inclucde_non_published_content]\n\n'
           '  Output and optionally download all new baseContents from parent bundle ID\n\n'
           '<bundle_title> [download] [inclucde_non_published_bundles] [inclucde_non_published_content]\n\n'
           '  Output and optionally download all new baseContents from parent bundle title\n\n'           
          )
    sys.exit(0)

def postRest(url):
    c.setopt(pycurl.POST, 0)
    c.setopt(pycurl.URL, url)
    response = cStringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, response.write)
    c.perform()
    return ET.XML(response.getvalue())

# Output bundle(s) with new item(s)
if 'ls' in sys.argv[1:]:
    etBundles = postRest(apiUrl + '/bundle')
    for etBundle in etBundles:
        # Published switch
        if etBundle.find('published').text == 'true' or 'inclucde_non_published_bundles' in sys.argv[1:]:
            for etBaseContentId in etBundle.findall('content/baseContent'):
                baseContentId = etBaseContentId.attrib.get('id')
                # Check if baseContent is new
                if len(etLocalRepository.findall('baseContent[@id="' + baseContentId + '"]/title')) == 0:
                    # Request baseContent
                    etBaseContent = postRest(apiUrl + '/baseContent/' + baseContentId)
                    # Published switch
                    if etBaseContent.find('published').text == 'true' or 'inclucde_non_published_content' in sys.argv[1:]:
                        print ET.tostring(etBundle) + "\n"
                        break
    sys.exit(0)

etBundles = postRest(apiUrl + '/bundle')

for argv in sys.argv[1:]:
    for etBundle in etBundles:
        if argv in (etBundle.attrib.get('id'), etBundle.find('title').text):
            print 'Request: ' + ET.tostring(etBundle) + "\n"
            for etBaseContentId in etBundle.findall('content/baseContent'):
                baseContentId = etBaseContentId.attrib.get('id')
                # Check if baseContent is new
                if len(etLocalRepository.findall('baseContent[@id="' + baseContentId + '"]/title')) == 0:
                    # Request baseContent
                    etBaseContent = postRest(apiUrl + '/baseContent/' + baseContentId)
                    # Published switch
                    if etBaseContent.find('published').text == 'true' or 'inclucde_non_published_content' in sys.argv[1:]:
                        print ET.tostring(etBaseContent) + "\n"
                        if 'download' in sys.argv[1:]:
                            etLocalRepository.append(etBaseContent)
                            # Try download attachment.
                            try:       
                                c.setopt(pycurl.POST, 0)
                                c.setopt(pycurl.URL, etBaseContent.find('url').text)            
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
                                fileDir = baseDir + '/' + etBundle.attrib.get('id')  + '-' + etBundle.find('title').text
                                if not os.path.exists(fileDir):
                                    os.makedirs(fileDir)
                                open(fileDir + '/' + filename, 'wb').write(response.getvalue())
                            except: 
                                pass                            
open(baseDir + '/' + localRepository, 'wb').write(ET.tostring(etLocalRepository))
