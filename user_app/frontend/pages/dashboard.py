"""Dashboard page — project list or welcome screen."""

from fasthtml.common import Div, H1, H3, P, A, Span, Form, Button, Section, Safe, Script, Img, Input, Style

from user_app.frontend.layout import sidebar_layout

_FRIENDLY_STATE = {
    "draft": "Setting up",
    "input_ready": "Setting up",
    "memory_ready": "Ready to plan",
    "plan_ready": "Plan ready",
    "plan_approved": "Ready to build",
    "site_generated": "Ready to publish",
    "preview": "Ready to publish",
    "published": "Live",
    "error": "Needs attention",
}


def _initials(name: str) -> str:
    words = [w for w in name.split() if w]
    if not words:
        return "?"
    return "".join(w[0].upper() for w in words[:2])


def _accent(brand) -> str:
    """Return hex color (no #) for card accent gradient."""
    if brand and brand.primary_color:
        return brand.primary_color.lstrip("#")
    return "7c3aed"


def dashboard_page(user, projects, show_new_button=True, active_tab="unfinished", page=1):
    """Show welcome CTA if no projects, otherwise redesigned project cards."""

    total_projects = len(projects)
    published_projects_list = [p for p in projects if p.state.value == "published"]
    published_count = len(published_projects_list)
    unfinished_count = total_projects - published_count

    if active_tab == "live":
        display_projects = published_projects_list
    elif active_tab == "unfinished":
        display_projects = [p for p in projects if p.state.value != "published"]
    else:
        display_projects = projects

    ITEMS_PER_PAGE = 6
    total_items = len(display_projects)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    start_idx = (page - 1) * ITEMS_PER_PAGE
    paginated_projects = display_projects[start_idx:start_idx + ITEMS_PER_PAGE]

    # ── Page header ───────────────────────────────────────────────────────────
    page_header = Div(
        Div(cls="pc-header-glow"),
        Div(
            Div(
                Div(
                    Span("✦", cls="pc-header-eyebrow-icon"),
                    Span("Dashboard", cls="pc-header-eyebrow-text"),
                    cls="pc-header-eyebrow",
                ),
                H1("Your Pages", cls="pc-header-title"),
                Div(
                    Div(
                        Span(cls="pc-stat-dot pc-stat-dot--live"),
                        Span(str(published_count), cls="pc-stat-num"),
                        Span("live", cls="pc-stat-label"),
                        cls="pc-stat-badge",
                    ),
                    Div(cls="pc-stat-sep"),
                    Div(
                        Span(cls="pc-stat-dot pc-stat-dot--progress"),
                        Span(str(unfinished_count), cls="pc-stat-num"),
                        Span("in progress", cls="pc-stat-label"),
                        cls="pc-stat-badge",
                    ),
                    cls="pc-stats",
                ),
                cls="pc-header-left",
            ),
            A(
                Span("+", cls="pc-new-icon"),
                Span("New Page", cls="pc-new-text"),
                href="/pages/new",
                cls="pc-new-btn",
            ) if show_new_button else "",
            cls="pc-header-inner",
        ),
        cls="pc-page-header",
    )

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = Div(
        A("All", href="?tab=all&page=1",
          cls=f"pc-tab{'  pc-tab--active' if active_tab == 'all' else ''}"),
        A("Live", href="?tab=live&page=1",
          cls=f"pc-tab{'  pc-tab--active' if active_tab == 'live' else ''}"),
        A("Unfinished", href="?tab=unfinished&page=1",
          cls=f"pc-tab{'  pc-tab--active' if active_tab == 'unfinished' else ''}"),
        cls="pc-tabs",
    )

    # ── Cards ─────────────────────────────────────────────────────────────────
    cards = []

    if not projects:
        cards.append(Div(
            Div("✨", style="font-size:2.5rem;margin-bottom:0.75rem"),
            H3("Build your first website", style="margin-bottom:0.5rem;color:var(--color-text)"),
            P("From idea to live site in under 60 seconds.",
              style="color:var(--color-text-light);margin-bottom:1.5rem"),
            A("+ Create a Page", href="/pages/new", cls="button button-primary",
              style="text-decoration:none;display:inline-block"),
            cls="pc-empty",
        ))
    elif not paginated_projects:
        cards.append(Div(
            P("No pages in this category.", style="color:var(--color-text-light);font-style:italic"),
            cls="pc-empty",
        ))
    else:
        for p in paginated_projects:
            brand = p.brand_memory
            name = brand.business_name if brand else "Untitled"
            industry = brand.services[0] if brand and brand.services else ""
            state = p.state.value
            friendly = _FRIENDLY_STATE.get(state, state.replace("_", " "))
            is_published = state == "published"
            safe_name = name.replace("'", "\\'").replace('"', '\\"')
            acc = _accent(brand)
            initials = _initials(name)

            share_btn = (
                Button("Share",
                       cls="pc-action-btn",
                       onclick=f"showShareModal('{p.id}', '{safe_name}')")
                if is_published else ""
            )

            card = Div(
                # ── Gradient header ──────────────────────────────────────────
                A(
                    Div(
                        Div(initials, cls="pc-initials"),
                        Span(friendly, cls=f"pc-state-pill pc-state--{state}"),
                        cls="pc-card-header-inner",
                    ),
                    href=f"/pages/{p.id}",
                    cls="pc-card-header",
                    style=(
                        f"background:linear-gradient(135deg,#{acc}28 0%,#{acc}0a 100%);"
                        f"border-bottom:1px solid #{acc}22;"
                    ),
                ),
                # ── Body ─────────────────────────────────────────────────────
                A(
                    Div(
                        Div(name, cls="pc-name"),
                        Div(industry, cls="pc-industry") if industry else "",
                        cls="pc-body",
                    ),
                    href=f"/pages/{p.id}",
                    cls="pc-body-link",
                ),
                # ── Actions ──────────────────────────────────────────────────
                Div(
                    Div(
                        A("View →", href=f"/pages/{p.id}",
                          cls="pc-action-btn pc-action-btn--primary"),
                        A("Edit", href=f"/pages/{p.id}/edit",
                          cls="pc-action-btn"),
                        share_btn,
                        Button("Details",
                               cls="pc-action-btn",
                               hx_get=f"/pages/{p.id}/details",
                               hx_target="#modal-body",
                               onclick="document.getElementById('project-modal').style.display='flex'"),
                        cls="pc-action-left",
                    ),
                    Button("✕", cls="pc-delete-btn", type="button",
                           title="Delete",
                           onclick=f"openDeleteModal('{p.id}','{safe_name}')"),
                    cls="pc-actions",
                ),
                cls="pc-card",
            )
            cards.append(card)

    # ── Pagination ────────────────────────────────────────────────────────────
    pagination = ""
    if total_pages > 1:
        prev_btn = (
            A("← Prev", href=f"?tab={active_tab}&page={page-1}", cls="btn btn-outline btn-sm")
            if page > 1 else
            Button("← Prev", cls="btn btn-outline btn-sm", disabled=True)
        )
        next_btn = (
            A("Next →", href=f"?tab={active_tab}&page={page+1}", cls="btn btn-outline btn-sm")
            if page < total_pages else
            Button("Next →", cls="btn btn-outline btn-sm", disabled=True)
        )
        pagination = Div(
            prev_btn,
            Span(f"{page} / {total_pages}", style="font-size:0.875rem;color:var(--color-text-light)"),
            next_btn,
            style="display:flex;justify-content:center;align-items:center;gap:1rem;margin-top:2rem",
        )

    # ── Shared modal CSS ──────────────────────────────────────────────────────
    shared_modal_css = Safe("""<style>
.ob-modal-overlay{
  position:fixed;inset:0;z-index:1000;
  background:rgba(7,7,15,.82);backdrop-filter:blur(8px);
  display:flex;align-items:center;justify-content:center;padding:1rem;
}
.ob-modal-card{
  background:var(--color-surface,#0f0f24);
  border:1px solid var(--color-border,rgba(37,99,235,.18));
  border-radius:1.25rem;
  width:100%;
  box-shadow:0 0 0 1px rgba(255,255,255,.04),0 24px 64px rgba(0,0,0,.6);
  animation:ob-modal-pop .22s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes ob-modal-pop{
  from{opacity:0;transform:scale(.92) translateY(10px)}
  to{opacity:1;transform:scale(1) translateY(0)}
}
.ob-modal-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:1.25rem 1.5rem;
  border-bottom:1px solid var(--color-border,rgba(37,99,235,.18));
}
.ob-modal-header-left{display:flex;align-items:center;gap:.75rem;}
.ob-modal-icon-wrap{
  width:36px;height:36px;border-radius:.625rem;
  display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;
  background:rgba(37,99,235,.12);border:1px solid rgba(37,99,235,.25);
}
.ob-modal-title{font-size:1rem;font-weight:700;color:var(--color-text,#e2e8f0);}
.ob-modal-close{
  background:none;border:none;cursor:pointer;
  color:var(--color-text-light,#64748b);
  width:32px;height:32px;border-radius:.5rem;
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;line-height:1;
  transition:background .15s,color .15s;flex-shrink:0;
}
.ob-modal-close:hover{background:rgba(255,255,255,.07);color:var(--color-text,#e2e8f0);}
.ob-modal-body{padding:1.5rem;}
</style>""")

    # ── Details modal ─────────────────────────────────────────────────────────
    details_modal = Div(
        Div(
            # Header
            Div(
                Div(
                    Div(
                        Safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                             'stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px">'
                             '<rect x="3" y="3" width="18" height="18" rx="2"/>'
                             '<line x1="9" y1="9" x2="15" y2="9"/>'
                             '<line x1="9" y1="13" x2="15" y2="13"/>'
                             '<line x1="9" y1="17" x2="12" y2="17"/></svg>'),
                        cls="ob-modal-icon-wrap",
                    ),
                    Span("Page Details", cls="ob-modal-title"),
                    cls="ob-modal-header-left",
                ),
                Button("✕", cls="ob-modal-close",
                       onclick="document.getElementById('project-modal').style.display='none'"),
                cls="ob-modal-header",
            ),
            # Body
            Div(id="modal-body", cls="modal-body-content ob-modal-body"),
            cls="ob-modal-card",
            style="max-width:480px",
        ),
        id="project-modal", cls="ob-modal-overlay",
        style="display:none",
        onclick="if(event.target===this)this.style.display='none'",
    )

    # ── Share / QR modal ──────────────────────────────────────────────────────
    share_modal = Div(
        Div(
            # Header
            Div(
                Div(
                    Div(
                        Safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                             'stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px">'
                             '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/>'
                             '<circle cx="18" cy="19" r="3"/>'
                             '<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>'
                             '<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'),
                        cls="ob-modal-icon-wrap",
                    ),
                    Span("Share Page", cls="ob-modal-title"),
                    cls="ob-modal-header-left",
                ),
                Button("✕", cls="ob-modal-close",
                       onclick="document.getElementById('share-modal').style.display='none'"),
                cls="ob-modal-header",
            ),
            # Body
            Div(
                P("", id="share-modal-name",
                  style="font-size:0.82rem;color:var(--color-text-light,#64748b);"
                        "margin:0 0 1.25rem;text-align:center"),
                # QR code
                Div(
                    Img(id="share-qr-img", src="", alt="QR Code", width="200", height="200",
                        style="display:block;border-radius:12px;border:1px solid var(--color-border);"
                              "background:#fff;padding:10px"),
                    style="display:flex;justify-content:center;margin-bottom:1.25rem",
                ),
                # URL row
                Div(
                    Input(type="text", id="share-url-input", readonly=True,
                          style="flex:1;font-size:0.78rem;"
                                "background:rgba(255,255,255,.04);"
                                "border:1px solid var(--color-border,rgba(37,99,235,.18));"
                                "border-radius:.625rem;padding:.5rem .75rem;"
                                "color:var(--color-text,#e2e8f0);min-width:0;outline:none"),
                    Button("Copy", id="share-copy-btn", onclick="copyShareLink()",
                           style="flex-shrink:0;padding:.5rem 1.1rem;border-radius:.625rem;"
                                 "background:var(--color-primary,#2563eb);color:#fff;border:none;"
                                 "font-size:0.78rem;font-weight:600;cursor:pointer;"
                                 "transition:opacity .15s"),
                    style="display:flex;gap:.5rem;margin-bottom:1rem",
                ),
                A("↓ Download QR", id="share-qr-download", href="#", download="qr-code.png",
                  style="display:block;text-align:center;font-size:0.8rem;"
                        "color:var(--color-text-light,#64748b);text-decoration:none;"
                        "padding:.4rem;border-radius:.5rem;transition:color .15s"),
                cls="ob-modal-body",
                style="text-align:center",
            ),
            cls="ob-modal-card",
            style="max-width:360px",
        ),
        id="share-modal", cls="ob-modal-overlay",
        style="display:none;z-index:1001",
        onclick="if(event.target===this)this.style.display='none'",
    )

    share_js = Script(Safe("""
(function () {
  function showShareModal(pageId, name) {
    var url = window.location.origin + '/sites/' + pageId;
    var qrSrc = 'https://api.qrserver.com/v1/create-qr-code/'
      + '?size=210x210&data=' + encodeURIComponent(url) + '&margin=8&bgcolor=ffffff&color=000000';
    document.getElementById('share-modal-name').textContent = name;
    document.getElementById('share-url-input').value = url;
    document.getElementById('share-qr-img').src = qrSrc;
    document.getElementById('share-qr-download').href = qrSrc;
    document.getElementById('share-qr-download').download = 'qr-' + name.replace(/[^a-z0-9]/gi, '-') + '.png';
    document.getElementById('share-copy-btn').textContent = 'Copy';
    document.getElementById('share-modal').style.display = 'flex';
  }
  function copyShareLink() {
    var input = document.getElementById('share-url-input');
    var btn = document.getElementById('share-copy-btn');
    navigator.clipboard.writeText(input.value).then(function () {
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
    }).catch(function () {
      input.select(); document.execCommand('copy');
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
    });
  }
  window.showShareModal = showShareModal;
  window.copyShareLink = copyShareLink;
})();
"""))

    search_css = Style(Safe("""
.pc-search-bar{margin-bottom:1.25rem;}
.pc-search-wrap{
  position:relative;display:flex;align-items:center;
}
.pc-search-icon{
  position:absolute;left:0.875rem;pointer-events:none;
  color:var(--color-text-light,#64748b);
  width:16px;height:16px;flex-shrink:0;
}
.pc-search-input{
  width:100%;
  background:var(--color-surface,#0f0f24);
  border:1px solid var(--color-border,rgba(37,99,235,.2));
  border-radius:0.75rem;
  padding:0.625rem 2.5rem 0.625rem 2.75rem;
  color:var(--color-text,#e2e8f0);
  font-size:0.9rem;
  transition:border-color .2s,box-shadow .2s;
  outline:none;
}
.pc-search-input:focus{
  border-color:var(--color-primary,#2563eb);
  box-shadow:0 0 0 3px rgba(37,99,235,.15);
}
.pc-search-input::placeholder{color:var(--color-text-light,#64748b);}
.pc-search-clear{
  position:absolute;right:0.75rem;
  background:none;border:none;
  color:var(--color-text-light,#64748b);
  cursor:pointer;font-size:1rem;
  padding:0.2rem 0.4rem;line-height:1;
  border-radius:4px;transition:color .15s;
  display:none;
}
.pc-search-clear:hover{color:var(--color-text,#e2e8f0);}
.pc-no-results{
  display:none;grid-column:1/-1;
  text-align:center;padding:3rem 1rem;
  color:var(--color-text-light,#64748b);
  font-size:0.95rem;
}
"""))

    search_bar = Div(
        Div(
            Safe('<svg class="pc-search-icon" viewBox="0 0 24 24" fill="none" '
                 'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                 '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'),
            Input(
                type="text", id="pc-search",
                placeholder="Search pages by name or industry…",
                cls="pc-search-input",
                autocomplete="off",
            ),
            Button("✕", id="pc-search-clear", cls="pc-search-clear", type="button"),
            cls="pc-search-wrap",
        ),
        cls="pc-search-bar",
    )

    search_js = Script(Safe("""
(function () {
  var input    = document.getElementById('pc-search');
  var clearBtn = document.getElementById('pc-search-clear');
  var noRes    = document.getElementById('pc-no-results');
  if (!input) return;

  function norm(str) {
    return (str || '').replace(/\\s+/g, ' ').trim().toLowerCase();
  }

  function filter(q) {
    q = norm(q);
    var cards   = document.querySelectorAll('.pc-card');
    var visible = 0;
    cards.forEach(function (card) {
      var nameEl  = card.querySelector('.pc-name');
      var indEl   = card.querySelector('.pc-industry');
      var name     = norm(nameEl  ? nameEl.innerText  : '');
      var industry = norm(indEl   ? indEl.innerText   : '');
      var match    = !q || name.includes(q) || industry.includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    if (noRes) noRes.style.display = (visible === 0 && q) ? 'block' : 'none';
    clearBtn.style.display = q ? 'inline-flex' : 'none';
  }

  input.addEventListener('input', function () { filter(this.value); });
  clearBtn.addEventListener('click', function () {
    input.value = '';
    filter('');
    input.focus();
  });
})();
"""))

    delete_modal = Div(
        Div(
            # Header
            Div(
                Div(
                    Div(
                        Safe('<svg viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2" '
                             'stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px">'
                             '<polyline points="3 6 5 6 21 6"/>'
                             '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
                             '<path d="M10 11v6"/><path d="M14 11v6"/>'
                             '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>'),
                        style="width:36px;height:36px;border-radius:.625rem;"
                              "display:flex;align-items:center;justify-content:center;flex-shrink:0;"
                              "background:rgba(248,113,113,.12);border:1px solid rgba(248,113,113,.3)",
                    ),
                    Span("Delete Page?", cls="ob-modal-title"),
                    cls="ob-modal-header-left",
                ),
                Button("✕", cls="ob-modal-close", onclick="closeDeleteModal()"),
                cls="ob-modal-header",
            ),
            # Body
            Div(
                Div(
                    Span("You're about to delete "),
                    Span("", id="del-modal-name",
                         style="color:var(--color-text,#e2e8f0);font-weight:600"),
                    Span(". This action "),
                    Span("cannot be undone.", style="color:#f87171;font-weight:600"),
                    style="font-size:.9rem;color:#94a3b8;line-height:1.7;margin-bottom:1.5rem",
                ),
                Div(
                    Button("Cancel", cls="button button-secondary",
                           onclick="closeDeleteModal()",
                           style="padding:.6rem 1.4rem;font-size:.875rem"),
                    Form(
                        Button("Delete", type="submit",
                               style="background:#ef4444;color:#fff;border:none;"
                                     "padding:.6rem 1.4rem;border-radius:.625rem;"
                                     "font-size:.875rem;font-weight:600;cursor:pointer;"
                                     "transition:background .15s"),
                        method="post", id="del-modal-form", action="", style="margin:0",
                    ),
                    style="display:flex;gap:.75rem;justify-content:flex-end",
                ),
                cls="ob-modal-body",
            ),
            cls="ob-modal-card",
            style="max-width:420px;border-color:rgba(248,113,113,.2);"
                  "box-shadow:0 0 60px rgba(248,113,113,.08),0 24px 48px rgba(0,0,0,.5)",
        ),
        id="del-modal", cls="ob-modal-overlay",
        style="display:none;z-index:9999",
        onclick="if(event.target===this)closeDeleteModal()",
    )

    delete_modal_css = Safe("")  # styles now in shared_modal_css

    delete_modal_js = Script(Safe("""
function openDeleteModal(pageId, pageName) {
  document.getElementById('del-modal-name').textContent = pageName || 'this page';
  document.getElementById('del-modal-form').action = '/pages/' + pageId + '/delete';
  document.getElementById('del-modal').style.display = 'flex';
}
function closeDeleteModal() {
  document.getElementById('del-modal').style.display = 'none';
}
document.addEventListener('keydown', function(e) {
  if (e.key !== 'Escape') return;
  closeDeleteModal();
  document.getElementById('project-modal').style.display = 'none';
  document.getElementById('share-modal').style.display = 'none';
});
"""))

    content = Div(
        search_css,
        shared_modal_css,
        delete_modal_css,
        Div(
            page_header,
            tabs,
            search_bar,
            Div(*cards, Div("No pages match your search.", id="pc-no-results", cls="pc-no-results"), cls="pc-grid"),
            pagination if pagination else "",
            cls="step-content",
        ),
        details_modal,
        share_modal,
        delete_modal,
        share_js,
        search_js,
        delete_modal_js,
        cls="dashboard-content",
    )

    analytics = {
        "total": total_projects,
        "published": published_count,
        "unfinished": unfinished_count,
    }

    return sidebar_layout(
        content,
        user=user,
        title="Okenaba - Pages",
        active_nav="pages",
        analytics=analytics,
    )
