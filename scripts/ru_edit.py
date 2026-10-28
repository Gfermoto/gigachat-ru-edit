#!/usr/bin/env python3
"""Русская редактура через GigaChat API. Credentials: ~/.config/gigachat.env"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ENV_PATH = Path.home() / ".config" / "gigachat.env"

BASE_SYSTEM = """Ты литературный редактор русского языка. Правишь текст, не пишешь с нуля.

Правила:
- Сохрани смысл, факты, длину (±10%) и ритм фразы.
- Убери только явные ошибки, кальки и тяжёлый канцелярит.
- Не делай текст «официальнее»: запрещены обороты вроде «является»,
  «осуществляет», «в рамках», «по вопросу», «данный».
- Живые глаголы не заменяй на канцелярит («осуществляет приём», «производит анализ»).
- Тон спокойный, без пафоса и рекламного шума.
- Не добавляй обещания, фичи и цифры, которых не было.
- Если текст уже хорош — верни его без изменений.
- Ответ только результатом правки — без пояснений и кавычек вокруг всего текста.
"""


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def system_prompt() -> str:
    terms = (os.environ.get("GIGACHAT_PRESERVE_TERMS") or "").strip()
    if not terms:
        return BASE_SYSTEM
    cleaned = ", ".join(t.strip() for t in terms.split(",") if t.strip())
    if not cleaned:
        return BASE_SYSTEM
    extra = (
        f"- Не трогай и не переводи термины: {cleaned}.\n"
    )
    # Insert before the final "Ответ только…" rule
    marker = "- Если текст уже хорош"
    if marker in BASE_SYSTEM:
        return BASE_SYSTEM.replace(marker, extra + marker)
    return BASE_SYSTEM + "\n" + extra


def client():
    from gigachat import GigaChat

    creds = (os.environ.get("GIGACHAT_CREDENTIALS") or "").strip()
    if not creds:
        print(
            "Нет GIGACHAT_CREDENTIALS в окружении или ~/.config/gigachat.env.\n"
            "Studio → Получить ключ → вставить Authorization Key (Basic …).",
            file=sys.stderr,
        )
        sys.exit(2)
    scope = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    model = os.environ.get("GIGACHAT_MODEL", "GigaChat-3-Ultra")
    base_url = (os.environ.get("GIGACHAT_BASE_URL") or "").strip() or None
    verify = os.environ.get("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    kwargs = dict(
        credentials=creds,
        scope=scope,
        model=model,
        verify_ssl_certs=verify,
        timeout=120.0,
    )
    if base_url:
        kwargs["base_url"] = base_url
    return GigaChat(**kwargs)


def edit_one(giga, text: str) -> str:
    text = text.strip()
    if not text:
        return text
    from gigachat.models import Chat, Messages, MessagesRole

    payload = Chat(
        messages=[
            Messages(role=MessagesRole.SYSTEM, content=system_prompt()),
            Messages(
                role=MessagesRole.USER,
                content="Отредактируй русский текст:\n\n" + text,
            ),
        ],
        temperature=0.2,
    )
    resp = giga.chat(payload)
    out = resp.choices[0].message.content or ""
    return out.strip()


def edit_batch(giga, items: list[dict]) -> list[dict]:
    """items: [{id, text}, ...] → [{id, out}, ...]"""
    blob = json.dumps(
        [{"id": it["id"], "text": it["text"]} for it in items],
        ensure_ascii=False,
        indent=2,
    )
    from gigachat.models import Chat, Messages, MessagesRole

    user = (
        "Отредактируй поле text у каждого объекта. Верни ТОЛЬКО JSON-массив "
        'вида [{"id":"...","out":"..."}, ...] с теми же id, без markdown.\n\n'
        + blob
    )
    payload = Chat(
        messages=[
            Messages(role=MessagesRole.SYSTEM, content=system_prompt()),
            Messages(role=MessagesRole.USER, content=user),
        ],
        temperature=0.2,
    )
    raw = (giga.chat(payload).choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return [{"id": it["id"], "out": edit_one(giga, it["text"])} for it in items]
    if not isinstance(parsed, list):
        raise SystemExit("GigaChat вернул не массив JSON")
    by_id = {str(x.get("id")): x.get("out", "") for x in parsed if isinstance(x, dict)}
    return [{"id": it["id"], "out": by_id.get(str(it["id"]), it["text"])} for it in items]


def main() -> int:
    load_env(ENV_PATH)
    ap = argparse.ArgumentParser(description="GigaChat RU edit")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Один фрагмент")
    g.add_argument("--json-file", type=Path, help='JSON [{"id","text"},...] или {"id":"text"}')
    ap.add_argument("--out", type=Path, help="Куда писать результат (default stdout)")
    args = ap.parse_args()

    with client() as giga:
        if args.text is not None:
            result = edit_one(giga, args.text)
            data = result
        else:
            items = json.loads(args.json_file.read_text(encoding="utf-8"))
            if isinstance(items, dict):
                items = [{"id": k, "text": v} for k, v in items.items()]
            edited = edit_batch(giga, items)
            data = json.dumps(edited, ensure_ascii=False, indent=2)

    if args.out:
        args.out.write_text(data if isinstance(data, str) else data, encoding="utf-8")
    else:
        sys.stdout.write(data if isinstance(data, str) else data)
        if not str(data).endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
