@echo off
rem Compila y lanza las pruebas A-J. Pide las contrasenas de los usuarios de demostracion.
cd /d "%~dp0"
javac -encoding UTF-8 -d clases -cp lib\postgresql-42.7.14.jar src\nova\*.java || exit /b 1
java -cp "clases;lib\postgresql-42.7.14.jar" nova.PruebasRubrica
