# Study Task Manager
### COMPSCI5012 Internet Technology 2025-26 — Group BP

A Django web application for university students to manage study tasks and deadlines.

---

## Setup & Run

### 1. Install Django
```bash
pip install -r requirements.txt
```

### 2. Apply migrations (creates SQLite database)
```bash
python manage.py migrate
```

### 3. (Optional) Create a superuser for Django admin
```bash
python manage.py createsuperuser
```

### 4. Run the development server
```bash
python manage.py runserver
```

### 5. Open your browser
Visit: http://127.0.0.1:8000/

---

## Features

| Requirement | Status | Description |
|---|---|---|
| M1 | ✅ | User registration & login |
| M2 | ✅ | Create tasks with titles |
| M3 | ✅ | Set deadlines on tasks |
| M4 | ✅ | Per-user categories |
| M5 | ✅ | Dashboard task list |
| M6 | ✅ | Mark tasks as completed |
| S1 | ✅ | Edit tasks |
| S2 | ✅ | Delete tasks |
| C1 | ✅ | Filter by category |
| W1 | ✅ | Calendar integration |

---

## Project Structure

```
studytaskmanager/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← created after migrate
├── studytaskmanager/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/
│   ├── migrations/
│   ├── templates/
│   │   └── tasks/
│   │       ├── partials/
│   │       │   └── task_row.html
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── task_form.html
│   │       └── ...
│   ├── static/
│   │   └── tasks/
│   │       ├── styles.css
│   │       └── app.js
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_ajax.py
│   ├── services.py         ← business logic helpers
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
```

---

## Tech Stack
- **Backend**: Django 4.2 (Python)
- **Database**: SQLite
- **Frontend**: HTML + Vanilla JS + Bootstrap 5
- **Auth**: Django built-in authentication

## WCAG 2.2 Accessibility
- All forms have explicit `<label>` elements
- Error messages use `role="alert"` for screen readers
- Focus states styled with visible outlines (`:focus-visible`)
- Skip link added (`Skip to main content`)
- Live status updates use `role="status"` + `aria-live="polite"`
- `aria-label` on icon buttons for screen readers
- Colour contrast meets AA standard

## AJAX Interactivity
- Dashboard task completion uses asynchronous `fetch` requests to:
  - Mark a task complete without reloading
  - Update pending/completed counters
  - Move the task into the completed list instantly
- Progressive enhancement retained: links still fall back to the normal non-JS complete flow.

## Lighthouse Before/After Evidence (How To Capture)
1. Open Chrome DevTools on `/login/` and `/dashboard/`.
2. Run Lighthouse for Performance, Accessibility, and Best Practices.
3. Save screenshots/exports for the **before** report.
4. Apply UI optimizations (deferred JS, static CSS/JS, semantic landmarks).
5. Re-run Lighthouse on the same pages and save **after** screenshots.
6. Include tool, pages tested, key score changes, and short reflection in your report.

Suggested 4-6 line reflection:
- We deferred third-party and app JavaScript so rendering is less blocked on first load.
- We moved presentation and behavior out of templates into static CSS/JS files, reducing inline overhead.
- We reduced asset complexity to Bootstrap CDN plus one local stylesheet and one local script.
- We improved semantic structure (`main`, labels, status region, skip link), which improved accessibility scoring.
- Dashboard interactivity now uses AJAX updates instead of full reloads, improving perceived responsiveness.

## Run Tests
```bash
python manage.py test
```

Includes tests for:
- Dashboard auth protection
- User isolation on dashboard data
- AJAX completion behavior
- AJAX completion access control
