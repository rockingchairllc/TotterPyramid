<!DOCTYPE html>
<html>
<head>
    <title>Homepage Login</title>
    <link rel="shortcut icon" href="images/favicon.png" />
	<link rel="apple-touch-icon" href="images/apple-touch-icon.png" />
    <link rel="stylesheet" href="style.css" >
    <script src="js/jquery-1.6.2.min.js"></script>
    <script src="js/jquery-ui-1.8.16.custom.min.js"></script>
</head>
<body>
	<div class="login_register_wrap drop-shadow curved curved-vt-2">
            <h1>Welcome to Totter</h1>
            <form id="loginForm">
                <fieldset>
                    <input type="text" id="user_name" value="Project ID" /><br />
                    <input type="text" id="user_password" value="Project Key" /><br />
					<input type="submit" id="loginSubmit" value="View Project" /><br />
                </fieldset>
            </form>
            
	</div><!-- .login_register_wrap -->

<div class="footer wrapper">
<?php include ('footer.php'); ?>