<?php
// outputs e.g.  somefile.txt was last modified: December 29 2002 22:16:23.

$fileName     =  $_POST['fileName']; 
$path   = getcwd(); 
$fileName = $path . $fileName;

if (file_exists($fileName)) {
	if(is_readable($fileName)){
		echo(filemtime($fileName));
	}
	else {
		echo(" ERROR - Is Not Readable");
	}
}
else {
	echo(" ERROR - File Doesn't Exist");
}

?>