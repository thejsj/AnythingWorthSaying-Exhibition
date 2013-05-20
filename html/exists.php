<?php

$url = $_POST['url'];

$urlExists = is_200($url);

function is_200($url)
{
    $options['http'] = array(
        'method' => "HEAD",
        'ignore_errors' => 1,
        'max_redirects' => 0
    );
    $body = file_get_contents($url, NULL, stream_context_create($options));
    sscanf($http_response_header[0], 'HTTP/%*d.%*d %d', $code);
    if($code === 200){
    	echo 1;
    }
    else {
    	echo 0;
    }
}

?>