@echo off
REM ============================================================
REM  Gera SinapescREAP.exe para instalar/usar no notebook Windows
REM  Requisitos: Python 3.10+ instalado e no PATH
REM ============================================================
cd /d "%~dp0"

echo [1/3] Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [2/3] Gerando executavel com PyInstaller...
python -m PyInstaller --noconfirm build_exe.spec
if errorlevel 1 goto :error

echo [3/3] Pronto!
echo.
echo Arquivo gerado:
echo   dist\SinapescREAP.exe
echo.
echo Copie esse .exe para o notebook e execute. Na primeira vez,
echo abra Configuracoes e importe o JSON da Conta de Servico Google.
echo.
pause
exit /b 0

:error
echo.
echo Falha na geracao do exe. Verifique se o Python esta instalado.
pause
exit /b 1
