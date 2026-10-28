# gigachat-ru-edit

[Cursor Agent Skill](https://cursor.com/docs) + CLI для **литературной правки русского текста** через [GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview).

По умолчанию: модель [`GigaChat-3-Ultra`](https://developers.sber.ru/docs/ru/gigachat/models/gigachat-3-ultra.md) на `https://api.giga.chat/v1` (Freemium для физлиц, scope `GIGACHAT_API_PERS`).

## Возможности

- Спокойная правка грамматики и канцелярита **без переписывания с нуля**
- Один фрагмент или пакет JSON-строк
- Секреты только в `~/.config/gigachat.env`
- Опциональный список терминов (`GIGACHAT_PRESERVE_TERMS`), которые нельзя переводить

## Установка skill в Cursor

```bash
git clone https://github.com/Gfermoto/gigachat-ru-edit.git ~/.cursor/skills/gigachat-ru-edit
```

Перезапустите агент / откройте новый чат — skill подхватится по `description` в `SKILL.md`.

## Setup API

1. Получите Authorization Key в [кабинете разработчика](https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api).
2. Создайте env:

```bash
mkdir -p ~/.config
cp .env.example ~/.config/gigachat.env
chmod 600 ~/.config/gigachat.env
# отредактируйте GIGACHAT_CREDENTIALS=Basic …
```

3. Python-зависимости:

```bash
uv venv ~/.local/share/gigachat-ru-edit/.venv
uv pip install --python ~/.local/share/gigachat-ru-edit/.venv/bin/python -r requirements.txt
# или: pip install -r requirements.txt  (в своём venv)
```

## CLI

```bash
PY=~/.local/share/gigachat-ru-edit/.venv/bin/python
SKILL=~/.cursor/skills/gigachat-ru-edit

$PY "$SKILL/scripts/ru_edit.py" --text 'Текст для правки'

# пакет
echo '[{"id":"a","text":"Привет как дела"}]' > /tmp/ru.json
$PY "$SKILL/scripts/ru_edit.py" --json-file /tmp/ru.json
```

## Для агента

Инструкции агенту — в [`SKILL.md`](./SKILL.md). Кратко: собрать RU-фрагменты → CLI → показать diff → применять после OK.

## Лицензия

[MIT](./LICENSE)
