# Hand FX Suite

**Скачать с GitHub (облако Cursor файлы само не отдаёт):**

- Репозиторий: https://github.com/ssspp068-maker/hand-fx-suite
- ZIP: https://github.com/ssspp068-maker/hand-fx-suite/archive/refs/heads/main.zip

```bat
git clone https://github.com/ssspp068-maker/hand-fx-suite.git
cd hand-fx-suite
run.bat
```

`run.bat` сам: venv → pip → скачает модели MediaPipe → запустит `main.py`.

---

Один Windows-проект, который собирает идеи из 5 Instagram-рилсов:

| Клавиша | Режим | Откуда идея |
|--------|--------|-------------|
| `1` | **Portal** — фильтр внутри полигона между пальцами | OpenCV portal / filter hands |
| `2` | **Delete Me** — «удаление» человека с сохранённого фона | invisibility / person delete |
| `3` | **Cubes** — wireframe-кубы на ладонях | TouchDesigner AR cubes |
| `4` | **Style Mask** — стилизованный слой в маске по рукам | CapCut + AI mask (локальный аналог) |
| `5` | **Trails** — скелет, шлейфы пальцев, блобы | TD hand tracking / lines+blobs |

> Это **не 1:1 копия** каждого рилса (особенно TouchDesigner и CapCut+Kling). Это один Python-стек, который даёт тот же класс эффектов локально на вебкаме.

## Быстрый старт (Windows)

Нужно: **Python 3.10–3.12** (рекомендуется 3.11), вебкам.

```bat
cd hand-fx-suite
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
python main.py
```

Если камера занята / чёрный экран:

```bat
python main.py --camera 1
python main.py --no-mirror
```

## Клавиши

### Глобальные
- `1`…`5` — смена режима
- `M` — зеркало (selfie)
- `H` — подсказки
- `S` — скриншот в `screenshots/`
- `Q` / `Esc` — выход

### По режимам
- **Portal:** `F` фильтр, кулак/сжатие пальцев = lock портала, `R` reset, `G` скелет
- **Delete Me:** отойти из кадра → `B` захват фона → войти обратно; `E` on/off, `X` hitbox
- **Cubes:** `G` скелет
- **Style Mask:** `F` форма маски (quad/diamond/strip), опционально положи `assets/style_overlay.png`
- **Trails:** `V` блобы, `G` скелет, `C` очистить шлейфы

## Структура

```
hand-fx-suite/
  main.py
  requirements.txt
  HANDOFF.md
  models/                 # уже лежит в проекте
    hand_landmarker.task
    selfie_segmenter.tflite
  core/                   # camera / hands / person / fx
  modes/                  # 5 режимов
  assets/                 # сюда style_overlay.png (опционально)
  screenshots/
```

## Ограничения (важно)

1. **Style Mask** без внешнего AI: если нет `assets/style_overlay.png`, используется локальный OpenCV-stylize (не Kling/CapCut).
2. **Cubes / Trails** — Python/OpenCV-аналог TD, не `.toe` проект.
3. **Delete Me** зависит от освещения и фона; сначала обязательно `B` на пустой сцене.
4. Нужен **MediaPipe ≥ 0.10.31** (Tasks API). Версии `0.10.30` на Windows + Python 3.12 падают с `function 'free' not found`.

## Если вылетело с `function 'free' not found`

1. Удали папку `.venv` в проекте
2. Запусти `run.bat` снова

## Если pip ругается на mediapipe

- Поставь Python **3.11 x64** (или 3.10 / 3.12)
- Удали `.venv`, затем только: `run.bat`
- Не используй Python 3.13+, если wheel ещё нет
