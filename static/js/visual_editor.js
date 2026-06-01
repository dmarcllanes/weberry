(function () {
  var PAGE_ID = window.__OKENABA_PAGE_ID__;
  if (!PAGE_ID) return;

  var EDIT_SELECTOR = 'h1,h2,h3,h4,h5,h6,p,li,button,td,th,blockquote,label';
  var SKIP_ANCESTORS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'NAV', 'FOOTER']);

  // ── Inject editor CSS ──────────────────────────────────────────────────────
  var style = document.createElement('style');
  style.textContent = [
    '#__ob-bar__{',
      'position:fixed;top:0;left:0;right:0;z-index:2147483647;',
      'background:var(--ob-surface,#0f0f24);border-bottom:1px solid var(--ob-border,rgba(37,99,235,.3));',
      'padding:10px 20px;display:flex;align-items:center;gap:12px;',
      'font-family:system-ui,-apple-system,sans-serif;font-size:14px;',
      'box-shadow:0 2px 16px rgba(0,0,0,.5);',
    '}',
    '#__ob-bar__ .ob-bar-title{color:var(--ob-text,#e2e8f0);font-weight:600;}',
    '#__ob-bar__ .ob-bar-hint{color:var(--ob-muted,#64748b);font-size:13px;}',
    '#__ob-bar__ .ob-bar-actions{margin-left:auto;display:flex;gap:8px;align-items:center;}',
    '#__ob-bar__ button{',
      'padding:6px 18px;border-radius:6px;border:none;cursor:pointer;',
      'font-size:13px;font-weight:500;transition:opacity .2s;',
    '}',
    '#__ob-save-btn__{background:var(--ob-primary,#2563eb);color:#fff;}',
    '#__ob-save-btn__:hover{background:var(--ob-primary-hover,#1d4ed8);}',
    '#__ob-save-btn__:disabled{opacity:.5;cursor:not-allowed;}',
    '#__ob-cancel-btn__{background:rgba(255,255,255,.08);color:var(--ob-muted,#94a3b8);}',
    '#__ob-cancel-btn__:hover{opacity:.75;}',
    '.__ob-editable{outline:none !important;transition:outline .12s;}',
    '.__ob-editable:hover{outline:2px dashed color-mix(in srgb,var(--ob-primary,#2563eb) 55%,transparent) !important;outline-offset:3px;cursor:text;}',
    '.__ob-editable[contenteditable="true"]{',
      'outline:2px solid var(--ob-primary,#2563eb) !important;outline-offset:3px;cursor:text;',
    '}',
  ].join('');
  document.head.appendChild(style);

  // ── Build the top bar ──────────────────────────────────────────────────────
  var bar = document.createElement('div');
  bar.id = '__ob-bar__';
  bar.innerHTML = [
    '<span class="ob-bar-title">&#9998; Visual Editor</span>',
    '<span class="ob-bar-hint">Click any text to edit</span>',
    '<div class="ob-bar-actions">',
      '<button id="__ob-save-btn__">Save Changes</button>',
      '<button id="__ob-cancel-btn__">Cancel</button>',
    '</div>',
  ].join('');
  document.body.insertBefore(bar, document.body.firstChild);
  document.body.style.paddingTop = '48px';

  // ── Helpers ────────────────────────────────────────────────────────────────
  function hasSkipAncestor(el) {
    var p = el.parentElement;
    while (p && p !== document.body) {
      if (SKIP_ANCESTORS.has(p.tagName)) return true;
      p = p.parentElement;
    }
    return false;
  }

  function hasEditableDescendant(el) {
    return !!el.querySelector('.__ob-editable');
  }

  // ── Mark editable elements ─────────────────────────────────────────────────
  var elements = Array.from(document.querySelectorAll(EDIT_SELECTOR));
  elements.forEach(function (el) {
    if (hasSkipAncestor(el)) return;
    var text = el.innerText.trim();
    if (text.length < 2) return;

    el.dataset.obOriginal = text;
    el.classList.add('__ob-editable');
    el.contentEditable = 'false';

    el.addEventListener('click', function (e) {
      if (el.contentEditable === 'true') return;
      e.preventDefault();
      e.stopPropagation();
      el.contentEditable = 'true';
      el.focus();
      // place cursor at click position
      var range = document.caretRangeFromPoint
        ? document.caretRangeFromPoint(e.clientX, e.clientY)
        : null;
      if (range) {
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      }
    });

    el.addEventListener('blur', function () {
      el.contentEditable = 'false';
    });

    el.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        el.innerText = el.dataset.obOriginal;
        el.contentEditable = 'false';
        el.blur();
      }
      // Confirm edit on Enter (single-line elements)
      if (e.key === 'Enter' && !e.shiftKey) {
        var tag = el.tagName.toLowerCase();
        if (tag !== 'p' && tag !== 'blockquote' && tag !== 'li') {
          e.preventDefault();
          el.contentEditable = 'false';
          el.blur();
        }
      }
    });
  });

  // ── Save ───────────────────────────────────────────────────────────────────
  document.getElementById('__ob-save-btn__').addEventListener('click', async function () {
    var btn = this;
    var params = new URLSearchParams();
    var idx = 0;

    document.querySelectorAll('.__ob-editable[data-ob-original]').forEach(function (el) {
      var original = el.dataset.obOriginal;
      var edited = el.innerText.trim();
      if (edited && original !== edited) {
        params.append('original_' + idx, original);
        params.append('edited_' + idx, edited);
        idx++;
      }
    });

    if (idx === 0) {
      window.top.location.href = '/pages/' + PAGE_ID;
      return;
    }

    btn.textContent = 'Saving…';
    btn.disabled = true;

    try {
      await fetch('/pages/' + PAGE_ID + '/edit-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString(),
        redirect: 'follow',
      });

      // Update stored originals so a second save works
      document.querySelectorAll('.__ob-editable').forEach(function (el) {
        el.dataset.obOriginal = el.innerText.trim();
      });

      // Notify parent frame to show the save-success modal
      window.parent.postMessage({ type: 'ob-save-success', pageId: PAGE_ID }, '*');
    } catch (err) {
      alert('Save failed. Please try again.');
    } finally {
      btn.textContent = 'Save Changes';
      btn.disabled = false;
    }
  });

  // ── Cancel ─────────────────────────────────────────────────────────────────
  document.getElementById('__ob-cancel-btn__').addEventListener('click', function () {
    window.top.location.href = '/pages/' + PAGE_ID;
  });
})();
