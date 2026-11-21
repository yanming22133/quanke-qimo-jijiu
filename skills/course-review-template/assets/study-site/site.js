// 章节清单：id 必须唯一，file 为相对于 index.html 的路径。
const units = [
  {
    id: '1',
    badge: '智库单栏',
    title: '① 现代财经智库风（Editorial）',
    file: 'unit/1.html',
    icon: '01',
    stars: '★★★★★ 默认卡片',
    core: true,
    desc: '经典顶部渐变大横幅 + 单栏左彩条星级卡片 + 暖象牙纸面，适合经管/金融/法学。'
  },
  {
    id: 'academic-book',
    badge: '专著讲义',
    title: '② 学术专著讲义风（Academic Book）',
    file: 'unit/theme-academic-book.html',
    icon: '02',
    stars: '★★★★★ 三线表+双栏',
    core: false,
    desc: '双细线居中扉页头 + 书签下划线分栏 + 学术三线表 + 宽屏双栏列表 + 全衬线排版。'
  },
  {
    id: 'bento-tech',
    badge: 'Bento看板',
    title: '③ 极简 Bento 科技看板风（Bento Tech）',
    file: 'unit/theme-bento-tech.html',
    icon: '03',
    stars: '★★★★ 多列便当网格',
    core: false,
    desc: '圆角悬浮顶栏 + 胶囊分段控制器 + 宽屏双列 Bento 网格 + 顶彩条卡片与等宽方块编号。'
  },
  {
    id: 'notion-minimal',
    badge: '无框笔记',
    title: '④ 极简 Notion 笔记流风（Notion Minimal）',
    file: 'unit/theme-notion-minimal.html',
    icon: '04',
    stars: '★★★★ 纯白文档流',
    core: false,
    desc: '彻底去除外框卡片，780px 黄金列宽纯白文档流 + 手账荧光笔划重点 + 极简文字导航。'
  },
  {
    id: 'night-terminal',
    badge: '暗夜仪表盘',
    title: '⑤ 暗夜终端专注风（Night Terminal）',
    file: 'unit/theme-night-terminal.html',
    icon: '05',
    stars: '★★★★★ 深夜护眼',
    core: true,
    desc: '深海暗色背景 + 胶囊发光导航 + 霓虹光晕暗色玻璃卡片 + 终端风代码块与护眼配色。'
  },
  {
    id: 'swiss-poster',
    badge: '瑞士海报',
    title: '⑥ 瑞士国际主义海报风（Swiss Poster）',
    file: 'unit/theme-swiss-poster.html',
    icon: '06',
    stars: '★★★★★ 红黑硬网格',
    core: true,
    desc: '包豪斯零圆角 2px 纯黑结构网格 + 瑞士红黑撞色块 + 超粗标题与反白条形小标。'
  },
  {
    id: 'cornell-notes',
    badge: '康奈尔笔记',
    title: '⑦ 康奈尔活页笔记风（Cornell Notes）',
    file: 'unit/theme-cornell-notes.html',
    icon: '07',
    stars: '★★★★★ 双区活页本',
    core: true,
    desc: '方格纸底纹 + 红色装订双竖线 + 宽屏左线索区(230px)/右笔记正文区真实康奈尔结构。'
  },
  {
    id: 'newspaper-broadsheet',
    badge: '财经大报',
    title: '⑧ 经典财经大报风（Broadsheet）',
    file: 'unit/theme-newspaper-broadsheet.html',
    icon: '08',
    stars: '★★★★ FT鲑鱼粉报刊',
    core: false,
    desc: 'FT 经典鲑鱼粉暖报纸底色 + 刊头双粗细线 + 无阴影社论分割版面 + 首字下沉排版。'
  },
  {
    id: 'neobrutalism',
    badge: '新粗野卡牌',
    title: '⑨ 新粗野主义卡牌风（Neo-Brutalism）',
    file: 'unit/theme-neobrutalism.html',
    icon: '09',
    stars: '★★★★★ 潮酷硬投影',
    core: true,
    desc: '点阵底纹 + 2.5px 粗黑框 + 6px 实心偏移硬投影 + 柠檬黄/珊瑚粉/电子青弹跳撞色卡牌。'
  },
  {
    id: 'chinese-ink',
    badge: '宋韵水墨',
    title: '⑩ 东方宋韵水墨书院风（Chinese Ink）',
    file: 'unit/theme-chinese-ink.html',
    icon: '10',
    stars: '★★★★ 宣纸朱砂印',
    core: false,
    desc: '宣纸留白渐变 + 朱砂方印星标 + 双细内框书院卡片 + 竹青浓墨全宋体典雅排版。'
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
