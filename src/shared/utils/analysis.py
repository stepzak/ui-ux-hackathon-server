from collections import Counter

import pandas as pd


import pyarrow.parquet as pq
import pandas as pd
from collections import Counter

def extract_metrics_from_parquet(hits_path: str, visits_path: str, chunk_size: int = 10000):
    """
    Извлекает метрики из Parquet-файлов по чанкам, чтобы не грузить всё в память.
    """
    # Инициализируем агрегаты
    visits_count = 0
    hits_count = 0
    visit_duration_sum = 0
    bounce_count = 0
    page_views_sum = 0
    error_count = 0
    not_bounce_count = 0
    link_click_count = 0

    # Для подсчёта целей
    all_goals_str = ""
    device_counts = Counter()
    os_counts = Counter()

    visits_table = pq.ParquetFile(visits_path)
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()

        visits_count += len(df_batch)
        visit_duration_sum += df_batch['ym:s:visitDuration'].sum()
        bounce_count += df_batch['ym:s:bounce'].sum()
        page_views_sum += df_batch['ym:s:pageViews'].sum()

        if 'ym:s:deviceCategory' in df_batch.columns:
            device_counts.update(df_batch['ym:s:deviceCategory'].value_counts())
        if 'ym:s:operatingSystem' in df_batch.columns:
            os_counts.update(df_batch['ym:s:operatingSystem'].value_counts())

        if 'ym:s:goalsID' in df_batch.columns:
            goals_series = df_batch['ym:s:goalsID'].dropna().astype(str)
            all_goals_str += " " + " ".join(goals_series)

    hits_table = pq.ParquetFile(hits_path)
    for batch in hits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()

        hits_count += len(df_batch)
        error_count += (df_batch['ym:pv:httpError'] != 0).sum()
        not_bounce_count += df_batch['ym:pv:notBounce'].sum()
        link_click_count += df_batch['ym:pv:link'].sum()

        if 'ym:pv:goalsID' in df_batch.columns:
            goals_series = df_batch['ym:pv:goalsID'].dropna().astype(str)
            all_goals_str += " " + " ".join(goals_series)

    metrics = {
        "visits_count": visits_count,
        "hits_count": hits_count,
        "avg_visit_duration": visit_duration_sum / visits_count if visits_count > 0 else 0,
        "bounce_rate": bounce_count / visits_count if visits_count > 0 else 0,
        "avg_page_views": page_views_sum / visits_count if visits_count > 0 else 0,
        "error_rate": error_count / hits_count if hits_count > 0 else 0,
        "not_bounce_rate": not_bounce_count / hits_count if hits_count > 0 else 0,
        "link_click_rate": link_click_count / hits_count if hits_count > 0 else 0,
    }

    goals_list = all_goals_str.strip().split()
    goal_counts = Counter(goals_list)
    metrics['form_view_count'] = goal_counts.get('94939123', 0)
    metrics['form_submit_count'] = goal_counts.get('94939720', 0)
    metrics['vk_contact_clicks'] = goal_counts.get('225392702', 0)
    metrics['tg_contact_clicks'] = goal_counts.get('225392736', 0)

    return metrics