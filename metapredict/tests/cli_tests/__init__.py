import os
import subprocess
import sys

## Init file for the CLI tests in metapredict
##
## The command-line tools are run as `python -m metapredict.scripts.<module>`
## using the same interpreter that is running the tests, with the repository
## root placed first on PYTHONPATH. This means the tests always exercise the
## metapredict source in this checkout, even if a different (non-editable)
## copy of metapredict is installed in site-packages.
##

# directory holding the test files (tests/), and the repository root above the
# metapredict package, which is what needs to be importable as 'metapredict'
TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(os.path.dirname(TESTS_DIR))

# input FASTA file shared by the CLI tests, and the scratch directory outputs are written to
THREE_SEQS_FASTA = os.path.join(TESTS_DIR, 'input_data', 'three_seqs.fasta')
OUTPUT_DIR = os.path.join(TESTS_DIR, 'output')


def run_cli(command_name, arguments, outfile=None):
    """
    Run one of the metapredict command-line tools and return the completed
    process.

    Parameters
    ----------
    command_name : str
        Name of the console script as installed by pyproject.toml (e.g.
        'metapredict-predict-idrs'). This maps directly onto the module
        metapredict.scripts.<command_name with '-' replaced by '_'>.

    arguments : list of str
        Command-line arguments passed to the tool.

    outfile : str or None
        If provided, this file is deleted before the command runs so that a
        stale output file from an earlier run can never make a test pass.

    Returns
    -------
    subprocess.CompletedProcess
        The finished process, with .stdout, .stderr and .returncode
        (0 = no error) available.
    """

    # remove any old output file, and fail loudly if that didn't work
    if outfile is not None:
        if os.path.isfile(outfile):
            os.remove(outfile)
        if os.path.isfile(outfile):
            raise Exception('When preparing to run the command, the output file was not deleted')

    module_name = 'metapredict.scripts.' + command_name.replace('-', '_')
    cmd = [sys.executable, '-m', module_name] + list(arguments)

    # put this checkout first on the import path for the subprocess
    env = dict(os.environ)
    existing_path = env.get('PYTHONPATH', '')
    if existing_path:
        env['PYTHONPATH'] = REPO_ROOT + os.pathsep + existing_path
    else:
        env['PYTHONPATH'] = REPO_ROOT

    # the graphing tools only save files in these tests, so use a non-GUI
    # matplotlib backend to avoid needing a display
    env['MPLBACKEND'] = 'Agg'

    return subprocess.run(cmd, capture_output=True, text=True, cwd=TESTS_DIR, env=env)
