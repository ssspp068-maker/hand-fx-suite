# HANDOFF — понедельник

## Как забрать проект из облака

1. Открой: https://github.com/ssspp068-maker/hand-fx-suite
2. кнопка **Code → Download ZIP**  
   или: https://github.com/ssspp068-maker/hand-fx-suite/archive/refs/heads/main.zip
3. Распакуй на Windows
4. Запусти `run.bat`

Альтернатива:

```bat
git clone https://github.com/ssspp068-maker/hand-fx-suite.git
cd hand-fx-suite
run.bat
```

## Что делает run.bat

1. Создаёт `.venv` на Python 3.11
2. `pip install -r requirements.txt`
3. `python scripts/download_models.py` (модели не в git — качаются отдельно)
4. `python main.py`

## Чеклист PASS/FAIL

1. Окно открылось, видна камера
2. `1` Portal — фильтр между руками, `F` меняет фильтр
3. Кулак фиксирует портал, `R` сбрасывает
4. `2` Delete Me — отойти, `B`, войти → человек «пропадает»
5. `3` Cubes — кубы на ладонях
6. `4` Style Mask — маска со стилизацией, `F` форма
7. `5` Trails — шлейфы + блобы
8. `S` скриншот, `Q` выход

## Если не стартует

- Нет Python 3.10–3.12 → поставь 3.11 с python.org (галка PATH)
- `function 'free' not found` → удали папку `.venv`, снова `run.bat` (нужен mediapipe ≥ 0.10.31)
- Камера занята → закрой Zoom/Telegram, или `run.bat --camera 1`
- Модели не скачались → интернет / повтор `python scripts/download_models.py`
