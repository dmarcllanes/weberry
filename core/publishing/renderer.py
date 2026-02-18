# Mobile nav hamburger toggle — injected after validation so stored HTML stays script-free.
NAV_TOGGLE_JS = """<script>
(function(){
  var btn=document.getElementById("menu-btn");
  var nav=document.getElementById("nav-links");
  if(!btn||!nav)return;
  btn.addEventListener("click",function(){
    if(nav.classList.contains("open")){
      nav.classList.remove("open");
      setTimeout(function(){if(!nav.classList.contains("open"))nav.style.display="none";},350);
    }else{
      nav.style.display="flex";
      requestAnimationFrame(function(){requestAnimationFrame(function(){nav.classList.add("open");});});
    }
  });
  function check(){
    if(getComputedStyle(btn).display==="none"){
      nav.style.display="";nav.classList.remove("open");
    }else if(!nav.classList.contains("open")){
      nav.style.display="none";
    }
  }
  window.addEventListener("resize",check);
  check();
})();
</script>"""


def inject_nav_js(html: str) -> str:
    """Inject mobile nav toggle JS before </body>."""
    return html.replace("</body>", NAV_TOGGLE_JS + "</body>", 1)


def render_final_page(html: str, css: str) -> str:
    """Inline CSS into the HTML page inside a <style> tag before </head>, then inject nav JS."""
    style_block = f"<style>\n{css}\n</style>"

    head_close = html.lower().find("</head>")
    if head_close == -1:
        result = f"<!DOCTYPE html>\n<html>\n<head>\n{style_block}\n</head>\n<body>\n{html}\n</body>\n</html>"
    else:
        result = html[:head_close] + style_block + "\n" + html[head_close:]

    return inject_nav_js(result)
