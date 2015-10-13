<?php
	// file used for retrieving and displaying posts

	function hotRank($votes, $timestamp){ // hot ranking algorithm 
		settype($votes, "int");
		settype($timestamp, "int");

		if($votes > 0){
			$y = 1;
		}else if($votes < 0){
			$y = -1;
		}else{
			$y = 0;
		}

		if(abs($votes) >= 1){
			$z = abs($votes);
		}else{
			$z = 1;
		}

		$rank = log($z, 10) + (($y*$timestamp)/45000);

		return $rank;
	}

	$conn = new mysqli('localhost', 'user', 'password', 'Submissions_db');

	$userid = mysqli_real_escape_string($conn, $_POST['userid']);
	$userlat = floatval($_POST['lat']); // need to get these values from the client
	$userlong = floatval($_POST['long']);
	$displayMode = intval($_POST['displayMode']);
	$lowPost = intval($_POST['lowPost']);
	$highPost = intval($_POST['highPost']);

	$radius = 10; // radius in miles around which the user can see posts

	$query = "SELECT * FROM userdata_tbl WHERE userid = '".$userid."';";
	$result = mysqli_query($conn, $query);
	$n = mysqli_affected_rows($conn);
	if($n <= 0){
		$add = "INSERT INTO userdata_tbl (userid, votehistory)
				VALUES('".$userid."', '');";
		mysqli_query($conn, $add);
	}

	if($displayMode == 0){ // hot post view
		$query = 'SELECT *, ( 3959 * acos( cos( radians('.$userlat.') ) * cos( radians( Latitude ) ) 
	* cos( radians( Longitude ) - radians('.$userlong.') ) + sin( radians('.$userlat.') ) * sin(radians(Latitude)) ) ) AS distance 
	FROM posts_tbl 
	HAVING distance <= '.$radius.' ';
	}else if($displayMode == 1){ // new post view
		$query = 'SELECT *, ( 3959 * acos( cos( radians('.$userlat.') ) * cos( radians( Latitude ) ) 
	* cos( radians( Longitude ) - radians('.$userlong.') ) + sin( radians('.$userlat.') ) * sin(radians(Latitude)) ) ) AS distance 
	FROM posts_tbl 
	HAVING distance <= '.$radius.' ';
	}else if($displayMode == 2){ // top post view
		$query = 'SELECT *, ( 3959 * acos( cos( radians('.$userlat.') ) * cos( radians( Latitude ) ) 
	* cos( radians( Longitude ) - radians('.$userlong.') ) + sin( radians('.$userlat.') ) * sin(radians(Latitude)) ) ) AS distance 
	FROM posts_tbl 
	HAVING distance <= '.$radius.' ';
	}else if($displayMode == 3){ // bad post view
		$query = 'SELECT *, ( 3959 * acos( cos( radians('.$userlat.') ) * cos( radians( Latitude ) ) 
	* cos( radians( Longitude ) - radians('.$userlong.') ) + sin( radians('.$userlat.') ) * sin(radians(Latitude)) ) ) AS distance 
	FROM posts_tbl 
	HAVING distance <= '.$radius.' ';
	}else if($displayMode == 4){ // your post view
		$query = 'SELECT * FROM posts_tbl WHERE userid = "'.$userid.'";';
	}else if($displayMode == -1){ // debug
		$query = 'SELECT * FROM `posts_tbl` ORDER BY `posts_tbl`.`votes` DESC;';
	}

	if($displayMode == 0 || $displayMode == 1 || $displayMode == 2 || $displayMode == 3){ // checks for blocks and hides
		// checks block table for blocked users to exclude from a user's output
		$blockcheck = 'SELECT * FROM blocks_tbl WHERE userid_blocker = "'.$userid.'";';
		$blockresult = mysqli_query($conn, $blockcheck);
		$n = mysqli_affected_rows($conn);

		if($n > 0){
			while($blockrow = mysqli_fetch_array($blockresult)){
				$query .= 'AND NOT userid = "'.$blockrow['userid_blocked'].'" ';
			}
		}

		// checks hide table for hidden posts to exclude from a user's output
		$hidecheck = 'SELECT * FROM hides_tbl WHERE userid = "'.$userid.'";';
		$hideresult = mysqli_query($conn, $hidecheck);
		$n = mysqli_affected_rows($conn);

		if($n > 0){
			while($hiderow = mysqli_fetch_array($hideresult)){
				$query .= 'AND NOT postid = "'.$hiderow['postid'].'" ';
			}
		}

		if($displayMode == 0 || $displayMode == 2){
			$query .= 'ORDER BY votes DESC
			LIMIT '.$lowPost.' , 20;';
		}else if($displayMode == 1){
			$query .= 'ORDER BY timestamp DESC
			LIMIT '.$lowPost.' , 20;';
		}else if($displayMode == 3){
			$query .= 'ORDER BY votes 
			LIMIT '.$lowPost.' , 20;';
		}

		file_put_contents("file_debug.txt", $query);
	}

	$result = mysqli_query($conn, $query);
	//var_dump($result); //debugging for results, returns false if no posts
	$n = mysqli_affected_rows($conn);

	if($n > 0){  // there are posts in the user's area
		$content = array();
		$i = 0;
		while($row = mysqli_fetch_array($result)){

			$a = array();
			$a['Title'] = $row['Title'];
			$a['Caption'] = $row['Caption'];
			$a['Location'] = $row['Location'];
			$a['Votes'] = $row['votes'];
			$a['Userid'] = $row['userid'];
			$a['Postid'] = $row['postid'];
			$a['Timestamp'] = $row['timestamp'];

			$query2 = 'SELECT * FROM votes_tbl WHERE userid = "'.$row['userid'].'" AND postid = "'.$row['postid'].'";';
			$result2 = mysqli_query($conn, $query2);
			$n2 = mysqli_affected_rows($conn);
			if($n2 > 0){
				$row2 = mysqli_fetch_array($result2);
				$a['Previousvote'] = $row2['vote'];
			}else{
				$a['Previousvote'] = 0;
			}

			if($displayMode == 0){ // get hot ranking if sorting by hot
				$a['hotRank'] = hotRank($row['votes'], $row['timestamp']);
			}
			
			$a['MediaType'] = $row['mediaType'];
			
			$content[$i] = $a;
			++$i;
		}

		if($displayMode == 0){
			usort($content, function($a, $b) { // sort by rank
				return $a['hotRank'] - $b['hotRank'];
			});
			$content = array_reverse($content); // reverse to get desc order
		}

		$posts = array('Data' => $content);
		
	}else{
		$posts = array('Data' => array());
	}

	echo json_encode($posts);
	mysqli_close($conn);
?>