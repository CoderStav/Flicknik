<?php
	// file used for submitting post hides

	$conn = new mysqli('localhost', 'user', 'password', 'Submissions_db');
	
	$userid = mysqli_real_escape_string($conn, $_POST['userid']);
	$postid = mysqli_real_escape_string($conn, $_POST['postid']);

	$query = "INSERT INTO hides_tbl (userid, postid)
			  VALUES('".$userid."', '".$postid."');";
	mysqli_query($conn, $query);

	mysqli_close($conn);

?>