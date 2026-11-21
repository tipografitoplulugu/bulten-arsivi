/**
 * Tipografi Bülteni Arşivi — İstemci Taraflı Arama ve Arayüz Motoru (app.js)
 * Türkçe karakter duyarlı tam metin arama, filtreleme, sayfalama, alıntı ve tema desteği.
 */

(() => {
  "use strict";

  const PAGE_SIZE = 20;
  const THEME_STORAGE_KEY = "tipografi-archive-theme";
  const STRINGS = {
    tr: {
      pageTitle: "Tipografi Bülteni Arşivi",
      metaDescription: "2019’dan bu yana her ay yayımladığımız Tipografi Bülteni arşivi. Türkiye’de ve dünyada tipografi alanında öne çıkan gelişmeler.",
      language: "Dil seçimi",
      publications: "Yayın bağlantıları",
      logoAlt: "Türkçe Tipografi Topluluğu logosu",
      brand: "Türkçe Tipografi Topluluğu",
      heroTitle: "Tipografi Bülteni Arşivi",
      heroCopy: "2019’dan bu yana her ay yayımladığımız bültenlerde, Türkiye’de ve dünyada tipografi alanında öne çıkan gelişmeleri bir araya getiriyoruz. Anahtar kelimelerle arama yapabilir, yeni sayılar eklendikçe büyüyen arşivimizi keşfedebilirsiniz.",
      issuesLabel: "YAYIMLANAN SAYI",
      articlesLabel: "DİZİNLENEN GELİŞME",
      rangeLabel: "ARŞİV KAPSAMI",
      searchHeading: "ARŞİVDE ARA",
      searchPlaceholder: "Örneğin değişken yazıtipi, Monotype, kaligrafi",
      searchAria: "Aranacak ifade",
      clearAria: "Aramayı temizle",
      yearLabel: "YIL",
      allYears: "Tümü",
      yearAria: "Yıl filtreleme",
      searchButton: "Ara",
      topicsHeading: "ÖNE ÇIKAN ARAMALAR",
      distribution: "Yıllara göre dağılım",
      previous: "← Önceki",
      next: "Sonraki →",
      pagination: "Sayfalama",
      footer: "Alt bilgi",
      subscribe: "Bültene Abone Ol",
      languageNote: "İngilizce özetler seçili sayılar için sunuluyor. Bültenin tamamı Türkçe yayımlanıyor.",
      themeDark: "Koyu moda geç",
      themeLight: "Açık moda geç",
      loading: "Arşiv verileri yükleniyor…",
      loadError: "Arşiv verileri yüklenemedi. Lütfen internet bağlantınızı kontrol edip sayfayı yenileyin.",
      noResults: "“{query}” ifadesiyle{year} eşleşen bir gelişme bulunamadı. Yazımı kontrol edin veya daha kısa bir arama deneyin.",
      noYearResults: "{year} yılı için arşiv kaydı bulunamadı.",
      resultsSummary: "{articles} gelişme · {issues} bültende · En yeniden eskiye",
      chartAria: "Arama sonuçlarının yıllara göre dağılım grafiği",
      chartTitle: "{year}: {count} gelişme",
      excerptInTitle: "Başlıkta eşleşme: {title}.",
      excerptInLink: "Aranan ifade “{query}” bu kaydın içeriğindeki bir bağlantıda eşleşiyor.",
      relevantParagraphs: "İlgili paragrafları oku",
      summaryLabel: "İngilizce özet",
      readIssue: "Bu sayıyı aç ↗",
      originalIssue: "Alıntı yap",
      copy: "Kopyala",
      copied: "Kopyalandı!",
      citationCopyAria: "Alıntıyı panoya kopyala",
      pageLabel: "Sayfa {page} / {total}",
      topicNames: ["Değişken Yazıtipi", "Monotype", "Gutenberg", "Yapay Zekâ", "Lisanslama", "Kaligrafi", "TDC", "Google Fonts", "Arial"],
      months: { "Ocak": "Ocak", "Şubat": "Şubat", "Mart": "Mart", "Nisan": "Nisan", "Mayıs": "Mayıs", "Haziran": "Haziran", "Temmuz": "Temmuz", "Ağustos": "Ağustos", "Eylül": "Eylül", "Ekim": "Ekim", "Kasım": "Kasım", "Aralık": "Aralık" },
    },
    en: {
      pageTitle: "Typography Newsletter Archive",
      metaDescription: "Explore the Turkish Typography Society’s monthly archive, published since 2019, covering notable developments in typography in Türkiye and around the world.",
      language: "Language",
      publications: "Publications",
      logoAlt: "Turkish Typography Society logo",
      brand: "Turkish Typography Society",
      heroTitle: "Typography Newsletter Archive",
      heroCopy: "Since 2019, we have brought together notable developments in typography in Türkiye and around the world in a monthly newsletter. Search English summaries by keyword and explore the archive.",
      issuesLabel: "ISSUES PUBLISHED",
      articlesLabel: "NEWS INDEXED",
      rangeLabel: "ARCHIVE COVERAGE",
      searchHeading: "SEARCH THE ARCHIVE",
      searchPlaceholder: "Try variable fonts, Monotype, calligraphy",
      searchAria: "Search phrase",
      clearAria: "Clear search",
      yearLabel: "YEAR",
      allYears: "All years",
      yearAria: "Filter by year",
      searchButton: "Search",
      topicsHeading: "POPULAR SEARCHES",
      distribution: "Results by year",
      previous: "← Previous",
      next: "Next →",
      pagination: "Pagination",
      footer: "Footer",
      subscribe: "Subscribe to the newsletter",
      languageNote: "English translations are available for the archive. Original Turkish issues are linked.",
      themeDark: "Switch to dark mode",
      themeLight: "Switch to light mode",
      loading: "Loading archive…",
      loadError: "The archive could not be loaded. Check your internet connection and refresh the page.",
      noResults: "No news items matched “{query}”{year}. Check the spelling or try a shorter search.",
      noYearResults: "No English newsletter entries were found for {year}.",
      resultsSummary: "{articles} news items · across {issues} issues · Newest first",
      chartAria: "Chart of search results by year",
      chartTitle: "{count} news items in {year}",
      excerptInTitle: "Title match: {title}.",
      excerptInLink: "The search phrase “{query}” appears in a link in this entry.",
      relevantParagraphs: "Read matching paragraphs",
      summaryLabel: "English summary",
      translationLabel: "English translation",
      readEnglishIssue: "Read English translation of the newsletter.",
      readIssue: "Read the original issue in Turkish ↗",
      originalIssue: "Cite this entry",
      copy: "Copy",
      copied: "Copied!",
      citationCopyAria: "Copy citation to clipboard",
      pageLabel: "Page {page} / {total}",
      topicNames: ["Variable fonts", "Monotype", "Gutenberg", "AI", "Font licensing", "Calligraphy", "TDC", "Google Fonts", "Arial"],
      months: { "Ocak": "January", "Şubat": "February", "Mart": "March", "Nisan": "April", "Mayıs": "May", "Haziran": "June", "Temmuz": "July", "Ağustos": "August", "Eylül": "September", "Ekim": "October", "Kasım": "November", "Aralık": "December" },
    },
  };

  const initialLanguageParams = new URLSearchParams(window.location.search);
  let currentLanguage = initialLanguageParams.has("lang")
    ? (initialLanguageParams.get("lang") === "en" ? "en" : "tr")
    : (/\/en(?:\/|$)/.test(window.location.pathname) ? "en" : "tr");
  let englishTranslations = {};
  let translationsLoaded = false;

  const SUN_SVG = `<circle cx="12" cy="12" r="3.5"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>`;
  const MOON_SVG = `<path d="M20.1 15.2A8.4 8.4 0 0 1 8.8 3.9 8.5 8.5 0 1 0 20.1 15.2Z"/>`;

  // State
  let archiveData = [];
  let archiveStats = {};
  let englishIssueKeys = new Set();
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
  const languageToggle = document.querySelector(".language-toggle");
  const languageNote = document.getElementById("language-note");

  function t(key, values = {}) {
    let value = STRINGS[currentLanguage][key] ?? STRINGS.tr[key] ?? key;
    if (typeof value !== "string") return value;
    return value.replace(/\{(\w+)\}/g, (_, name) => values[name] ?? "");
  }

  function localizedItem(item) {
    return currentLanguage === "en" ? englishTranslations[String(item.id)] : null;
  }

  function formatNumber(value) {
    return Number(value || 0).toLocaleString(currentLanguage === "en" ? "en-US" : "tr-TR");
  }

  function issueName(item) {
    const month = STRINGS[currentLanguage].months[item.ay] || item.ay;
    return [month, item.yil].filter(Boolean).join(" ");
  }

  function englishIssueUrl(item) {
    const monthNumber = Object.keys(STRINGS.tr.months).indexOf(item.ay) + 1;
    const url = new URL("en/issue.html", document.baseURI);
    url.searchParams.set("year", String(item.yil));
    url.searchParams.set("month", String(monthNumber));
    return url.toString();
  }

  function hasEnglishIssue(item) {
    const monthNumber = Object.keys(STRINGS.tr.months).indexOf(item.ay) + 1;
    return monthNumber > 0 && englishIssueKeys.has(`${item.yil}-${monthNumber}`);
  }

  function setText(id, key) {
    const element = document.getElementById(id);
    if (element) element.textContent = t(key);
  }

  function applyLanguage() {
    document.documentElement.lang = currentLanguage;
    document.title = t("pageTitle");
    const description = document.getElementById("document-description");
    if (description) description.setAttribute("content", t("metaDescription"));

    setText("hero-title", "heroTitle");
    setText("hero-copy", "heroCopy");
    setText("stat-issues-label", "issuesLabel");
    setText("stat-articles-label", "articlesLabel");
    setText("stat-range-label", "rangeLabel");
    setText("search-heading", "searchHeading");
    setText("year-label", "yearLabel");
    setText("all-years-option", "allYears");
    setText("search-submit", "searchButton");
    setText("topics-heading", "topicsHeading");
    setText("distribution-summary", "distribution");
    setText("prev-page-btn", "previous");
    setText("next-page-btn", "next");
    setText("footer-name", "brand");
    setText("subscribe-link", "subscribe");

    const logo = document.querySelector(".brand-logo");
    if (logo) logo.alt = t("logoAlt");
    const brand = document.querySelector(".brand-name");
    if (brand) brand.textContent = t("brand");
    const brandLinks = document.querySelector(".brand-links");
    if (brandLinks) brandLinks.setAttribute("aria-label", t("publications"));
    if (languageToggle) languageToggle.setAttribute("aria-label", t("language"));
    const footer = document.querySelector(".archive-footer");
    if (footer) footer.setAttribute("aria-label", t("footer"));
    const pagination = document.getElementById("pagination-container");
    if (pagination) pagination.setAttribute("aria-label", t("pagination"));

    if (searchInput) {
      searchInput.placeholder = t("searchPlaceholder");
      searchInput.setAttribute("aria-label", t("searchAria"));
    }
    if (searchClearBtn) searchClearBtn.setAttribute("aria-label", t("clearAria"));
    if (yearSelect) yearSelect.setAttribute("aria-label", t("yearAria"));

    document.querySelectorAll(".topic-btn").forEach((button, index) => {
      button.textContent = STRINGS[currentLanguage].topicNames[index] || button.dataset.topic;
    });

    const trLink = document.getElementById("language-tr");
    const enLink = document.getElementById("language-en");
    if (trLink) {
      trLink.classList.toggle("active", currentLanguage === "tr");
      if (currentLanguage === "tr") trLink.setAttribute("aria-current", "page"); else trLink.removeAttribute("aria-current");
    }
    if (enLink) {
      enLink.classList.toggle("active", currentLanguage === "en");
      if (currentLanguage === "en") enLink.setAttribute("aria-current", "page"); else enLink.removeAttribute("aria-current");
    }

    if (languageNote) {
      const translatedIssueRecords = Object.keys(englishTranslations).map((id) => {
        const item = archiveData.find((record) => String(record.id) === id);
        return item ? {key: `${item.yil}-${item.ay}`, year: item.yil} : null;
      }).filter(Boolean);
      const translatedIssues = new Map(translatedIssueRecords.map((issue) => [issue.key, issue.year]));
      const translatedYears = [...new Set(translatedIssueRecords.map((issue) => issue.year))].sort((a, b) => a - b);
      if (currentLanguage === "en") {
        if (translationsLoaded && englishIssueKeys.size) {
          const fullYears = [...new Set([...englishIssueKeys].map((key) => Number(key.split("-")[0])))].sort((a, b) => a - b);
          const yearText = fullYears.length ? ` (${fullYears[0]}–${fullYears[fullYears.length - 1]})` : "";
          languageNote.textContent = `Full English translations cover ${formatNumber(englishIssueKeys.size)} ${englishIssueKeys.size === 1 ? "issue" : "issues"}${yearText}. Original Turkish issues are linked.`;
        } else if (translationsLoaded) {
          const yearText = translatedYears.length ? ` (${translatedYears.join("–")})` : "";
          languageNote.textContent = `English summaries currently cover ${formatNumber(translatedIssues.size)} ${translatedIssues.size === 1 ? "issue" : "issues"}${yearText}. The full newsletter is published in Turkish.`;
        } else {
          languageNote.textContent = STRINGS.en.languageNote;
        }
        languageNote.hidden = false;
      } else {
        languageNote.hidden = true;
      }
    }

    updateThemeUI(getActiveTheme());
    if (archiveStats.total_issues && statIssues) statIssues.textContent = formatNumber(archiveStats.total_issues);
    if (archiveStats.total_articles && statArticles) statArticles.textContent = formatNumber(archiveStats.total_articles);
    if (archiveStats.min_year && archiveStats.max_year && statRange) statRange.textContent = `${archiveStats.min_year}–${archiveStats.max_year}`;
    if (yearSelect && archiveStats.years) {
      yearSelect.innerHTML = `<option value="Tümü">${escapeHtml(t("allYears"))}</option>` +
        archiveStats.years.map((year) => `<option value="${year}">${year}</option>`).join("");
      if (activeYear !== "Tümü") yearSelect.value = activeYear;
    }
  }

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
    const locale = currentLanguage === "en" ? "en-US" : "tr-TR";
    let normalized = text.toLocaleLowerCase(locale);
    if (currentLanguage === "tr") normalized = normalized.replace(/ı/g, "i");
    return normalized
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
    const locale = currentLanguage === "en" ? "en-US" : "tr-TR";
    const normSent = sentence.toLocaleLowerCase(locale);
    const normQ = query.toLocaleLowerCase(locale);
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
    if (currentLanguage === "tr" && title.toLocaleLowerCase("tr-TR").includes("küçük puntolar")) {
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
      return t("excerptInTitle", {title: readableTitle});
    }

    return t("excerptInLink", {query});
  }

  function highlightedExcerpt(text, query) {
    if (!query) return escapeHtml(text);
    const words = query.trim().split(/\s+/).filter(Boolean);
    if (!words.length) return escapeHtml(text);

    // Escape regex characters
    const escaped = words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const regex = new RegExp(`(${escaped.join("|")})`, "gi");

    const parts = text.split(regex);
    const locale = currentLanguage === "en" ? "en-US" : "tr-TR";
    return parts
      .map((part) => {
        if (words.some((w) => part.toLocaleLowerCase(locale) === w.toLocaleLowerCase(locale))) {
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
      const label = theme === "dark" ? t("themeLight") : t("themeDark");
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

    let svg = `<svg class="chart-svg" viewBox="0 0 ${svgWidth} ${svgHeight}" role="img" aria-label="${escapeHtml(t("chartAria"))}">`;

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
          <title>${escapeHtml(t("chartTitle", {year: yr, count: formatNumber(count)}))}</title>
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

      const translated = localizedItem(item);
      if (currentLanguage === "en" && !translated) return false;

      // If no text query, match all within year filter
      if (!normQuery) {
        return year && year !== "Tümü";
      }

      // 2. Query matching
      const normTitle = normalizeForMatch(currentLanguage === "en" ? translated.title : item.baslik);
      const normContent = normalizeForMatch(currentLanguage === "en" ? (translated.content || translated.summary) : item.icerik);
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
      const topic = currentLanguage === "en" ? btn.getAttribute("data-topic-en") : btn.getAttribute("data-topic");
      btn.classList.toggle("active", topic.toLocaleLowerCase("tr-TR") === query.toLocaleLowerCase("tr-TR"));
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
      const yearText = year !== "Tümü"
        ? (currentLanguage === "en" ? ` in ${year}` : ` ${year} yılında`)
        : "";
      const emptyMessage = !query && year !== "Tümü"
        ? t("noYearResults", {year})
        : t("noResults", {query: query || year, year: yearText});
      statusContainer.innerHTML = `
        <div class="app-status">${escapeHtml(emptyMessage)}</div>
      `;
      return;
    }

    statusContainer.innerHTML = "";
    resultsContent.style.display = "block";

    // Summary
    const distinctIssues = new Set(currentResults.map((r) => r.bulten)).size;
    resultSummary.textContent = t("resultsSummary", {
      articles: formatNumber(currentResults.length),
      issues: formatNumber(distinctIssues),
    });

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
        const translated = localizedItem(item);
        const cleanIssue = currentLanguage === "en" ? issueName(item) : item.bulten;
        const title = currentLanguage === "en" ? translated.title : item.baslik;
        const translatedContent = currentLanguage === "en" ? (translated.content || translated.summary) : "";
        const body = currentLanguage === "en"
          ? (activeQuery ? translatedContent : translated.summary)
          : cleanVisualLines(item.icerik);
        const excerpt = currentLanguage === "en"
          ? (activeQuery ? matchingExcerpt(title, translatedContent, activeQuery) : body)
          : matchingExcerpt(title, body, activeQuery);
        const highlighted = highlightedExcerpt(excerpt, activeQuery);
        const relParagraphs = currentLanguage === "en" ? [] : matchingParagraphs(body, activeQuery);

        // Citation
        const cleanTitle = (item.baslik || "").replace(/[*_#`]/g, "").trim();
        const citation = currentLanguage === "en"
          ? `Turkish Typography Society. (${cleanIssue}). ${cleanTitle}. Typography Newsletter. ${item.url || ""}`
          : `Türkçe Tipografi Topluluğu. (${item.yil || ""}, ${item.ay || ""}). ${cleanTitle}. Tipografi Bülteni. ${item.url || ""}`;
        const citationSafe = escapeHtml(citation);

        const paragraphsBlock = relParagraphs.length > 0
          ? `
            <details class="card-expander">
              <summary class="card-summary">${escapeHtml(t("relevantParagraphs"))}</summary>
              <div class="card-expander-body">
                ${relParagraphs.map(formatMarkdownParagraph).join("")}
              </div>
            </details>
          `
          : "";

        return `
          <article class="result-card" data-id="${item.id}">
            <div class="result-meta">
              <strong>${escapeHtml(currentLanguage === "en" ? cleanIssue.toLocaleUpperCase("en-US") : turkishUpper(cleanIssue))}</strong>
            </div>
            <h3>${escapeHtml(title)}</h3>
            ${currentLanguage === "en" ? `<div class="section-eyebrow summary-eyebrow">${escapeHtml(t(hasEnglishIssue(item) ? "translationLabel" : "summaryLabel"))}</div>` : ""}
            <p class="result-excerpt">${highlighted}</p>
            ${currentLanguage === "en" && hasEnglishIssue(item) ? `<a href="${escapeHtml(englishIssueUrl(item))}" class="result-issue-link result-issue-link--translated">${escapeHtml(t("readEnglishIssue"))}</a>` : ""}
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer" class="result-issue-link">${escapeHtml(t("readIssue"))}</a>
            ${paragraphsBlock}
            <details class="card-expander">
              <summary class="card-summary">${escapeHtml(t("originalIssue"))}</summary>
              <div class="card-expander-body">
                <div class="citation-row">
                  <div class="citation-box">${citationSafe}</div>
                  <button type="button" class="citation-copy-btn" data-citation="${citationSafe}" aria-label="${escapeHtml(t("citationCopyAria"))}">${escapeHtml(t("copy"))}</button>
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
      pageLabel.textContent = t("pageLabel", {page: currentPage, total: totalPages});
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
      btn.textContent = t("copied");
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = origText;
        btn.classList.remove("copied");
      }, 2000);
    }).catch(() => {
      // Fallback
      btn.textContent = t("copied");
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = t("copy");
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

    if (languageToggle) {
      languageToggle.addEventListener("click", (event) => {
        const link = event.target.closest("a[id^='language-']");
        if (!link) return;
        event.preventDefault();
        const nextLanguage = link.id === "language-en" ? "en" : "tr";
        const currentUrl = new URL(window.location.href);
        let rootPath = currentUrl.pathname;
        if (/(^|\/)en(?:\/|$)/.test(rootPath)) rootPath = rootPath.replace(/en(?:\/index\.html)?\/?$/, "");
        if (!rootPath.endsWith("/")) rootPath += "/";
        const url = new URL(`${rootPath}${nextLanguage === "en" ? "en/" : ""}`, currentUrl.origin);
        const query = searchInput.value.trim();
        if (query) url.searchParams.set("q", query);
        const year = yearSelect.value;
        if (year && year !== "Tümü") url.searchParams.set("yil", year);
        const theme = currentUrl.searchParams.get("theme");
        if (theme) url.searchParams.set("theme", theme);
        window.location.assign(url.toString());
      });
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
        const topic = currentLanguage === "en" ? btn.getAttribute("data-topic-en") : btn.getAttribute("data-topic");
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
      statusContainer.innerHTML = `<div class="app-status">${escapeHtml(t("loading"))}</div>`;
      const [response, translationsResponse, issueManifestResponse] = await Promise.all([
        fetch("arsiv.json"),
        fetch("arsiv-en.json"),
        fetch("issues-en.json").catch(() => null),
      ]);
      if (!response.ok || !translationsResponse.ok) {
        throw new Error(`HTTP ${!response.ok ? response.status : translationsResponse.status}`);
      }
      const data = await response.json();
      const translationsData = await translationsResponse.json();
      const issueManifest = issueManifestResponse && issueManifestResponse.ok
        ? await issueManifestResponse.json()
        : {issues: []};
      archiveData = data.items || [];
      englishTranslations = translationsData.items || {};
      englishIssueKeys = new Set((issueManifest.issues || []).map((issue) => `${issue.year}-${issue.month}`));
      translationsLoaded = true;
      archiveStats = data.stats || {};

      applyLanguage();

      // Populate Year Select
      if (archiveStats.years && yearSelect) {
        yearSelect.innerHTML = `<option value="Tümü">${escapeHtml(t("allYears"))}</option>` +
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
        <div class="app-status app-status--error">${escapeHtml(t("loadError"))} (${escapeHtml(err.message)})</div>
      `;
    }
  }

  // Public Interface for Inline form onsubmit
  window.ArchiveApp = {
    handleSearchSubmit,
  };

  // Start
  document.addEventListener("DOMContentLoaded", () => {
    applyLanguage();
    updateThemeUI(getActiveTheme());
    initEvents();
    loadArchiveData();
  });
})();
