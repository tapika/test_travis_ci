#!/usr/bin/python
import os
import sys
import platform

isWindows = platform.system().lower().find("windows") != -1

if isWindows:
    vswhere_path = r"c:\Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
    vs_path = os.popen('"{}" -latest -property installationPath'.format(vswhere_path)).read().rstrip()
    vsvars_path = os.path.join(vs_path, "VC\\Auxiliary\\Build\\vcvars64.bat")

    output = os.popen('"{}" && set'.format(vsvars_path)).read()

    for line in output.splitlines():
        pair = line.split("=", 1)
        if(len(pair) >= 2):
            os.environ[pair[0]] = pair[1]


print("OS: " + platform.system().lower())
print("Current directory: " + os.getcwd() )

#print("environment variables:")
#for item, value in os.environ.items():
#    print('{}: {}'.format(item, value))

#if isWindows:
#    exitCode=os.system("cmake . && cmake --build .")
#else:
#    exitCode=os.system("./bootstrap && make && sudo make install")

#sys.exit(exitCode)

