#!/usr/bin/python
import os, sys, platform
import argparse
import builder
from builder import execcmd

isWindows = platform.system().lower().find("windows") != -1

parser = argparse.ArgumentParser()
parser.add_argument('-buildtype', help='Select build configuration, one of: Debug/Release')
args = parser.parse_args()

buildType = args.buildtype
if buildType == None: buildType="Release"

builtByBuilder=os.environ.get('TRAVIS')

print("build.py, running on python " + platform.python_version() )

if isWindows:
    execcmd("where ninja")
else:
    execcmd("which ninja")

scriptDir=os.path.dirname(os.path.realpath(__file__))
projDir = os.path.join(scriptDir, "..", "src")

builder.gitClone("-b cling-patches http://root.cern.ch/git/llvm.git", projDir)
toolsDir = os.path.join(projDir, "tools")

os.chdir(toolsDir)
builder.gitClone("http://root.cern.ch/git/cling.git", "cling")

os.chdir(toolsDir)
builder.gitClone("-b cling-patches http://root.cern.ch/git/clang.git", "clang")

if isWindows:
    cacheDir = "x64-" + buildType
else:
    cacheDir = "WSL-" + buildType

cachePath = os.path.join(scriptDir, "..", "out", cacheDir)

if not os.path.exists(cachePath):
    os.makedirs(cachePath)

os.chdir(cachePath)

cmd = "cmake -G Ninja -DCMAKE_BUILD_TYPE={}".format(buildType)
#cmd = "cmake -DCMAKE_BUILD_TYPE={}".format(buildType)
# -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON

if isWindows:
    cmd = cmd + ' -DCMAKE_INSTALL_PREFIX:PATH="{}"'.format(os.path.join(scriptDir, "out", "install", cacheDir))

    #ninjaPath =  os.path.join(os.environ["VSINSTALLDIR"],"Common7\\IDE\\CommonExtensions\\Microsoft\\CMake\\Ninja\\ninja.exe" )
    #cmd = cmd + ' -DCMAKE_MAKE_PROGRAM="{}"'.format(ninjaPath)

    # cmake is really strict even to case sensitive paths. Vs uses 'X' in uppercase.
    #cl_path = os.popen('where cl.exe').read().rstrip().replace("Hostx64", "HostX64")
    #cmd = cmd + ' -DCMAKE_CXX_COMPILER:FILEPATH="{}"'.format(cl_path)
    #cmd = cmd + ' -DCMAKE_C_COMPILER:FILEPATH="{}"'.format(cl_path)

cmd = cmd + ' "{}"'.format(projDir)
execcmd(cmd)

buildCpus = 8
if builtByBuilder:
    buildCpus = 2

os.chdir(cachePath)
cmd='ninja -j {} cling'.format(buildCpus)
if not execcmd(cmd, True, 5*60):    # N min
    print ("\nNote: Cancelled build, timeout\n")


