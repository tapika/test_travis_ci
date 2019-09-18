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

scriptDir=os.path.dirname(os.path.realpath(__file__))
projDir = os.path.join(scriptDir, "..", "cppreflect")

builder.gitClone("https://github.com/tapika/cppreflect", projDir)

if isWindows:
    cacheDir = "x64-" + buildType
else:
    cacheDir = "WSL-" + buildType

cachePath = os.path.join(scriptDir, "..", "out", cacheDir)

if not os.path.exists(cachePath):
    os.makedirs(cachePath)

os.chdir(cachePath)

#cmd = "cmake -G Ninja -DCMAKE_BUILD_TYPE={}".format(buildType)
cmd = "cmake -DCMAKE_BUILD_TYPE={}".format(buildType)
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

cmd='cmake --build "{}" --config {}'.format(cachePath, buildType)
execcmd(cmd)


