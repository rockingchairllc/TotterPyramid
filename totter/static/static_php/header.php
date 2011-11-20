<!DOCTYPE html>
<html>
<head>
    <title>Totter</title>
    <link rel="shortcut icon" href="images/favicon.png" />
	<link rel="apple-touch-icon" href="images/apple-touch-icon.png" />
    <link rel="stylesheet" href="style.css" >
    <script src="js/jquery-1.6.2.min.js"></script>
    <script src="js/jquery-ui-1.8.16.custom.min.js"></script>
</head>
<body>
	<div class="wrapper drop-shadow curved curved-vt-2">
            
            <!-- Begin the Header -->
            <div class="header">
            
                <div class="user_info">
                    <h4 class="username_first_name">Username</h4>
                    <ul class="tool_tip drop-shadow">
                        <li><a href="#">Edit Profile</a></li>
                        <li><a href="#">User Link</a></li>
                        <li><a href="#">User Link</a></li>
                        <li><a href="#">User Link</a></li>
                        <li><a href="#">User Link</a></li>
                    </ul>
                    <img src="http://graph.facebook.com/12402757/picture?type=square" class="user_photo" />
                </div><!-- .user_info -->
                           
                <h1 class="logo">Totter</h1>
                
                <!-- Clear the float to prevent the header from collapsing -->
                <div class="clearfloat"></div>
                
			</div><!-- .header -->
            
            <!-- Add Idea and Modal Overlay -->
            <div class="add_idea">
                <div class="add_idea_overlay" onClick="addIdea()"></div>
                <div class="add_idea_modal drop-shadow">
                    <h1>Add Idea</h1>
                    <textarea>Start typing your idea...</textarea>
                    <a href="javascript:void(0)" onClick="addIdea()">Cancel</a>
                    <button type="button" onClick="addIdea()">Add Idea</button>
                </div><!-- idea_idea_modal -->
            </div><!-- .add_idea -->
            
            <script>
			function addIdea() {
				$('.add_idea').toggle();
			}
			</script>
            <!-- END Add Idea and Modal Overlay -->