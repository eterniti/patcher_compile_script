What is is this?
This is a simple python script that will download a toolchain and the xv2patcher source code and build it.
The latest version of the script can always be downloaded from: https://github.com/eterniti/patcher_compile_script


This project is born from the paranoia introduced by antivirus vendor by flaging the patcher dlls as virus.

The purpose is that just anyone can easily compile their own version of the patcher and compare it with the one from the release and verify they're EQUIVALENT.

To compare the dll produced by this script and the official one, please read "HOW TO COMPARE DLLS.txt" (you can't just compare file hashes!)


Requirements: python. Which version? Dunno, I use 3.10, I guess any 3.x that is not too old will work.
You also need to have git installed.


You don't need to install python requirements.txt by yourself. The script will use its own python virtual environment and install its dependencies (it won't affect your other python apps)

You just need to double click RUN.bat (DO NOT run the .py files directly!)


The script will only download a mingw64 if one hasn't been downloaded before.
So, if at any point you want to change the mingw64 (only available in "Custom" mode), just delete the mingw64 folder before running the script.

The xv2patcher compilation will give LOTS of warning. Just ignore them (I will address warnings in the future)
