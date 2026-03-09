import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import {
  getApiRoot,
  getDashboardAggregates,
  getHealthStatus,
  getSourceSystems,
} from "./api/resources";
import { useApiRequest } from "./hooks/useApiRequest";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api (same-origin proxy)";
const dashboardStatuses = [
  { key: "new", label: "New", accentClass: "status-accent-new" },
  { key: "accepted", label: "Accepted", accentClass: "status-accent-accepted" },
  { key: "in_progress", label: "In Progress", accentClass: "status-accent-progress" },
  { key: "completed", label: "Completed", accentClass: "status-accent-completed" },
  { key: "rejected", label: "Rejected", accentClass: "status-accent-rejected" },
];

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
    summaryTitle: "Backend health preview",
    requestFactory: getHealthStatus,
    renderData(data) {
      return (
        <div className="summary-stack">
          <p className="summary-kicker">Service status</p>
          <p className="summary-value">{data.status}</p>
        </div>
      );
    },
  },
  {
    path: "/stages",
    navLabel: "Elaboration",
    eyebrow: "Elaboration Route",
    title: "Detailed stage review will be built here",
    description:
      "The elaboration route is ready for the next tasks that will add the list view, filters, and the editing form.",
    summaryTitle: "Available source systems",
    requestFactory: getSourceSystems,
    renderData(data) {
      return (
        <ul className="data-list">
          {data.map((sourceSystem) => (
            <li key={sourceSystem.id} className="data-list-item">
              <span className="data-label">{sourceSystem.name}</span>
              <span className="data-value">{sourceSystem.base_url}</span>
            </li>
          ))}
        </ul>
      );
    },
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

function DashboardPage() {
  const { data, error, isLoading, reload } = useApiRequest(getDashboardAggregates, []);

  const totals = data
    ? {
        total: Object.values(data).reduce((sum, value) => sum + value, 0),
        active: (data.new || 0) + (data.accepted || 0) + (data.in_progress || 0),
        completedRate:
          Object.values(data).reduce((sum, value) => sum + value, 0) > 0
            ? Math.round(((data.completed || 0) / Object.values(data).reduce((sum, value) => sum + value, 0)) * 100)
            : 0,
      }
    : null;

  return (
    <main className="page-content">
      <section className="dashboard-hero">
        <div className="dashboard-copy">
          <p className="eyebrow">Dashboard</p>
          <h1>Idea funnel at a glance</h1>
          <p className="body">
            Track the full flow from raw opportunities to completed evaluations, then jump
            straight into the next action.
          </p>
          <div className="cta-row">
            <Link className="primary-link" to="/filter">
              Start quick filter
            </Link>
            <Link className="secondary-link" to="/stages">
              Open elaboration workspace
            </Link>
          </div>
        </div>
        <aside className="dashboard-side">
          <div className="spotlight-card">
            <p className="spotlight-label">API base</p>
            <p className="spotlight-value">{apiBaseUrl}</p>
          </div>
          <div className="spotlight-card">
            <p className="spotlight-label">Pipeline focus</p>
            <p className="spotlight-copy">
              Prioritize accepted ideas and push in-progress research toward completion.
            </p>
          </div>
        </aside>
      </section>

      <section className="summary-card">
        <div className="summary-header">
          <div>
            <p className="summary-label">Live aggregates</p>
            <h3 className="summary-title">Funnel overview</h3>
          </div>
          <button className="ghost-button" type="button" onClick={reload}>
            Reload
          </button>
        </div>

        {isLoading ? (
          <div className="request-state request-state-loading">
            <p className="request-state-title">Loading dashboard aggregates</p>
            <p className="request-state-copy">
              Waiting for the backend summary from `/api/dashboard/aggregates/`.
            </p>
          </div>
        ) : null}

        {!isLoading && error ? (
          <div className="request-state request-state-error">
            <p className="request-state-title">Dashboard request failed</p>
            <p className="request-state-copy">{error.message}</p>
          </div>
        ) : null}

        {!isLoading && !error && data ? (
          <>
            <div className="metric-grid">
              <article className="metric-card">
                <p className="metric-label">Total ideas</p>
                <p className="metric-value">{totals.total}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">Active pipeline</p>
                <p className="metric-value">{totals.active}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">Completion rate</p>
                <p className="metric-value">{totals.completedRate}%</p>
              </article>
            </div>

            <div className="funnel-grid">
              {dashboardStatuses.map((status) => (
                <article
                  key={status.key}
                  className={`funnel-card ${status.accentClass}`}
                >
                  <p className="funnel-label">{status.label}</p>
                  <p className="funnel-value">{data[status.key] ?? 0}</p>
                </article>
              ))}
            </div>
          </>
        ) : null}
      </section>

      <section className="summary-card">
        <div className="summary-header">
          <div>
            <p className="summary-label">Workflow entry points</p>
            <h3 className="summary-title">Choose the next move</h3>
          </div>
        </div>
        <div className="workflow-grid">
          <Link className="workflow-card" to="/filter">
            <span className="workflow-kicker">Quick Filter</span>
            <strong className="workflow-title">Sort new ideas fast</strong>
            <span className="workflow-copy">
              Review incoming ideas one by one and decide whether each item is worth
              keeping.
            </span>
          </Link>
          <Link className="workflow-card" to="/stages">
            <span className="workflow-kicker">Elaboration</span>
            <strong className="workflow-title">Deepen promising ideas</strong>
            <span className="workflow-copy">
              Move into detailed research, SEO validation, implementation planning, and
              completion.
            </span>
          </Link>
        </div>
      </section>

      <RequestSummary
        summaryTitle="API discovery"
        requestFactory={getApiRoot}
        renderData={(data) => (
          <ul className="data-list">
            {Object.entries(data).map(([key, value]) => (
              <li key={key} className="data-list-item">
                <span className="data-label">{key}</span>
                <span className="data-value">{value}</span>
              </li>
            ))}
          </ul>
        )}
      />
    </main>
  );
}

function RequestSummary({ summaryTitle, requestFactory, renderData }) {
  const { data, error, isLoading, reload } = useApiRequest(requestFactory, []);

  return (
    <section className="summary-card">
      <div className="summary-header">
        <div>
          <p className="summary-label">Backend preview</p>
          <h3 className="summary-title">{summaryTitle}</h3>
        </div>
        <button className="ghost-button" type="button" onClick={reload}>
          Reload
        </button>
      </div>

      {isLoading ? (
        <div className="request-state request-state-loading">
          <p className="request-state-title">Loading data from API</p>
          <p className="request-state-copy">
            Waiting for the backend response through the shared request hook.
          </p>
        </div>
      ) : null}

      {!isLoading && error ? (
        <div className="request-state request-state-error">
          <p className="request-state-title">Request failed</p>
          <p className="request-state-copy">{error.message}</p>
        </div>
      ) : null}

      {!isLoading && !error ? renderData(data) : null}
    </section>
  );
}

function RoutePage({ eyebrow, title, description, summaryTitle, requestFactory, renderData }) {
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
      <RequestSummary
        summaryTitle={summaryTitle}
        requestFactory={requestFactory}
        renderData={renderData}
      />
    </main>
  );
}

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {pages.filter((page) => page.path !== "/").map((page) => (
          <Route
            key={page.path}
            path={page.path}
            element={
              <RoutePage
                eyebrow={page.eyebrow}
                title={page.title}
                description={page.description}
                summaryTitle={page.summaryTitle}
                requestFactory={page.requestFactory}
                renderData={page.renderData}
              />
            }
          />
        ))}
      </Routes>
    </AppLayout>
  );
}
