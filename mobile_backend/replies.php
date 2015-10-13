<?php
	// file used for retrieving and displaying replies	

	$conn = new mysqli("localhost", "user", "password", "Submissions_db");

	$postid = mysqli_real_escape_string($conn, $_POST["postid"]);
	$userid = mysqli_real_escape_string($conn, $_POST["userid"]);

	$query = "SELECT * FROM replies_tbl WHERE postid = '".$postid."' ORDER BY votes DESC;";
	$result = mysqli_query($conn, $query);

	$n = mysqli_affected_rows($conn);

	if($n > 0){
		$content = array();
		$i = 0;
		while($row = mysqli_fetch_array($result)){
			
			$query2 = "SELECT * FROM replyUsernames_tbl WHERE userid = '".$row['userid']."' AND postid = '".$row['postid']."';";
			$result2 = mysqli_query($conn, $query2);
			$row2 = mysqli_fetch_array($result2);
			file_put_contents("file_debug.txt", $postid);
			
			$reply = array();
			$reply["body"] = $row["body"];
			$reply["votes"] = $row["votes"];
			$reply["replyid"] = $row["replyid"];
			$reply["name"] = $row2["name"];
			$reply["timestamp"] = $row["timestamp"];
			$reply["color"] = $row2["color"];
			
			$query3 = 'SELECT * FROM votes_tbl WHERE userid = "'.$row['userid'].'" AND postid = "'.$row['replyid'].'";';
			$result3 = mysqli_query($conn, $query3);
			$n3 = mysqli_affected_rows($conn);
			if($n3 > 0){
				$row3 = mysqli_fetch_array($result3);
				$reply["previousvote"] = $row3["vote"];
			}else{
				$reply["previousvote"] = 0;
			}
			
			$content[$i] = $reply;
			++$i;
		}
		$result = array("Data" => $content);
	}else{
		$result = array("Data" => array());
	}

	echo json_encode($result);
	mysqli_close($conn);
?>