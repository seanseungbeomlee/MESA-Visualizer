#!/usr/bin/env python3

# A sample tool handler illustrating use of the tool handler interface.

import tools.tool_helpers as helpers

tool_name = "mesa_binary"

#-------------------------------------------------------------------------------

class jobPackage:
    # A class to manage a particular job package. The job directory should
    # already have been set up by the dispatcher.

    def __init__(self, job_id, parms, job_dir, job_url):
        # Tool-specific actions to create a job package.
        # Search and replace in template files to generate files for job.
        self.tool_name = tool_name
        self.job_id    = job_id
        self.job_dir   = job_dir
        self.job_url   = job_url
        self.parms     = parms
        self.slurm_id  = 0
        self.status    = helpers.STAT_UNKNOWN
        self.detail    = ""
        helpers.process_template(self.job_dir+"inlist", parms)
	    # TODO: Add more helpers.process_template for other inlist files for mesa_binary
        helpers.process_template(self.job_dir+"inlist1_special", parms)
        helpers.process_template(self.job_dir+"inlist2_special", parms)
        helpers.process_template(self.job_dir+"inlist_project", parms)
        helpers.process_template(self.job_dir+"inlist_defaults", parms)

    def getJobDetailStatus(self):
        # Any tool-specific details from the Slurm job status once it
        # has begun to execute. Return a string with any necessary embedded
        # newlines or HTML markup. Newlines will be converted to <br> tags.
        output = ""
        try:
            # FIXME: Need to change for mesa_binary
            output += helpers.show_text_file(self.job_dir+"stdout", 10)
            if self.status == helpers.STAT_COMPLETED:
                output += helpers.blank_lines(1)
                output += helpers.show_image(self.job_url+"/plot.png")
                output += helpers.blank_lines(1)
                output += helpers.show_movie(self.job_url+"/splash_xz_dens_8422566.mp4", w=800, h=600, mtype="video/mp4")
        except:
            output = "could not read stdout file"
        return output

    def preSlurmActions(self):
        # Anything you want to do before the Slurm script is submitted.
        # If anything fails, raise an exception and it will be caught by the
        # shepherd.
        return

    def postSlurmActions(self):
        # Anything you want to do after the Slurm script completes.
        # If anything fails, raise an exception and it will be caught by the
        # shepherd.
        return
