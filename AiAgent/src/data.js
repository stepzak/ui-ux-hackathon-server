export const DATASETS = [
]

export const METRIC_SAMPLE = {
  visits_count: 1431873,
  hits_count: 6489694,
  avg_visit_duration: 295.49613268774533,
  bounce_rate: 0.10674131015809363,
  avg_page_views: 2.7385242964983627,
  error_rate: 0,
  not_bounce_rate: 0.2715896928268112,
  link_click_rate: 0.07807841170939647,
  form_view_count: 1759,
  form_submit_count: 1,
  vk_contact_clicks: 66,
  tg_contact_clicks: 207,
  device_category_distribution: null,
  os_distribution: null
}

export const CRITERIA = [
  {
    id: 'criterion-1',
    title: 'Критерий сравнения 1',
    versions: [
      { id: 'a', label: 'Версия A', value: '—', percent: 62 },
      { id: 'b', label: 'Версия B', value: '—', percent: 48 },
    ],
    sparkline: [40, 56, 44, 68, 55]
  },
  {
    id: 'criterion-3',
    title: 'Критерий сравнения 3',
    versions: [
      { id: 'a', label: 'Версия A', value: '—', percent: 50 },
      { id: 'b', label: 'Версия B', value: '—', percent: 64 },
    ],
    sparkline: [64, 52, 61, 58, 63]
  }
]

export const PROFILE = {
  version: 'Версия A',
  tag: 'анализ',
  metrics: [
    { id: 'metric-1', label: 'Показатель 1', value: '—' },
    { id: 'metric-2', label: 'Показатель 2', value: '—' },
    { id: 'metric-3', label: 'Показатель 3', value: '—' },
    { id: 'metric-4', label: 'Показатель 4', value: '—' }
  ],
  blocks: [

  ],
  charts: [
    { id: 'chart-1', title: 'Диаграмма 1' },
    { id: 'chart-2', title: 'Диаграмма 2' },
    { id: 'chart-3', title: 'Дашборд 1' }
  ]
}
