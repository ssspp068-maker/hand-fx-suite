# Старт

1. Скачай: https://github.com/ssspp068-maker/hand-fx-suite/archive/refs/heads/main.zip
2. Распакуй
3. Запусти `run.bat`

Готово. Откроется окно с камерой; клавиши `1`…`5` — режимы.

Если Python не установлен — поставь **3.11** с https://www.python.org/downloads/  
(включи галку **Add python.exe to PATH**). Подойдёт и 3.10 / 3.12.

## Если вылетело с `function 'free' not found`

Это старый MediaPipe. Лечение:

1. Удали папку `.venv` внутри проекта
2. Снова запусти `run.bat` (подтянется MediaPipe ≥ 0.10.31)

## Камера

```bat
run.bat --camera 1
```
