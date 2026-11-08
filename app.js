/**
 * Tipografi Bülteni Arşivi — İstemci Taraflı Arama ve Arayüz Motoru (app.js)
 * Türkçe karakter duyarlı tam metin arama, filtreleme, sayfalama, alıntı ve tema desteği.
 */

(() => {
  "use strict";

  const PAGE_SIZE = 20;
  const THEME_STORAGE_KEY = "tipografi-archive-theme";

  const SUN_SVG = `<circle cx="12" cy="12" r="3.5"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>`;
  const MOON_SVG = `<path d="M20.1 15.2A8.4 8.4 0 0 1 8.8 3.9 8.5 8.5 0 1 0 20.1 15.2Z"/>`;

  // State
  let archiveData = [];
  let archiveStats = {};
  let currentResults = [];
  let currentPage = 1;
  let activeQuery = "";
  let activeYear = "Tümü";

  // Elements
  const themeToggleBtn = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");
  const searchInput = document.getElementById("search-input");
  const searchClearBtn = document.getElementById("search-clear-btn");
  const yearSelect = document.getElementById("year-select");
  const searchForm = document.getElementById("search-form");
  const topicsGrid = document.getElementById("topics-grid");
  const resultsContent = document.getElementById("results-content");
  const statusContainer = document.getElementById("status-container");
  const resultSummary = document.getElementById("result-summary");
  const chartContainer = document.getElementById("chart-container");
  const resultsList = document.getElementById("results-list");
  const paginationContainer = document.getElementById("pagination-container");
  const prevPageBtn = document.getElementById("prev-page-btn");
  const nextPageBtn = document.getElementById("next-page-btn");
  const pageLabel = document.getElementById("page-label");
  const firstResultAnchor = document.getElementById("first-result");

  // Stat Elements
  const statIssues = document.getElementById("stat-issues");
  const statArticles = document.getElementById("stat-articles");
  const statRange = document.getElementById("stat-range");

  // -------------------------------------------------------------
  // String & Turkish Normalization Utilities
  // -------------------------------------------------------------

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function turkishUpper(text) {
    if (!text) return "";
    return text.replace(/i/g, "İ").replace(/ı/g, "I").toUpperCase();
  }

  function normalizeForMatch(text) {
    if (!text) return "";
    return text
      .toLocaleLowerCase("tr-TR")
      .replace(/ı/g, "i")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\p{L}\p{N}]+/gu, " ")
      .trim();
  }

  function textContainsQuery(text, query) {
    const normText = normalizeForMatch(text);
    const normQuery = normalizeForMatch(query);
    if (!normQuery) return false;
    return normText.includes(normQuery);
  }

  function cleanVisualLines(text) {
    if (!text) return "";
    return text
      .split("\n")
      .filter((line) => !/^\s*(?:\*|_)?\s*Görsel(?:\/Video)?\s*:\s*/i.test(line))
      .join("\n")
      .trim();
  }

  function plainText(markdownText) {
    let text = cleanVisualLines(markdownText);
    text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1");
    text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
    text = text.replace(/^\s{0,3}#{1,6}\s*/gm, "");
    text = text.replace(/[*_~`]/g, "");
    text = text.replace(/^\s*[-+>]\s*/gm, "");
    return text.replace(/\s+/g, " ").trim();
  }

  function matchingParagraphs(body, query) {
    const paragraphs = cleanVisualLines(body).split(/\n\s*\n/);
    return paragraphs
      .map((p) => p.trim())
      .filter((p) => p && textContainsQuery(plainText(p), query));
  }

  function cropAroundQuery(sentence, query, limit = 460) {
    if (sentence.length <= limit || query.length >= limit) {
      return sentence;
    }
    const normSent = sentence.toLocaleLowerCase("tr-TR");
    const normQ = query.toLocaleLowerCase("tr-TR");
    const pos = normSent.indexOf(normQ);
    if (pos < 0) return sentence;

    let start = Math.max(0, pos - Math.floor((limit - query.length) / 2));
    let end = Math.min(sentence.length, start + limit);
    start = Math.max(0, end - limit);

    while (start > 0 && !/\s/.test(sentence[start - 1])) {
      start--;
    }
    while (end < sentence.length && !/\s/.test(sentence[end])) {
      end++;
    }

    const excerpt = sentence.slice(start, end).trim();
    return (start > 0 ? "…" : "") + excerpt + (end < sentence.length ? "…" : "");
  }

  function matchingExcerpt(title, body, query) {
    let searchBody = body;
    if (title.toLocaleLowerCase("tr-TR").includes("küçük puntolar")) {
      const lines = body
        .split("\n")
        .filter((line) => textContainsQuery(plainText(line), query));
      if (lines.length > 0) {
        searchBody = lines.join("\n");
      }
    }

    const readable = plainText(searchBody);
    const sentences = readable.split(/(?<=[.!?])\s+/).filter(Boolean);

    for (const sent of sentences) {
      if (textContainsQuery(sent, query)) {
        return cropAroundQuery(sent, query);
      }
    }

    const readableTitle = plainText(title);
    if (textContainsQuery(readableTitle, query)) {
      return `Başlıkta eşleşme: ${readableTitle}.`;
    }

    return `Aranan ifade “${query}” bu kaydın içeriğindeki bir bağlantıda eşleşiyor.`;
  }

  function highlightedExcerpt(text, query) {
    if (!query) return escapeHtml(text);
    const words = query.trim().split(/\s+/).filter(Boolean);
    if (!words.length) return escapeHtml(text);

    // Escape regex characters
    const escaped = words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const regex = new RegExp(`(${escaped.join("|")})`, "gi");

    const parts = text.split(regex);
    return parts
      .map((part) => {
        if (words.some((w) => part.toLocaleLowerCase("tr-TR") === w.toLocaleLowerCase("tr-TR"))) {
          return `<mark class="search-hit">${escapeHtml(part)}</mark>`;
        }
        return escapeHtml(part);
      })
      .join("");
  }

  function formatMarkdownParagraph(md) {
    let html = escapeHtml(md);
    // Link replacement: [text](url)
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italic: *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    return `<p>${html}</p>`;
  }

  // -------------------------------------------------------------
  // Theme Management
  // -------------------------------------------------------------

  function getActiveTheme() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }

  function updateThemeUI(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (themeIcon) {
      themeIcon.innerHTML = theme === "dark" ? SUN_SVG : MOON_SVG;
    }
    if (themeToggleBtn) {
      const label = theme === "dark" ? "Açık moda geç" : "Koyu moda geç";
      themeToggleBtn.setAttribute("aria-label", label);
      themeToggleBtn.setAttribute("title", label);
    }
  }

  function toggleTheme() {
    const current = getActiveTheme();
    const next = current === "dark" ? "light" : "dark";
    updateThemeUI(next);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch (_) {}

    const url = new URL(window.location.href);
    url.searchParams.set("theme", next);
    window.history.replaceState({}, "", url.toString());

    // Redraw chart if open so colors match theme
    if (currentResults.length > 0) {
      renderDistributionChart(currentResults);
    }
  }

  // -------------------------------------------------------------
  // Year Distribution Bar Chart (SVG)
  // -------------------------------------------------------------

  function renderDistributionChart(matches) {
    if (!chartContainer) return;

    const countsByYear = {};
    const minYear = 2019;
    const maxYear = archiveStats.max_year || 2026;

    for (let y = minYear; y <= maxYear; y++) {
      countsByYear[y] = 0;
    }

    for (const item of matches) {
      if (item.yil && countsByYear[item.yil] !== undefined) {
        countsByYear[item.yil]++;
      }
    }

    const years = Object.keys(countsByYear).map(Number).sort((a, b) => a - b);
    const maxCount = Math.max(...Object.values(countsByYear), 1);

    const svgWidth = 720;
    const svgHeight = 220;
    const padding = { top: 20, right: 20, bottom: 40, left: 35 };
    const chartW = svgWidth - padding.left - padding.right;
    const chartH = svgHeight - padding.top - padding.bottom;

    const barWidth = Math.min(48, Math.max(16, (chartW / years.length) * 0.65));
    const step = chartW / years.length;

    let svg = `<svg class="chart-svg" viewBox="0 0 ${svgWidth} ${svgHeight}" role="img" aria-label="Arama sonuçlarının yıllara göre dağılım grafiği">`;

    // Horizontal grid lines & Y labels (0, max/2, max)
    const yTicks = [0, Math.ceil(maxCount / 2), maxCount];
    const uniqueYTicks = Array.from(new Set(yTicks));

    for (const tick of uniqueYTicks) {
      const y = padding.top + chartH - (tick / maxCount) * chartH;
      svg += `
        <line x1="${padding.left}" y1="${y}" x2="${svgWidth - padding.right}" y2="${y}" stroke="var(--chart-grid)" stroke-width="1" />
        <text x="${padding.left - 8}" y="${y + 4}" fill="var(--muted)" font-family="'DM Mono', monospace" font-size="11" text-anchor="end">${tick}</text>
      `;
    }

    // Bars & X labels
    years.forEach((yr, idx) => {
      const count = countsByYear[yr];
      const barH = (count / maxCount) * chartH;
      const x = padding.left + idx * step + (step - barWidth) / 2;
      const y = padding.top + chartH - barH;

      svg += `
        <g class="chart-bar-group" tabindex="0">
          <title>${yr}: ${count} gelişme</title>
          <rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" fill="var(--chart-bar)" rx="2" style="cursor: pointer; transition: opacity 120ms ease;">
            <animate attributeName="height" from="0" to="${barH}" dur="0.25s" fill="freeze" />
            <animate attributeName="y" from="${padding.top + chartH}" to="${y}" dur="0.25s" fill="freeze" />
          </rect>
          <text x="${x + barWidth / 2}" y="${svgHeight - 12}" fill="var(--muted)" font-family="'DM Mono', monospace" font-size="12" text-anchor="middle">${yr}</text>
        </g>
      `;
    });

    svg += `</svg>`;
    chartContainer.innerHTML = svg;
  }

  // -------------------------------------------------------------
  // Search Engine
  // -------------------------------------------------------------

  function filterItems(query, year) {
    const normQuery = normalizeForMatch(query);
    const queryTokens = normQuery.split(" ").filter(Boolean);

    return archiveData.filter((item) => {
      // 1. Year filter
      if (year && year !== "Tümü" && String(item.yil) !== String(year)) {
        return false;
      }

      // If no text query, match all within year filter
      if (!normQuery) {
        return year && year !== "Tümü";
      }

      // 2. Query matching
      const normTitle = normalizeForMatch(item.baslik);
      const normContent = normalizeForMatch(item.icerik);
      const combined = `${normTitle} ${normContent}`;

      // Check phrase first
      if (combined.includes(normQuery)) {
        return true;
      }

      // Check if all tokens match
      return queryTokens.every((token) => combined.includes(token));
    });
  }

  function executeSearch(shouldScroll = false) {
    const query = activeQuery.trim();
    const year = activeYear;

    // Reset pagination
    currentPage = 1;

    // Topic button active styling
    document.querySelectorAll(".topic-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-topic").toLocaleLowerCase("tr-TR") === query.toLocaleLowerCase("tr-TR"));
    });

    if (!query && year === "Tümü") {
      resultsContent.style.display = "none";
      statusContainer.innerHTML = "";
      updateURL(query, year, 1);
      return;
    }

    currentResults = filterItems(query, year);
    renderResultsView(query, year);
    updateURL(query, year, 1);

    if (shouldScroll) {
      scrollToFirstResult();
    }
  }

  function renderResultsView(query, year) {
    if (currentResults.length === 0) {
      resultsContent.style.display = "none";
      const yearText = year !== "Tümü" ? ` ${year} yılında` : "";
      statusContainer.innerHTML = `
        <div class="app-status">
          “<strong>${escapeHtml(query || year)}</strong>” ifadesiyle${yearText} eşleşen bir gelişme bulunamadı. Yazımı kontrol edin veya daha kısa bir arama deneyin.
        </div>
      `;
      return;
    }

    statusContainer.innerHTML = "";
    resultsContent.style.display = "block";

    // Summary
    const distinctIssues = new Set(currentResults.map((r) => r.bulten)).size;
    resultSummary.innerHTML = `
      <strong>${currentResults.length.toLocaleString("tr-TR")}</strong> gelişme
      <span class="result-summary-separator">·</span>
      <strong>${distinctIssues}</strong> bültende
      <span class="result-summary-separator">·</span>
      <span style="color:var(--muted)">En yeniden eskiye</span>
    `;

    // Render bar chart
    renderDistributionChart(currentResults);

    // Render current page cards
    renderPageCards();
  }

  function renderPageCards() {
    const totalPages = Math.ceil(currentResults.length / PAGE_SIZE) || 1;
    currentPage = Math.max(1, Math.min(currentPage, totalPages));

    const startIdx = (currentPage - 1) * PAGE_SIZE;
    const endIdx = startIdx + PAGE_SIZE;
    const pageItems = currentResults.slice(startIdx, endIdx);

    const cardsHtml = pageItems
      .map((item, idx) => {
        const cleanIssue = item.bulten;
        const body = cleanVisualLines(item.icerik);
        const excerpt = matchingExcerpt(item.baslik, body, activeQuery);
        const highlighted = highlightedExcerpt(excerpt, activeQuery);
        const relParagraphs = matchingParagraphs(body, activeQuery);

        // Citation
        const cleanTitle = (item.baslik || "").replace(/[*_#`]/g, "").trim();
        const citation = `Türkçe Tipografi Topluluğu. (${item.yil || ""}, ${item.ay || ""}). ${cleanTitle}. Tipografi Bülteni. ${item.url || ""}`;
        const citationSafe = escapeHtml(citation);

        const paragraphsBlock = relParagraphs.length > 0
          ? `
            <details class="card-expander">
              <summary class="card-summary">İlgili paragrafları oku</summary>
              <div class="card-expander-body">
                ${relParagraphs.map(formatMarkdownParagraph).join("")}
              </div>
            </details>
          `
          : "";

        return `
          <article class="result-card" data-id="${item.id}">
            <div class="result-meta">
              <strong>${escapeHtml(turkishUpper(cleanIssue))}</strong>
            </div>
            <h3>${escapeHtml(item.baslik)}</h3>
            <p class="result-excerpt">${highlighted}</p>
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer" class="result-issue-link">Bu sayıyı aç ↗</a>
            ${paragraphsBlock}
            <details class="card-expander">
              <summary class="card-summary">Alıntı yap</summary>
              <div class="card-expander-body">
                <div class="citation-row">
                  <div class="citation-box">${citationSafe}</div>
                  <button type="button" class="citation-copy-btn" data-citation="${citationSafe}" aria-label="Alıntıyı panoya kopyala">Kopyala</button>
                </div>
              </div>
            </details>
          </article>
        `;
      })
      .join("");

    resultsList.innerHTML = cardsHtml;

    // Bind citation copy buttons
    resultsList.querySelectorAll(".citation-copy-btn").forEach((btn) => {
      btn.addEventListener("click", handleCitationCopy);
    });

    // Pagination controls
    if (totalPages > 1) {
      paginationContainer.style.display = "grid";
      pageLabel.textContent = `Sayfa ${currentPage} / ${totalPages}`;
      prevPageBtn.disabled = currentPage <= 1;
      nextPageBtn.disabled = currentPage >= totalPages;
    } else {
      paginationContainer.style.display = "none";
    }
  }

  function handleCitationCopy(e) {
    const btn = e.currentTarget;
    const text = btn.getAttribute("data-citation");
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
      const origText = btn.textContent;
      btn.textContent = "Kopyalandı!";
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = origText;
        btn.classList.remove("copied");
      }, 2000);
    }).catch(() => {
      // Fallback
      btn.textContent = "Kopyalandı!";
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = "Kopyala";
        btn.classList.remove("copied");
      }, 2000);
    });
  }

  function scrollToFirstResult() {
    if (firstResultAnchor) {
      firstResultAnchor.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function updateURL(query, year, page) {
    const url = new URL(window.location.href);
    if (query) {
      url.searchParams.set("q", query);
    } else {
      url.searchParams.delete("q");
    }

    if (year && year !== "Tümü") {
      url.searchParams.set("yil", year);
    } else {
      url.searchParams.delete("yil");
    }

    if (page > 1) {
      url.searchParams.set("sayfa", page);
    } else {
      url.searchParams.delete("sayfa");
    }

    window.history.replaceState({}, "", url.toString());
  }

  // -------------------------------------------------------------
  // Event Handlers & Initialization
  // -------------------------------------------------------------

  function handleSearchSubmit() {
    activeQuery = searchInput.value;
    activeYear = yearSelect.value;
    executeSearch(true);
  }

  function initEvents() {
    // Theme toggle
    if (themeToggleBtn) {
      themeToggleBtn.addEventListener("click", toggleTheme);
    }

    // Search Input Clear Button
    if (searchInput && searchClearBtn) {
      searchInput.addEventListener("input", () => {
        searchClearBtn.style.display = searchInput.value ? "flex" : "none";
      });
      searchClearBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchClearBtn.style.display = "none";
        searchInput.focus();
        handleSearchSubmit();
      });
    }

    // Year change triggers search immediately
    if (yearSelect) {
      yearSelect.addEventListener("change", () => {
        activeYear = yearSelect.value;
        activeQuery = searchInput.value;
        executeSearch(true);
      });
    }

    // Popular Topics clicks
    if (topicsGrid) {
      topicsGrid.addEventListener("click", (e) => {
        const btn = e.target.closest(".topic-btn");
        if (!btn) return;
        const topic = btn.getAttribute("data-topic");
        searchInput.value = topic;
        if (searchClearBtn) searchClearBtn.style.display = "flex";
        yearSelect.value = "Tümü";
        activeQuery = topic;
        activeYear = "Tümü";
        executeSearch(true);
      });
    }

    // Pagination Prev / Next
    if (prevPageBtn) {
      prevPageBtn.addEventListener("click", () => {
        if (currentPage > 1) {
          currentPage--;
          renderPageCards();
          updateURL(activeQuery, activeYear, currentPage);
          scrollToFirstResult();
        }
      });
    }

    if (nextPageBtn) {
      nextPageBtn.addEventListener("click", () => {
        const totalPages = Math.ceil(currentResults.length / PAGE_SIZE) || 1;
        if (currentPage < totalPages) {
          currentPage++;
          renderPageCards();
          updateURL(activeQuery, activeYear, currentPage);
          scrollToFirstResult();
        }
      });
    }
  }

  async function loadArchiveData() {
    try {
      statusContainer.innerHTML = '<div class="app-status">Arşiv verileri yükleniyor…</div>';
      const response = await fetch("arsiv.json");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      archiveData = data.items || [];
      archiveStats = data.stats || {};

      // Populate Stats
      if (archiveStats.total_issues && statIssues) {
        statIssues.textContent = archiveStats.total_issues.toLocaleString("tr-TR");
      }
      if (archiveStats.total_articles && statArticles) {
        statArticles.textContent = archiveStats.total_articles.toLocaleString("tr-TR");
      }
      if (archiveStats.min_year && archiveStats.max_year && statRange) {
        statRange.textContent = `${archiveStats.min_year}–${archiveStats.max_year}`;
      }

      // Populate Year Select
      if (archiveStats.years && yearSelect) {
        yearSelect.innerHTML = `<option value="Tümü">Tümü</option>` +
          archiveStats.years.map((y) => `<option value="${y}">${y}</option>`).join("");
      }

      statusContainer.innerHTML = "";

      // Check URL parameters on initial load
      const params = new URLSearchParams(window.location.search);
      const urlQuery = params.get("q") || "";
      const urlYear = params.get("yil") || "Tümü";
      const urlPage = parseInt(params.get("sayfa") || "1", 10);

      if (urlQuery) {
        searchInput.value = urlQuery;
        activeQuery = urlQuery;
        if (searchClearBtn) searchClearBtn.style.display = "flex";
      }
      if (urlYear && urlYear !== "Tümü") {
        yearSelect.value = urlYear;
        activeYear = urlYear;
      }

      if (urlQuery || (urlYear && urlYear !== "Tümü")) {
        currentResults = filterItems(activeQuery, activeYear);
        currentPage = isNaN(urlPage) ? 1 : urlPage;
        renderResultsView(activeQuery, activeYear);
      }
    } catch (err) {
      console.error("Arşiv verisi yüklenemedi:", err);
      statusContainer.innerHTML = `
        <div class="app-status app-status--error">
          Arşiv verileri yüklenemedi. Lütfen internet bağlantınızı kontrol edip sayfayı yenileyin. (${escapeHtml(err.message)})
        </div>
      `;
    }
  }

  // Public Interface for Inline form onsubmit
  window.ArchiveApp = {
    handleSearchSubmit,
  };

  // Start
  document.addEventListener("DOMContentLoaded", () => {
    updateThemeUI(getActiveTheme());
    initEvents();
    loadArchiveData();
  });
})();
