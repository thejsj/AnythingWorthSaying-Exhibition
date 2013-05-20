<?php 
	function url(){
	  $protocol = ($_SERVER['HTTPS'] && $_SERVER['HTTPS'] != "off") ? "https" : "http";
	  return $protocol . "://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
	}
?>
<!doctype html>
<html class="<?php echo $class; ?>">
<head>
	<title>Anything Worth Saying</title>
	<link rel="stylesheet" href="scripts/style.css" type="text/css">
</head>
<body data-mode="<?php echo($mode); ?>">
	<h1><a href="#"><img id="main_image" src="scripts/imgs/sign.png" /></a></h1>
	<div id="video-container"></div>
		<div style="clear:both"></div>
	<ul id="container"></ul>
	<!-- Javscript -->
	<script>var base = "<?php echo url(); ?>";</script>
	<script src="libraries/jquery_1_9_1.js"></script>
	<script src="libraries/jqueryUI_1_9_2.js"></script>
	<script src="libraries/lettering.js"></script>
	<script src="super.js"></script>
</body>
</html>