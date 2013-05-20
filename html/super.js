$(document).ready(function(){

	/*	Declare Globals 
=========================== */

	var size; //width //heigth 
	var objects = []; 
	var borderSize = 10;
	var thumnailSize = [120, 65];
	var videoOpen = false; 
	var url = base;
	var jsonUrl = "/generatedVideos/assets/videos.json";
	var jsonUrlComplete = url + "/generatedVideos/assets/videos.json";
	var infinteLoop = 0;
	var allMoving = true;
	var videoContainerWidth  = 853;
	var videoContainerHeight = 480;
	var originalVideoContainerWidth  = 853;
	var originalVideoContainerHeight = 480;
	var lastModified = 0; 
	var mode = $("body").data("mode");
	var playVideo = true;
	var newVideo  = false;

	var about =  '<div id="about">';
		about += '<h3>Anything Worth Saying</h3>';  
		about += '<p>AWS started with a very simple question: "Do you have anything worth saying?" I held up a sign with this question and went around Richmond, VA trying to convince people to answer it. Fortunately, many people did and their participation provided a wide array of different responses. Take a look!<br/><br/>A project by <a href="http://thejsj.com">TheJSJ</a></p>';
		about += '</div>';

	/*	Take Care of Size 
=========================== */
	
	if(mode == 1){
		$("html").click(function(e){
			//e.preventDefault();
		});
	}

	console.log("HELLLO!!!!");

	var adjustDocumentHeight = function(){
		var width = $(window).outerWidth();
		var height = $(window).outerHeight(); 
		$("body").css("height", $(window).outerHeight() - (borderSize * 2));
		$("#video-container").css("height", 0).css("width", 0).css("top", height/2).css("left",width/2);
		$("h1")
			.css("width", "920px")
			.css("height", "auto")
			.css("top" , ((height - parseInt($("h1").outerHeight())) / 2))
			.css("left", ((width - parseInt($("h1").outerWidth())) / 2))
			.click(function(){
				if(mode == 0){
					openDialog(about);
				}
			});
		return [width, height];
	};

	size = adjustDocumentHeight(); 

	function checkHeight(){
		size = adjustDocumentHeight(); 
		setTimeout(function(){
			if(size[1] != $(document).height() || size[0] != $(document).width()){
				if(infinteLoop < 10){
					checkHeight();
				}
				infinteLoop++;
			}
			else {
				infinteLoop = 0;
			}
		}, 1000);
	}

	$(window).resize(function() {
		checkHeight();
	});

	$("h1").lettering();

	/*	Get Video Data 
=========================== */

	// fileName
	// lastModified
	var getTimeModified = function(){
		$.post("modified.php", { fileName: jsonUrl})
			.done(function(data) {
				if(data != lastModified){
					getNewVideos();
				}
				lastModified = data; 
			})
			.fail(function() { //console.log("error"); 
			})
			.always(function() { });
	}

	var seeIfExists = function(fileurl, key, videoOrThumb){
		$.post("exists.php", { url: fileurl})
			.done(function(data){
				if(videoOrThumb == 0){ //Video
					if(data == 1){
						//console.log("seeIfExists: " + 1 + " --key: " + key);
						objects[key].video_exists = 1;
					}
					else {
						//console.log("seeIfExists: " + 0 + " --key: " + key);
						objects[key].video_exists = 0;
					}
				}
				if(videoOrThumb == 0){ // Thumb
					if(data == 1){
						//console.log("seeIfExists: " + 1 + " --key: " + key);
						objects[key].thumb_exists = 1;
					}
					else {
						//console.log("seeIfExists: " + 0 + " --key: " + key);
						objects[key].thumb_exists = 0;
					}
				}
			})
			.fail(function() { 
				//console.log("Exists.php error"); 
			})
			.always(function() { 
				//console.log("Exists.php done!!!!"); 
			});
	}

	setInterval(getTimeModified,1000);

	var getNewVideos = function(){
		console.log("Get New Videos");
		$.getJSON(jsonUrlComplete, function(data) {
		// Add Videos to HTML
			var allObjects = []
			console.log("data");
			console.log(data);
			$.each(data, function(key, val) {
				allObjects.push([val.id, val.videoLocation, val.thumbLocation, val.accepted, val.lastModified, val.webmLocation]);
			});
			if(allObjects.length != objects.length){
				for(i = objects.length; i < allObjects.length; i++){
					objects.push(new Constructor(
							allObjects[i][0], 
							allObjects[i][1], 
							allObjects[i][2], 
							allObjects[i][3], 
							allObjects[i][4],
							allObjects[i][5]
							)
						);
				}
				console.log("Adding Things : " + objects.length)
				if(mode == 1){
					newVideo = true;
					objects[objects.length - 1].openVideo();
				}
			}
		});
	}

	function resetMoving(functionId){
		for(key in objects){
			if(objects[key].key == functionId){
				objects[key].moving = false; 
				$("#" + objects[key].key).addClass("selected");
			}
			else {
				objects[key].moving = true;
				$("#" + objects[key].key).removeClass("selected");
			}
		}
	}

	function playRandomVideo(){
		setTimeout(function(){
			var randomVideo = parseInt(Math.random() * objects.length);
			objects[randomVideo].openVideo();
		}, 800);
	}

	/*	Declare the Video Class 
=========================== */

	var defaultSpeed = 6;

	var Constructor = function(key, video_location, thumb_location, accepted, last_modified, webmLocation) {

    	this.key = key; 
    	this.thumKey = 1; 
    	this.video_location = video_location;
    	this.thumb_location = thumb_location;
    	this.last_modified = last_modified;
    	this.webmLocation = null; 
    	if(webmLocation != undefined && webmLocation.length > 0){
    		this.webmLocation = webmLocation; 
    	}
    	this.moving = true; 
    	this.accepted = accepted; // 0 - Accepted / 1 - Rejected
    	this.z = parseInt(Math.random() * 500);
    	this.hover = false;
    	this.speed = defaultSpeed;
    	this.rotationSpeed = Math.random() * 2; 
    	this.x = (Math.random() * (size[0] - 50 - thumnailSize[0])) + borderSize; 
    	this.y = (Math.random() * (size[1] - 50 - thumnailSize[1])) + borderSize; 
    	this.rotation = 0; 

    	this.directionX = (parseInt(Math.random() * 2) == 0) ? true : false;
    	this.directionY = (parseInt(Math.random() * 2) == 0) ? true : false;
    	this.directionR = (parseInt(Math.random() * 2) == 0) ? true : false;

    	this.thumb_exists = -1; 
    	this.video_exists = -1; //1 - Exists / 0 - Doesn't Exist

    	this.checkExistence();
   
	}

	Constructor.prototype.checkExistence = function(){
		//console.log("CHECK EXISTENCE!!! - " + this.key);
		//console.log(this.thumb_exists);
	    //console.log(this.video_exists);
		seeIfExists(url + this.thumb_location, this.key, 1);
	    seeIfExists(url + this.video_location, this.key, 0);
	    var key = this.key;
		setTimeout(function(){    
	    	if(objects[key].thumb_exists == 1 && objects[key].video_exists == 1){
		    	console.log("Initiating - " + key);
		    	objects[key].init();
		    }
		    else if(objects[key].thumb_exists == -1 && objects[key].thumb_exists == -1){
		    	//console.log("Cheking Again")
		    	objects[key].checkExistence();
		    }
		    else if(objects[key].thumb_exists == undefined && objects[key].thumb_exists == undefined){
		    	//console.log("Cheking Again")
		    	objects[key].checkExistence();
		    }
		    else if(objects[key].thumb_exists == 0 || objects[key].thumb_exists == 0){
		    	//console.log("Something is Missing!!!!")
		    	//console.log(objects[key].thumb_location);
		    	//console.log(objects[key].video_location);
		    }
	    },500);
	}

    Constructor.prototype.init = function(){
		if(mode == 1 || (mode == 0 && this.accepted == 0)) {
			var check_url = url + this.thumb_location; 

			$("#container").append('<li id="' + this.key + '" class="thumbnail" style="z-index: '+this.z+';"></li>');
			this.setBg(); 
			this.move(); 

			//One you start doing this... start animating the size of the thing... 
			var time = parseInt(Math.random() * 10000);
			$("#" + this.key).delay(2000).animate({
				width: thumnailSize[0],
				height: thumnailSize[1]
			}, time)
			var that = this; 
			$("#" + this.key)
				.click(function(e){
					if(mode == 0){
						that.openVideo(); 
						e.stopPropagation();
					}
				}).mouseover(function () {
					if(mode == 0){
						that.speed = 0.0;
						that.hover = true;
					}
				}).mouseout(function () {
					if(mode == 0){
						that.speed = defaultSpeed;
						that.hover = false;
					}
				});

			$(document).bind('click', function (e) {
				resetMoving(-1);
				e.stopPropagation();
			});
		}
    }

	Constructor.prototype.move = function() {
		if(this.moving){
		    if(this.directionX)
		    	this.x =  this.x - this.speed; 
		    else
		    	this.x =  this.x + this.speed; 
		    if(this.directionY) 
		    	this.y =  this.y - this.speed; 
		    else
		    	this.y =  this.y + this.speed; 
		   	if(this.directionR) 
		    	this.rotation = (this.rotation + this.rotationSpeed)%360; 
		    else
		    	this.rotation = (this.rotation - this.rotationSpeed)%360; 

		    var outsideMargin = 200;
		    //if(this.x < -borderSize || this.x > size[0] - thumnailSize[0] - (borderSize * 3)){
		    if(this.x < -outsideMargin || this.x > (size[0] + outsideMargin) ) {
		    	if(this.x < -borderSize){
		    		this.directionX = true;
		    	}
		    	else {
		    		this.directionX = false;
		    	}
		    	this.directionX = !this.directionX;
		    	this.z = parseInt(Math.random() * 500);
		    	$("#" + this.key).css("z-index", this.z);
		    	$("#" + this.key).css("-webkit-transform", "rotate(7deg)");
		    }
		    //if(this.y <  -(borderSize * 2.75) || this.y > size[1] - thumnailSize[1] - (borderSize * 4.75) ) {
		    if(this.y < -outsideMargin || this.y > (size[1] + outsideMargin) ) {
		    	if(this.y < -(borderSize * 2.75)){
		    		this.directionY = true;
		    	}
		    	else {
		    		this.directionY = false;
		    	}
		    	this.directionY = !this.directionY;
		    	this.z = parseInt(Math.random() * 500);
		    	$("#" + this.key).css("z-index", this.z);
		    	
		    }
		    this.setPos();
		}
		var key = this.key;
		if(mode == 0){
			var speed = 10 + (objects.length / 4);
		}
		else{ 
			var speed = 60 + (objects.length / 4);
		}

		setTimeout(function(){
			try{
				objects[key].move();
			}
			catch(err){
				console.log("Failed to Move Object With Key: " + key);
				console.log(objects);
			}
	    },speed);
	};

	Constructor.prototype.setPos = function() {
		$("#" + this.key).css("left", this.x);
    	$("#" + this.key).css("top", this.y);
    	if(objects.length < 85){
	    	$("#" + this.key).css("-webkit-transform", "rotate("+this.rotation+"deg)");
	    }
	};	

	Constructor.prototype.setBg = function() {
		if(this.thumKey < 3){
			this.thumKey++;
		}
		else {
			this.thumKey = 1;
		}
		var imgurl = "url(" + url + this.thumb_location+")";
		$("#" + this.key).css("background-image",imgurl);
		var key = this.key;
	};

	Constructor.prototype.openVideo = function(){

		if(videoOpen){
			var that = this;
			$("#video-container").animate({
				opacity: 1,
				height: 1,
				width: 1,
				top: "+=157px",
				left: "+=280px",
				borderWidth: 0
			}, 500, function() {
				// Animation complete.
				videoOpen = false;
				if(mode == 0){
					for(key in objects){
						objects[key].moving = true; 
					}
				}
				openVid(that);
			});
		}
		else {
			openVid(this);
		}

		function openVid(thiss){

			//Determine Size
			if(mode == 1){
				// Find new width and Height for our video...
				// Find the smallest alternative between these two... 
				var proportion = originalVideoContainerWidth / originalVideoContainerHeight; 
				var vdWidthWidth = 0; 
				var vdWidtHeight = 0; 
				// Let's do it based on width
				vdWidthWidth = size[0] - 300;
				vdWidtHeight = (size[1] - 300) * proportion;
				if(vdWidtHeight >  vdWidthWidth){
					videoContainerWidth  = vdWidthWidth;
					videoContainerHeight = vdWidthWidth * (1/proportion);
				}
				else {
					videoContainerWidth  = vdWidtHeight;
					videoContainerHeight = vdWidtHeight * (1/proportion);
				}
			}

			var bdhtml    = '<video id="main_video" width="'+videoContainerWidth+'" height="'+videoContainerHeight+'" controls>';
				if(!newVideo){
	  				bdhtml   += '<source src="'+url+thiss.video_location+'" type="video/mp4">';
	  				if(thiss.webmLocation != null){
	  					bdhtml   += '<source src="'+url+thiss.webmLocation+'" type="video/webm">';
	  				}
	  			}
	  			else {
	  				bdhtml   += '<source src="'+url+'/generatedVideos/assets/newVideo.mp4" type="video/mp4">';
	  			}
  				bdhtml   += '</video>';
			var that = thiss;
			openDialog(bdhtml, "",thiss);
		}
	}

	function openDialog(bdhtml, secondaryText, thiss){

		var videoContainer = $("#video-container");
		
		videoContainer
			.css("top", size[1]/2)
			.css("left", size[0]/2)
			.html(bdhtml)
		if(mode == 1){
			$("#main_video")
				.bind("ended", function(){
					if(newVideo){
						newVideo = false; 
						var bdhtml2    = '<video id="main_video" width="'+videoContainerWidth+'" height="'+videoContainerHeight+'" controls>';
		  					bdhtml2   += '<source src="'+url+thiss.video_location+'" type="video/mp4">';
		  					if(thiss.webmLocation != null){
			  					bdhtml2   += '<source src="'+url+thiss.webmLocation+'" type="video/webm">';
			  				}
	  						bdhtml2   += '</video>';
	  					videoContainer.html(bdhtml2);


	  					var timer1 = setTimeout(function() {
	  						videoFailed(thiss);
	  					}, 3000);

	  					setTimeout(function(){
		  					$("#main_video")
		  						.trigger("play")
		  						.bind("ended", function(){
									closeVideo(); 
									if(playVideo){
										playRandomVideo();
								    }
		  						})
		  						.bind("timeupdate", function(){
									clearTimeout(timer1);
									$(this).unbind("timeupdate");
								})
						}, 700);

	  					$("#main_video")[0]
			    			.removeAttribute("controls");
					}
					else {
						//console.log("VIDEO ENDED!");
						closeVideo(); 
						if(playVideo){
							playRandomVideo();
					    }
					}
			    });
			$("#main_video")[0]
			    .removeAttribute("controls");

		}

		var timer1 = setTimeout(function() {
			videoFailed(thiss);
		}, 3000);

		videoContainer
			.animate({
				opacity: 1,
				width: videoContainerWidth,
				height: videoContainerHeight,
				top: size[1]/2 - (videoContainerHeight/2),
				left: size[0]/2 - (videoContainerWidth/2),
				borderWidth: 10
			}, 1000, function() {
				// Animation complete.
				videoOpen = true;
				if(mode == 0){
					for(key in objects){
						objects[key].moving = false;
					}
				}
				/* Open a way to close this thing!!!! */
				var pos = $(this).position(); 
				var hgt = $(this).outerHeight();
				//console.log("playingVideo");
					setTimeout(function(){
					$("#main_video")
						.trigger("play")
						.bind("timeupdate", function(){
							clearTimeout(timer1);
							$(this).unbind('timeupdate');
						})
					}, 700);
					/*
					.bind("onwaiting", function(){
						console.log("onwaiting STATE");
					})
					.bind("readyState", function(){
						console.log("READY STATE");
					})
					.bind("seeking", function(){
						console.log("seekingseeking STATE");
					})
					.bind("paused", function(){
						console.log("paused STATE");
					})
					.bind("onstalled", function(){
						console.log("onstalled STATE");
					})
					.bind("onsuspend", function(){
						console.log("onsuspend STATE");
					})
					.bind("error", function(){
						console.log("error STATE");
					})
					.bind("canplaythrough", function(){
						console.log("canplaythrough STATE");
					})
					.bind("canplay", function(){
						console.log("canplay STATE");
					})
					*/
				//mainVideo[0].webkitRequestFullScreen();
				if(mode == 0){
					$("body")
						.prepend("<div id='close-box' class='close-box'>x</div>");
					$("#close-box")
						.css("left", pos.left - 5)
						.css("top", pos.top - 40)
						.animate({
							opacity: 1,
							width: 20,
							height: 20,
							padding: 5
						}, 1000)
						.click(function(){
							if(mode == 0){
								closeVideo(); 
							}
						});
				}
				//Add Secondary Text
				if(secondaryText != null && secondaryText != ""){
					$("body")
						.prepend("<div id='secondary-text'>" + secondaryText + "</div>");
					$("#secondary-text")
						.css("left", pos.left + 15)
						.css("top", pos.top + hgt + 20)
						.animate({
							opacity: 1,
							width: 300,
							padding: 15
						}, 2000);
				}
				else {
				}

			});
	}

	function closeVideo(){
		if(videoOpen){
			$("#video-container").animate({
				opacity: 1,
				height: 0,
				width: 0,
				top: size[1]/2,
				left: size[0]/2,
				borderWidth: 0
			}, 500, function() {
				// Animation complete.
				videoOpen = false;
				if(mode == 0){
					for(key in objects){
						objects[key].moving = true;
					}
				}
				$(this).html("");
			});
			if(mode == 0){
				closeBox($("#close-box"));
				closeBox($("#secondary-text"));
				$(".close-box").each(function(){
					$(this).animate({
						width: 0,
						height: 0
					}, 200, function(){
						//Complete
						$(this).remove(); 
					});
				})
				function closeBox(that){
					$(that).animate({
						width: 0,
						height: 0
					}, 200, function(){
						//Complete
						$(this).remove(); 
					});
				}
			}
			
		}
	}

	var videoFailed = function(thiss){
		//console.log("Playing New Video - timer1");
		console.log("Activating Timer");
		$("#video-container").html("<div class='oops'><div>OOOPPPSSS....</div><div class='oops_small'>(This Video Failed. Jorge Sucks!)</div></div>");
		setTimeout(function(){
			closeVideo();
			$("#" + thiss.key).animate({
				opacity: 0,
			}, 1000, function(){
				$(this).remove(); 
				console.log("Remove Element: " + thiss.key);
				objects[thiss.key].moving = false; 
			});
			if(mode == 1){
				if(playVideo){
					playRandomVideo();
	   		 	}
	   		}
		}, 2000);
	}

	/*	Other
=========================== */

	$(document).keypress(function(e) {
		//console.log(e.which);
		var key = e.which;
		if(key == 114){
			// R key - Refresh Page
			document.location.reload(true);
		}
		if(key == 109){
			// M key - Moving 
			for(key in objects){
				objects[key].moving = !objects[key].moving;
			}
		}
		if(key == 112){
			// M key - Moving 
			playVideo = !playVideo;
			if(playVideo){
				playRandomVideo();
			}
			else {
				closeVideo();
			}
		}
	});

});