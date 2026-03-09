import { Route, Routes, useLocation } from "react-router-dom";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "not configured";

const pages = [
  {
    path: "/",
    eyebrow: "Dashboard Route",
    title: "Idea pipeline overview will live here",
    description:
      "The dashboard route is ready. Next tasks will add aggregates, progress indicators, and navigation into the two working flows.",
  },
  {
    path: "/filter",
    eyebrow: "Quick Filter Route",
    title: "Primary idea screening starts on this page",
    description:
      "The quick filter route is wired and ready for the upcoming card workflow with accept and reject actions.",
  },
  {
    path: "/stages",
    eyebrow: "Elaboration Route",
    title: "Detailed stage review will be built here",
    description:
      "The elaboration route is ready for the next tasks that will add the list view, filters, and the editing form.",
  },
];

function RoutePage({ eyebrow, title, description }) {
  const location = useLocation();

  return (
    <main className="app-shell">
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
            <dd>Routing is enabled and the page is rendered through React Router</dd>
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
  );
}
