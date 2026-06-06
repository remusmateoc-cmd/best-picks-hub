@echo off
cd /d "c:\Ai Cloude code\aplicatie de minat\product-research-agent"

echo [%date% %time%] Pornesc scanarea...

:: Ruleaza agentii si genereaza site-ul (raspunde automat "y" la deploy)
echo y | python main.py >> logs\auto_update.log 2>&1

:: Push pe GitHub
git add docs/
git commit -m "auto-update %date%" >> logs\auto_update.log 2>&1
git push >> logs\auto_update.log 2>&1

echo [%date% %time%] Gata! Site actualizat.
