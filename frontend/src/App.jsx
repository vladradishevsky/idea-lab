const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "not configured";

export default function App() {
  return (
    <main className="app">
      <section className="card">
        <p className="eyebrow">Idea Lab</p>
        <h1>Frontend is ready for development</h1>
        <p className="body">
          React application started successfully and is ready to work with the backend API.
        </p>
        <dl className="status-list">
          <div className="status-item">
            <dt>Frontend status</dt>
            <dd>Build completed, Vite dev server is running</dd>
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
