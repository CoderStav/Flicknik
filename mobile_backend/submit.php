<?php
	// file used for sumbitting both posts and replies

	ob_start();
	var_dump($_FILES);
	$string = ob_get_clean();
	//no touching above or breaks txt file output

	function random_0_1(){
		// returns random number with flat distribution from 0 to 1
		return (float)mt_rand()/(float)mt_getrandmax();
	}

	function nameGenerator(){
		$animalList = fopen("animals.txt", 'r');
		$adjectiveList = fopen("adjectives.txt", 'r');
		$animals = fread($animalList, filesize("animals.txt"));
		$adjectives = fread($adjectiveList, filesize("adjectives.txt"));
		fclose($animalList);
		fclose($adjectiveList);

		$animals = explode("\n", $animals);
		$adjectives = explode("\n", $adjectives);

		$adj1 = ucfirst(trim($adjectives[rand(0, sizeOf($adjectives)-1)]));
		$adj2 = ucfirst(trim($adjectives[rand(0, sizeOf($adjectives)-1)]));
		$animal = ucfirst(trim($animals[rand(0, sizeOf($animals)-1)]));

		return $adj1.$adj2.$animal;
	}

	function makeThumbnail($dir,$isVid){
		$debug_log = "file_debug.txt";
		$debug_logz = "file_debuge.txt";

		$sourcedir = dirname(__FILE__);
		$pic = $sourcedir.'/'.$dir;
		//file_put_contents($debug_logz, "\n\npic=".$pic);
		if($isVid == 1){
			file_put_contents($debug_log, "\nisVid=".$isVid);
		}
		$thumbdir = dirname($pic).'/thumbnails/';
		file_put_contents($debug_log, "\nthumbdir=".$thumbdir);
		$thumbfile = $thumbdir.basename($pic);
		
		file_put_contents($debug_log, "\nthumbfile=".$thumbfile."\n");

		if(!file_exists($thumbfile)){
			$image = imagecreatefromjpeg($pic);

			$thumb_width = 200;
			$thumb_height = 150;

			$width = imagesx($image);
			$height = imagesy($image);

			if($width < $height){ // rotation code (Does not work yet)
				$portrait = true;
				$rotate = imagerotate($image, 90, 0);
			}else{
				$portrait = false;
			}

			$original_aspect = $width / $height;
			$thumb_aspect = $thumb_width / $thumb_height;

			if ( $original_aspect >= $thumb_aspect )
			{
			   // If image is wider than thumbnail (in aspect ratio sense)
			   $new_height = $thumb_height;
			   $new_width = $width / ($height / $thumb_height);
			}
			else
			{
			   // If the thumbnail is wider than the image
			   $new_width = $thumb_width;
			   $new_height = $height / ($width / $thumb_width);
			}

			$thumb = imagecreatetruecolor( $thumb_width, $thumb_height );

			// Resize and crop
			imagecopyresampled($thumb,
							   $image,
							   0 - ($new_width - $thumb_width) / 2, // Center the image horizontally
							   0 - ($new_height - $thumb_height) / 2, // Center the image vertically
							   0, 0,
							   $new_width, $new_height,
							   $width, $height);

			if(!file_exists($thumbdir)){
				mkdir($thumbdir, 0777, true);
			}

			imagejpeg($thumb,$thumbfile,80);			
			file_put_contents($debug_logz, $thumbfile);
		}
	}

	function idGenerator($length){
		$legalchars = "abcdefghijklmnopqrstuvwxyz0123456789";
		$cn = new mysqli('localhost', 'user', 'password', 'Submissions_db');
		$postident = '';
		$isunique = false;
		$tries = 0;
		while($isunique == false){
			if($tries > 3){
				++$length;
				$tries = 0;
			}
			for($i = 0; $i < $length; $i++){
				$postident .= $legalchars[rand(0, strlen($legalchars)-1)];
			}
			$qr = 'SELECT * FROM posts_tbl where postid = "'.$postident.'";';
			mysqli_query($cn, $qr);
			$n = mysqli_affected_rows($cn);
			if($n == 0){
				$isunique = true;
			}else{
				++$tries;
			}

			$qr = 'SELECT * FROM replies_tbl where replyid = "'.$postident.'";';
			mysqli_query($cn, $qr);
			$n = mysqli_affected_rows($cn);
			if($n == 0){
				$isunique = true;
			}else{
				++$tries;
			}
		}
		mysqli_close($cn);
		return $postident;
	}

	function base64_to_jpg($base64_string, $output_file){
		$ifp = fopen($output_file, "wb");

		fwrite($ifp, base64_decode($base64_string));
		fclose($ifp);

		return $output_file;
	}

	$submitOK = true;
	$errormsg = "";

	$postType = $_GET['postType'];

	if($postType == "submission"){

		$conn = new mysqli("localhost", "user", "password", "Submissions_db");

		$lat = $_POST['lat'];
		$long = $_POST['long'];
		$userid = mysqli_real_escape_string($conn, $_POST['userid']);
		$title = mysqli_real_escape_string($conn, $_POST['title']);
		$caption = mysqli_real_escape_string($conn, $_POST['caption']);
		$mediaType = intval($_POST['mediaType']); # 0 - pictures, 1 - videos
		$postid = idGenerator(7);
		
		$file_tmp = $_FILES["file"]["tmp_name"];
		
		file_put_contents("submitData.txt", $file_tmp);
		
		$file_path = "uploads/".$userid."/";
		
		if(!file_exists($file_path)){
			mkdir($file_path, 0777, true);
		}

		if($mediaType == 1){
			$file_path = $file_path.$postid.'.mp4';
			move_uploaded_file($file_tmp, $file_path);
		}else{
			$file_path = $file_path.$postid.'.jpg';
			move_uploaded_file($file_tmp, $file_path);
			makeThumbnail($file_path,$mediaType);
		}

		if($submitOK == true){
			if(file_exists($file_path)){
				$add = "INSERT INTO posts_tbl (Title, Caption, Location, Latitude, Longitude, votes, userid, postid, timestamp, mediaType, IP_client, IP_server)
						VALUES('".$title."', '".$caption."', '".$file_path."', ".$lat.", ".$long.", 0, '".$userid."', '".$postid."', ".time().", ".$mediaType.", '".$_SERVER['REMOTE_ADDR']."', 						'".$_SERVER['HTTP_X_FORWARDED_FOR']."');";
				echo true;
			}else{
				echo false;
			}
			mysqli_query($conn, $add);
		}else{
			file_put_contents($debug_log, $errormsg);
		}

		mysqli_close($conn);

	}else if($postType == "reply"){

		$conn = new mysqli("localhost", "user", "password", "Submissions_db");

		$body = mysqli_real_escape_string($conn, $_POST['body']);
		$userid = mysqli_real_escape_string($conn, $_POST['userid']);
		$postid = mysqli_real_escape_string($conn, $_POST['postid']);
		$replyid = idGenerator(7);

		$query = "SELECT * FROM replyUsernames_tbl WHERE postid = '".$postid."' AND userid = '".$userid."';";
		mysqli_query($conn, $query);
		$n = mysqli_affected_rows($conn);

		file_put_contents("file_debug.txt", $n);

		if($n <= 0){
			$add = "INSERT INTO replyUsernames_tbl (postid, userid, name, color)
					VALUES('".$postid."', '".$userid."', '".nameGenerator()."', '".random_0_1().",".random_0_1().",".random_0_1()."');";
			mysqli_query($conn, $add);
		}

		if($submitOK == true){
			$add = "INSERT INTO replies_tbl (body, votes, userid, postid, replyid, timestamp, IP_client, IP_server)
					VALUES('".$body."', 0, '".$userid."', '".$postid."', '".$replyid."', ".time().", '".$_SERVER['REMOTE_ADDR']."', '".$_SERVER['HTTP_X_FORWARDED_FOR']."');";
			mysqli_query($conn, $add);
		}
		mysqli_close($conn);
	}
?>