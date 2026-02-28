from core.billing.trial import is_trial_expired


def should_pause_site(trial_ends_at) -> bool:
    """Pause only free-credit pages after their 7-day trial expires.
    Paid-credit pages have trial_ends_at = None and are never paused."""
    if trial_ends_at is None:
        return False
    return is_trial_expired(trial_ends_at)


def get_paused_html(business_name: str = "") -> str:
    name = business_name or "This site"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Site Paused</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #f9fafb;
            color: #374151;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
        }}
        h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        p {{
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{name}</h1>
        <p>This site is currently paused. The owner can reactivate it by purchasing more credits.</p>
    </div>
</body>
</html>"""
