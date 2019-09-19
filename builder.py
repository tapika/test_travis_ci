#!/usr/bin/python
import os, sys, platform
import subprocess, shlex, shutil
import datetime
import psutil

isWindows = platform.system().lower().find("windows") != -1

def printEnv():
    print("---------------------------------------------------")
    print("Environment variables:")
    print("---------------------------------------------------")
    for item, value in os.environ.items():
        print('{}: {}'.format(item, value))

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

#--------------------------------------------------------------
# Start command, if exit code is not zero, throw exception.
#--------------------------------------------------------------
def execcmd(cmd, measureTime = True, timeout = 60*60*60):
    if measureTime:
        print(cmd)
        sys.stdout.flush()
        start_time = datetime.datetime.now() 

    proc = subprocess.Popen(cmd, shell=True)
    try:
        proc.wait(timeout=timeout)
        exitCode = proc.returncode
    except subprocess.TimeoutExpired:
        print("- Timeout, killing executing process")
        sys.stdout.flush()
        kill(proc.pid)
        return False

    time_elapsed = datetime.datetime.now() - start_time 
    if measureTime:
        print('\nElapsed time: {} sec\n'.format(time_elapsed))
        sys.stdout.flush()
                                 
    if exitCode != 0:
        msg="Command '{}' failed, exit code: {}".format(cmd, exitCode)
        raise Exception(msg)

    return True

if isWindows:
    vswhere_path = r"c:\Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"

    vs_path = os.popen('"{}" -latest -property installationPath'.format(vswhere_path)).read().rstrip()
    if vs_path == "":
        vs_path="C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise"

    vsvars_path = os.path.join(vs_path, "VC\\Auxiliary\\Build\\vcvars64.bat")

    if not os.path.exists(vsvars_path):
        print("Error: " + vsvars_path + " does not exists")
        sys.stdout.flush()

    output = os.popen('"{}" && set'.format(vsvars_path)).read()

    for line in output.splitlines():
        pair = line.split("=", 1)
        if(len(pair) >= 2):
            os.environ[pair[0]] = pair[1]


if os.utime in getattr(os, 'supports_follow_symlinks', []):
    def lutime(path, times):
        os.utime(path, times, follow_symlinks=False)
else:
    def lutime(path, times):
        if not os.path.islink(path):
            os.utime(path, times)


#--------------------------------------------------------------
# Clones or checkouts git repostory, restores modification times of 
# each file.
#--------------------------------------------------------------
def gitClone(gitUrl, dir, setTimestamps = True):

    if os.path.exists(dir):
        os.chdir(dir)
        return

    cmd="git clone --depth=1 {} {}".format(gitUrl, dir)
    execcmd(cmd)

    if not setTimestamps:
        return

    filelist = set()

    for root, subdirs, files in os.walk(dir):
        for d in subdirs:
            if(d == ".git" or d == "out"):
                subdirs.remove(d);

        for file in files:
            filelist.add(os.path.relpath(os.path.join(root, file), dir))

    os.chdir(dir)

    mtime = 0
    start_time = datetime.datetime.now() 
    process = subprocess.Popen(shlex.split('git whatchanged --pretty=%at'), stdout=subprocess.PIPE)

    for line in process.stdout:
        line = line.strip().decode()

        # Blank line between Date and list of files
        if not line: continue

        # File line
        if line.startswith(':'):
            file = os.path.normpath(line.split('\t')[-1])
            if file in filelist:
                filelist.remove(file)
                # print mtime, file
                lutime(file, (mtime, mtime))

        # Date line
        else:
            mtime = int(line)

        # All files done?
        if not filelist:
            break

    time_elapsed = datetime.datetime.now() - start_time 
    print('\nTimestamps updated in: {} sec\n'.format(time_elapsed))

