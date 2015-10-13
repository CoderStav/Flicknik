<?php
ob_start();
var_dump($_FILES);
$string = ob_get_clean();

$tmp_name = $_FILES["file"]["tmp_name"];
$name = $_FILES["file"]["name"];
move_uploaded_file($tmp_name, "testapi/$name");

file_put_contents("multi2.txt",$string);
?>