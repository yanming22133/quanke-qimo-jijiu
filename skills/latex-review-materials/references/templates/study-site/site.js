// 章节清单：id 必须唯一，file 为相对于 index.html 的路径。
const units = [
  {
    id: '1',
    badge: '第 1 章',
    title: '第一章 示例章节',
    file: 'unit/1.html',
    icon: '01',
    stars: '★★★★★ 核心重点',
    core: true,
    desc: '演示 Markdown 模板的分栏、星级卡片、列表、高亮、表格、Mermaid 流程图、单题自测与默写模式。'
  }
];

const STORAGE_KEY = 'course_review_progress_v1';
const sidebar = document.querySelector('#sidebar');
const nav = document.querySelector('#navList');
const welcome = document.querySelector('#welcome');
const wrap = document.querySelector('#frameWrap');
const frame = document.querySelector('#frame');
const mobile = document.querySelector('#mobileToggle');
const collapse = document.querySelector('#collapse');
const chapterGrid = document.querySelector('#chapterGrid');
const progressText = document.querySelector('#progressText');
const progressFill = document.querySelector('#progressFill');

function getReviewed() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

function setReviewedMap(map) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {}
}

function updateProgressUI() {
  const reviewed = getReviewed();
  const doneCount = units.filter(u => reviewed[u.id]).length;
  if (progressText) progressText.textContent = `${doneCount}/${units.length}`;
  if (progressFill) progressFill.style.width = `${units.length ? Math.round((doneCount / units.length) * 100) : 0}%`;

  nav.querySelectorAll('[data-id]').forEach(btn => {
    btn.classList.toggle('reviewed', !!reviewed[btn.dataset.id]);
  });
  chapterGrid.querySelectorAll('[data-card-id]').forEach(card => {
    const isDone = !!reviewed[card.dataset.cardId];
    card.classList.toggle('reviewed', isDone);
    const status = card.querySelector('.status-tag');
    if (status) status.textContent = isDone ? '✓ 已复习' : '进入学习 →';
  });
}

function buildNav() {
  nav.innerHTML = '';

  const homeBtn = document.createElement('button');
  homeBtn.type = 'button';
  homeBtn.className = 'nav-item';
  homeBtn.dataset.home = 'true';
  homeBtn.innerHTML = `
    <span class="nav-icon">🏠</span>
    <span class="nav-text-wrap">
      <span class="nav-text">总览主页</span>
    </span>
  `;
  homeBtn.addEventListener('click', () => selectUnit(null, true));
  nav.appendChild(homeBtn);

  units.forEach(u => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'nav-item';
    b.dataset.id = u.id;
    b.title = `${u.title}（${u.stars}）`;
    b.innerHTML = `
      <span class="nav-icon">${u.icon}</span>
      <span class="nav-text-wrap">
        <span class="nav-text">${u.title}</span>
        <span class="nav-stars ${u.core ? 'core' : ''}">${u.stars}</span>
      </span>
      <span class="nav-done-dot" title="已复习">✓</span>
    `;
    b.addEventListener('click', () => selectUnit(u.id, true));
    nav.appendChild(b);
  });
}

function buildWelcomeCards() {
  chapterGrid.innerHTML = '';
  units.forEach(u => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = `chapter-card ${u.core ? 'is-core' : ''}`;
    card.dataset.cardId = u.id;
    card.innerHTML = `
      <div class="chapter-card-top">
        <span class="ch-badge">${u.badge}</span>
        <span class="ch-stars ${u.stars.startsWith('★★★★★') ? 'five' : ''}">${u.stars}</span>
      </div>
      <h4>${u.title}</h4>
      <p>${u.desc}</p>
      <div class="chapter-card-foot">
        <span class="status-tag">进入学习 →</span>
      </div>
    `;
    card.addEventListener('click', () => selectUnit(u.id, true));
    chapterGrid.appendChild(card);
  });
}

function selectUnit(id, push = false) {
  const unit = units.find(u => u.id === id);
  welcome.style.display = unit ? 'none' : 'block';
  wrap.classList.toggle('active', !!unit);

  nav.querySelectorAll('.nav-item').forEach(b => {
    if (b.dataset.home) {
      b.classList.toggle('active', !unit);
    } else {
      b.classList.toggle('active', !!unit && b.dataset.id === unit.id);
    }
  });

  if (unit) {
    if (frame.getAttribute('src') !== unit.file) {
      frame.src = unit.file;
    }
    frame.title = unit.title;
  }

  if (push) {
    try {
      const url = new URL(location.href);
      unit ? url.searchParams.set('unit', unit.id) : url.searchParams.delete('unit');
      history.pushState(null, '', url);
    } catch {}
  }

  sidebar.classList.remove('open');
  mobile.setAttribute('aria-expanded', 'false');
}

document.querySelectorAll('[data-jump]').forEach(btn => {
  btn.addEventListener('click', () => selectUnit(btn.dataset.jump, true));
});

mobile.addEventListener('click', () => {
  const open = sidebar.classList.toggle('open');
  mobile.setAttribute('aria-expanded', String(open));
});

collapse.addEventListener('click', () => {
  const closed = sidebar.classList.toggle('collapsed');
  collapse.setAttribute('aria-expanded', String(!closed));
  try {
    localStorage.setItem('studySidebarCollapsed', String(closed));
  } catch {}
});

try {
  if (localStorage.getItem('studySidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
  }
} catch {}
collapse.setAttribute('aria-expanded', String(!sidebar.classList.contains('collapsed')));

window.addEventListener('message', e => {
  if (e.data && e.data.type === 'strategy-review-toggle') {
    const map = getReviewed();
    map[e.data.unitId] = !!e.data.reviewed;
    setReviewedMap(map);
    updateProgressUI();
  } else if (e.data && e.data.type === 'strategy-jump') {
    selectUnit(e.data.unitId, true);
  }
});

window.addEventListener('storage', e => {
  if (e.key === STORAGE_KEY) updateProgressUI();
});

window.addEventListener('popstate', () => {
  selectUnit(new URLSearchParams(location.search).get('unit'), false);
});

buildNav();
buildWelcomeCards();
updateProgressUI();
selectUnit(new URLSearchParams(location.search).get('unit'), false);
