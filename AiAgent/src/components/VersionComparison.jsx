import { useMemo, useState, useEffect } from 'react'

const metricNames = {
  visitDuration: 'Среднее время визита',
  bounceRate: 'Bounce Rate',
  funnelCompletion: 'Доля завершивших воронку',
  conversion: 'Конверсия CTA'
}

export default function VersionComparison({ versions }) {
  const [selection, setSelection] = useState({
    left: versions[0]?.id || '',
    right: versions[1]?.id || versions[0]?.id || ''
  })

  useEffect(() => {
    setSelection((prev) => ({
      left: versions.find((version) => version.id === prev.left)?.id || versions[0]?.id || '',
      right:
        versions.find((version) => version.id === prev.right)?.id ||
        versions[1]?.id ||
        versions[0]?.id ||
        ''
    }))
  }, [versions])

  const { leftVersion, rightVersion, rows } = useMemo(() => {
    const leftVersion = versions.find((version) => version.id === selection.left)
    const rightVersion = versions.find((version) => version.id === selection.right)

    const metricKeys = Array.from(
      new Set(
        versions.flatMap((version) => Object.keys(version.basicMetrics || {}))
      )
    )

    const rows = metricKeys.map((key) => {
      const leftValue = leftVersion?.basicMetrics?.[key] || '—'
      const rightValue = rightVersion?.basicMetrics?.[key] || '—'
      const delta = formatDelta(leftValue, rightValue)

      return {
        key,
        label: metricNames[key] || key,
        leftValue,
        rightValue,
        delta
      }
    })

    return { leftVersion, rightVersion, rows }
  }, [versions, selection])

  const handleSelectChange = (side, value) => {
    setSelection((prev) => ({ ...prev, [side]: value }))
  }

  return (
    <section className="panel" id="comparison">
      <header className="panel__header">
        <div>
          <p className="eyebrow">Модуль сравнения</p>
          <h2>Сводка по версиям</h2>
          <p className="panel__description">
            Выберите две версии, чтобы увидеть разницу по ключевым метрикам. Результаты можно
            сохранять и возвращаться к ним позже.
          </p>
        </div>
      </header>

      <div className="comparison-selectors">
        <Selector
          label="Версия A"
          value={selection.left}
          versions={versions}
          onChange={(event) => handleSelectChange('left', event.target.value)}
        />
        <Selector
          label="Версия B"
          value={selection.right}
          versions={versions}
          onChange={(event) => handleSelectChange('right', event.target.value)}
        />
      </div>

      <div className="comparison-table">
        <div className="comparison-table__header">
          <span>Метрика</span>
          <span>{leftVersion?.label || '—'}</span>
          <span>{rightVersion?.label || '—'}</span>
          <span>Δ</span>
        </div>
        {rows.map((row) => {
          const className = row.delta.startsWith('+')
            ? 'delta delta--up'
            : row.delta.startsWith('-')
              ? 'delta delta--down'
              : 'delta'

          return (
            <div className="comparison-row" key={row.key}>
              <span>{row.label}</span>
              <span>{row.leftValue}</span>
              <span>{row.rightValue}</span>
              <span className={className}>{row.delta}</span>
            </div>
          )
        })}
      </div>

      <div className="insight-grid">
        <InsightCard
          title="Блуждание по сайту"
          description="Следим за visitDuration и bounce=1. Повторяющиеся маршруты → ставим подсказки и закрепляем CTA."
        />
        <InsightCard
          title="Проблемы с навигацией"
          description="Если переходы между календарём и программами растут, значит не хватает контента в карточках."
        />
        <InsightCard
          title="Ошибки форм"
          description="Фиксируем 4xx/5xx, делим на фронт/бэк и добавляем отчёт прямо в карточку версии."
        />
      </div>
    </section>
  )
}

const Selector = ({ label, value, versions, onChange }) => (
  <label className="field selector">
    <span>{label}</span>
    <select value={value} onChange={onChange}>
      {versions.map((version) => (
        <option value={version.id} key={version.id}>
          {version.label}
        </option>
      ))}
    </select>
  </label>
)

const InsightCard = ({ title, description }) => (
  <article className="insight-card">
    <h3>{title}</h3>
    <p>{description}</p>
  </article>
)

const formatDelta = (left, right) => {
  if (!left || !right || left === '—' || right === '—') {
    return 'n/a'
  }

  const parseNumber = (value) => {
    const digits = parseFloat(value.toString().replace('%', '').replace(':', '.'))
    return Number.isNaN(digits) ? null : digits
  }

  const leftNumber = parseNumber(left)
  const rightNumber = parseNumber(right)

  if (leftNumber === null || rightNumber === null) {
    return 'n/a'
  }

  const delta = rightNumber - leftNumber
  const prefix = delta > 0 ? '+' : ''

  return `${prefix}${delta.toFixed(2)}`
}
