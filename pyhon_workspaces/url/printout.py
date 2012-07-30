import urllib2
import cookielib
import xml.etree.ElementTree as ET

login_url = 'http://217.21.192.152:8080/catchplus/auth/signIn'
api_url = 'http://217.21.192.152:8080/catchplus/api/';
username = 'instituut01@admin.nl';
password = 'qwerty';
data = 'username=' + username + '&password=' + password

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
opener.open(login_url, data).read()






xmlCollections = opener.open(api_url + 'collection').read()
for etCollection in ET.XML(xmlCollections).findall('collection'):
    xmlCollection = ET.tostring(etCollection)
    print 'Collection id='+etCollection.attrib.get('id')
    print 'Collection dateCreated='+etCollection.find('dateCreated').text
    print 'Collection deleted='+etCollection.find('deleted').text
    print 'Collection description='+etCollection.find('description').text
    print 'Collection lastUpdated='+etCollection.find('lastUpdated').text
    print 'Collection published='+etCollection.find('published').text
    print 'Collection title='+etCollection.find('title').text
    for etCollectionBundleBundle in etCollection.findall('bundle/bundle'):
        xmlBundle = opener.open(api_url + 'bundle/' + etCollectionBundleBundle.attrib.get('id')).read()
        etBundle = ET.XML(xmlBundle)
        print '\tBundle id='+etBundle.attrib.get('id')
        print '\tBundle dateCreated='+etBundle.find('dateCreated').text
        print '\tBundle deleted='+etBundle.find('deleted').text
        print '\tBundle description='+etBundle.find('description').text
        print '\tBundle lastUpdated='+etBundle.find('lastUpdated').text
        print '\tBundle published='+etBundle.find('published').text
        print '\tBundle title='+etBundle.find('title').text
        for etBundleContentBaseContent in ET.XML(xmlBundle).findall('content/baseContent'):
            xmlBaseContent = opener.open(api_url + 'baseContent/' + etBundleContentBaseContent.attrib.get('id')).read()
            etBaseContent = ET.XML(xmlBaseContent)
            print '\t\tBaseContent id='+etBaseContent.attrib.get('id')
            print '\t\tBaseContent dateCreated='+etBaseContent.find('dateCreated').text
            print '\t\tBaseContent deleted='+etBaseContent.find('deleted').text
            print '\t\tBaseContent description='+etBaseContent.find('description').text
            print '\t\tBaseContent lastUpdated='+etBaseContent.find('lastUpdated').text
            print '\t\tBaseContent published='+etBaseContent.find('published').text
            print '\t\tBaseContent title='+etBaseContent.find('title').text                      
            print '\t\tBaseContent url='+etBaseContent.find('url').text
            print etCollection.attrib.get('id') +'/'+ etBundle.attrib.get('id')  +'/'+ etBaseContent.attrib.get('id')
            print ''
            try:
                fileBinary = opener.open(etBaseContent.find('url').text)
                fileName = fileBinary.info()['Content-Disposition'].replace('filename=','')
                open(fileName, 'wb').write(fileBinary.read())
            except: 
                pass


            
            
            
            
            
            
            