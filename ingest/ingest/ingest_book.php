<?php
require 'ingest_include.php';
require includedir . 'ingest_convert2path.php';
require 'ingest_compute_request.php';
list($bookdir, $filename, $extension) = bfe_parameters();
$pages = array();
if ($extension == 'jpg')
  $dir = jpegdir($bookdir);
else if ($extension == 'tif')
  $dir = tiffdir($bookdir);
else if ($extension == 'ppm')
  $dir = ppmdir($bookdir);
if (is_dir($dir) && is_readable($dir))
{
  foreach (scandir($dir) as $dirobj)
  {
    if
    (
            $dirobj != '.'
            && $dirobj != '..'
            && is_readable($dir . '/' . $dirobj)
            && is_file($dir . '/' . $dirobj)
            && strtolower(pathinfo($dir . '/' . $dirobj, 4)) == $extension
    )
      $pages[] = pathinfo($dirobj, 8);
  }
}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
  <head>
  </head>
  <body>
    <a href="ingest_file.php?path=/<?php print $bookdir?>">Back</a>
    <title>Ingest Fields</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel='stylesheet' type='text/css' href='../include/ingest_basic_style.css'/>
    <div id='div_pages'></div>
      <div><button style="width: 200px;" onclick="compute_selection()">Compute selection</button></div>
      <div><button style="width: 200px;" onclick="compute_all()">Compute all</button></div>
    <div id='div_output'>
      <p>Compute requests</p>
      <textarea id="ta_output" rows="10" cols="30" disabled="disabled"></textarea>
    </div>
    <script type='text/javascript'>

      var bookdir = '<?php print $bookdir; ?>';
      var filename = '<?php print $filename; ?>';
      var extension = '<?php print $extension; ?>';
      eval('pages=<?php print json_encode($pages); ?>');

      var html = '';
      html += '<p>Pages</p>';
      html += '<select id="sel_pages" size="15" multiple="multiple">';
      for (var key in pages)
        html += '<option selected="selected" value="' + pages[key] + '">' + pages[key] + '</option>';
      html += '</select><br>';
      document.getElementById('div_pages').innerHTML = html;

      function compute_all()
      {
        for (var key in pages)
          document.getElementById('ta_output').innerHTML += http_request(make_query('ingest_compute_request1.php', [['bookdir',bookdir],['filename',pages[key]],['extension',extension]])) + '\n';
      }

      function compute_selection()
      {
        var $spages = document.getElementById('sel_pages').options
        for (var key in $spages)
        {
          if ($spages[key].selected)
            document.getElementById('ta_output').innerHTML += http_request(make_query('ingest_compute_request1.php', [['bookdir',bookdir],['filename',$spages[key].value],['extension',extension]])) + '\n';
        }
      }

      function http_request(url)
      {
        if (window.XMLHttpRequest)
          xmlhttp=new XMLHttpRequest();
        else
          xmlhttp=new ActiveXObject('Microsoft.XMLHTTP');
        xmlhttp.open('GET', url, false);
        xmlhttp.send();
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
          return xmlhttp.responseText;
        else
          alert('xmlhttp error\nreadyState: ' + xmlhttp.readyState + '\nstatus: ' + xmlhttp.status + '\nrequested URL: ' + url);
      }

      function make_query(page, pvs)
      {
        var url = page;
        for(var key in pvs)
        {
          if (!url.match('[?]'))
            url += '?'+pvs[key][0]+'='+pvs[key][1];
          else
            url += '&'+pvs[key][0]+'='+pvs[key][1];
        }
        return url;
      }

    </script>
  </body>
</html>
