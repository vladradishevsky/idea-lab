import { NavLink, Route, Routes, useLocation } from "react-router-dom";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "not configured";

const pages = [
  {
    path: "/",
    navLabel: "Dashboard",
    eyebrow: "Dashboard Route",
    title: "Idea pipeline overview will live here",
    description:
      "The dashboard route is ready. Next tasks will add aggregates, progress indicators, and navigation into the two working flows.",
  },
  {
    path: "/filter",
    navLabel: "Quick Filter",
    eyebrow: "Quick Filter Route",
    title: "Primary idea screening starts on this page",
    description:
      "The quick filter route is wired and ready for the upcoming card workflow with accept and reject actions.",
  },
  {
    path: "/stages",
    navLabel: "Elaboration",
    eyebrow: "Elaboration Route",
    title: "Detailed stage review will be built here",
    description:
      "The elaboration route is ready for the next tasks that will add the list view, filters, and the editing form.",
  },
];

function AppLayout({ children }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-block">
          <p className="brand-kicker">Idea Lab</p>
          <div>
            <h2 className="brand-title">Business idea review cockpit</h2>
            <p className="brand-subtitle">
              Navigate the workflow from dashboard to screening and detailed elaboration.
            </p>
          </div>
        </div>
        <nav className="app-nav" aria-label="Primary">
          {pages.map((page) => (
            <NavLink
              key={page.path}
              to={page.path}
              className={({ isActive }) => (isActive ? "nav-link is-active" : "nav-link")}
              end={page.path === "/"}
            >
              {page.navLabel}
            </NavLink>
          ))}
        </nav>
      </header>
      {children}
    </div>
  );
}

function RoutePage({ eyebrow, title, description }) {
  const location = useLocation();

  return (
    <main className="page-content">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="body">{description}</p>
        </div>
        <dl className="status-list">
          <div className="status-item">
            <dt>Current route</dt>
            <dd>{location.pathname}</dd>
          </div>
          <div className="status-item">
            <dt>Frontend status</dt>
            <dd>Shared layout and primary navigation are now enabled</dd>
          </div>
          <div className="status-item">
            <dt>Backend API base URL</dt>
            <dd>{apiBaseUrl}</dd>
          </div>
        </dl>
      </section>
    </main>
  );
}

export default function App() {
  return (
    <AppLayout>
      <Routes>
        {pages.map((page) => (
          <Route
            key={page.path}
            path={page.path}
            element={
              <RoutePage
                eyebrow={page.eyebrow}
                title={page.title}
                description={page.description}
              />
            }
          />
        ))}
      </Routes>
    </AppLayout>
  );
}
