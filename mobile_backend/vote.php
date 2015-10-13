<?php

$debug_log = "file_debug.txt";

$cn = new mysqli('localhost', 'user', 'password', 'Submissions_db');

$userid = mysqli_real_escape_string($cn, $_POST['userid']);
$id = mysqli_real_escape_string($cn, $_POST['id']);
$voteType = $_POST['voteType'];
$postType = $_POST['postType'];

if($voteType == "upvote"){
	$vote = 1;
}else if($voteType == "downvote"){
	$vote = -1;
}

if($postType == "submission"){
	$qr = 'SELECT * from posts_tbl where postid = "'.$id.'";';
	$rs = mysqli_query($cn, $qr);
	$prow = mysqli_fetch_array($rs);
}else if($postType == "reply"){
	$qr = 'SELECT * from replies_tbl where replyid = "'.$id.'";';
	$rs = mysqli_query($cn, $qr);
	$prow = mysqli_fetch_array($rs);
}

$hasvoted = false;
$revote = false;

$qr = 'SELECT * from votes_tbl WHERE postid = "'.$id.'" AND userid = "'.$userid.'";';
$rs = mysqli_query($cn, $qr);
$n = mysqli_affected_rows($cn);

if($n > 0){
	$hasvoted = true;
	$votelisting = mysqli_fetch_array($rs);
	if($votelisting['postid'] == $id && $votelisting['vote'] != $vote){ //if user has voted and is trying to chage their vote, remove old entry and replace with new one
		$revote = true;
	}
}

if($hasvoted == true && $revote == true){
	$qr = 'UPDATE votes_tbl SET vote = '.$vote.' WHERE userid = "'.$userid.'" AND postid = "'.$id.'";';
	
	if($postType == "submission"){
		$qr2 = 'UPDATE posts_tbl SET votes = '.(($prow['votes'] - -$vote) + $vote).' WHERE postid = "'.$id.'";';
	}else if($postType == "reply"){
		$qr2 = 'UPDATE replies_tbl SET votes = '.(($prow['votes'] - -$vote) + $vote).' WHERE replyid = "'.$id.'";';
	}
	
	mysqli_query($cn, $qr);
	mysqli_query($cn, $qr2);
}else if($hasvoted == false){
	$qr = 'INSERT INTO votes_tbl (vote, userid, postid)
		   VALUES('.$vote.', "'.$userid.'", "'.$id.'");';
	
	if($postType == "submission"){
		$qr2 = 'UPDATE posts_tbl SET votes = '.(($prow['votes']) + $vote).' WHERE postid = "'.$id.'";';
	}else if($postType == "reply"){
		$qr2 = 'UPDATE replies_tbl SET votes = '.(($prow['votes']) + $vote).' WHERE replyid = "'.$id.'";';
	}
	
	mysqli_query($cn, $qr);
	mysqli_query($cn, $qr2);
}

mysqli_close($cn);
?>