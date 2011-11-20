<!DOCTYPE html>
<html>
<head>
    <title>Totter</title>
    <link rel="shortcut icon" href="images/favicon.png" />
	<link rel="apple-touch-icon" href="images/apple-touch-icon.png" />
    <link rel="stylesheet" href="style.css" >
</head>
<body>
	
    <div class="login_register_wrap drop-shadow curved curved-vt-2">
            
            <h1 class="title">Welcome to Totter</h1>
            <form id="loginForm">
                <fieldset>
                    <input type="text" value="Username" /><br />
                    
                    <input type="text" value="Password" /><br />
				    <a href="#ForgotPassword" class="forgot_password">Forgot Password?</a>
                    
                    <div class="remember_me">
                    	<input type="checkbox" />
                        <label>Remember me</label>
					</div><!-- .remember_me -->
                    <input type="submit" class="login_btn" value="Login" />
                </fieldset>
            </form>
			
            <h3 class="register">New here?  <a href="#register"class="register_btn">Register</a></h3>
        
            <div class="fb_login">
            	<div id="fb-root"></div>
				<script>
                  window.fbAsyncInit = function() {
                    FB.init({
                      appId      : 'YOUR_APP_ID',
                      status     : true, 
                      cookie     : true,
                      xfbml      : true
                    });
                  };
                  (function(d){
                     var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
                     js = d.createElement('script'); js.id = id; js.async = true;
                     js.src = "//connect.facebook.net/en_US/all.js";
                     d.getElementsByTagName('head')[0].appendChild(js);
                   }(document));
                </script>
                <fb:login-button size="medium" scope="email">Login with Facebook</fb:login-button> 
            </div><!-- .fb_login -->
            
	</div><!-- .login_register_wrap -->
    
<!-- include normal wrapper for footer-links -->
<div class="footer wrapper">
<?php include ('footer.php'); ?>