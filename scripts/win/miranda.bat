@echo off

%~dp0\bin\uv.exe run --with-requirements requirements.txt --cache-dir .uvcache --offline main.py