import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import {
  getApiRoot,
  getDashboardAggregates,
  getHealthStatus,
  getNextQuickFilterStage,
  getSourceSystems,
} from "./api/resources";
import { useApiRequest } from "./hooks/useApiRequest";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api (same-origin proxy)";
const dashboardStatuses = [
  { key: "new", label: "Новые", accentClass: "status-accent-new" },
  { key: "accepted", label: "Принятые", accentClass: "status-accent-accepted" },
  { key: "in_progress", label: "В работе", accentClass: "status-accent-progress" },
  { key: "completed", label: "Завершённые", accentClass: "status-accent-completed" },
  { key: "rejected", label: "Отклонённые", accentClass: "status-accent-rejected" },
];

const pages = [
  {
    path: "/",
    navLabel: "Дашборд",
    eyebrow: "Главная страница",
    title: "Обзор воронки идей будет здесь",
    description:
      "Маршрут главной страницы готов. Следующие задачи будут развивать агрегаты, визуализацию прогресса и рабочую навигацию по двум основным сценариям.",
  },
  {
    path: "/filter",
    navLabel: "Фильтрация",
    eyebrow: "Быстрая фильтрация",
    title: "Первичный отбор идей начинается на этой странице",
    description:
      "Маршрут быстрой фильтрации подключён и готов к следующему шагу: карточки идей с действиями принятия и отклонения.",
    summaryTitle: "Проверка состояния backend",
    requestFactory: getHealthStatus,
    renderData(data) {
      return (
        <div className="summary-stack">
          <p className="summary-kicker">Состояние сервиса</p>
          <p className="summary-value">{data.status}</p>
        </div>
      );
    },
  },
  {
    path: "/stages",
    navLabel: "Проработка",
    eyebrow: "Детальная проработка",
    title: "Подробная работа с идеями будет собрана здесь",
    description:
      "Маршрут проработки готов для следующих задач: список идей, фильтры и форма редактирования карточки.",
    summaryTitle: "Доступные источники",
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
            <h2 className="brand-title">Панель оценки бизнес-идей</h2>
            <p className="brand-subtitle">
              Переходи между дашбордом, первичной фильтрацией и детальной проработкой.
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
          <p className="eyebrow">Дашборд</p>
          <h1>Воронка идей одним взглядом</h1>
          <p className="body">
            Следи за полным потоком: от новых возможностей до завершённых карточек, а потом сразу переходи к следующему действию.
          </p>
          <div className="cta-row">
            <Link className="primary-link" to="/filter">
              Начать фильтрацию
            </Link>
            <Link className="secondary-link" to="/stages">
              Открыть проработку
            </Link>
          </div>
        </div>
        <aside className="dashboard-side">
          <div className="spotlight-card">
            <p className="spotlight-label">Базовый адрес API</p>
            <p className="spotlight-value">{apiBaseUrl}</p>
          </div>
          <div className="spotlight-card">
            <p className="spotlight-label">Фокус работы</p>
            <p className="spotlight-copy">
              Доводи принятые идеи до результата и вытягивай карточки в работе к завершению.
            </p>
          </div>
        </aside>
      </section>

      <section className="summary-card">
        <div className="summary-header">
          <div>
            <p className="summary-label">Живые агрегаты</p>
            <h3 className="summary-title">Сводка по воронке</h3>
          </div>
          <button className="ghost-button" type="button" onClick={reload}>
            Обновить
          </button>
        </div>

        {isLoading ? (
          <div className="request-state request-state-loading">
            <p className="request-state-title">Загружаем агрегаты дашборда</p>
            <p className="request-state-copy">
              Ждём сводку от backend по `/api/dashboard/aggregates/`.
            </p>
          </div>
        ) : null}

        {!isLoading && error ? (
          <div className="request-state request-state-error">
            <p className="request-state-title">Не удалось загрузить дашборд</p>
            <p className="request-state-copy">{error.message}</p>
          </div>
        ) : null}

        {!isLoading && !error && data ? (
          <>
            <div className="metric-grid">
              <article className="metric-card">
                <p className="metric-label">Всего идей</p>
                <p className="metric-value">{totals.total}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">Активный поток</p>
                <p className="metric-value">{totals.active}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">Доля завершённых</p>
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
            <p className="summary-label">Точки входа</p>
            <h3 className="summary-title">Выбери следующий шаг</h3>
          </div>
        </div>
        <div className="workflow-grid">
          <Link className="workflow-card" to="/filter">
            <span className="workflow-kicker">Быстрая фильтрация</span>
            <strong className="workflow-title">Быстро разобрать новые идеи</strong>
            <span className="workflow-copy">
              Просматривай входящие идеи по одной и сразу решай, стоит ли оставлять каждую в работе.
            </span>
          </Link>
          <Link className="workflow-card" to="/stages">
            <span className="workflow-kicker">Проработка</span>
            <strong className="workflow-title">Углубить перспективные идеи</strong>
            <span className="workflow-copy">
              Переходи к исследованию, SEO-проверке, планированию реализации и завершению карточки.
            </span>
          </Link>
        </div>
      </section>

      <RequestSummary
        summaryTitle="Обзор API"
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

function QuickFilterPage() {
  const { data, error, isLoading, reload } = useApiRequest(getNextQuickFilterStage, []);
  const nextStage = data?.results?.[0] ?? null;

  return (
    <main className="page-content">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">Быстрая фильтрация</p>
          <h1>Следующая идея для первичной оценки</h1>
          <p className="body">
            Страница уже подключена к списку идей и по умолчанию подбирает первую
            доступную карточку без отклонённых записей.
          </p>
        </div>
        <dl className="status-list">
          <div className="status-item">
            <dt>Источник данных</dt>
            <dd>GET /api/stages/?page_size=1</dd>
          </div>
          <div className="status-item">
            <dt>Правило по умолчанию</dt>
            <dd>Отклонённые идеи скрыты до отдельного фильтра из следующих задач</dd>
          </div>
          <div className="status-item">
            <dt>Базовый адрес backend API</dt>
            <dd>{apiBaseUrl}</dd>
          </div>
        </dl>
      </section>

      <section className="summary-card">
        <div className="summary-header">
          <div>
            <p className="summary-label">Следующая карточка</p>
            <h3 className="summary-title">Предпросмотр идеи для фильтрации</h3>
          </div>
          <button className="ghost-button" type="button" onClick={reload}>
            Обновить
          </button>
        </div>

        {isLoading ? (
          <div className="request-state request-state-loading">
            <p className="request-state-title">Загружаем следующую идею</p>
            <p className="request-state-copy">
              Получаем первую доступную запись из списка stages для сценария быстрой
              фильтрации.
            </p>
          </div>
        ) : null}

        {!isLoading && error ? (
          <div className="request-state request-state-error">
            <p className="request-state-title">Не удалось получить идею</p>
            <p className="request-state-copy">{error.message}</p>
          </div>
        ) : null}

        {!isLoading && !error && nextStage ? (
          <article className="quick-filter-card">
            <div className="quick-filter-header">
              <div>
                <p className="summary-kicker">Статус</p>
                <p className="quick-filter-status">{nextStage.status}</p>
              </div>
              <div className="quick-filter-meta">
                <span>ID #{nextStage.id}</span>
                <span>Источник #{nextStage.source_system_id}</span>
              </div>
            </div>
            <h2 className="quick-filter-title">{nextStage.title}</h2>
            <p className="quick-filter-description">
              {nextStage.description || "Описание пока не заполнено во входящих данных."}
            </p>
            <dl className="quick-filter-details">
              <div className="quick-filter-detail">
                <dt>Категория</dt>
                <dd>{nextStage.category || "Не указана"}</dd>
              </div>
              <div className="quick-filter-detail">
                <dt>Ссылка на источник</dt>
                <dd>
                  <a
                    className="inline-link"
                    href={nextStage.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {nextStage.source_url}
                  </a>
                </dd>
              </div>
            </dl>
          </article>
        ) : null}

        {!isLoading && !error && !nextStage ? (
          <div className="request-state request-state-loading">
            <p className="request-state-title">Идей для фильтрации пока нет</p>
            <p className="request-state-copy">
              Backend не вернул ни одной записи по текущему условию выборки.
            </p>
          </div>
        ) : null}
      </section>

      <RequestSummary
        summaryTitle="Проверка состояния backend"
        requestFactory={getHealthStatus}
        renderData={(data) => (
          <div className="summary-stack">
            <p className="summary-kicker">Состояние сервиса</p>
            <p className="summary-value">{data.status}</p>
          </div>
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
          <p className="summary-label">Данные backend</p>
          <h3 className="summary-title">{summaryTitle}</h3>
        </div>
        <button className="ghost-button" type="button" onClick={reload}>
          Обновить
        </button>
      </div>

      {isLoading ? (
        <div className="request-state request-state-loading">
          <p className="request-state-title">Загружаем данные из API</p>
          <p className="request-state-copy">
            Ждём ответ backend через общий request hook.
          </p>
        </div>
      ) : null}

      {!isLoading && error ? (
        <div className="request-state request-state-error">
          <p className="request-state-title">Запрос завершился ошибкой</p>
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
            <dt>Текущий маршрут</dt>
            <dd>{location.pathname}</dd>
          </div>
          <div className="status-item">
            <dt>Состояние frontend</dt>
            <dd>Общий layout и основная навигация уже подключены</dd>
          </div>
          <div className="status-item">
            <dt>Базовый адрес backend API</dt>
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
        <Route path="/filter" element={<QuickFilterPage />} />
        {pages.filter((page) => !["/", "/filter"].includes(page.path)).map((page) => (
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
