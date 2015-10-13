<?php
	// file used for submitting reports

	$conn = new mysqli('localhost', 'user', 'password', 'Submissions_db');

	$userid_reporter = mysqli_real_escape_string($conn, $_POST['userid_reporter']);
	$postid = mysqli_real_escape_string($conn, $_POST['postid']);
	$category = intval($_POST['category']);

	$dupecheck = "SELECT * FROM reports_tbl WHERE userid_reporter = '".$userid_report."' AND postid = '".$postid."';";
	$result = mysqli_query($conn, $dupecheck);
	$n = mysqli_affected_rows($conn);
	
	if($n <= 0){
		// getting the userid of the author of the post
		$query = "SELECT * FROM posts_tbl WHERE postid = '".$postid."';";
		$result = mysqli_query($conn, $query);
		$reportedpost = mysqli_fetch_array($result);
		
		// submitting the report
		$query = "INSERT INTO reports_tbl (userid_reporter, userid_author, postid, category)
				  VALUES('".$userid_reporter."', '".$reportedpost['userid']."', '".$postid."', ".$category.");";
		mysqli_query($conn, $query);
	}
	
	mysqli_close($conn);

?>