// Base path của toàn bộ file tĩnh
const MISUI_BASE = (window.MISUI_BASE || "/static/mis-ui/");

const { useState, useEffect } = React;

/* ===== ICONS (GIỮ NGUYÊN) ===== */
function IconHome() {
  return (
    <svg viewBox="0 0 24 24" className="nav-svg">
      <path
        d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-5h-5v5H5a1 1 0 0 1-1-1v-9.5Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
function IconNews() {
  return (
    <svg viewBox="0 0 24 24" className="nav-svg">
      <rect x="4" y="5" width="14" height="14" rx="2" />
      <path d="M8 9h4M8 13h6M18 8v9a1 1 0 0 0 1 1h1" strokeLinecap="round" />
    </svg>
  );
}
function IconStructure() {
  return (
    <svg viewBox="0 0 24 24" className="nav-svg">
      <path d="M5 5h4v4H5zM15 5h4v4h-4zM10 15h4v4h-4z" />
      <path d="M9 7h6M12 9v4" strokeLinecap="round" />
    </svg>
  );
}
function IconStudy() {
  return (
    <svg viewBox="0 0 24 24" className="nav-svg">
      <path d="M4 7h16v10H4z" />
      <path d="M9 17v2.5M15 17v2.5" strokeLinecap="round" />
      <path d="M7 4.5h10" strokeLinecap="round" />
    </svg>
  );
}
function IconMoney() {
  return (
    <svg viewBox="0 0 24 24" className="nav-svg">
      <path d="M5 8h14v10H5z" />
      <circle cx="12" cy="13" r="2.8" />
      <path d="M8 5h8" strokeLinecap="round" />
    </svg>
  );
}

/* ===== SIDEBAR DATA (GIỮ NGUYÊN) ===== */
const SIDEBAR_ITEMS = [
  { icon: <IconHome />, label: "Trang chủ", key: "home" },
  { icon: <IconNews />, label: "Tin tức", key: "news" },
  {
    icon: <IconStructure />,
    label: "Cơ cấu",
    key: "structure",
    children: [
      { label: "School", key: "structure-school" },
      { label: "Faculty", key: "structure-faculty" },
      { label: "Lecture", key: "structure-lecture" },
    ],
  },
  {
    icon: <IconStudy />,
    label: "Góc học tập",
    key: "study",
    children: [
      { label: "Major", key: "study-major" },
      { label: "Course", key: "study-course" },
      { label: "Curriculum", key: "study-curriculum" },
    ],
  },
  {
    icon: <IconMoney />,
    label: "Tài chính",
    key: "finance",
    children: [{ label: "Học phí", key: "finance-fee" }],
  },
];

/* ===== TRANG → FILE HTML (GIỮ NGUYÊN) ===== */
// Nếu file bạn dùng PAGE_URLS:
const PAGE_URLS = {
  home: MISUI_BASE + "home/home.html",
  news: MISUI_BASE + "news/news.html",

  "structure-school":  MISUI_BASE + "structure/school.html",
  "structure-faculty": MISUI_BASE + "structure/faculty.html",
  "structure-lecture": MISUI_BASE + "structure/lecture.html",

  "study-major":      MISUI_BASE + "study/major.html",
  "study-course":     MISUI_BASE + "study/course.html",
  "study-curriculum": MISUI_BASE + "study/curriculum.html",

  "finance-fee": MISUI_BASE + "finance/tuition.html",
};

/* ===== TRANG → CSS/JS RIÊNG (MỚI) ===== */
const PAGE_ASSETS = {
  home: { css: [MISUI_BASE + "home/home.css?v=3"], js: [MISUI_BASE + "home/home.js?v=3"] },
  news: { css: [MISUI_BASE +"news/news.css?v=3"], js: [MISUI_BASE +"news/news.js?v=3"] },

  "structure-school":  { css: [MISUI_BASE + "structure/school.css"],   js: [MISUI_BASE + "structure/school.js"] },
  "structure-faculty": { css: [MISUI_BASE +"structure/faculty.css"],  js: [MISUI_BASE +"structure/faculty.js"] },
  "structure-lecture": { css: [MISUI_BASE +"structure/lecture.css?v=11"],  js: [MISUI_BASE +"structure/lecture.js?v=11"] },

  "study-major":      { css: [MISUI_BASE +"study/major.css"],      js: [MISUI_BASE +"study/major.js"] },
  "study-course":     { css: [MISUI_BASE +"study/course.css"],     js: [MISUI_BASE +"study/course.js"] },
  "study-curriculum": { css: [MISUI_BASE +"study/curriculum.css?v=20"], js: [MISUI_BASE +"study/curriculum.js?v=20"] },

  "finance-fee": { css: [MISUI_BASE +"finance/tuition.css?v=3"], js: [MISUI_BASE +"finance/tuition.js?v=1"] },
};

/* ===== HELPER NẠP/DỠ TÀI NGUYÊN (KHÔNG ĐỤNG SIDEBAR/TOPBAR) ===== */
function unloadAssets(prevKey) {
  if (!prevKey) return;
  document.querySelectorAll(`[data-page-asset="${prevKey}"]`).forEach((el) => el.remove());
}

function ensureCSSLoaded(key) {
  const assets = PAGE_ASSETS[key];
  if (!assets?.css) return;
  assets.css.forEach((href) => {
    // tránh trùng lặp theo data-attr
    const exists = document.querySelector(`link[rel="stylesheet"][data-page-asset="${key}"][href="${href}"]`);
    if (exists) return;
    const el = document.createElement("link");
    el.rel = "stylesheet";
    el.href = href;
    el.dataset.pageAsset = key;
    document.head.appendChild(el);
  });
}

function loadJSForKey(key) {
  const assets = PAGE_ASSETS[key];
  if (!assets?.js || assets.js.length === 0) return Promise.resolve();
  return Promise.all(
    assets.js.map(
      (src) =>
        new Promise((resolve, reject) => {
          const exists = document.querySelector(`script[data-page-asset="${key}"][src="${src}"]`);
          if (exists) return resolve();
          const s = document.createElement("script");
          s.src = src;
          s.async = false; // giữ thứ tự
          s.dataset.pageAsset = key;
          s.onload = resolve;
          s.onerror = () => reject(new Error("Load failed: " + src));
          document.body.appendChild(s);
        })
    )
  );
}

/* ===== TIỆN ÍCH ===== */
function isParentActive(itemKey, currentKey) {
  if (!currentKey) return false;
  return currentKey.startsWith(itemKey + "-");
}

/* ===== SIDEBAR (GIỮ NGUYÊN MARKUP + ICON SVG) ===== */
function Sidebar({ openMenu, currentKey, onTopClick, onSubClick }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">P</div>
        <div className="brand-title">
          <strong>PHENIKAA</strong>
          <small>University</small>
        </div>
      </div>

      <div className="nav-section-title">Chức năng</div>

      {SIDEBAR_ITEMS.map((item) => {
        const hasChildren = !!item.children;
        const open = openMenu === item.key;
        const parentIsActive = isParentActive(item.key, currentKey);

        return (
          <div key={item.key}>
            <div
              className={`nav-item ${open || parentIsActive || currentKey === item.key ? "active" : ""}`}
              onClick={() => onTopClick(item, hasChildren)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
              {hasChildren && <span className="chevron"></span>}
            </div>

            {hasChildren && (open || parentIsActive) && (
              <ul className="submenu">
                {item.children.map((child) => (
                  <li
                    key={child.key}
                    className={`submenu-item ${currentKey === child.key ? "active" : ""}`}
                    onClick={() => onSubClick(child.key)}
                  >
                    {child.label}
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </aside>
  );
}

/* ===== TOPBAR (GIỮ NGUYÊN) ===== */
function Topbar() {
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // 1) Ưu tiên đọc JSON nhúng sẵn trong HTML
    const tag = document.getElementById("__USER");
    if (tag && tag.textContent) {
      try {
        const u = JSON.parse(tag.textContent);
        if (u && (u.id || u.username)) {
          setUser(u);
          setLoading(false);
          return;
        }
      } catch (e) {
        console.warn("USER json parse error:", e);
      }
    }

    // 2) Fallback: gọi API /api/whoami nếu có
    fetch("/api/whoami", { credentials: "same-origin" })
      .then(r => (r.ok ? r.json() : null))
      .then(data => {
        if (data && data.ok && data.user) setUser(data.user);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function initials(name) {
    if (!name) return "U";
    return name
      .split(/\s+/)
      .filter(Boolean)
      .slice(-2)
      .map(s => s[0]?.toUpperCase() || "")
      .join("") || "U";
  }

  return (
    <div className="topbar">
      <div className="search-box">
        🔍 <input placeholder="Tìm kiếm thông tin" />
      </div>

      {/* Bên phải */}
      <div className="user-block">
        {/* Chưa lấy xong trạng thái: giữ chỗ */}
        {loading ? (
          <button className="btn ghost" disabled>Đang kiểm tra…</button>
        ) : user ? (
          // ĐÃ đăng nhập → hiển thị tên + avatar, click vào sẽ mở /admin/
          <button className="user-btn" onClick={() => (window.location.href = "/admin/")}>
            <div className="user-meta">
              <div className="user-name">{user.full_name || user.name || user.username}</div>
              <div className="user-role">{user.role_label || user.role || (user.is_staff ? "Cán bộ" : "Sinh viên")}</div>
            </div>
            <div className="avatar">{initials(user.full_name || user.name || user.username)}</div>
          </button>
        ) : (
          // CHƯA đăng nhập → nút đăng nhập
          <a className="btn primary" href="/admin/login/?next=/">
            Đăng nhập
          </a>
        )}
      </div>
    </div>
  );
}


/* ===== APP ===== */
function App() {
  const [openMenu, setOpenMenu] = useState("structure");
  const [currentKey, setCurrentKey] = useState("home");
  const [htmlContent, setHtmlContent] = useState("");
  const prevKeyRef = React.useRef(null);

  // tải nội dung + nạp CSS/JS theo currentKey
  useEffect(() => {
    const url = PAGE_URLS[currentKey];
    if (!url) {
      setHtmlContent("<p>Không tìm thấy trang.</p>");
      return;
    }

    // dỡ asset của trang trước, nạp CSS trang mới
    unloadAssets(prevKeyRef.current);
    ensureCSSLoaded(currentKey);

    let cancelled = false;

    fetch(url, { cache: "no-store" })
      .then((res) => res.text())
      .then((text) => {
        if (cancelled) return;

        // lấy phần <body> nếu có
        const bodyMatch = text.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
        const html = bodyMatch ? bodyMatch[1] : text;

        setHtmlContent(html);
        // nạp JS của trang sau khi DOM đã gắn
        return loadJSForKey(currentKey);
      })
      .then(() => {
        if (cancelled) return;
        // phát sự kiện để JS trang hook vào
        window.dispatchEvent(new CustomEvent("misui:page-mounted", { detail: { key: currentKey } }));
      })
      .catch(() => {
        if (!cancelled) setHtmlContent("<p style='color:#b91c1c'>Lỗi tải trang.</p>");
      });

    prevKeyRef.current = currentKey;
    return () => {
      cancelled = true;
    };
  }, [currentKey]);

  // click menu cha
  const handleTopClick = (item, hasChildren) => {
    if (hasChildren) {
      setOpenMenu((prev) => (prev === item.key ? null : item.key));
    } else {
      setCurrentKey(item.key);
    }
  };

  // click menu con
  const handleSubClick = (subKey) => {
    setCurrentKey(subKey);
  };

  return (
    <div className="app-shell">
      <Sidebar
        openMenu={openMenu}
        currentKey={currentKey}
        onTopClick={handleTopClick}
        onSubClick={handleSubClick}
      />
      <div className="main-area">
        <Topbar />
        <div className="content-wrapper">
          <div className="page-title">{currentKey}</div>
          <div className="panel" dangerouslySetInnerHTML={{ __html: htmlContent }}></div>
        </div>
      </div>
    </div>
  );
}

/* ===== MOUNT ===== */
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
