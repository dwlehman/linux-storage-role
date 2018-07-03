import subprocess

def run_command(command):
    """ Run a git command.

        :return: (stdout, stderr, returncode) tuple
    """
    proc = subprocess.Popen(command,
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = proc.communicate()
    while True:
        if proc.returncode is not None:
            return (stdoutdata.decode('utf-8'), stderrdata.decode('utf-8'), proc.returncode)

