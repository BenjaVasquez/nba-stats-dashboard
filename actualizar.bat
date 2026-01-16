@echo off
title NBA DASHBOARD - GESTION DE DATOS
color 0b

:menu
cls
echo ====================================================
echo    MENU DE ACTUALIZACION NBA
echo ====================================================
echo  1. Actualizar Fixture y Lesiones (Diario)
echo  2. Unir partes de Estadisticas (Merge JSON)
echo  3. Salir
echo ====================================================
set /p opt="Selecciona una opcion: "

if %opt%==1 (
    python process_fixture.py
    python fetch_injuries.py
    pause
    goto menu
)
if %opt%==2 (
    python merge_data.py
    pause
    goto menu
)
if %opt%==3 exit