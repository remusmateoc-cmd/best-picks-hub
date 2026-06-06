@echo off
cd /d "c:\Ai Cloude code\aplicatie de minat\product-research-agent"

if not exist logs mkdir logs

echo [%date% %time%] === START UPDATE === >> logs\auto_update.log

:: Scaneaza produse si genereaza site (raspunde automat "y" la deploy)
echo y | python main.py >> logs\auto_update.log 2>&1

:: Publica pe GitHub
git add docs/ reports/ >> logs\auto_update.log 2>&1
git commit -m "auto-update %date%" >> logs\auto_update.log 2>&1
git push origin main >> logs\auto_update.log 2>&1

echo [%date% %time%] === GATA === >> logs\auto_update.log
