@echo off
title Djamtala Scripts
cd /d "%~dp0"
python outils\app_scripts.py
if errorlevel 1 pause
