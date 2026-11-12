@echo off
rem Compila y arranca la aplicacion. Necesita javac y java en el PATH (JDK 17).
cd /d "%~dp0"
javac -encoding UTF-8 -d clases -cp lib\postgresql-42.7.14.jar src\nova\*.java || exit /b 1
java -cp "clases;lib\postgresql-42.7.14.jar" nova.VentanaLogin
