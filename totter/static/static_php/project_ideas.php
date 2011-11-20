<?php include ('header.php'); ?>            
            
            <!-- Begin the main content. -->
            <h1 class="title">Title of the Project</h1>
            <h3>by <a href="#">Username</a></h3>
            
            <div class="the_content">
                <ul class="tabs">
                	<li><a href="project_overview.php">Overview</a></li>
                    <li><a href="project_ideas.php" class="active_tab">Ideas</a></li>
                    <li><a href="#">People</a></li>
                </ul><!-- .tabs -->
                
                <ul class="project_stats">
                	<li>
                    	People<br />
                        <span class="project_stat">42</span>
                    </li>
                    <li>
                    	Ideas<br />
                        <span class="project_stat">3</span>
                    </li>
                    <li>
                    	Deadline<br />
                        <span class="project_stat">None</span>
                    </li>
                    <button type="button" onClick="addIdea()" class="add_idea_button">Add Idea</button>
                </ul><!-- .project_stats -->
                
                <div class="sort_by">
                    Sort by:<br />
                    <button type="button">Date</button>
                    <button type="button">Rating</button>
                    <button type="button">User</button>
                </div><!-- .sort_by -->
                
                <ul class="project_ideas">
                	<li>
                    	<div class="idea_author">
                        	<a href="#">
                                <img src="http://graph.facebook.com/178405602197920/picture?type=square" />
                            </a>
                        </div><!-- .idea_author -->
                        <div class="idea_body">
                            <div class="idea_meta">
                            <div class="username"><a href="#">Username</a></div>
                             <strong>Total Rating: 48</strong>
                             <div class="like_love">
                                 <a href="#" class="like_love">Like It</a> 
                                 &bull; 
                                 <a href="#" class="like_love">Love It</a> 
                             </div><!-- like_love -->
                            </div><!-- .idea_meta -->
                        	<div class="idea_description">
                            	Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                Quisque mi mi, viverra vel imperdiet eget, cursus at dolor. Integer luctus scelerisque fringilla.
                            </div>
                            <div class="comment_time">
                                 <a href="javascript:void(0)" class="comment_on_idea" onClick="showComment()">Comment</a> 
                                 &#124; 
                                 September 18th at 9:30am
                             </div><!-- .comment_time -->
                             
                            <ul class="project_idea_comments">
                                 <li class="new_comment first_update">
                                    <input type="text" value="Start Typing"  /><br />
                                    <span class="enter_to_submit">Push Enter to Submit</span>
                                 </li><!-- .new_comment -->
                                 
                                 <!-- Append all new comments to the ul.project_idea_comments -->
                                 
                                 <li class="first_update">
                                        <a href="#">
                                            <img src="http://graph.facebook.com/12404109/picture?type=square" width="32" height="32" />
                                        </a>
                                    <div class="comment_body">
                                        <a href="#">Username</a>
                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                    </div>
                                 </li>
                                 <li>
                                        <a href="#">
                                            <img src="http://graph.facebook.com/12432946/picture?type=square" width="32" height="32" />
                                        </a>
                                    <div class="comment_body">
                                        <a href="#">Username</a>
                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                    </div>
                                 </li>
                                 <li class="last_update">
                                        <a href="#">
                                            <img src="http://graph.facebook.com/1000499831/picture?size=square" width="32" height="32" />
                                        </a>
                                    <div class="comment_body">
                                        <a href="#">Username</a>
                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                    </div>
                                 </li>
                            </ul><!-- .project_idea_comments -->
                        </div><!-- idea_body -->
                    </li>
                	<li>
                    	<div class="idea_author">
                        	<a href="#">
                                <img src="http://graph.facebook.com/82701710/picture?type=square" />
                            </a>
                        </div><!-- .idea_author -->
                        <div class="idea_body">
                            <div class="idea_meta">
                            <div class="username"><a href="#">Username</a></div>
                             <strong>Total Rating: 38</strong>
                             <div class="like_love">
                                 <a href="#" class="like_love">Like It</a> 
                                 &bull; 
                                 <a href="#" class="like_love">Love It</a> 
                             </div><!-- .like_love -->
                            </div><!-- .idea_meta -->
                        	<div class="idea_description">
                            	Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                Quisque mi mi, viverra vel imperdiet eget, cursus at dolor. Integer luctus scelerisque fringilla.
                            </div>
                            <div class="comment_time">
                                 <a href="javascript:void(0)" class="comment_on_idea" onClick="showComment()">Comment</a> 
                                 &#124; 
                                 September 18th at 9:30am
                             </div><!-- .comment_time -->
                             

                            <ul class="project_idea_comments">
                                 <li class="new_comment first_update">
                                    <input type="text" value="Start Typing"  /><br />
                                    <span class="enter_to_submit">Push Enter to Submit</span>
                                 </li><!-- .new_comment -->
                                 
                                 <!-- Append all new comments to the ul.project_idea_comments -->
                                 <li class="first_update">
                                        <a href="#">
                                            <img src="http://graph.facebook.com/12409002/picture?type=square" width="32" height="32" />
                                        </a>
                                    <div class="comment_body">
                                        <a href="#">Username</a>
                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                    </div>
                                 </li>
                                 <li class="last_update">
                                        <a href="#">
                                            <img src="http://graph.facebook.com/10005352/picture?size=square" width="32" height="32" />
                                        </a>
                                    <div class="comment_body">
                                        <a href="#">Username</a>
                                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                                    </div>
                                 </li>
                            </ul><!-- .project_idea_comments -->
                        </div><!-- idea_body -->
                    </li>
                </ul><!-- .project_ideas -->
            </div><!-- .the_content -->

<script>
function showComment() {
	$('.new_comment').toggle();
}
</script>
<?php include ('footer.php'); ?>