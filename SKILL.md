---
name: gigachat-ru-edit
description: >-
  Edits and polishes Russian prose via GigaChat API (grammar, style, calm tone).
  Use when the user asks for GigaChat / гигачат / правку русского / литературную
  редактуру, or when polishing RU UI copy, marketing text, docs, or PR descriptions.
---

# GigaChat — русская редактура

Cursor Agent Skill: правка русского текста через [GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview)
(`GigaChat-3-Ultra` на `https://api.giga.chat/v1` для физлиц Freemium).

Секреты **только** в `~/.config/gigachat.env` — никогда в git и не в чат.

## Когда вызывать

- Пользователь сказал «через GigaChat» / «гигачат» / «поправь русский»
- Полировка RU UI, маркетинга, docs, описаний PR / коммитов
- Пакетная правка JSON-словаря строк

**Не** вызывать для кода, API-идентификаторов, чисто EN-строк.

## Setup

1. Ключ: [GigaChat Developers](https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api) →
   Authorization Key (Basic …). Scope `GIGACHAT_API_PERS` для физлиц.
2. Файл `~/.config/gigachat.env` (chmod 600):

```bash
GIGACHAT_CREDENTIALS=Basic ....   # Authorization Key целиком
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_BASE_URL=https://api.giga.chat/v1
GIGACHAT_MODEL=GigaChat-3-Ultra
GIGACHAT_VERIFY_SSL_CERTS=false
# опционально: термины через запятую, которые нельзя переводить
# GIGACHAT_PRESERVE_TERMS=Hub,FOG,LoRa,MQTT
```

3. Venv + пакет:

```bash
uv venv ~/.local/share/gigachat-ru-edit/.venv
uv pip install --python ~/.local/share/gigachat-ru-edit/.venv/bin/python -r requirements.txt
```

4. Установка skill в Cursor (личное):

```bash
git clone https://github.com/Gfermoto/gigachat-ru-edit.git ~/.cursor/skills/gigachat-ru-edit
```

Или symlink на уже клонированный репозиторий.

## Workflow для агента

1. Собрать RU-фрагменты (абзац / ключи i18n / файл).
2. Запустить CLI — **не** выдумывать правки самому, если пользователь просил GigaChat:

```bash
PY=~/.local/share/gigachat-ru-edit/.venv/bin/python
SKILL=~/.cursor/skills/gigachat-ru-edit

$PY "$SKILL/scripts/ru_edit.py" --text 'Текст для правки'
$PY "$SKILL/scripts/ru_edit.py" --json-file /tmp/ru-in.json
# JSON in: [{"id":"k1","text":"…"}, …]  или  {"k1":"…","k2":"…"}
# stdout: plain text  или  [{"id","out"}, …]
```

3. Показать diff; применять в файлы только после OK (или если явно сказано «правь» / «применяй»).
4. Сохранять длину (±10%), смысл и тон. Не добавлять фичи и обещания.
5. Термины из `GIGACHAT_PRESERVE_TERMS` (и разумные product names из контекста) не переводить.

## Промпт (зашит в CLI)

Редактор, не автор с нуля: грамматика, порядок слов, канцелярит; без пафоса;
живые глаголы не заменять канцеляритом; если текст уже хорош — вернуть без изменений.

## Ошибки

| Симптом | Действие |
|---------|----------|
| Нет `GIGACHAT_CREDENTIALS` | Попросить Authorization Key, не гадать |
| 401 / 403 | Ключ / scope; перевыпуск в Studio |
| SSL в WSL | `GIGACHAT_VERIFY_SSL_CERTS=false` |
| Пустой batch JSON | CLI сам падает в правку по одному |

## Лицензия

MIT — см. `LICENSE`.
