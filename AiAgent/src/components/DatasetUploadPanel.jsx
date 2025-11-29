export default function DatasetUploadPanel({ versions, onUpdateVersion, onAddVersion }) {
  const handleFieldChange = (id, field, value) => {
    onUpdateVersion(id, { [field]: value })
  }

  const handleMetricChange = (id, metricKey, value) => {
    onUpdateVersion(id, {
      basicMetrics: (prev) => ({
        ...prev,
        [metricKey]: value
      })
    })
  }

  const handleFileChange = (id, file) => {
    if (!file) return

    onUpdateVersion(id, {
      fileName: file.name,
      lastUpdated: new Date().toISOString().slice(0, 10)
    })
  }

  return (
    <section className="panel" id="upload">
      <header className="panel__header">
        <div>
          <p className="eyebrow">Модуль загрузки версий</p>
          <h2>Готовим датасеты к сравнению</h2>
          <p className="panel__description">
            Загрузите выгрузки за 2022 и 2024 годы, добавьте комментарии и базовые метрики. Это
            позволит аналитикам быстрее проверять гипотезы без ожидания бэкенда.
          </p>
        </div>
        <button className="ghost-button" onClick={onAddVersion}>
          + Добавить версию
        </button>
      </header>

      <div className="upload-grid">
        {versions.map((version) => (
          <div className="upload-card" key={version.id}>
            <div className="upload-card__top">
              <div>
                <p className="eyebrow">{version.year || 'Год не указан'}</p>
                <h3>{version.label}</h3>
              </div>
              {version.lastUpdated && <span className="tag">обновлено {version.lastUpdated}</span>}
            </div>

            <label className="field">
              <span>Название версии</span>
              <input
                type="text"
                value={version.label}
                onChange={(event) => handleFieldChange(version.id, 'label', event.target.value)}
              />
            </label>

            <label className="field">
              <span>Год</span>
              <input
                type="number"
                value={version.year || ''}
                onChange={(event) =>
                  handleFieldChange(version.id, 'year', Number(event.target.value) || '')
                }
                placeholder="2024"
              />
            </label>

            <label className="field field--file">
              <span>Файлы hits и visits (Parquet)</span>
              <input
                type="file"
                accept=".parquet,.pq"
                onChange={(event) => handleFileChange(version.id, event.target.files[0])}
              />
              {version.fileName && <p className="file-name">{version.fileName}</p>}
            </label>

            <label className="field">
              <span>Комментарий</span>
              <textarea
                value={version.notes}
                placeholder="Опишите, какие фичи включены в этой версии."
                onChange={(event) => handleFieldChange(version.id, 'notes', event.target.value)}
              />
            </label>

            <div className="metric-box">
              <p className="eyebrow">Базовые метрики</p>
              <div className="metric-grid">
                {Object.entries(version.basicMetrics).map(([key, value]) => (
                  <label className="field metric-field" key={key}>
                    <span>{metricLabelMap[key] || key}</span>
                    <input
                      type="text"
                      value={value}
                      onChange={(event) => handleMetricChange(version.id, key, event.target.value)}
                    />
                  </label>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

const metricLabelMap = {
  visitDuration: 'Среднее время визита',
  bounceRate: 'Bounce Rate',
  funnelCompletion: 'Завершение воронки',
  conversion: 'Конверсия CTA'
}
