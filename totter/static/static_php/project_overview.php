<?php include ('header.php'); ?>            
            
            <!-- Begin the main content. -->
            <h1 class="title">Title of the Project</h1>
            <h3>by <a href="#">Username</a></h3>
            <div class="the_content">
            	<ul class="tabs">
                	<li><a href="project_overview.php" class="active_tab">Overview</a></li>
                    <li><a href="project_ideas.php">Ideas</a></li>
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
                
                <div class="project_description">
                    <h2>Description</h2>
                    <p>
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci. 
                        Quisque mi mi, viverra vel imperdiet eget, cursus at dolor. Integer luctus scelerisque fringilla. 
                        Donec molestie bibendum nunc sed posuere. Nullam non risus eros, sed blandit tortor. 
                        Ut dui nisl, rhoncus id venenatis nec, sodales quis nisl. 
                        Cras neque lorem, venenatis sit amet accumsan ut, semper quis sapien.
                         Sed tempus laoreet auctor.
                     </p>
                 </div><!-- .project_description -->
                 
                 <ul class="project_updates">
                 	<h2>Updates</h2>
                    <li class="first_update">
                    	<span class="project_update_date">Wed 9/21/2011 at 9pm</span><br />
						Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci.
                    </li>
                 	<li>
                    	<span class="project_update_date">Wed 9/21/2011 at 9pm</span><br />
						Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci.
                    </li>
                 	<li>
                    	<span class="project_update_date">Wed 9/21/2011 at 9pm</span><br />
						Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci.
                    </li>
                 	<li class="last_update">
                    	<span class="project_update_date">Wed 9/21/2011 at 9pm</span><br />
						Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget dictum orci.
                    </li>
                 </ul><!-- .project_updates -->
                 
                 
            </div><!-- .the_content -->
<?php include ('footer.php'); ?>