Requirements: python. Which version? Dunno, I use 3.10, I guess any 3.x that is not too old will work.
You also need to have git installed.


You don't need to install python requirements.txt by yourself. The script will use its own python virtual environment and install its dependencies (it won't affect your other python apps)

You just need to double click RUN.bat (DO NOT run the .py files directly!)


The script will only download a mingw64 if one hasn't been downloaded before.
So, if at any point you want to change the mingw64 (only available in "Custom" mode), just delete the mingw64 folder before running the script.

The xv2patcher compilation will give LOTS of warning. Just ignore them (I will address warnings in the future)
