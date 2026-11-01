import html
import os
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

LOGO_URL = "https://raw.githubusercontent.com/tipografitoplulugu/tipografi-bulteni-arsivi/main/logo.png"

st.set_page_config(
    page_title="Tipografi Bülteni Arşivi",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLOR_THEMES = {
    "light": {
        "scheme": "light",
        "paper": "#F7F8F5",
        "surface": "#FFFFFF",
        "surface_subtle": "#F0F2EB",
        "ink": "#161811",
        "muted": "#5D6255",
        "placeholder": "#5D6255",
        "line": "#DDE1D4",
        "line_strong": "#C4CBB7",
        "accent": "#D5FD42",
        "accent_hover": "#C7EE35",
        "accent_soft": "#EFF8CF",
        "accent_soft_ink": "#334500",
        "link": "#334500",
        "link_hover": "#243400",
        "on_accent": "#121212",
        "focus": "#334500",
        "focus_ring": "#334500",
        "info_bg": "#EFF8CF",
        "info_ink": "#161811",
        "success": "#245C37",
        "success_bg": "#EAF4E4",
        "success_border": "#C5D8B8",
        "danger": "#8A261E",
        "danger_bg": "#FBEDEA",
        "danger_border": "#E6C1BA",
        "chart_grid": "#DDE1D4",
        "chart_bar": "#334500",
        "disabled_bg": "#ECEEE7",
        "disabled_ink": "#5D6255",
    },
    "dark": {
        "scheme": "dark",
        "paper": "#121212",
        "surface": "#1B1B1B",
        "surface_subtle": "#252525",
        "ink": "#F5F5F0",
        "muted": "#A3A3A3",
        "placeholder": "#A3A3A3",
        "line": "#333333",
        "line_strong": "#4A4A4A",
        "accent": "#D5FD42",
        "accent_hover": "#C7EE35",
        "accent_soft": "#30391A",
        "accent_soft_ink": "#D5FD42",
        "link": "#D5FD42",
        "link_hover": "#C7EE35",
        "on_accent": "#121212",
        "focus": "#D5FD42",
        "focus_ring": "#D5FD42",
        "info_bg": "#202619",
        "info_ink": "#F5F5F0",
        "success": "#B5E48A",
        "success_bg": "#25331B",
        "success_border": "#455C2A",
        "danger": "#FFAAA3",
        "danger_bg": "#3A211F",
        "danger_border": "#70403C",
        "chart_grid": "#333333",
        "chart_bar": "#D5FD42",
        "disabled_bg": "#262626",
        "disabled_ink": "#A3A3A3",
    },
}

THEME_STORAGE_KEY = "tipografi-archive-theme"
URL_THEME = st.query_params.get("theme")
if URL_THEME in COLOR_THEMES:
    st.session_state["archive_theme"] = URL_THEME
elif "archive_theme" not in st.session_state:
    st.session_state["archive_theme"] = "light"


def toggle_archive_theme() -> None:
    next_theme = "light" if st.session_state.get("archive_theme") == "dark" else "dark"
    st.session_state["archive_theme"] = next_theme
    st.query_params["theme"] = next_theme


CURRENT_THEME_NAME = st.session_state.get("archive_theme", "light")
CURRENT_THEME = COLOR_THEMES.get(CURRENT_THEME_NAME, COLOR_THEMES["light"])
SUN_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<g fill="none" stroke="#000" stroke-linecap="round" stroke-width="1.8">'
    '<circle cx="12" cy="12" r="3.5"/>'
    '<path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>'
    '</g></svg>'
)
MOON_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<path d="M20.1 15.2A8.4 8.4 0 0 1 8.8 3.9 8.5 8.5 0 1 0 20.1 15.2Z" '
    'fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"/>'
    '</svg>'
)
ICON_FOR_NEXT_THEME = (SUN_ICON_SVG if CURRENT_THEME_NAME == "dark" else MOON_ICON_SVG).replace(
    "#000", CURRENT_THEME["link"]
)
THEME_CSS_VARIABLES = "\n".join(
    f"--{key.replace('_', '-')}: {value};"
    for key, value in CURRENT_THEME.items()
    if key != "scheme"
) + f"\n--theme-icon-image: url('data:image/svg+xml,{quote(ICON_FOR_NEXT_THEME, safe='')}');"
THEME_BOOTSTRAP = f"""
<script>
(() => {{
  const key = {THEME_STORAGE_KEY!r};
  const serverTheme = {CURRENT_THEME_NAME!r};
  const valid = value => value === "light" || value === "dark";
  const parentWindow = window.parent;
  const root = parentWindow.document.documentElement;
  const url = new URL(parentWindow.location.href);
  const queryTheme = url.searchParams.get("theme");
  let savedTheme = null;
  try {{ savedTheme = parentWindow.localStorage.getItem(key); }} catch (error) {{}}
  const systemTheme = parentWindow.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  const theme = valid(queryTheme) ? queryTheme : (valid(savedTheme) ? savedTheme : systemTheme);
  root.style.colorScheme = theme;
  if (!valid(queryTheme)) {{
    try {{ parentWindow.localStorage.setItem(key, theme); }} catch (error) {{}}
    url.searchParams.set("theme", theme);
    parentWindow.location.replace(url.href);
    return;
  }}
  try {{ parentWindow.localStorage.setItem(key, serverTheme); }} catch (error) {{}}
  parentWindow.__archiveThemeCurrent = serverTheme;
  const syncToggle = () => {{
    const button = parentWindow.document.querySelector(".st-key-archive_theme_toggle button");
    if (!button) return;
    const current = parentWindow.__archiveThemeCurrent || serverTheme;
    button.setAttribute("aria-label", current === "dark" ? "Açık moda geç" : "Koyu moda geç");
    button.setAttribute("title", current === "dark" ? "Açık moda geç" : "Koyu moda geç");
    if (button.dataset.archiveThemeBound !== "true") {{
      button.dataset.archiveThemeBound = "true";
      button.addEventListener("click", () => {{
        const activeTheme = parentWindow.__archiveThemeCurrent || serverTheme;
        const nextTheme = activeTheme === "dark" ? "light" : "dark";
        parentWindow.__archiveThemeCurrent = nextTheme;
        button.setAttribute("aria-label", nextTheme === "dark" ? "Açık moda geç" : "Koyu moda geç");
        button.setAttribute("title", nextTheme === "dark" ? "Açık moda geç" : "Koyu moda geç");
        try {{ parentWindow.localStorage.setItem(key, nextTheme); }} catch (error) {{}}
      }});
    }}
  }};
  const performScroll = () => {{
    let attempts = 0;
    const timer = setInterval(() => {{
      attempts++;
      const el = parentWindow.document.getElementById("first-result")
              || parentWindow.document.querySelector(".app-status");
      if (el) {{
        clearInterval(timer);
        const reduced = parentWindow.matchMedia("(prefers-reduced-motion: reduce)").matches;
        el.scrollIntoView({{ behavior: reduced ? "auto" : "smooth", block: "start" }});
      }} else if (attempts >= 60) {{
        clearInterval(timer);
      }}
    }}, 30);
  }};
  parentWindow.__scrollToFirstResult = performScroll;

  const bindSearchTriggers = () => {{
    const topicButtons = parentWindow.document.querySelectorAll("[class*='st-key-topic_'] button");
    topicButtons.forEach(btn => {{
      if (btn.dataset.scrollBound !== "true") {{
        btn.dataset.scrollBound = "true";
        btn.addEventListener("click", () => {{
          parentWindow.__shouldScrollToResult = true;
        }});
      }}
    }});
    const submitBtn = parentWindow.document.querySelector("[data-testid='stFormSubmitButton'] button");
    if (submitBtn && submitBtn.dataset.scrollBound !== "true") {{
      submitBtn.dataset.scrollBound = "true";
      submitBtn.addEventListener("click", () => {{
        parentWindow.__shouldScrollToResult = true;
      }});
    }}
    const searchInput = parentWindow.document.querySelector("[data-testid='stTextInput'] input");
    if (searchInput && searchInput.dataset.scrollBound !== "true") {{
      searchInput.dataset.scrollBound = "true";
      searchInput.addEventListener("keydown", (e) => {{
        if (e.key === "Enter") {{
          parentWindow.__shouldScrollToResult = true;
        }}
      }});
    }}
    const prevBtn = parentWindow.document.querySelector(".st-key-previous_page button");
    if (prevBtn && prevBtn.dataset.scrollBound !== "true") {{
      prevBtn.dataset.scrollBound = "true";
      prevBtn.addEventListener("click", () => {{
        parentWindow.__shouldScrollToResult = true;
      }});
    }}
    const nextBtn = parentWindow.document.querySelector(".st-key-next_page button");
    if (nextBtn && nextBtn.dataset.scrollBound !== "true") {{
      nextBtn.dataset.scrollBound = "true";
      nextBtn.addEventListener("click", () => {{
        parentWindow.__shouldScrollToResult = true;
      }});
    }}
  }};

  const handleObserver = () => {{
    syncToggle();
    bindSearchTriggers();
    if (parentWindow.__shouldScrollToResult) {{
      const el = parentWindow.document.getElementById("first-result")
              || parentWindow.document.querySelector(".app-status");
      if (el) {{
        parentWindow.__shouldScrollToResult = false;
        const reduced = parentWindow.matchMedia("(prefers-reduced-motion: reduce)").matches;
        setTimeout(() => {{
          el.scrollIntoView({{ behavior: reduced ? "auto" : "smooth", block: "start" }});
        }}, 40);
      }}
    }}
  }};

  parentWindow.__archiveThemeCurrent = serverTheme;
  syncToggle();
  bindSearchTriggers();
  if (!parentWindow.__citationCopyBound) {{
    parentWindow.__citationCopyBound = true;
    parentWindow.document.addEventListener("click", async (e) => {{
      const btn = e.target.closest(".citation-copy-btn");
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      if (btn.dataset.copying === "true") return;
      btn.dataset.copying = "true";
      const text = btn.getAttribute("data-copy") || "";
      if (!text) return;
      const fallback = (val) => {{
        const ta = parentWindow.document.createElement("textarea");
        ta.value = val;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        parentWindow.document.body.appendChild(ta);
        ta.select();
        let ok = false;
        try {{ ok = parentWindow.document.execCommand("copy"); }} catch (err) {{}}
        ta.remove();
        return ok;
      }};
      try {{
        if (parentWindow.navigator.clipboard && parentWindow.isSecureContext) {{
          try {{
            await parentWindow.navigator.clipboard.writeText(text);
          }} catch (err) {{
            if (!fallback(text)) throw err;
          }}
        }} else if (!fallback(text)) {{
          throw new Error("Clipboard unavailable");
        }}
        btn.textContent = "Kopyalandı";
        btn.classList.add("copied");
        btn.setAttribute("aria-label", "Alıntı kopyalandı");
        setTimeout(() => {{
          btn.textContent = "Kopyala";
          btn.classList.remove("copied");
          btn.setAttribute("aria-label", "Alıntıyı panoya kopyala");
          delete btn.dataset.copying;
        }}, 2000);
      }} catch (err) {{
        console.error("Kopyalama başarısız:", err);
        delete btn.dataset.copying;
      }}
    }});
  }}
  if (!parentWindow.__archiveThemeObserver) {{
    parentWindow.__archiveThemeObserver = new MutationObserver(handleObserver);
    parentWindow.__archiveThemeObserver.observe(parentWindow.document.body, {{ childList: true, subtree: true }});
  }}
  if (!parentWindow.document.querySelector("link[href*='family=DM+Mono']")) {{
    const linkFont = parentWindow.document.createElement("link");
    linkFont.rel = "stylesheet";
    linkFont.href = "https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap";
    parentWindow.document.head.appendChild(linkFont);
  }}
}})();
</script>
"""
components.html(THEME_BOOTSTRAP, height=0, scrolling=False)
st.markdown(
    f"<style>:root {{ color-scheme: {CURRENT_THEME['scheme']}; {THEME_CSS_VARIABLES} }}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: var(--paper);
        color: var(--ink);
        font-family: "Inter", sans-serif;
    }
    /* Hide Streamlit's in-app toolbar actions (Share, menu, and adjacent
       controls). The content links below are also left-aligned so they stay
       clear if the host renders its own toolbar outside the app. */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stMain"] .block-container { max-width: 1120px; padding: 2rem 2.25rem 5rem; }
    h1, h2, h3, h4 {
        color: var(--ink) !important;
        font-family: "Instrument Serif", serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em !important;
        font-variant-ligatures: common-ligatures contextual !important;
        -webkit-font-variant-ligatures: common-ligatures contextual !important;
        font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
        -webkit-font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
    }
    [data-testid="stHeadingWithActionElements"] h1 {
        font-size: clamp(2.8rem, 6vw, 5.25rem) !important;
        line-height: 1.02 !important;
        font-weight: 400 !important;
        margin: .4rem 0 .8rem !important;
        letter-spacing: normal !important;
        font-variant-ligatures: common-ligatures contextual !important;
        -webkit-font-variant-ligatures: common-ligatures contextual !important;
        font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
        -webkit-font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
    }
    [data-testid="stHeadingWithActionElements"] h1 span {
        letter-spacing: normal !important;
        font-variant-ligatures: common-ligatures contextual !important;
        -webkit-font-variant-ligatures: common-ligatures contextual !important;
        font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
        -webkit-font-feature-settings: "liga" 1, "dlig" 1, "locl" 0 !important;
    }
    [data-testid="stHeadingWithActionElements"] h2 { font-size: clamp(1.6rem, 3vw, 2.2rem) !important; }
    [data-testid="stHeadingWithActionElements"] h3,
    [data-testid="stHeadingWithActionElements"] h3 span,
    [data-testid="stVerticalBlockBorderWrapper"] h3,
    [data-testid="stVerticalBlockBorderWrapper"] h3 span,
    h3 {
        letter-spacing: 0.015em !important;
    }
    p, li, label, [data-testid="stMarkdownContainer"] { color: var(--ink); }
    p { line-height: 1.7; }
    a, [data-testid="stMarkdownContainer"] a { color: var(--link) !important; text-underline-offset: 3px; }
    a:hover { color: var(--link-hover) !important; }
    .brand-logo {
        display: block; flex: 0 0 48px; width: 48px; height: 48px;
        border-radius: 11px; background: var(--surface-subtle); object-fit: cover;
    }
    .brand-identity { display: flex; align-items: center; gap: .8rem; min-width: 0; }
    .brand-links {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex: 1 1 auto;
        min-width: 0;
        gap: .5rem;
        color: var(--muted);
        font-family: "DM Mono", monospace;
        font-size: .84rem;
        white-space: nowrap;
    }
    .brand-name { font-size: 1.08rem; font-weight: 650; letter-spacing: .01em; }
    .archive-brand-header {
        display: flex; align-items: center; justify-content: space-between;
        gap: 1.25rem; min-width: 0; min-height: 48px; padding-right: 48px;
    }
    .st-key-archive_brand_row { position: relative !important; min-height: 48px; }
    .st-key-archive_theme_toggle {
        position: absolute !important; top: 4px; right: 0;
        width: 40px !important; height: 40px !important;
        margin: 0 !important; padding: 0 !important; z-index: 2;
    }
    .st-key-archive_theme_toggle [data-testid="stButton"] button {
        position: relative !important;
        display: grid !important; place-items: center !important;
        width: 40px !important; min-width: 40px !important;
        height: 40px !important; min-height: 40px !important; max-height: 40px !important;
        padding: 0 !important; border: 0 !important; border-radius: 50% !important;
        background: transparent !important; color: transparent !important;
        font-size: 0 !important; line-height: 0 !important; box-shadow: none !important;
        appearance: none !important; -webkit-appearance: none !important;
    }
    .st-key-archive_theme_toggle [data-testid="stButton"] button p {
        margin: 0 !important; font-size: 0 !important; line-height: 0 !important;
    }
    .st-key-archive_theme_toggle [data-testid="stButton"] button::before {
        content: ""; position: absolute; width: 20px; height: 20px;
        background: var(--theme-icon-image) center / contain no-repeat;
    }
    .hero-eyebrow, .section-eyebrow {
        font-family: "DM Mono", monospace;
        color: var(--link); font-size: .72rem; font-weight: 500;
        letter-spacing: .12em; text-transform: uppercase;
        display: block;
        margin-bottom: .65rem;
    }
    .topics-eyebrow {
        margin-top: 1.35rem;
        margin-bottom: .75rem;
    }
    .hero-copy {
        max-width: 690px;
        padding-bottom: 2.6rem;
        color: var(--muted);
        font-size: 1.08rem;
        line-height: 1.72;
    }
    .hero-rule { border: 0; border-top: 1px solid var(--line); margin: 1.8rem 0 1.5rem; }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        column-gap: 1.5rem;
        row-gap: 1.1rem;
    }
    .stat-item { min-width: 0; }
    .stat-label {
        font-family: "DM Mono", monospace;
        margin-bottom: .2rem;
        color: var(--muted);
        font-size: .72rem;
        line-height: 1.4;
        letter-spacing: .06em;
        text-transform: uppercase;
    }
    .stat-value {
        color: var(--ink);
        font: 1.55rem/1.2 "Instrument Serif", serif;
        letter-spacing: -.02em;
        overflow-wrap: anywhere;
    }
    .archive-footer {
        font-family: "DM Mono", monospace;
        margin-top: 1.6rem;
        border-top: 1px solid var(--line);
        padding: 1.05rem 0 .2rem;
        color: var(--muted);
        font-size: .82rem;
        line-height: 1.45;
    }
    .footer-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .75rem 1.5rem;
    }
    .footer-name {
        font-family: "DM Mono", monospace;
        color: var(--muted);
        font-size: inherit;
        font-weight: 400;
    }
    .footer-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: .75rem 1.1rem;
    }
    .footer-subscribe {
        font-family: "DM Mono", monospace;
        color: var(--muted);
        font-size: inherit;
        font-weight: 400;
    }
    .footer-subscribe a {
        font-family: "DM Mono", monospace;
        color: var(--link) !important;
        font-weight: 400;
    }
    .footer-social {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: .85rem;
    }
    .footer-social a {
        display: inline-flex;
        width: 1.2rem;
        height: 1.2rem;
        align-items: center;
        justify-content: center;
        color: var(--muted) !important;
        border-radius: 4px;
        text-decoration: none !important;
        transition: color 120ms ease;
    }
    .footer-social a:hover { color: var(--link) !important; }
    .footer-social svg { display: block; width: 100%; height: 100%; }
    .footer-social .icon-fill { fill: currentColor; }
    .footer-social .icon-stroke {
        fill: none;
        stroke: currentColor;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-width: 2;
    }
    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label {
        display: none !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stFormSubmitButton"] button {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border-radius: 12px !important;
        font-size: .98rem;
        line-height: 1.2;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [role="combobox"] {
        border: 0 !important;
        background: var(--surface) !important;
        color: var(--ink) !important;
        box-shadow: none !important;
        appearance: none !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextInputRootElement"] input::placeholder,
    [data-testid="stTextInput"] input::-webkit-input-placeholder,
    [data-testid="stTextInputRootElement"] input::-webkit-input-placeholder,
    [data-testid="stTextInput"] input::-moz-placeholder,
    [data-testid="stTextInputRootElement"] input::-moz-placeholder {
        color: var(--placeholder) !important;
        opacity: .55 !important;
    }
    /* Streamlit wraps text inputs in a theme-colored root that is separate
       from the input itself. Keep that wrapper the same size and surface. */
    [data-testid="stTextInputRootElement"] {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        background: var(--surface) !important;
        box-shadow: none !important;
        overflow: hidden;
    }
    [data-testid="stTextInputRootElement"] [data-testid="stTextInputField"] {
        box-sizing: border-box !important;
        height: 46px !important;
        min-height: 46px !important;
        max-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stSelectbox"] [role="group"]:focus-within {
        border: 2px solid var(--focus) !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div > div {
        background-color: var(--surface) !important;
        background-image: none !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] svg {
        color: var(--muted) !important;
        fill: var(--muted) !important;
    }
    /* Streamlit's current selectbox uses a React Aria group around its input
       and chevron button. Style that group directly; the input alone does
       not control the dark trailing segment. */
    [data-testid="stSelectbox"] [role="group"] {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        background: var(--surface) !important;
        box-shadow: none !important;
        overflow: hidden;
    }
    [data-testid="stSelectbox"] [role="group"] [role="combobox"] {
        box-sizing: border-box !important;
        height: 46px !important;
        min-height: 46px !important;
        max-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [role="group"] button {
        box-sizing: border-box !important;
        width: 42px !important;
        height: 46px !important;
        min-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: var(--surface) !important;
        color: var(--muted) !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [role="group"] button:hover,
    [data-testid="stSelectbox"] [role="group"] button:focus {
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    [data-testid="stSelectbox"] [role="group"] svg {
        color: var(--muted) !important;
        fill: currentColor !important;
    }
    [role="listbox"] [role="option"] { background: var(--surface) !important; color: var(--ink) !important; }
    [role="listbox"] [role="option"]:hover { background: var(--surface-subtle) !important; }
    [role="listbox"] [role="option"][aria-selected="true"] {
        background: var(--accent-soft) !important;
        color: var(--accent-soft-ink) !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stSelectbox"] [role="combobox"]:focus {
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-testid="stForm"] { border: 0; padding: 0; }
    [data-testid="stButton"] button {
        min-height: 40px;
        border: 1px solid var(--line);
        border-radius: 12px !important;
        background: var(--surface);
        color: var(--ink);
        font-family: "DM Mono", monospace;
        font-size: .83rem;
        appearance: none !important;
        -webkit-appearance: none !important;
        box-shadow: none !important;
        transition: border-color 120ms ease, background 120ms ease, color 120ms ease;
    }
    [data-testid="stButton"] button:hover { border-color: var(--line-strong); background: var(--surface-subtle); color: var(--ink); }
    [data-testid="stButton"] button:disabled,
    [data-testid="stFormSubmitButton"] button:disabled {
        border-color: var(--line) !important;
        background: var(--disabled-bg) !important;
        color: var(--disabled-ink) !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button {
        border-radius: 12px !important;
        font-family: "DM Mono", monospace;
        font-size: .82rem;
        opacity: .6;
        transition: opacity 140ms ease, border-color 140ms ease, background 140ms ease;
    }
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:hover,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:focus,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:focus-visible,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:active {
        opacity: 1;
    }
    [data-testid="stFormSubmitButton"] button {
        border: 1px solid var(--accent) !important;
        border-radius: 12px !important;
        background: var(--accent) !important;
        color: var(--on-accent) !important;
        appearance: none !important;
        -webkit-appearance: none !important;
        box-shadow: none !important;
        font-family: "DM Mono", monospace;
        font-weight: 500;
        font-size: .95rem;
        letter-spacing: .02em;
        padding: 0 1rem !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stFormSubmitButton"] button p,
    [data-testid="stFormSubmitButton"] button span {
        font-family: "DM Mono", monospace !important;
        color: var(--on-accent) !important;
        margin: 0;
        line-height: 1.2;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--accent-hover) !important;
        background: var(--accent-hover) !important;
        color: var(--on-accent) !important;
    }
    [data-testid="stSpinner"] svg { color: var(--accent) !important; }
    [data-testid="stSpinner"] circle { stroke: var(--accent) !important; }
    [data-testid="stButton"] button:focus-visible,
    [data-testid="stFormSubmitButton"] button:focus-visible,
    .archive-theme-toggle:focus-visible {
        border: 2px solid var(--focus) !important;
        outline: none !important;
        box-shadow: none !important;
    }
    a:focus-visible { outline: 2px solid var(--focus) !important; outline-offset: 2px !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line) !important; border-radius: 16px !important;
        background: var(--surface) !important; box-shadow: none !important;
    }
    .result-summary {
        font-family: "DM Mono", monospace;
        font-size: .84rem;
        color: var(--muted);
        margin-bottom: .6rem;
    }
    .result-summary strong {
        color: var(--link);
        font-weight: 500;
    }
    .result-meta {
        font-family: "DM Mono", monospace;
        display: flex; flex-wrap: wrap; justify-content: space-between; gap: .35rem 1rem;
        margin-bottom: .6rem; color: var(--muted); font-size: .78rem; letter-spacing: .015em;
    }
    .result-meta strong { color: var(--link); font-weight: 500; }
    .result-excerpt { margin: .2rem 0 .8rem; color: var(--muted); font-size: .96rem; line-height: 1.72; }
    mark.search-hit { border-radius: 3px; background: var(--accent-soft); color: var(--accent-soft-ink); padding: 0 .12em; }
    [data-testid="stExpander"] {
        border: 1px solid var(--line-strong) !important;
        border-radius: 12px !important;
        background: var(--paper) !important;
        box-shadow: none !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details > summary {
        background: var(--surface) !important;
        background-image: none !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stExpander"] details { border: 0 !important; outline: none !important; box-shadow: none !important; }
    [data-testid="stExpander"]:focus-within {
        border: 2px solid var(--focus) !important;
        box-shadow: none !important;
    }
    [data-testid="stExpander"] summary:focus-visible { outline: none !important; }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: var(--ink) !important;
        font-size: .9rem;
        font-weight: 560;
        padding: .45rem .75rem;
    }
    [data-testid="stExpander"] summary * { color: var(--ink) !important; }
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:hover * {
        background: var(--surface-subtle) !important;
        background-image: none !important;
        color: var(--ink) !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        border-top: 1px solid var(--line) !important;
        padding: .85rem 1rem !important;
        background: var(--paper) !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] div:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .citation-row {
        display: flex;
        align-items: stretch;
        gap: .75rem;
        width: 100%;
        margin: 0 !important;
    }
    .citation-box {
        flex: 1 1 auto;
        min-width: 0;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        background: var(--surface-subtle) !important;
        color: var(--ink) !important;
        padding: .85rem 1rem;
        font-size: .94rem;
        line-height: 1.65;
        overflow-wrap: anywhere;
        word-break: normal;
        box-sizing: border-box;
    }
    .citation-copy-btn {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex: 0 0 96px !important;
        width: 96px !important;
        min-width: 96px !important;
        padding: 0 .8rem !important;
        border: 1px solid var(--accent) !important;
        border-radius: 10px !important;
        background: var(--accent) !important;
        color: var(--on-accent) !important;
        font-family: "DM Mono", monospace !important;
        font-size: .86rem !important;
        font-weight: 500 !important;
        appearance: none !important;
        -webkit-appearance: none !important;
        box-shadow: none !important;
        cursor: pointer;
        transition: background-color 120ms ease, border-color 120ms ease;
        box-sizing: border-box !important;
        user-select: none;
        white-space: nowrap;
    }
    .citation-copy-btn:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
    }
    .citation-copy-btn:focus-visible {
        outline: 2px solid var(--focus) !important;
        outline-offset: 2px !important;
    }
    .citation-copy-btn.copied {
        background: var(--success-bg) !important;
        border-color: var(--success-border) !important;
        color: var(--success) !important;
    }
    .app-status {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--info-bg);
        color: var(--info-ink);
        padding: .85rem 1rem;
        line-height: 1.6;
        scroll-margin-top: 2rem;
    }
    #first-result {
        scroll-margin-top: 5rem;
        display: block;
        height: 0;
        margin: 0;
        padding: 0;
    }
    [data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    iframe[height="0"] {
        position: absolute !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }
    .app-status--error {
        border-color: var(--danger-border);
        background: var(--danger-bg);
        color: var(--danger);
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    hr { border-color: var(--line) !important; }
    @media (max-width: 760px) {
        #first-result { scroll-margin-top: 4rem; }
        [data-testid="stMain"] .block-container { padding: 1.15rem 1rem 3rem; }
        [data-testid="stHeadingWithActionElements"] h1 { font-size: clamp(2.45rem, 11vw, 3.6rem) !important; }
        .hero-copy { font-size: 1rem; }
        .st-key-archive_brand_row { min-height: 100px; }
        .st-key-archive_theme_toggle { top: 55px; }
        .archive-brand-header { align-items: flex-start; flex-direction: column; gap: .65rem; padding-right: 0; }
        .brand-links { width: calc(100% - 48px); white-space: nowrap; }
        .footer-content { align-items: flex-start; flex-direction: column; }
        .footer-actions { justify-content: flex-start; }
        .footer-social { justify-content: flex-start; gap: .8rem; }
        .stat-grid { grid-template-columns: minmax(0, 1fr); row-gap: 1.05rem; }
        .result-meta { flex-direction: column; gap: .2rem; }
        .citation-row { gap: .5rem; }
        .citation-copy-btn { flex: 0 0 84px !important; width: 84px !important; min-width: 84px !important; padding: 0 .5rem !important; font-size: .82rem !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .55rem; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: min(100%, 180px); flex: 1 1 180px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Original Medium and Substack links for the archive's 93 issues.
BULTEN_URLS = {
    "Ocak 2019": "https://medium.com/tipografi/tipografi-haberleri-ocak-2019-604f7ccb2b07",
    "Şubat 2019": "https://medium.com/tipografi/tipografi-haberleri-şubat-2019-20a4558cf898",
    "Mart 2019": "https://medium.com/tipografi/tipografi-haberleri-mart-2019-27f1060df7bc",
    "Nisan 2019": "https://medium.com/tipografi/tipografi-haberleri-nisan-2019-ad2ff81a02a7",
    "Mayıs 2019": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2019-b0fe22fb7228",
    "Haziran 2019": "https://medium.com/tipografi/tipografi-haberleri-haziran-2019-cdcb17025b40",
    "Temmuz 2019": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2019-153421028174",
    "Ağustos 2019": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2019-f19b996e323f",
    "Eylül 2019": "https://medium.com/tipografi/tipografi-haberleri-eylül-2019-6c85e8d07d41",
    "Ekim 2019": "https://medium.com/tipografi/tipografi-haberleri-ekim-2019-9d95ca9dc851",
    "Kasım 2019": "https://medium.com/tipografi/tipografi-haberleri-kasım-2019-1068f7aba186",
    "Aralık 2019": "https://medium.com/tipografi/tipografi-haberleri-aralık-2019-b655b51e2939",
    "Ocak 2020": "https://medium.com/tipografi/tipografi-haberleri-ocak-2020-5cd73e88420c",
    "Şubat 2020": "https://medium.com/tipografi/tipografi-haberleri-şubat-2020-4942a3299f3e",
    "Mart 2020": "https://medium.com/tipografi/tipografi-haberleri-mart-2020-d4b96a791d32",
    "Nisan 2020": "https://medium.com/tipografi/tipografi-haberleri-nisan-2020-c3da4f9a1e28",
    "Mayıs 2020": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2020-15f2875c5a19",
    "Haziran 2020": "https://medium.com/tipografi/tipografi-haberleri-haziran-2020-ba2a3e54fb51",
    "Temmuz 2020": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2020-f398d60949d7",
    "Ağustos 2020": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2020-6cd4fcbd9a3b",
    "Eylül 2020": "https://medium.com/tipografi/tipografi-haberleri-eylül-2020-7cb342277bd3",
    "Ekim 2020": "https://medium.com/tipografi/tipografi-haberleri-ekim-2020-a04d29bed91b",
    "Kasım 2020": "https://medium.com/tipografi/tipografi-haberleri-kasım-2020-e0d7c2fc6b9f",
    "Aralık 2020": "https://medium.com/tipografi/tipografi-haberleri-aralık-2020-d881afb1a230",
    "Ocak 2021": "https://medium.com/tipografi/tipografi-haberleri-ocak-2021-3429aabca4ed",
    "Şubat 2021": "https://medium.com/tipografi/tipografi-haberleri-şubat-2021-6b4d000da517",
    "Mart 2021": "https://medium.com/tipografi/tipografi-haberleri-mart-2021-2b733a4da85d",
    "Nisan 2021": "https://medium.com/tipografi/tipografi-haberleri-nisan-2021-fd6cdff4e9c4",
    "Mayıs 2021": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2021-d8cf2966d3ea",
    "Haziran 2021": "https://medium.com/tipografi/tipografi-haberleri-haziran-2021-623c191197a7",
    "Temmuz 2021": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2021-83e6b71d3f15",
    "Ağustos 2021": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2021-b87f55e89171",
    "Eylül 2021": "https://medium.com/tipografi/tipografi-haberleri-eylül-2021-9ac0312435e3",
    "Ekim 2021": "https://medium.com/tipografi/tipografi-haberleri-ekim-2021-cfac56c9bf63",
    "Kasım 2021": "https://medium.com/tipografi/tipografi-haberleri-kasım-2021-315e190a2dca",
    "Aralık 2021": "https://medium.com/tipografi/tipografi-haberleri-aralık-2021-28519238bd95",
    "Ocak 2022": "https://medium.com/tipografi/tipografi-haberleri-ocak-2022-c3389a6d20f7",
    "Şubat 2022": "https://medium.com/tipografi/tipografi-haberleri-şubat-2022-9d9bcbc58c9c",
    "Mart 2022": "https://medium.com/tipografi/tipografi-haberleri-mart-2022-8b40ca83e307",
    "Nisan 2022": "https://medium.com/tipografi/tipografi-haberleri-nisan-2022-23a68f22d53",
    "Mayıs 2022": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2022-c258249bd466",
    "Haziran 2022": "https://medium.com/tipografi/tipografi-haberleri-haziran-2022-55f6efe264b",
    "Temmuz 2022": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2022-5bef2d0161ed",
    "Ağustos 2022": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2022-16cd48b4cf42",
    "Eylül 2022": "https://medium.com/tipografi/tipografi-haberleri-eylül-2022-971dc3981ffd",
    "Ekim 2022": "https://medium.com/tipografi/tipografi-haberleri-ekim-2022-a5a2414d62b8",
    "Kasım 2022": "https://medium.com/tipografi/tipografi-haberleri-kasım-2022-4f991e4c973b",
    "Aralık 2022": "https://medium.com/tipografi/tipografi-haberleri-aralık-2022-812bc46e6f13",
    "Ocak 2023": "https://medium.com/tipografi/tipografi-bülteni-ocak-2023-9dfac3c77718",
    "Şubat 2023": "https://medium.com/tipografi/tipografi-bülteni-şubat-2023-61bc8fd552ce",
    "Mart 2023": "https://medium.com/tipografi/tipografi-bülteni-mart-2023-3a93154ac01b",
    "Nisan 2023": "https://medium.com/tipografi/tipografi-bülteni-nisan-2023-a14f05be724a",
    "Mayıs 2023": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2023-805c3ba8bd36",
    "Haziran 2023": "https://medium.com/tipografi/tipografi-bülteni-haziran-2023-66206d1949ee",
    "Temmuz 2023": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2023-677cf7be9318",
    "Ağustos 2023": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2023-5ee8b04702ec",
    "Eylül 2023": "https://medium.com/tipografi/tipografi-bülteni-eylül-2023-92014965a49a",
    "Ekim 2023": "https://medium.com/tipografi/tipografi-bülteni-ekim-2023-8dfb252f2a1b",
    "Kasım 2023": "https://medium.com/tipografi/tipografi-bülteni-kasım-2023-2ba98f905d1f",
    "Aralık 2023": "https://medium.com/tipografi/tipografi-bülteni-aralık-2023-dc3a5cc03c6a",
    "Ocak 2024": "https://medium.com/tipografi/tipografi-bülteni-ocak-2024-92f521042bae",
    "Şubat 2024": "https://medium.com/tipografi/tipografi-bülteni-şubat-2024-c2e94d6a58ae",
    "Mart 2024": "https://medium.com/tipografi/tipografi-bülteni-mart-2024-7dbe9c27c694",
    "Nisan 2024": "https://medium.com/tipografi/tipografi-bülteni-nisan-2024-df8f79c906db",
    "Mayıs 2024": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2024-b4a80020ec7f",
    "Haziran 2024": "https://medium.com/tipografi/tipografi-bülteni-haziran-2024-2db3b5b4b237",
    "Temmuz 2024": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2024-1e68e9d4a48c",
    "Ağustos 2024": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2024-d8271c2ec119",
    "Eylül 2024": "https://medium.com/tipografi/tipografi-bülteni-eylül-2024-03f75b4d6162",
    "Ekim 2024": "https://medium.com/tipografi/tipografi-bülteni-ekim-2024-6f8a5ee599fc",
    "Kasım 2024": "https://medium.com/tipografi/tipografi-bülteni-kasım-2024-7ac6873bb581",
    "Aralık 2024": "https://medium.com/tipografi/tipografi-bülteni-aralık-2024-b5fc8e46b4ce",
    "Ocak 2025": "https://medium.com/tipografi/tipografi-bülteni-ocak-2025-4f4f7ad5aca1",
    "Şubat 2025": "https://medium.com/tipografi/tipografi-bülteni-şubat-2025-d8c2206c0274",
    "Mart 2025": "https://medium.com/tipografi/tipografi-bülteni-mart-2025-09e6ff1f9a12",
    "Nisan 2025": "https://medium.com/tipografi/tipografi-bülteni-nisan-2025-9ca46327e554",
    "Mayıs 2025": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2025-81cc9ee02d83",
    "Haziran 2025": "https://medium.com/tipografi/tipografi-bülteni-haziran-2025-057366758db6",
    "Temmuz 2025": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2025-f69f62427adc",
    "Ağustos 2025": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2025-410f52e44a70",
    "Eylül 2025": "https://medium.com/tipografi/tipografi-bülteni-eylül-2025-fa7a0941bd68",
    "Ekim 2025": "https://medium.com/tipografi/tipografi-bülteni-ekim-2025-803661d110ac",
    "Kasım 2025": "https://medium.com/tipografi/tipografi-bülteni-kasım-2025-6a52698d71d0",
    "Aralık 2025": "https://medium.com/tipografi/tipografi-bülteni-aralık-2025-119b6d532a2b",
    "Ocak 2026": "https://tipografi.substack.com/p/tipografi-bulteni-ocak-2026",
    "Şubat 2026": "https://tipografi.substack.com/p/tipografi-bulteni-subat-2026",
    "Mart 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mart-2026",
    "Nisan 2026": "https://tipografi.substack.com/p/tipografi-bulteni-nisan-2026",
    "Mayıs 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mays-2026",
    "Haziran 2026": "https://tipografi.substack.com/p/tipografi-bulteni-haziran-2026",
    "Temmuz 2026": "https://tipografi.substack.com/p/tipografi-bulteni-temmuz-2026",
    "Ağustos 2026": "https://tipografi.substack.com/p/tipografi-bulteni-agustos-2026",
    "Eylül 2026": "https://tipografi.substack.com/p/tipografi-bulteni-eylul-2026",
    "Ekim 2026": "https://tipografi.substack.com/p/tipografi-bulteni-ekim-2026",
}

POPULAR_TOPICS = [
    "Değişken Yazıtipi", "Monotype", "Gutenberg", "Yapay Zekâ",
    "Lisanslama", "Kaligrafi", "TDC", "Google Fonts", "Arial",
]
ALL_YEARS = "Tümü"
PAGE_SIZE = 20
APP_DIR = Path(__file__).resolve().parent


def find_database() -> Optional[Path]:
    """Find the existing SQLite archive without moving or modifying it."""
    candidates = []
    configured = os.environ.get("TIPOGRAFI_DB_PATH")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend([APP_DIR / "tipografi_arsivi.db", Path.cwd() / "tipografi_arsivi.db"])
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


@st.cache_resource(show_spinner=False)
def get_connection(db_uri: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def issue_name(full_name: str) -> str:
    return full_name.split(":", 1)[-1].strip() if ":" in full_name else full_name.strip()


def turkish_upper(text: str) -> str:
    """Uppercase Turkish text with the correct dotted and dotless I forms."""
    return text.translate(str.maketrans({"i": "İ", "ı": "I"})).upper()


def get_issue_url(name: str, year: int) -> str:
    clean_name = issue_name(name)
    if clean_name in BULTEN_URLS:
        return BULTEN_URLS[clean_name]
    # Same fallback used by the original app for future issues.
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    slug = clean_name.lower().translate(tr_map).replace(" ", "-")
    return f"https://tipografi.substack.com/p/{slug}"


def build_fts_query(query: str) -> str:
    phrase = re.sub(r"\s+", " ", query).strip().replace('"', "")
    return f'"{phrase}"'


def clean_visual_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not re.match(r"^\s*(?:\*|_)?\s*Görsel(?:/Video)?\s*:\s*", line, re.I)
    ).strip()


def plain_text(markdown_text: str) -> str:
    text = clean_visual_lines(markdown_text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]", "", text).replace(chr(96), "")
    text = re.sub(r"^\s*[-+>]\s*", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_match(text: str) -> str:
    """Normalize accents and Turkish dotted/dotless i for snippet matching."""
    folded = unicodedata.normalize("NFKD", text.casefold().replace("ı", "i"))
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^\w]+", " ", folded, flags=re.UNICODE).split())


def text_contains_query(text: str, query: str) -> bool:
    normalized_text = normalize_for_match(text)
    normalized_query = normalize_for_match(query)
    return bool(normalized_query and normalized_query in normalized_text)


def matching_paragraphs(body: str, query: str) -> list[str]:
    """Return only readable Markdown paragraphs that contain the search query."""
    paragraphs = re.split(r"\n\s*\n", clean_visual_lines(body).strip())
    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip() and text_contains_query(plain_text(paragraph), query)
    ]


def crop_around_query(sentence: str, query: str, limit: int = 460) -> str:
    if len(sentence) <= limit or len(query) >= limit:
        return sentence
    position = sentence.casefold().find(query.casefold())
    if position < 0:
        return sentence
    start = max(0, position - (limit - len(query)) // 2)
    end = min(len(sentence), start + limit)
    start = max(0, end - limit)
    while start > 0 and not sentence[start - 1].isspace():
        start -= 1
    while end < len(sentence) and not sentence[end - 1].isspace():
        end += 1
    excerpt = sentence[start:end].strip()
    return ("…" if start else "") + excerpt + ("…" if end < len(sentence) else "")


def matching_excerpt(title: str, body: str, query: str) -> str:
    """Choose a sentence that contains the searched phrase, not the article opening."""
    search_body = body
    if "küçük puntolar" in title.casefold():
        matching_lines = [
            line for line in body.splitlines() if text_contains_query(plain_text(line), query)
        ]
        if matching_lines:
            search_body = "\n".join(matching_lines)

    readable = plain_text(search_body)
    sentences = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", readable)
        if part.strip()
    ]
    for sentence in sentences:
        if text_contains_query(sentence, query):
            return crop_around_query(sentence, query)

    # FTS5 also indexes headings and Markdown link destinations. Make those
    # matches explicit if the visible body text has no matching sentence.
    readable_title = plain_text(title)
    if text_contains_query(readable_title, query):
        return f"Başlıkta eşleşme: {readable_title}."
    return f"Aranan ifade “{query}” bu kaydın içeriğindeki bir bağlantıda eşleşiyor."


def highlighted_excerpt(text: str, query: str) -> str:
    """Return escaped HTML with a safe, understated match highlight."""
    if not query:
        return html.escape(text)
    pattern = re.compile(re.escape(query), flags=re.IGNORECASE)
    pieces, cursor = [], 0
    for match in pattern.finditer(text):
        pieces.append(html.escape(text[cursor:match.start()]))
        pieces.append(f'<mark class="search-hit">{html.escape(match.group(0))}</mark>')
        cursor = match.end()
    pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)


def result_filter(query: str, year: str) -> tuple[str, list]:
    clauses = ["haberler_fts MATCH ?"]
    parameters = [build_fts_query(query)]
    if year != ALL_YEARS:
        clauses.append("h.yil = ?")
        parameters.append(int(year))
    return " AND ".join(clauses), parameters


def get_counts(connection: sqlite3.Connection) -> tuple[int, int]:
    row = connection.execute(
        "SELECT COUNT(DISTINCT dosya_adi), COUNT(*) FROM haberler"
    ).fetchone()
    return int(row[0] or 0), int(row[1] or 0)


def get_years(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT DISTINCT yil FROM haberler WHERE yil IS NOT NULL ORDER BY yil DESC"
    ).fetchall()
    return [str(row[0]) for row in rows if row[0]]


def count_matches(connection: sqlite3.Connection, where: str, params: list) -> tuple[int, int]:
    row = connection.execute(
        f"""SELECT COUNT(*), COUNT(DISTINCT h.bulten_adi)
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where}""",
        params,
    ).fetchone()
    return int(row[0] or 0), int(row[1] or 0)


def fetch_matches(connection: sqlite3.Connection, where: str, params: list, page: int) -> list:
    return connection.execute(
        f"""SELECT h.id, h.bulten_adi, h.yil, h.ay, h.baslik, h.icerik
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where}
            ORDER BY h.yil DESC, h.id DESC LIMIT ? OFFSET ?""",
        [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
    ).fetchall()


def get_year_distribution(connection: sqlite3.Connection, where: str, params: list) -> pd.DataFrame:
    rows = connection.execute(
        f"""SELECT h.yil, COUNT(*) AS adet
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where} GROUP BY h.yil ORDER BY h.yil""",
        params,
    ).fetchall()
    values = {int(row["yil"]): int(row["adet"]) for row in rows}
    years = list(range(2019, max(values.keys(), default=2026) + 1))
    return pd.DataFrame(
        {"Gelişme sayısı": [values.get(year, 0) for year in years]},
        index=[str(year) for year in years],
    )


def set_page(page: int) -> None:
    st.session_state["archive_page"] = page
    st.session_state["scroll_to_results"] = True


def choose_topic(topic: str) -> None:
    st.session_state["archive_query"] = topic
    st.session_state["archive_page"] = 1
    st.session_state["scroll_to_results"] = True


def copy_button_markup(value: str, theme: dict[str, str]) -> str:
    """Build a compact, accessible clipboard button for an APA citation."""
    safe_value = html.escape(value, quote=True)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@500&display=swap">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
button {{
  display: block; width: 100%; height: 48px; padding: 0 .8rem;
  border: 1px solid {theme['accent']}; border-radius: 10px;
  background: {theme['accent']}; color: {theme['on_accent']};
  font: 500 .86rem/1.2 "DM Mono", monospace;
  appearance: none; -webkit-appearance: none; box-shadow: none;
  cursor: pointer; transition: background-color 120ms ease, border-color 120ms ease;
}}
button:hover {{ background: {theme['accent_hover']}; border-color: {theme['accent_hover']}; }}
button:focus-visible {{ outline: 2px solid {theme['focus']}; outline-offset: 2px; }}
button[data-copied="true"] {{ background: {theme['success_bg']}; border-color: {theme['success_border']}; color: {theme['success']}; }}
</style>
</head>
<body>
<button id="copyCitation" type="button" data-copy="{safe_value}"
        aria-label="Alıntıyı panoya kopyala" aria-live="polite">Kopyala</button>
<script>
const button = document.getElementById("copyCitation");
function fallbackCopy(text) {{
  const field = document.createElement("textarea");
  field.value = text;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.opacity = "0";
  document.body.appendChild(field);
  field.select();
  const copied = document.execCommand("copy");
  field.remove();
  return copied;
}}
button.addEventListener("click", async () => {{
  const text = button.dataset.copy;
  try {{
    if (navigator.clipboard && window.isSecureContext) {{
      try {{ await navigator.clipboard.writeText(text); }}
      catch (error) {{ if (!fallbackCopy(text)) throw error; }}
    }} else if (!fallbackCopy(text)) {{
      throw new Error("Clipboard unavailable");
    }}
    button.textContent = "Kopyalandı";
    button.dataset.copied = "true";
    button.setAttribute("aria-label", "Alıntı kopyalandı");
  }} catch (error) {{
    button.textContent = "Kopyalanamadı";
    button.setAttribute("aria-label", "Alıntı kopyalanamadı");
  }}
  window.setTimeout(() => {{
    button.textContent = "Kopyala";
    delete button.dataset.copied;
    button.setAttribute("aria-label", "Alıntıyı panoya kopyala");
  }}, 1600);
}});
</script>
</body>
</html>"""


def render_status(message: str, *, error: bool = False) -> None:
    """Render a theme-aware status message with an appropriate live role."""
    class_name = "app-status app-status--error" if error else "app-status"
    role = "alert" if error else "status"
    st.markdown(
        f'<div class="{class_name}" role="{role}">{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


db_path = find_database()
if db_path is None:
    render_status(
        "Arşiv veritabanı bulunamadı. tipografi_arsivi.db dosyasını app.py ile "
        "aynı klasöre koyun ya da TIPOGRAFI_DB_PATH ortam değişkeniyle yolunu belirtin.",
        error=True,
    )
    st.stop()

try:
    conn = get_connection(db_path.as_uri() + "?mode=ro")
    total_issues, total_articles = get_counts(conn)
    available_years = get_years(conn)
except (sqlite3.Error, OSError) as error:
    render_status(f"Arşiv veritabanı okunamadı: {error}", error=True)
    st.stop()


with st.container(key="archive_brand_row"):
    st.markdown(
        f'<header class="archive-brand-header">'
        f'<div class="brand-identity"><img class="brand-logo" src="{LOGO_URL}" '
        'alt="Türkçe Tipografi Topluluğu logosu">'
        '<div><div class="brand-name">Türkçe Tipografi Topluluğu</div></div></div>'
        '<nav class="brand-links" aria-label="Yayın bağlantıları">'
        '<a href="https://tipografi.substack.com/">Substack</a>'
        '<span aria-hidden="true">·</span>'
        '<a href="https://medium.com/tipografi">Medium</a></nav></header>',
        unsafe_allow_html=True,
    )
    is_dark = CURRENT_THEME_NAME == "dark"
    st.button(
        " ",
        key="archive_theme_toggle",
        help="Açık moda geç" if is_dark else "Koyu moda geç",
        on_click=toggle_archive_theme,
        type="secondary",
    )

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)
st.title("Tipografi Bülteni Arşivi")
st.markdown(
    '<div class="hero-copy">2019’dan bu yana her ay yayımladığımız bültenlerde, '
    'Türkiye’de ve dünyada tipografi alanında öne çıkan gelişmeleri bir araya getiriyoruz. '
    'Anahtar kelimelerle arama yapabilir, yeni sayılar eklendikçe büyüyen arşivimizi keşfedebilirsiniz.</div>',
    unsafe_allow_html=True,
)

stat_items = []
for label, value in zip(
    ("YAYIMLANAN SAYI", "DİZİNLENEN GELİŞME", "ARŞİV KAPSAMI"),
    (f"{total_issues:,}", f"{total_articles:,}",
     f"{min(available_years)}–{max(available_years)}" if available_years else "—"),
):
    stat_items.append(
        '<div class="stat-item">'
        f'<div class="stat-label">{html.escape(label)}</div>'
        f'<div class="stat-value">{html.escape(value)}</div>'
        '</div>'
    )
st.markdown(
    '<div class="stat-grid">' + "".join(stat_items) + '</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)

with st.form("archive_search"):
    search_col, year_col, submit_col = st.columns(
        [5, 1.6, 1.05], vertical_alignment="bottom"
    )
    with search_col:
        st.markdown('<div class="section-eyebrow">ARŞİVDE ARA</div>', unsafe_allow_html=True)
        st.text_input(
            "Aranacak ifade", key="archive_query",
            placeholder="Örneğin değişken yazıtipi, Monotype, kaligrafi",
            label_visibility="collapsed",
        )
    with year_col:
        st.markdown('<div class="section-eyebrow">YIL</div>', unsafe_allow_html=True)
        st.selectbox(
            "Yıl", [ALL_YEARS, *available_years],
            key="archive_year", label_visibility="collapsed",
        )
    with submit_col:
        search_submitted = st.form_submit_button("Ara", type="primary", use_container_width=True)

if search_submitted:
    st.session_state["scroll_to_results"] = True

st.markdown('<div class="section-eyebrow topics-eyebrow">ÖNE ÇIKAN ARAMALAR</div>', unsafe_allow_html=True)
for row_start in range(0, len(POPULAR_TOPICS), 3):
    topic_cols = st.columns(3)
    for offset, topic in enumerate(POPULAR_TOPICS[row_start:row_start + 3]):
        with topic_cols[offset]:
            st.button(
                topic, key=f"topic_{row_start + offset}", on_click=choose_topic,
                args=(topic,), use_container_width=True,
            )

query = str(st.session_state.get("archive_query", "")).strip()
selected_year = str(st.session_state.get("archive_year", ALL_YEARS))
filter_key = (query.casefold(), selected_year)
if st.session_state.get("_archive_filter_key") != filter_key:
    st.session_state["_archive_filter_key"] = filter_key
    st.session_state["archive_page"] = 1
current_page = max(1, int(st.session_state.get("archive_page", 1)))

if query:
    try:
        where, params = result_filter(query, selected_year)
        with st.spinner("Arşiv taranıyor…"):
            result_count, issue_count = count_matches(conn, where, params)
            page_count = max(1, (result_count + PAGE_SIZE - 1) // PAGE_SIZE)
            current_page = min(current_page, page_count)
            rows = fetch_matches(conn, where, params, current_page) if result_count else []
            distribution = get_year_distribution(conn, where, params) if result_count else None
    except sqlite3.Error as error:
        render_status(
            f"Bu arama çalıştırılamadı. Başka bir ifade deneyin. Veritabanı yanıtı: {error}",
            error=True,
        )
        rows = []
        result_count = issue_count = 0
        page_count = 1
        distribution = None

    if result_count:
        st.markdown(
            f'<div class="result-summary"><strong>{result_count:,}</strong> gelişme · '
            f'<strong>{issue_count}</strong> bülten'
            "　<span style='color:var(--muted)'>·　En yeniden eskiye</span></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Yıllara göre dağılım", expanded=False):
            chart_data = distribution.rename_axis("Yıl").reset_index()
            chart_spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "description": "Arama sonuçlarının yıllara göre dağılımı.",
                "background": CURRENT_THEME["paper"],
                "height": 220,
                "mark": {"type": "bar", "color": CURRENT_THEME["chart_bar"]},
                "encoding": {
                    "x": {
                        "field": "Yıl",
                        "type": "ordinal",
                        "sort": None,
                        "axis": {
                            "title": None,
                            "labelAngle": 0,
                            "labelColor": CURRENT_THEME["muted"],
                            "labelFontSize": 12,
                            "labelPadding": 10,
                            "tickSize": 0,
                            "domain": False,
                        },
                    },
                    "y": {
                        "field": "Gelişme sayısı",
                        "type": "quantitative",
                        "axis": {
                            "title": None,
                            "labelColor": CURRENT_THEME["muted"],
                            "gridColor": CURRENT_THEME["chart_grid"],
                            "gridOpacity": 1,
                            "tickColor": "transparent",
                            "domain": False,
                            "format": "d",
                        },
                    },
                    "tooltip": [
                        {"field": "Yıl", "type": "ordinal", "title": "Yıl"},
                        {
                            "field": "Gelişme sayısı",
                            "type": "quantitative",
                            "title": "Gelişme sayısı",
                        },
                    ],
                },
                "config": {
                    "view": {"stroke": None},
                    "axis": {"labelFont": "DM Mono, monospace", "gridWidth": 1},
                },
            }
            st.vega_lite_chart(
                chart_data,
                spec=chart_spec,
                height=260,
                use_container_width=True,
                theme=None,
                alt="Arama sonuçlarının yıllara göre dağılımı",
            )

        for idx, row in enumerate(rows):
            clean_issue = issue_name(row["bulten_adi"] or "")
            issue_url = get_issue_url(clean_issue, int(row["yil"] or 0))
            body = clean_visual_lines(row["icerik"] or "")
            relevant_paragraphs = matching_paragraphs(body, query)
            excerpt = matching_excerpt(row["baslik"] or "", body, query)

            with st.container(border=True):
                if idx == 0:
                    st.markdown('<div id="first-result"></div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="result-meta">'
                    f'<strong>{html.escape(turkish_upper(clean_issue))}</strong>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.subheader(row["baslik"] or "Başlıksız gelişme")
                st.markdown(
                    f'<p class="result-excerpt">{highlighted_excerpt(excerpt, query)}</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"[Bu sayıyı aç ↗]({issue_url})")

                if relevant_paragraphs:
                    with st.expander("İlgili paragrafları oku", expanded=False):
                        st.markdown("\n\n".join(relevant_paragraphs))

                title = re.sub(r"[*_#]", "", row["baslik"] or "").strip().replace(chr(96), "")
                citation = (
                    f"Türkçe Tipografi Topluluğu. ({int(row['yil'] or 0)}, "
                    f"{row['ay'] or ''}). {title}. Tipografi Bülteni. {issue_url}"
                )
                with st.expander("Alıntı yap", expanded=False):
                    citation_safe = html.escape(citation)
                    citation_attr = html.escape(citation, quote=True)
                    st.markdown(
                        f'<div class="citation-row">'
                        f'<div class="citation-box">{citation_safe}</div>'
                        f'<button type="button" class="citation-copy-btn" data-copy="{citation_attr}" '
                        f'aria-label="Alıntıyı panoya kopyala">Kopyala</button>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        if page_count > 1:
            st.markdown("")
            prev_col, label_col, next_col = st.columns([1, 2, 1])
            with prev_col:
                st.button(
                    "← Önceki", disabled=current_page <= 1, on_click=set_page,
                    args=(current_page - 1,), use_container_width=True, key="previous_page",
                )
            with label_col:
                st.markdown(
                    f"<p style='text-align:center;color:var(--muted);font-family:\"DM Mono\",monospace;font-size:.82rem'>Sayfa {current_page} / {page_count}</p>",
                    unsafe_allow_html=True,
                )
            with next_col:
                st.button(
                    "Sonraki →", disabled=current_page >= page_count, on_click=set_page,
                    args=(current_page + 1,), use_container_width=True, key="next_page",
                )
    else:
        st.markdown('<div id="first-result"></div>', unsafe_allow_html=True)
        render_status(
            f"“{query}” ifadesiyle"
            + (f" {selected_year} yılında" if selected_year != ALL_YEARS else "")
            + " eşleşen bir gelişme bulunamadı. Yazımı kontrol edin veya daha kısa bir arama deneyin."
        )

if st.session_state.pop("scroll_to_results", False):
    scroll_seq = st.session_state.get("_scroll_seq", 0) + 1
    st.session_state["_scroll_seq"] = scroll_seq
    scroll_trigger = f"""<!doctype html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;">
<script>
(() => {{
  const p = window.parent;
  if (!p) return;
  if (typeof p.__scrollToFirstResult === 'function') {{
    p.__scrollToFirstResult();
  }} else {{
    let count = 0;
    const t = setInterval(() => {{
      count++;
      const el = p.document.getElementById('first-result') || p.document.querySelector('.app-status');
      if (el) {{
        clearInterval(t);
        const reduced = p.matchMedia('(prefers-reduced-motion: reduce)').matches;
        el.scrollIntoView({{ behavior: reduced ? 'auto' : 'smooth', block: 'start' }});
      }} else if (count >= 60) {{
        clearInterval(t);
      }}
    }}, 30);
  }}
}})();
</script>
</body>
</html>"""
    components.html(scroll_trigger, height=0, scrolling=False)

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)
st.markdown(
    """
    <footer class="archive-footer" aria-label="Alt bilgi">
      <div class="footer-content">
        <div class="footer-name">Türkçe Tipografi Topluluğu</div>
        <div class="footer-actions">
          <div class="footer-subscribe"><a href="https://tipografi.substack.com/" target="_blank" rel="noopener noreferrer">Bültene Abone Ol</a></div>
          <nav class="footer-social" aria-label="Sosyal medya bağlantıları">
          <a href="https://www.facebook.com/tipografi/" target="_blank" rel="noopener noreferrer" aria-label="Facebook" title="Facebook">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M13.6 21v-8.2h2.8l.4-3.2h-3.2V7.5c0-.9.3-1.6 1.6-1.6H17V3.1c-.3 0-1.3-.1-2.4-.1-2.4 0-4.1 1.5-4.1 4.3v2.4H7.8v3.2h2.7V21z"/></svg>
          </a>
          <a href="https://x.com/tipografi" target="_blank" rel="noopener noreferrer" aria-label="X" title="X">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M18.9 2H22l-6.8 7.8L23 22h-6.2l-4.9-6.4L6.3 22H3.1l7.3-8.4L2.7 2h6.4l4.4 5.9L18.9 2zm-1.1 17.8h1.7L8.4 4.1H6.6z"/></svg>
          </a>
          <a href="https://www.instagram.com/tipografitoplulugu/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" title="Instagram">
            <svg viewBox="0 0 24 24" aria-hidden="true"><rect class="icon-stroke" x="3.2" y="3.2" width="17.6" height="17.6" rx="5.1"/><circle class="icon-stroke" cx="12" cy="12" r="4.1"/><circle class="icon-fill" cx="17.7" cy="6.6" r="1.1"/></svg>
          </a>
          <a href="https://www.youtube.com/@tipografi" target="_blank" rel="noopener noreferrer" aria-label="YouTube" title="YouTube">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8z"/><path d="m9.6 15.8 6.2-3.8-6.2-3.8z" fill="var(--paper)"/></svg>
          </a>
          <a href="https://open.spotify.com/show/1Ij0BoHaoobj5Mez7mAS22" target="_blank" rel="noopener noreferrer" aria-label="Spotify" title="Spotify">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M12 1.8A10.2 10.2 0 1 0 12 22.2 10.2 10.2 0 0 0 12 1.8z"/><path d="M6.2 9.1c3.8-1.1 8.6-.7 11.7 1.2M7 12.1c3.2-.9 7.3-.5 9.9 1.1M7.8 15c2.6-.7 5.8-.4 7.9.9" fill="none" stroke="var(--paper)" stroke-width="1.4" stroke-linecap="round"/></svg>
          </a>
          <a href="https://tipografi.substack.com/" target="_blank" rel="noopener noreferrer" aria-label="Substack" title="Substack">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M3 4h18v2H3zm0 4h18v2H3zm0 4h18v2H3zm0 4h18v5l-9-3.5L3 21z"/></svg>
          </a>
          </nav>
        </div>
      </div>
    </footer>
    """,
    unsafe_allow_html=True,
)
