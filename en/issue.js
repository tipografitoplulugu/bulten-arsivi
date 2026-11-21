(() => {
  "use strict";

  const THEME_STORAGE_KEY = "tipografi-archive-theme";
  const SUN_SVG = `<circle cx="12" cy="12" r="3.5"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>`;
  const MOON_SVG = `<path d="M20.1 15.2A8.4 8.4 0 0 1 8.8 3.9 8.5 8.5 0 1 0 20.1 15.2Z"/>`;
  const status = document.getElementById("issue-status");
  const content = document.getElementById("issue-content");
  const themeButton = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[char]));
  }

  function renderInline(markdown) {
    let html = escapeHtml(markdown);
    html = html.replace(/!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/g, '<img src="$2" alt="$1" loading="lazy">');
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>");
    html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
    html = html.replace(/_([^_]+)_/g, "<em>$1</em>");
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    return html;
  }

  function renderMarkdown(markdown) {
    const lines = markdown.replace(/\r/g, "").split("\n");
    const html = [];
    let paragraph = [];
    let listTag = "";
    let quote = [];
    let code = [];
    let inCode = false;

    const flushParagraph = () => {
      if (paragraph.length) html.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
      paragraph = [];
    };
    const closeList = () => {
      if (listTag) html.push(`</${listTag}>`);
      listTag = "";
    };
    const flushQuote = () => {
      if (quote.length) html.push(`<blockquote><p>${renderInline(quote.join(" "))}</p></blockquote>`);
      quote = [];
    };
    const flushCode = () => {
      if (code.length) html.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
      code = [];
    };

    for (const line of lines) {
      if (inCode) {
        if (/^\s*```/.test(line)) {
          flushCode();
          inCode = false;
        } else {
          code.push(line);
        }
        continue;
      }
      if (/^\s*```/.test(line)) {
        flushParagraph(); closeList(); flushQuote();
        inCode = true;
        continue;
      }
      if (!line.trim()) {
        flushParagraph(); closeList(); flushQuote();
        continue;
      }

      const heading = line.match(/^(#{1,6})\s+(.+)$/);
      if (heading) {
        flushParagraph(); closeList(); flushQuote();
        const level = heading[1].length;
        html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
        continue;
      }
      if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
        flushParagraph(); closeList(); flushQuote();
        html.push("<hr>");
        continue;
      }
      const bullet = line.match(/^\s*[-*+]\s+(.+)$/);
      const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
      if (bullet || numbered) {
        flushParagraph(); flushQuote();
        const nextTag = bullet ? "ul" : "ol";
        if (listTag !== nextTag) {
          closeList();
          listTag = nextTag;
          html.push(`<${listTag}>`);
        }
        html.push(`<li>${renderInline((bullet || numbered)[1])}</li>`);
        continue;
      }
      const quoteLine = line.match(/^\s*>\s?(.*)$/);
      if (quoteLine) {
        flushParagraph(); closeList();
        quote.push(quoteLine[1]);
        continue;
      }
      flushQuote(); closeList();
      paragraph.push(line.trim());
    }

    flushParagraph(); closeList(); flushQuote();
    if (inCode) flushCode();
    return html.join("\n");
  }

  function updateTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const isDark = theme === "dark";
    themeIcon.innerHTML = isDark ? SUN_SVG : MOON_SVG;
    themeButton.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    themeButton.title = isDark ? "Switch to light mode" : "Switch to dark mode";
  }

  themeButton.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_STORAGE_KEY, next);
    updateTheme(next);
  });
  updateTheme(document.documentElement.getAttribute("data-theme") || "light");

  async function loadIssue() {
    const params = new URLSearchParams(window.location.search);
    const year = Number(params.get("year"));
    const month = Number(params.get("month"));
    if (!Number.isInteger(year) || !Number.isInteger(month) || month < 1 || month > 12) {
      throw new Error("Choose a valid issue from the archive.");
    }

    const manifestResponse = await fetch("issues-en.json");
    if (!manifestResponse.ok) throw new Error("The issue index could not be loaded.");
    const manifest = await manifestResponse.json();
    const issue = manifest.issues.find((entry) => entry.year === year && entry.month === month);
    if (!issue) throw new Error("An English translation for this issue could not be found.");

    const issueResponse = await fetch(issue.path);
    if (!issueResponse.ok) throw new Error("The English issue text could not be loaded.");
    const markdown = await issueResponse.text();
    content.innerHTML = renderMarkdown(markdown);
    content.hidden = false;
    document.getElementById("issue-translation-note").hidden = false;
    status.hidden = true;
    document.title = `${issue.title} · Typography Newsletter Archive`;
    const originalWrap = document.getElementById("issue-original-wrap");
    const originalLink = document.getElementById("issue-original-link");
    if (issue.url) {
      originalLink.href = issue.url;
      originalWrap.hidden = false;
    }
  }

  loadIssue().catch((error) => {
    status.textContent = error.message;
    status.classList.add("app-status--error");
  });
})();
