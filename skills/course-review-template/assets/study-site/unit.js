const STORAGE_KEY = 'strategy_study_reviewed_v1';

// Tab Switching
const tabs = document.querySelectorAll('.nav-tab');
const sections = document.querySelectorAll('.section');

function switchTab(targetId) {
  tabs.forEach(b => {
    const active = b.dataset.target === targetId;
    b.classList.toggle('active', active);
    b.setAttribute('aria-pressed', String(active));
  });
  sections.forEach(s => {
    s.classList.toggle('active', s.id === 'section-' + targetId);
  });
  renderVisibleMermaid();
  loadVisiblePdfs();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function loadVisiblePdfs() {
  document.querySelectorAll('.section.active iframe.pdf-viewer[data-src]').forEach(el => {
    if (!el.getAttribute('src')) {
      el.setAttribute('src', el.dataset.src);
    }
  });
}

// Offline Mermaid Rendering (renders visible sections cleanly)
if (window.mermaid) {
  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    theme: 'base',
    flowchart: {
      curve: 'basis',
      nodeSpacing: 26,
      rankSpacing: 46,
      padding: 12,
      useMaxWidth: true
    },
    themeVariables: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
      fontSize: '13px',
      primaryColor: '#e6f0ef',
      primaryTextColor: '#092627',
      primaryBorderColor: '#0f3d3e',
      lineColor: '#526063',
      secondaryColor: '#fef3c7',
      tertiaryColor: '#fef2f2'
    }
  });
}

function renderVisibleMermaid() {
  if (!window.mermaid) return;
  const nodes = Array.from(document.querySelectorAll('.section.active .mermaid:not([data-processed="true"])'));
  if (!nodes.length) return;
  window.mermaid.run({ nodes }).catch(() => {});
}

document.addEventListener('DOMContentLoaded', renderVisibleMermaid);
if (document.readyState !== 'loading') {
  renderVisibleMermaid();
}

tabs.forEach(button => {
  button.addEventListener('click', () => switchTab(button.dataset.target));
});

document.querySelectorAll('[data-switch-tab]').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.switchTab));
});

tabs.forEach(b => b.setAttribute('aria-pressed', String(b.classList.contains('active'))));

// Star Importance Filtering
const filterBtns = document.querySelectorAll('.filter-btn');
const kpCards = document.querySelectorAll('.kp-card[data-stars]');

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const minStars = Number(btn.dataset.min || 0);
    filterBtns.forEach(b => b.classList.toggle('active', b === btn));

    kpCards.forEach(card => {
      const stars = Number(card.dataset.stars || 0);
      card.classList.toggle('card-hidden', stars < minStars);
    });

    // Update empty messages per section
    sections.forEach(sec => {
      const msg = sec.querySelector('.empty-filter-msg');
      if (!msg) return;
      const secCards = sec.querySelectorAll('.kp-card[data-stars]');
      if (!secCards.length) return;
      const visibleCount = Array.from(secCards).filter(c => !c.classList.contains('card-hidden')).length;
      msg.style.display = visibleCount === 0 ? 'block' : 'none';
    });
  });
});

// Interactive Q&A Toggles
document.querySelectorAll('.qa-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const ans = btn.nextElementSibling;
    if (!ans) return;
    const open = ans.classList.toggle('open');
    btn.textContent = open ? '收起解析 ▲' : '查看参考答案与采分点 ▼';
  });
});

const toggleAllBtn = document.querySelector('#toggleAllAnswers');
if (toggleAllBtn) {
  let allOpen = false;
  toggleAllBtn.addEventListener('click', () => {
    allOpen = !allOpen;
    document.querySelectorAll('.qa-answer').forEach(ans => ans.classList.toggle('open', allOpen));
    document.querySelectorAll('.qa-toggle').forEach(btn => {
      btn.textContent = allOpen ? '收起解析 ▲' : '查看参考答案与采分点 ▼';
    });
    toggleAllBtn.textContent = allOpen ? '全部收起答案' : '全部展开答案';
  });
}

// Chapter Review Completion Sync
const reviewBtn = document.querySelector('#markReviewedBtn');
if (reviewBtn) {
  const unitId = document.body.dataset.unitId;
  const loadState = () => {
    try {
      const map = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return !!map[unitId];
    } catch {
      return false;
    }
  };

  const renderBtn = done => {
    reviewBtn.classList.toggle('done', done);
    reviewBtn.textContent = done ? '✓ 本章已标记为复习完成（点击取消）' : '☐ 标记本章已复习完成';
  };

  let isDone = loadState();
  renderBtn(isDone);

  reviewBtn.addEventListener('click', () => {
    isDone = !isDone;
    try {
      const map = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      map[unitId] = isDone;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
    } catch {}
    renderBtn(isDone);
    try {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({ type: 'strategy-review-toggle', unitId, reviewed: isDone }, '*');
      }
    } catch {}
  });
}

// Cross-unit jump buttons inside iframe
document.querySelectorAll('[data-jump-unit]').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.dataset.jumpUnit;
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'strategy-jump', unitId: targetId }, '*');
    }
  });
});

// 默写模式 (Cloze Recall Mode)
(function initReciteMode() {
  const navInner = document.querySelector('.nav-bar-inner');
  if (!navInner) return;

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'recite-btn';
  btn.id = 'reciteModeBtn';
  btn.setAttribute('aria-pressed', 'false');
  btn.textContent = '🧠 默写模式';

  const starFilter = navInner.querySelector('.star-filter');
  if (starFilter) {
    starFilter.appendChild(btn);
  } else {
    navInner.appendChild(btn);
  }

  let active = false;
  btn.addEventListener('click', () => {
    active = !active;
    document.body.classList.toggle('recite-mode', active);
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
    btn.textContent = active ? '👁️ 显示全部' : '🧠 默写模式';
    if (!active) {
      document.querySelectorAll('.page-wrap strong.revealed').forEach(el => el.classList.remove('revealed'));
    }
  });

  // Click any blurred <strong> to reveal/hide individually
  const pageWrap = document.querySelector('.page-wrap');
  if (pageWrap) {
    pageWrap.addEventListener('click', e => {
      if (!document.body.classList.contains('recite-mode')) return;
      const target = e.target.closest('.card strong, .qa-answer strong');
      if (!target) return;
      target.classList.toggle('revealed');
    });
  }
})();
