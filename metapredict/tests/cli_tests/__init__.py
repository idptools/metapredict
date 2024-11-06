import subprocess
import pytest
import os

## Init file for the CLI tests in metapredict
##
##
##

def run_command(cmd, outfile=None):
    """
    This function is a catch-all function that 
    
    1. Deletes a putative output file 
    2. Runs 

Function to run the command-line tool and return the output."""
    

    # if an outpufile was passed, try and delete and then check
    # it was actually deleted
    if outfile:
        try:
            os.remove(outfile)
        except Exception:
            pass

        # check the file is missing. This raises an exception if the file doesn't get removed
        if os.path.isfile(outfile):
            raise Exception('When preparing to run the command, the output file was not deleted')

    # run the command using subproccess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # return the output from subprocess, which has the following dot-variables associated
    # with it:
    #
    # .stdout (standard output to screen)
    # .stderr (standard error to screen)
    # .returncode (command return code; 0 = no errror)
    #
    return result