import { useEffect, useMemo, useState } from 'react'
import { DATASETS, PROFILE, METRIC_SAMPLE } from './data'
import { uploadDataset } from './services/loadingApi'
import { fetchComparisonMetrics, fetchVersionMetrics } from './services/metricsApi'
import './App.css'

const cloneProfile = () => ({
  version: PROFILE.version,
  tag: PROFILE.tag,
  metrics: PROFILE.metrics.map((metric) => ({ ...metric })),
  blocks: PROFILE.blocks.map((block) => ({ ...block, items: [...block.items] })),
  charts: PROFILE.charts.map((chart) => ({ ...chart })),
  raw: ''
})

const formatValue = (value) => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const buildProfileData = (payload, fallbackVersion) => {
  const profile = cloneProfile()
  if (!payload) {
    return profile
  }

  const next = { ...profile, tag: 'метрики', version: fallbackVersion || profile.version }

  if (typeof payload === 'object' && payload !== null) {
    const entries = Object.entries(payload)
    const metrics = entries.slice(0, profile.metrics.length).map(([key, value]) => ({
      id: key,
      label: key,
      value: formatValue(value)
    }))

    next.metrics = metrics.length ? metrics : profile.metrics
    next.version = payload.version || fallbackVersion || profile.version
  } else {
    next.metrics = next.metrics.map((metric, index) =>
      index === 0 ? { ...metric, value: formatValue(payload) } : metric
    )
  }
  return next
}

const secondsToTime = (seconds) => {
  if (!seconds && seconds !== 0) return '—'
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${mins}м ${secs.toString().padStart(2, '0')}с`
}

const toPercent = (value) => {
  if (value === null || value === undefined) return '—'
  return `${(Number(value) * 100).toFixed(3)}%`
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('ru-RU')
}

const formatMetricValue = (key, value) => {
  if (value === null || value === undefined) return '—'
  const lower = key.toLowerCase()
  if (lower.includes('rate')) return toPercent(value)
  if (lower.includes('duration')) return secondsToTime(value)
  return formatNumber(value)
}

const METRIC_LABELS = {
  visits_count: 'Визиты',
  hits_count: 'Хиты',
  avg_visit_duration: 'Время визита',
  bounce_rate: 'Bounce rate',
  avg_page_views: 'Страниц за визит',
  avg_page_depth: 'Глубина просмотра'
}

function App() {
  const [datasets, setDatasets] = useState(() => {
    const saved = window?.localStorage?.getItem('datasets')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return DATASETS
      }
    }
    return DATASETS
  })
  const [uploadForm, setUploadForm] = useState({ version: '', hitsFile: null, visitsFile: null })
  const [uploadState, setUploadState] = useState({ status: 'idle', message: '' })
  const [metricsVersion, setMetricsVersion] = useState('')
  const [metricsState, setMetricsState] = useState({ status: 'idle', message: '' })
  const [profilePayload, setProfilePayload] = useState(null)
  const [compareForm, setCompareForm] = useState({ left: '', right: '' })
  const [compareState, setCompareState] = useState({ status: 'idle', message: '' })
  const [comparePayload, setComparePayload] = useState({ left: null, right: null })
  const [compareInsights, setCompareInsights] = useState(null)
  const [showCompareOverlay, setShowCompareOverlay] = useState(false)

  const profileData = buildProfileData(profilePayload, metricsVersion)
  const metricSource = profilePayload || METRIC_SAMPLE

  const metricCards = useMemo(() => {
    const items = [
      {
        id: 'visits',
        label: METRIC_LABELS.visits_count,
        value: formatNumber(metricSource?.visits_count),
        hint: 'visits_count',
        hidden: metricSource?.visits_count === null || metricSource?.visits_count === undefined
      },
      {
        id: 'hits',
        label: METRIC_LABELS.hits_count,
        value: formatNumber(metricSource?.hits_count),
        hint: 'hits_count',
        hidden:
          metricSource?.hits_count === null ||
          metricSource?.hits_count === undefined ||
          metricSource?.hits_count === 0
      },
      {
        id: 'duration',
        label: METRIC_LABELS.avg_visit_duration,
        value: secondsToTime(metricSource?.avg_visit_duration),
        hint: 'avg_visit_duration',
        hidden:
          metricSource?.avg_visit_duration === null || metricSource?.avg_visit_duration === undefined
      },
      {
        id: 'bounce',
        label: METRIC_LABELS.bounce_rate,
        value: toPercent(metricSource?.bounce_rate),
        hint: 'bounce_rate',
        hidden: !metricSource?.bounce_rate
      },
      {
        id: 'pages',
        label: METRIC_LABELS.avg_page_views,
        value: metricSource?.avg_page_views ? metricSource.avg_page_views.toFixed(2) : '—',
        hint: 'avg_page_views',
        hidden: !metricSource?.avg_page_views
      },
      {
        id: 'depth',
        label: METRIC_LABELS.avg_page_depth,
        value: metricSource?.avg_page_depth ? metricSource.avg_page_depth.toFixed(2) : '—',
        hint: 'avg_page_depth',
        hidden: !metricSource?.avg_page_depth
      }
    ]

    return items.filter((item) => !item.hidden)
  }, [metricSource])

  const metricBars = useMemo(() => {
    const raw = [
      { id: 'visits', label: METRIC_LABELS.visits_count, value: metricSource?.visits_count || 0 },
      { id: 'hits', label: METRIC_LABELS.hits_count, value: metricSource?.hits_count || 0 },
      {
        id: 'duration',
        label: METRIC_LABELS.avg_visit_duration,
        value: metricSource?.avg_visit_duration || 0
      },
      {
        id: 'bounce',
        label: METRIC_LABELS.bounce_rate,
        value: metricSource?.bounce_rate ? metricSource.bounce_rate * 100 : 0
      },
      {
        id: 'pages',
        label: METRIC_LABELS.avg_page_views,
        value: metricSource?.avg_page_views || 0
      }
    ]

    const filtered = raw.filter((item) => item.value && item.value > 0)
    const max = Math.max(...filtered.map((item) => item.value), 1)

    return filtered.map((item) => ({
      ...item,
      valueLabel:
        item.id === 'bounce'
          ? toPercent(metricSource?.bounce_rate)
          : item.id === 'duration'
            ? secondsToTime(metricSource?.avg_visit_duration)
            : formatNumber(item.value),
      percent: Math.round((item.value / max) * 100)
    }))
  }, [metricSource])

  const compareRows = useMemo(() => {
    const left = comparePayload.left || {}
    const right = comparePayload.right || {}
    const exclude = ['error_rate', 'not_bounce_rate', 'link_click_rate']
    const keys = Array.from(
      new Set([
        ...Object.keys(left || {}),
        ...Object.keys(right || {}),
        'visits_count',
        'hits_count',
        'avg_visit_duration',
        'bounce_rate',
        'avg_page_views'
      ])
    ).filter((key) => !exclude.includes(key))

    return keys
      .filter((key) => typeof left[key] === 'number' || typeof right[key] === 'number')
      .map((key) => {
        const l = typeof left[key] === 'number' ? left[key] : null
        const r = typeof right[key] === 'number' ? right[key] : null
        const delta = l !== null && r !== null ? r - l : null

        return {
          key,
          label: METRIC_LABELS[key] || key,
          left: l,
          right: r,
          delta
        }
      })
  }, [comparePayload])

  const compareHighlights = useMemo(() => {
    const left = comparePayload.left || {}
    const right = comparePayload.right || {}
    const keys = [
      'visits_count',
      'hits_count',
      'avg_visit_duration',
      'bounce_rate',
      'avg_page_views'
    ]

    return keys.map((key) => {
      const l = left[key]
      const r = right[key]
      const deltaValue =
        typeof l === 'number' && typeof r === 'number' ? formatMetricValue(key, r - l) : '—'
      const tone =
        typeof l === 'number' && typeof r === 'number'
          ? r - l > 0
            ? 'up'
            : r - l < 0
              ? 'down'
              : ''
          : ''
      return {
        key,
        label: METRIC_LABELS[key] || key,
        left: formatMetricValue(key, l),
        right: formatMetricValue(key, r),
        delta: deltaValue,
        tone
      }
    })
  }, [comparePayload])

  const compareMini = useMemo(() => {
    const left = comparePayload.left || {}
    const right = comparePayload.right || {}
    const keys = ['visits_count', 'hits_count', 'avg_visit_duration', 'avg_page_views', 'bounce_rate']
    return keys
      .map((key) => {
        const l = typeof left[key] === 'number' ? left[key] : null
        const r = typeof right[key] === 'number' ? right[key] : null
        if (l === null && r === null) return null
        const total = (l || 0) + (r || 0)
        const leftShare = total > 0 ? (l || 0) / total : 0
        const rightShare = total > 0 ? (r || 0) / total : 0
        return {
          key,
          label: METRIC_LABELS[key] || key,
          left: l,
          right: r,
          leftWidth: Math.round(leftShare * 100),
          rightWidth: Math.round(rightShare * 100)
        }
      })
      .filter(Boolean)
  }, [comparePayload])

  useEffect(() => {
    window.localStorage.setItem('datasets', JSON.stringify(datasets))
  }, [datasets])

  const selectedFiles = useMemo(
    () => ({
      hits: uploadForm.hitsFile?.name || '',
      visits: uploadForm.visitsFile?.name || ''
    }),
    [uploadForm]
  )

  const handleUploadSubmit = async (event) => {
    event.preventDefault()
    const formElement = event.target

    if (!uploadForm.version || !uploadForm.hitsFile || !uploadForm.visitsFile) {
      setUploadState({ status: 'error', message: 'Заполните версию и выберите оба файла.' })
      return
    }

    setUploadState({ status: 'loading', message: 'Отправляем файлы...' })

    try {
      const response = await uploadDataset({
        version: uploadForm.version,
        hitsFile: uploadForm.hitsFile,
        visitsFile: uploadForm.visitsFile
      })

      setDatasets((prev) => {
        const updatedEntry = {
          id: `dataset-${uploadForm.version}-${Date.now()}`,
          title: uploadForm.version,
          state: 'загружено',
          badge: 'новая загрузка',
          markers: [uploadForm.hitsFile.name, uploadForm.visitsFile.name],
          notes: []
        }

        return [updatedEntry, ...prev]
      })

      formElement.reset()
      setUploadForm({ version: '', hitsFile: null, visitsFile: null })
      setUploadState({ status: 'success', message: 'Файлы загружены.' })
    } catch (error) {
      setUploadState({ status: 'error', message: error.message || 'Не удалось загрузить файлы.' })
    }
  }

  const handleMetricsSubmit = async (event) => {
    event.preventDefault()

    if (!metricsVersion.trim()) {
      setMetricsState({ status: 'error', message: 'Укажите версию.' })
      return
    }

    setMetricsState({ status: 'loading', message: 'Запрашиваем данные...' })

    try {
      const payload = await fetchVersionMetrics(metricsVersion.trim())
      setProfilePayload(payload)
      setMetricsState({ status: 'success', message: 'Метрики получены.' })
    } catch (error) {
      setMetricsState({ status: 'error', message: error.message || 'Не удалось получить данные.' })
    }
  }

  const handleCompareSubmit = async (event) => {
    event.preventDefault()
    if (!compareForm.left.trim() || !compareForm.right.trim()) {
      setCompareState({ status: 'error', message: 'Укажите обе версии.' })
      return
    }

    setCompareState({ status: 'loading', message: 'Получаем метрики первой версии...' })
    setShowCompareOverlay(true)

    try {
      const left = await fetchVersionMetrics(compareForm.left.trim())
      setCompareState({ status: 'loading', message: 'Получаем метрики второй версии...' })
      const right = await fetchVersionMetrics(compareForm.right.trim())
      setCompareState({ status: 'loading', message: 'Строим сравнение...' })
      const insights = await fetchComparisonMetrics(compareForm.left.trim(), compareForm.right.trim())

      setComparePayload({ left, right })
      setCompareInsights(insights)
      setCompareState({ status: 'success', message: 'Сравнение обновлено.' })
      setShowCompareOverlay(false)
    } catch (error) {
      setCompareState({ status: 'error', message: error.message || 'Не удалось сравнить версии.' })
      setShowCompareOverlay(false)
    }
  }

  const handleFileChange = (field, fileList) => {
    setUploadForm((prev) => ({
      ...prev,
      [field]: fileList?.[0] || null
    }))
  }

  return (
    <div className="shell">
      {showCompareOverlay && (
        <div className="compare-overlay">
          <div className="compare-overlay__card">
            <div className="compare-overlay__spinner" />
            <p>{compareState.message || 'Готовим сравнение...'}</p>
            <p>Сравнение может занять до 3-4 минут при первом запуске.</p>
          </div>
        </div>
      )}
      <header className="hero">
        <h1 className="hero__title">Анализ UX-дизайна</h1>
      </header>

      <section className="panel datasets" id="datasets">
        <header className="panel__header">
          <div className="panel__intro">
            <h2 className="panel__title">Добавить датасеты для сравнения</h2>
          </div>
        </header>

        <form className="datasets__form" onSubmit={handleUploadSubmit}>
          <label className="input">
            <span>Версия</span>
            <input
              type="text"
              value={uploadForm.version}
              placeholder="v1, v2, new_ui"
              onChange={(event) =>
                setUploadForm((prev) => ({ ...prev, version: event.target.value }))
              }
              required
            />
          </label>

          <label className="input input--file">
            <span>Файл с хитами (Parquet)</span>
            <div className="file-input">
              <input
                type="file"
                accept=".parquet,.pq"
                onChange={(event) => handleFileChange('hitsFile', event.target.files)}
                required
              />
              <span className="file-input__button">
                {selectedFiles.hits ? `Файл: ${selectedFiles.hits}` : 'Выбрать файл'}
              </span>
            </div>
          </label>

          <label className="input input--file">
            <span>Файл с визитами (Parquet)</span>
            <div className="file-input">
              <input
                type="file"
                accept=".parquet,.pq"
                onChange={(event) => handleFileChange('visitsFile', event.target.files)}
                required
              />
              <span className="file-input__button">
                {selectedFiles.visits ? `Файл: ${selectedFiles.visits}` : 'Выбрать файл'}
              </span>
            </div>
          </label>

          <button
            className="button button--ghost"
            type="submit"
            disabled={uploadState.status === 'loading'}
          >
            Загрузить
          </button>
        </form>

        {uploadState.status !== 'idle' && (
          <p className={`status status--${uploadState.status}`}>{uploadState.message}</p>
        )}

        <div className="datasets__grid">
          {datasets.map((dataset) => (
            <article className="dataset-card" key={dataset.id}>
              <div className="dataset-card__head">
                {dataset.badge && <span className="dataset-card__badge">{dataset.badge}</span>}
                <p className="dataset-card__title">{dataset.title}</p>
                <p className="dataset-card__state">{dataset.state}</p>
              </div>
              <div className="dataset-card__markers">
                {dataset.markers.map((marker) => (
                  <span className="dataset-card__marker" key={marker}>
                    {marker}
                  </span>
                ))}
              </div>
              <ul className="dataset-card__notes">
                {dataset.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
              {dataset.lastResponse && (
                <p className="dataset-card__response">{dataset.lastResponse}</p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="panel criteria" id="criteria">
        <header className="panel__header">
          <div className="panel__intro">
            <h2 className="panel__title">Сравнение двух версий</h2>
          </div>
        </header>

        <form className="criteria__form" onSubmit={handleCompareSubmit}>
          <label className="input">
            <span>Версия A</span>
            <input
              type="text"
              value={compareForm.left}
              onChange={(event) =>
                setCompareForm((prev) => ({ ...prev, left: event.target.value }))
              }
              placeholder="v1"
            />
          </label>
          <label className="input">
            <span>Версия B</span>
            <input
              type="text"
              value={compareForm.right}
              onChange={(event) =>
                setCompareForm((prev) => ({ ...prev, right: event.target.value }))
              }
              placeholder="v2"
            />
          </label>
          <button
            className="button button--ghost"
            type="submit"
            disabled={compareState.status === 'loading'}
          >
            Получить и сравнить
          </button>
        </form>

        {compareState.status !== 'idle' && (
          <p className={`status status--${compareState.status}`}>{compareState.message}</p>
        )}

        {compareRows.length > 0 && (
          <div className="comparison-table">
            <div className="comparison-table__header">
              <span>Метрика</span>
              <span>{compareForm.left || 'Версия A'}</span>
              <span>{compareForm.right || 'Версия B'}</span>
              <span>Δ</span>
            </div>
            {compareRows.map((row) => {
              const deltaFormatted =
                row.delta === null
                  ? '—'
                  : row.delta > 0
                    ? `+${formatMetricValue(row.key, row.delta)}`
                    : formatMetricValue(row.key, row.delta)

              const deltaClass =
                row.delta === null
                  ? 'delta'
                  : row.delta > 0
                    ? 'delta delta--up'
                    : 'delta delta--down'

              return (
                <div className="comparison-row" key={row.key}>
                  <span>{row.label}</span>
                  <span>{formatMetricValue(row.key, row.left)}</span>
                  <span>{formatMetricValue(row.key, row.right)}</span>
                  <span className={deltaClass}>{deltaFormatted}</span>
                </div>
              )
            })}
          </div>
        )}

        {compareHighlights.length > 0 && (
          <div className="compare-cards">
            {compareHighlights.map((item) => (
              <article className="compare-card" key={item.key}>
                <p className="compare-card__label">{item.label}</p>
                <div className="compare-card__values">
                  <span>{item.left}</span>
                  <span>{item.right}</span>
                </div>
                <span
                  className={`compare-card__delta ${
                    item.tone === 'up'
                      ? 'compare-card__delta--up'
                      : item.tone === 'down'
                        ? 'compare-card__delta--down'
                        : ''
                  }`}
                >
                  {item.delta}
                </span>
              </article>
            ))}
          </div>
        )}

        {compareMini.length > 0 && (
          <div className="mini-bars">
            {compareMini.map((item) => (
              <div className="mini-bar" key={item.key}>
                <div className="mini-bar__head">
                  <p>{item.label}</p>
                  <div className="mini-bar__legend">
                    <span className="mini-bar__dot mini-bar__dot--left" />
                    {compareForm.left || 'Версия A'}
                    <span className="mini-bar__dot mini-bar__dot--right" />
                    {compareForm.right || 'Версия B'}
                  </div>
                </div>
                <div className="mini-bar__track">
                  <span className="mini-bar__fill mini-bar__fill--left" style={{ width: `${item.leftWidth}%` }} />
                  <span className="mini-bar__fill mini-bar__fill--right" style={{ width: `${item.rightWidth}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {compareInsights && (
          <div className="insights-grid">
            <article className="insight-summary">
              <p className="insight-summary__label">Итог</p>
              <h3>{compareInsights.summary}</h3>
            </article>

            <div className="insight-columns">
              <div>
                <p className="insight-title">Улучшения</p>
                {compareInsights.improvements?.map((item) => (
                  <article className="insight-card" key={`imp-${item.metric}-${item.change}`}>
                    <div className="insight-card__head">
                      <p className="insight-card__metric">{item.title}</p>
                      <span className="insight-card__delta insight-card__delta--up">
                        {item.change}
                      </span>
                    </div>
                    <p className="insight-card__desc">{item.description}</p>
                    <p className="insight-card__hypo">{item.hypothesis}</p>
                    <div className="insight-card__values">
                      <span>v1: {formatMetricValue(item.metric, item.v1_value)}</span>
                      <span>v2: {formatMetricValue(item.metric, item.v2_value)}</span>
                    </div>
                  </article>
                ))}
              </div>
              <div>
                <p className="insight-title">Регрессии</p>
                {compareInsights.regressions?.map((item) => (
                  <article className="insight-card" key={`reg-${item.metric}-${item.change}`}>
                    <div className="insight-card__head">
                      <p className="insight-card__metric">{item.title}</p>
                      <span className="insight-card__delta insight-card__delta--down">
                        {item.change}
                      </span>
                    </div>
                    <p className="insight-card__desc">{item.description}</p>
                    <p className="insight-card__hypo">{item.hypothesis}</p>
                    <div className="insight-card__values">
                      <span>v1: {formatMetricValue(item.metric, item.v1_value)}</span>
                      <span>v2: {formatMetricValue(item.metric, item.v2_value)}</span>
                    </div>
                  </article>
                ))}
              </div>
            </div>

            {compareInsights.expected_no_change?.length > 0 && (
              <div className="insight-block">
                <p className="insight-title">Ожидали без изменений</p>
                <div className="insight-chips">
                  {compareInsights.expected_no_change.map((item) => (
                    <span className="insight-chip" key={`${item.metric}-${item.v1}`}>
                      {item.title}: {formatMetricValue(item.metric, item.v1_value)} →{' '}
                      {formatMetricValue(item.metric, item.v2_value)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {compareInsights.recommendations?.length > 0 && (
              <div className="insight-block">
                <p className="insight-title">Рекомендации</p>
                <ul className="insight-list">
                  {compareInsights.recommendations.map((rec) => (
                    <li key={rec}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

      </section>

      <section className="panel profile" id="profile">
        <header className="panel__header">
          <div className="panel__intro">
            <h2 className="panel__title">Анализ одной версии</h2>
          </div>
        </header>

        <form className="criteria__form" onSubmit={handleMetricsSubmit}>
          <label className="input">
            <span>Версия</span>
            <input
              type="text"
              value={metricsVersion}
              onChange={(event) => setMetricsVersion(event.target.value)}
              placeholder="v1"
            />
          </label>
          <button
            className="button button--ghost"
            type="submit"
            disabled={metricsState.status === 'loading'}
          >
            Получить метрики
          </button>
        </form>

        {metricsState.status !== 'idle' && (
          <p className={`status status--${metricsState.status}`}>{metricsState.message}</p>
        )}

        <div className="profile__grid">
          <div className="profile__column profile__column--left">
            <div className="profile-card">
              <p className="profile-card__badge">{profileData.tag}</p>
              <h3 className="profile-card__title">{profileData.version}</h3>
              <div className="profile-card__metrics">
                {profileData.metrics.map((metric) => (
                  <div className="profile-card__metric" key={metric.id}>
                    <p>{metric.label}</p>
                    <strong>{metric.value}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="profile-card profile-card--list">
              {profileData.blocks.map((block) => (
                <div className="profile-card__list-block" key={block.id}>
                  <p className="profile-card__list-title">{block.title}</p>
                  <ul>
                    {block.items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

          </div>

          <div className="profile__column profile__column--right">
            {profileData.charts.map((chart) => (
              <div className="profile-chart" key={chart.id}>
                <p>{chart.title}</p>
                <div className="profile-chart__canvas" aria-hidden="true">
                  <span />
                </div>
              </div>
            ))}

            <div className="metric-cards">
              {metricCards.map((card) => (
                <article className="metric-card" key={card.id}>
                  <p className="metric-card__label">{card.label}</p>
                  <strong className="metric-card__value">{card.value}</strong>
                  <span className="metric-card__hint">{card.hint}</span>
                </article>
              ))}
            </div>

            <div className="metric-bars">
              {metricBars.map((bar) => (
                <div className="metric-bar" key={bar.id}>
                  <div className="metric-bar__header">
                    <p>{bar.label}</p>
                    <strong>{bar.valueLabel}</strong>
                  </div>
                  <div className="metric-bar__track">
                    <span style={{ width: `${bar.percent}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default App
