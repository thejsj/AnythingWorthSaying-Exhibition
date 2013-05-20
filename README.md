# Anything Worth Saying - Exhibition Code

This is the code for my M.F.A exhibition. It consists of 3 components written in MAX/MSP (written?), Python and HTML/JS/PHP/AJAX. The MAX/MSP component runs on one computer and and is designed to be an interface to record videos. THe python files sniffs out videos and converts them to .mp4, creates a thumbnnail and creates a JSON to be read by AJAX. The HTML component is a user interface that plays these created videos instantly (Sniffing out for new JSON files with AJAX)[index-auto.php] or may be accesed for the user to interact with these videos with the mouse [index.php]. 

I only post this code for future reference. 

## See an instance of the project

[AWS Exhibition](http://aws.thejsj.com)

## Python Dependencies

*   xspf     - https://github.com/alastair/xspf -- Makes Playlist File
*	pyglet   - http://www.pyglet.org/download.html -- Plays Sound
*	pexpect  - http://www.noah.org/wiki/Pexpect#Download_and_Installation
