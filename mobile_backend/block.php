<?php
	// file used for submitting user blocks

	$conn = new mysqli('localhost', 'user', 'password', 'Submissions_db');

	$userid = mysqli_real_escape_string($conn, $_POST['userid']);
	$postid = mysqli_real_escape_string($conn, $_POST['postid']);
	
	// retrieves userid from post's row in posts_tbl
	$query = "SELECT * FROM posts_tbl WHERE postid = '".$postid."';";
	$result = mysqli_query($conn, $query);
	$postrow = mysqli_fetch_array($result);
	$userid_blocked = $postrow['userid'];
	
	// don't want the user blocking themselves
	if($userid != $userid_blocked){
		$query = "INSERT INTO blocks_tbl (userid_blocker, userid_blocked)
				  VALUES('".$userid."', '".$userid_blocked."')";
		mysqli_query($conn, $query);
	}

	mysqli_close($conn);

?>