# FastHTML & HTMX Reference

> Converted to Markdown (.md)

---

## About FastHTML

```python
from fasthtml.common import *
```

FastHTML is a Python library that brings together **Starlette**, **Uvicorn**, **HTMX**, and fastcore’s **FT (FastTags)** to build server‑rendered, HTML‑first applications.

### Key Notes

* Not compatible with FastAPI syntax (HTML‑first, not API‑first)
* Works with Pico CSS by default (optional)
* Compatible with vanilla JS and Web Components
* Not compatible with React, Vue, or Svelte
* Use `serve()` to run the app
* Use `Titled()` when a page title is required

---

## Minimal App

```python
from fasthtml.common import *
app, rt = fast_app()

name = str_enum('names', 'Alice', 'Bev', 'Charlie')

@rt
def foo(nm: name):
    return Title("FastHTML"), H1("My web app"), P(f"Hello, {nm}!")

serve()
```

Run:

```bash
python main.py
```

---

## FastTags (FT)

FastTags are Python expressions that map directly to HTML.

```python
Title("FastHTML"), H1("My web app"), P("Hello")
```

### Attributes

* Positional args → children
* Keyword args → attributes
* Use `cls` for `class`

```python
P("Hello", cls="text-muted")
```

---

## JavaScript

Use `Script()` to embed JS:

```python
Script(src="https://cdn.plot.ly/plotly.min.js")
```

Prefer Python over JS when possible.

---

## Routing & Responses

Handlers may return:

1. FastTags / tuples
2. Starlette Responses
3. JSON‑serializable objects

```python
@rt
async def serve_static(fname:str):
    return FileResponse(fname)
```

---

## Forms & Data Binding

```python
@dataclass
class Profile:
    email: str
    age: int

@rt
def edit(profile: Profile):
    return profile
```

FastHTML automatically binds form fields.

---

## Sessions & Cookies

```python
@rt
def set_cookie():
    return P("Set"), cookie("token", "abc")
```

---

## Authentication (Beforeware)

```python
def auth(req, sess):
    if not sess.get("user"):
        return RedirectResponse("/login")

app, rt = fast_app(before=Beforeware(auth))
```

---

## WebSockets

```python
app, rt = fast_app(exts='ws')

@rt
async def index():
    return Div(hx_ext='ws', ws_connect='/ws')
```

---

## Server‑Sent Events (SSE)

```python
@rt
async def stream():
    return EventStream(generator())
```

---

## Fastlite (SQLite)

```python
from fastlite import *

db = database('app.db')

class User:
    id: int
    name: str

users = db.create(User)
```

---

## MonsterUI

Tailwind‑based component system for FastHTML.

```python
from monsterui.all import *

Card(P("Hello"))
```

---

## HTMX Reference (Summary)

### Common Attributes

* `hx-get`
* `hx-post`
* `hx-target`
* `hx-swap`
* `hx-trigger`

### CSS Classes

* `htmx-request`
* `htmx-swapping`
* `htmx-settling`

---

## Starlette Notes

FastHTML inherits from Starlette.

```python
request.headers
request.url
request.session
```

---

## Final Notes

* HTML‑first mindset
* Python over JavaScript
* Server‑rendered by default
* HTMX for interactivity

---

*End of Markdown document.*
