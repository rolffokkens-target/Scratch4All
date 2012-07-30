<?php

require 'ingest_include.php';
require includedir . 'ingest_convert2path.php';
$rpath = get('path');
if (preg_match('/(\.\.)|[\:\;\*\?\"\<\>\|\']/', $rpath))
  $rpath = '';
$apath = GLOBAL_ROOT . $rpath;
if (is_dir($apath))
{
  $dir = get_dir();
  make_hmtl($dir);
}
if (is_file($apath))
{
  if (get('action') == 'ingest_book')
    ingest_book();
  make_jpg();
  ingest();
}

function get_dir()
{
  global $apath;
  $dir = array();
  if (is_dir($apath) && is_readable($apath))
    $dir = scandir($apath);
  return $dir;
}

function make_hmtl($dir)
{
  global $filetypes;
  global $foldertypes;
  global $apath;
  global $rpath;
  $html = '';
  $passed_filetypes = false;
  foreach ($dir as $cont)
  {
    if
    (
            $cont != '.'
            && $cont != '..'
            && is_readable($apath . '/' . $cont)
            && is_dir($apath . '/' . $cont)
    )
      $html .= '<a href="ingest_file.php?path=' . $rpath . '/' . $cont . '">+ ' . $cont . '</a><br>' . "\n";
  }
  foreach ($dir as $cont)
  {
    $path_info = pathinfo($cont);
    if
    (
            is_file($apath . '/' . $cont)
            && is_readable($apath . '/' . $cont)
            && in_array(strtolower($path_info["extension"]), $filetypes)
    )
    {
      $html .= '<a href="ingest_file.php?path=' . $rpath . '/' . $cont . '">' . $cont . '</a><br>' . "\n";
      $passed_filetypes = true;
    }
  }
  print '<link rel="stylesheet" type="text/css" href="../include/ingest_basic_style.css" />' . "\n";
  print '<a href="ingest_file.php?path=' . substr($rpath, 0, strrpos($rpath, '/')) . '">Back</a> | ';
  print '<a href="ingest_file.php">Home</a>';
  if (strlen($rpath))
  print ' | ' . $rpath;
  print '<br>' . "\n";
  print '<h1>Ingest bookpage</h1>' . "\n";
  if ($passed_filetypes)
    print '<h3><a href="ingest_file.php?path=' . $rpath . '/' . $cont . '&action=ingest_book">Ingest multiple book pages</a><br></h3>' . "\n";
  print $html;
}

function file_params()
{
  global $rpath;
  $pathinfo = pathinfo($rpath);
  $e = explode('/', $rpath);
  $bookdir = $e[1];
  $filename = $pathinfo['filename'];
  $extension = $pathinfo['extension'];
  return array($bookdir, $filename, $extension);
}

function make_jpg()
{
  global $apath;
  list($bookdir, $filename, $extension) = file_params();
  $jpegdir = jpegdir($bookdir);
  if (!is_dir($jpegdir))
  {
    if (!@mkdir($jpegdir, 0777, true))
      exit('ERROR: Make directory: "' . $jpegdir . '" failed');
    chmod($jpegdir, 0777);
  }
  $jpegpath = jpegpath($bookdir, $filename);
  if (is_file($jpegpath))
    return;

  if (strtolower($extension) == 'tiff' || strtolower($extension) == 'tif')
    exec("tifftopnm < " . escapeshellarg($apath) . " | pnmtojpeg > " . escapeshellarg($jpegpath));
  if (strtolower($extension) == 'ppm')
    exec("pnmtojpeg < " . escapeshellarg($apath) . " > " . escapeshellarg($jpegpath));

  if (!is_file($jpegpath))
    exit('ERROR: file: "' . $apath . '" not converted to: "' . $jpegpath . '"');
  chmod($jpegpath, 0660);
}

function ingest()
{
  list($bookdir, $filename, $extension) = file_params();
  exit(header('Location:ingest_offset.php?bookdir=' . $bookdir . '&filename=' . $filename . '&extension=' . $extension));
}

function ingest_book()
{
  list($bookdir, $filename, $extension) = file_params();
  exit(header('Location:ingest_book.php?bookdir=' . $bookdir . '&filename=' . $filename . '&extension=' . $extension));
}

?>
