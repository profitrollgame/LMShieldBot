#!/bin/bash
cd /home/supermine/Python/LMShieldBot
while true
do
        python3 shieldbot.py
        echo "Для полной остановки LMShieldBot сейчас пожалуйста, нажмите Ctrl+C до конца отсчёта!"
        echo "Перезагрузка через:"
        for i in 3 2 1
        do
                echo "$i..."
                sleep 1
        done
        echo "LMShieldBot запущен!"
done
