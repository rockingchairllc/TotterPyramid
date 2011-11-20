<?php include ('header.php'); ?>

            <!-- Begin the main content. Create the Totter -->
            <div class="the_content">
                <div class="create_totter">
                
                    <form id="create_project">
                        <fieldset>
                            <h1 class="title">Create Project</h1>
                            
                            <label>Title:</label><br />
                            <input type="text" /><br />
                            
                            <label>Description:</label><br />
                            <textarea></textarea><br />
                            
                            <label>Project URL:</label><br />
                            http://totter.com/<input type="text" class="create_project_url" /><br />
                            
                            <label>Project Key:</label><br />
                            <input type="text" /><br />
                            
                            <!-- 
                            Share Buttons
                            <button type="button">Share via Emai</button>
                            <button type="button">Share on Facebook</button>
                            -->
                            
                            <input type="submit" value="Create Totter" />
                        </fieldset>
                    </form><!-- #create_totter -->
                
                </div><!-- .create_totter -->
                
            </div><!-- .the_content -->
            
<?php include ('footer.php'); ?>