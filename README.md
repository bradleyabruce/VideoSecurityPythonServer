# VideoSecurityPythonServer

## Known Issues
1. Numpy
For some reason, the installing the newest version of the numpy package (v1.19 at the time of writing) will cause an issue when attempting to run the project. Installing v1.18 in place of v1.19 seems to fix this issue. The older version can be installed using: 
> pip install numpy==1.18