#!/usr/bin/python
import os, sys, platform
import subprocess, shlex

isWindows = platform.system().lower().find("windows") != -1

def printEnv():
    print("---------------------------------------------------")
    print("Environment variables:")
    print("---------------------------------------------------")
    for item, value in os.environ.items():
        print('{}: {}'.format(item, value))

printEnv()

if isWindows:
    vswhere_path = r"c:\Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
    vs_path = os.popen('"{}" -latest -property installationPath'.format(vswhere_path)).read().rstrip()
    vsvars_path = os.path.join(vs_path, "VC\\Auxiliary\\Build\\vcvars64.bat")

    output = os.popen('"{}" && set'.format(vsvars_path)).read()

    print("Importing environment: ")
    print (output)

    for line in output.splitlines():
        pair = line.split("=", 1)
        if(len(pair) >= 2):
            os.environ[pair[0]] = pair[1]


printEnv()
print("OS: " + platform.system().lower())
#print("Current directory: " + os.getcwd() )

if isWindows:
    subprocess.call("where git", shell=True)

if os.utime in getattr(os, 'supports_follow_symlinks', []):
    def lutime(path, times):
        os.utime(path, times, follow_symlinks=False)
else:
    def lutime(path, times):
        if not os.path.islink(path):
            os.utime(path, times)

#--------------------------------------------------------------
# Start command, if exit code is not zero, throw exception.
#--------------------------------------------------------------
def execcmd(cmd):
    exitCode = subprocess.call(cmd, shell=True)
    if exitCode != 0:
        msg="Command '{}' failed, exit code: {}".format(cmd, exitCode)
        raise Exception(msg)

#--------------------------------------------------------------
# Clones git repostory, restores modification times of 
# each file.
#--------------------------------------------------------------
def gitClone(gitUrl, dir):
    if not os.path.exists(dir):
        execcmd("git clone {} {}".format(gitUrl, dir))

    filelist = set()

    for root, subdirs, files in os.walk(dir):
        for d in subdirs:
            if(d == ".git" or d == "out"):
                subdirs.remove(d);

        for file in files:
            filelist.add(os.path.relpath(os.path.join(root, file), dir))

    os.chdir(dir)

    mtime = 0
    process = subprocess.Popen(shlex.split('git whatchanged --pretty=%at'), stdout=subprocess.PIPE)

    for line in process.stdout:
        line = line.strip()

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
            mtime = long(line)

        # All files done?
        if not filelist:
            break


scriptDir=os.path.dirname(os.path.realpath(__file__))

projDir = os.path.join(scriptDir, "..", "cppreflect")
gitClone("https://github.com/tapika/cppreflect", projDir)

buildType = "Release"

if isWindows:
    cacheDir = "x64-" + buildType
else:
    cacheDir = "WSL-" + buildType

cachePath = os.path.join(scriptDir, "..", "cppreflect", "out", cacheDir)

if not os.path.exists(cachePath):
    os.makedirs(cachePath)

os.chdir(cachePath)

#cmd = "cmake -G Ninja -DCMAKE_BUILD_TYPE={}".format(buildType)
cmd = "cmake -DCMAKE_BUILD_TYPE={}".format(buildType)

if isWindows:
    cmd = cmd + ' -DCMAKE_INSTALL_PREFIX:PATH="{}"'.format(os.path.join(scriptDir, "out", "install", cacheDir))

    ninjaPath =  os.path.join(os.environ["VSINSTALLDIR"],"Common7\\IDE\\CommonExtensions\\Microsoft\\CMake\\Ninja\\ninja.exe" )
    cmd = cmd + ' -DCMAKE_MAKE_PROGRAM="{}"'.format(ninjaPath)

    # cmake is really strict even to case sensitive paths. Vs uses 'X' in uppercase.
    cl_path = os.popen('where cl.exe').read().rstrip().replace("Hostx64", "HostX64")
    cmd = cmd + ' -DCMAKE_CXX_COMPILER:FILEPATH="{}"'.format(cl_path)
    cmd = cmd + ' -DCMAKE_C_COMPILER:FILEPATH="{}"'.format(cl_path)

cmd = cmd + ' "{}"'.format(projDir)

print(cmd)
execcmd(cmd)

cmd='cmake --build "{}" --config {}'.format(cachePath, buildType)
print(cmd)
execcmd(cmd)


