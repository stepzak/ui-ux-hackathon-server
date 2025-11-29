import pandas as pd
from collections import Counter
import pyarrow.parquet as pq
from collections import Counter as ColCounter

def extract_patterns_and_aggregates_from_full_data(hits_path: str, visits_path: str, chunk_size: int = 150_000, min_visits_threshold: int = 100):
    print(f"extracting patterns and aggregates from {hits_path}", flush=True)

    hits_table = pq.ParquetFile(hits_path)
    visits_table = pq.ParquetFile(visits_path)

    try:
        visits_agg_metrics = extract_metrics_from_visits_chunks(visits_table, chunk_size)
        print(f"Visits aggregation metrics done", flush=True)

        device_agg = aggregate_by_device_and_os_from_chunks(visits_table, chunk_size, min_visits_threshold)
        print(f"Device aggregation metrics done", flush=True)

        hits_agg_metrics = extract_metrics_from_hits_chunks(hits_table, chunk_size)
        print(f"Hits aggregation metrics: done", flush=True)

        funnels = extract_paths_and_funnels_from_chunks(hits_table, chunk_size)
        print(f"Paths aggregation metrics: done", flush=True)

       # patterns = extract_behavior_patterns_from_chunks(visits_table, hits_table, chunk_size)
        print(f"Patterns aggregation metrics: done", flush=True)

        metrics = {**visits_agg_metrics, **hits_agg_metrics}
        return {
           # "patterns": patterns,
            "device_agg": device_agg,
            "funnels": funnels,
            "metrics": metrics
        }
    finally:
        pass


def extract_metrics_from_visits_chunks(visits_table: pq.ParquetFile, chunk_size: int = 100_000) -> dict:
    visits_count = 0
    visit_duration_sum = 0
    bounce_count = 0
    page_views_sum = 0
    total_goals_from_visits = 0
    device_counts = Counter()
    os_counts = Counter()
    new_user_bounce_sum = 0
    new_user_duration_sum = 0
    new_user_goals_sum = 0
    new_user_count = 0
    returning_user_bounce_sum = 0
    returning_user_duration_sum = 0
    returning_user_goals_sum = 0
    returning_user_count = 0
    time_per_page = Counter()
    page_views_count = Counter()
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        visits_count += len(df_batch)
        if 'ym:s:visitDuration' in df_batch.columns:
            visit_duration_sum += df_batch['ym:s:visitDuration'].sum()
        if 'ym:s:bounce' in df_batch.columns:
            bounce_count += df_batch['ym:s:bounce'].sum()
        if 'ym:s:pageViews' in df_batch.columns:
            page_views_sum += df_batch['ym:s:pageViews'].sum()
        if 'ym:s:goalsID' in df_batch.columns:
            goals_str_series = df_batch['ym:s:goalsID'].dropna().astype(str)
            for goals_str in goals_str_series:
                goals_list = goals_str.split(',')
                for g in goals_list:
                    g_clean = g.strip()
                    if g_clean:
                        total_goals_from_visits += 1
        if 'ym:s:deviceCategory' in df_batch.columns:
            device_counts.update(df_batch['ym:s:deviceCategory'].value_counts())
        if 'ym:s:operatingSystem' in df_batch.columns:
            os_counts.update(df_batch['ym:s:operatingSystem'].value_counts())
        if 'ym:s:isNewUser' in df_batch.columns:
            new_users_batch = df_batch[df_batch['ym:s:isNewUser'] == 1]
            returning_users_batch = df_batch[df_batch['ym:s:isNewUser'] == 0]
            if 'ym:s:bounce' in new_users_batch.columns:
                new_user_bounce_sum += new_users_batch['ym:s:bounce'].sum()
            if 'ym:s:visitDuration' in new_users_batch.columns:
                new_user_duration_sum += new_users_batch['ym:s:visitDuration'].sum()
            if 'ym:s:goalsID' in new_users_batch.columns:
                new_user_goals_sum += new_users_batch['ym:s:goalsID'].notna().sum()
            new_user_count += len(new_users_batch)
            if 'ym:s:bounce' in returning_users_batch.columns:
                returning_user_bounce_sum += returning_users_batch['ym:s:bounce'].sum()
            if 'ym:s:visitDuration' in returning_users_batch.columns:
                returning_user_duration_sum += returning_users_batch['ym:s:visitDuration'].sum()
            if 'ym:s:goalsID' in returning_users_batch.columns:
                returning_user_goals_sum += returning_users_batch['ym:s:goalsID'].notna().sum()
            returning_user_count += len(returning_users_batch)
        if 'ym:s:endURL' in df_batch.columns and 'ym:s:visitDuration' in df_batch.columns:
            urls = df_batch['ym:s:endURL']
            durations = df_batch['ym:s:visitDuration']
            mask = urls.notna() & durations.notna()
            time_per_page.update(pd.Series(durations[mask].values, index=urls[mask]).groupby(level=0).sum())
            page_views_count.update(urls[mask].value_counts())
    avg_visit_duration = visit_duration_sum / visits_count if visits_count > 0 else 0
    bounce_rate = bounce_count / visits_count if visits_count > 0 else 0
    avg_page_views = page_views_sum / visits_count if visits_count > 0 else 0
    hits_count_placeholder = 0
    error_rate_placeholder = 0
    not_bounce_rate_placeholder = 0
    link_click_rate_placeholder = 0
    goals_str_full = " ".join(
        [str(g) for g in df_batch['ym:s:goalsID'].dropna()]) if 'ym:s:goalsID' in df_batch.columns else ""
    goals_list_full = goals_str_full.replace(',', ' ').split()
    goal_counts = ColCounter(goals_list_full)
    form_view_count = goal_counts.get('94939123', 0)
    form_submit_count = goal_counts.get('94939720', 0)
    vk_contact_clicks = goal_counts.get('225392702', 0)
    tg_contact_clicks = goal_counts.get('225392736', 0)
    avg_time_per_page = {page: time_per_page[page] / page_views_count[page] for page in time_per_page if
                         page_views_count[page] > 0}
    page_error_rates = {}
    new_user_metrics = {
        'bounce_rate': new_user_bounce_sum / new_user_count if new_user_count > 0 else 0,
        'avg_duration': new_user_duration_sum / new_user_count if new_user_count > 0 else 0,
        'conversion_rate': new_user_goals_sum / new_user_count if new_user_count > 0 else 0
    }
    returning_user_metrics = {
        'bounce_rate': returning_user_bounce_sum / returning_user_count if returning_user_count > 0 else 0,
        'avg_duration': returning_user_duration_sum / returning_user_count if returning_user_count > 0 else 0,
        'conversion_rate': returning_user_goals_sum / returning_user_count if returning_user_count > 0 else 0
    }
    form_metrics = {
        'view_rate': form_view_count / visits_count if visits_count > 0 else 0,
        'submit_rate': form_submit_count / visits_count if visits_count > 0 else 0,
        'drop_off_rate': (form_view_count - form_submit_count) / form_view_count if form_view_count > 0 else 0
    }
    avg_page_depth = avg_page_views
    return {
        "visits_count": visits_count,
        "hits_count": hits_count_placeholder,
        "avg_visit_duration": avg_visit_duration,
        "bounce_rate": bounce_rate,
        "avg_page_views": avg_page_views,
        "error_rate": error_rate_placeholder,
        "not_bounce_rate": not_bounce_rate_placeholder,
        "link_click_rate": link_click_rate_placeholder,
        "form_view_count": form_view_count,
        "form_submit_count": form_submit_count,
        "vk_contact_clicks": vk_contact_clicks,
        "tg_contact_clicks": tg_contact_clicks,
        "device_category_distribution": dict(device_counts),
        "os_distribution": dict(os_counts),
        "avg_time_per_page": avg_time_per_page,
        "page_error_rates": page_error_rates,
        "new_user_metrics": new_user_metrics,
        "returning_user_metrics": returning_user_metrics,
        "form_metrics": form_metrics,
        "avg_page_depth": avg_page_depth
    }

def extract_paths_and_funnels_from_chunks(hits_table: pq.ParquetFile, chunk_size: int) -> dict:
    all_paths = []
    for batch in hits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        df_batch['clean_url'] = (
            df_batch['ym:pv:URL']
            .str.replace(r'https?://[^/]+', '', regex=True)
            .str.split('?').str[0]
            .str.split('#').str[0]
            .str.rstrip('/')
            .replace('', '/')
        )
        paths_batch = df_batch.sort_values(['ym:pv:clientID', 'ym:pv:dateTime']).groupby('ym:pv:clientID')[
            'clean_url'].apply(list).reset_index()
        all_paths.extend(paths_batch['clean_url'].tolist())
    funnel_counts = {
        'start': 0,
        'to_application': 0,
        'to_form_view': 0,
        'to_form_submit': 0
    }
    for path in all_paths:
        if '/bachelor/programs' in path:
            funnel_counts['start'] += 1
            if '/bachelor/application' in path:
                funnel_counts['to_application'] += 1
    return funnel_counts

def aggregate_by_device_and_os_from_chunks(visits_table: pq.ParquetFile, chunk_size: int, min_visits_threshold: int = 100) -> list:
    agg_data = []
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        if 'ym:s:deviceCategory' in df_batch.columns and 'ym:s:operatingSystem' in df_batch.columns:
            group = df_batch.groupby(['ym:s:deviceCategory', 'ym:s:browser', "ym:s:mobilePhoneModel"]).agg(
                visits=('ym:s:visitID', 'count'),
                avg_duration=('ym:s:visitDuration', 'mean'),
                bounce_rate=('ym:s:bounce', 'mean'),
                form_view_rate=('ym:s:goalsID', lambda x: x.astype(str).str.contains('94939123', na=False).mean()),
                form_submit_rate=('ym:s:goalsID', lambda x: x.astype(str).str.contains('94939720', na=False).mean()),
            ).reset_index()
            group = group[group['visits'] >= min_visits_threshold]
            agg_data.append(group)
    if agg_data:
        final_df = pd.concat(agg_data, ignore_index=True)
        final_df = final_df.groupby(['ym:s:deviceCategory', 'ym:s:browser', "ym:s:mobilePhoneModel"]).agg(
            visits=('visits', 'sum'),
            avg_duration=('avg_duration', 'mean'),
            bounce_rate=('bounce_rate', 'mean'),
            form_view_rate=('form_view_rate', 'mean'),
            form_submit_rate=('form_submit_rate', 'mean')
        ).reset_index()
        final_df = final_df[final_df['visits'] >= min_visits_threshold]
        return final_df.to_dict(orient='records')
    return []


def aggregate_by_browser_and_device_from_chunks(visits_table: pq.ParquetFile, chunk_size: int, min_visits_threshold: int = 100) -> list:
    agg_data = []
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        if 'ym:s:browser' in df_batch.columns and 'ym:s:deviceCategory' in df_batch.columns:
            group = df_batch.groupby(['ym:s:browser', 'ym:s:deviceCategory']).agg(
                visits=('ym:s:visitID', 'count'),
                avg_duration=('ym:s:visitDuration', 'mean'),
                bounce_rate=('ym:s:bounce', 'mean'),
            ).reset_index()
            group = group[group['visits'] >= min_visits_threshold]
            agg_data.append(group)
    if agg_data:
        final_df = pd.concat(agg_data, ignore_index=True)
        final_df = final_df.groupby(['ym:s:browser', 'ym:s:deviceCategory']).agg(
            visits=('visits', 'sum'),
            avg_duration=('avg_duration', 'mean'),
            bounce_rate=('bounce_rate', 'mean'),
        ).reset_index()
        final_df = final_df[final_df['visits'] >= min_visits_threshold]
        return final_df.to_dict(orient='records')
    return []


def extract_metrics_from_hits_chunks(hits_table: pq.ParquetFile, chunk_size: int) -> dict:
    hits_count = 0
    error_count = 0
    not_bounce_count = 0
    link_click_count = 0
    total_goals_from_hits = 0
    for batch in hits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        hits_count += len(df_batch)
        if 'ym:pv:httpError' in df_batch.columns:
            error_count += (df_batch['ym:pv:httpError'] != 0).sum()
        if 'ym:pv:notBounce' in df_batch.columns:
            not_bounce_count += df_batch['ym:pv:notBounce'].sum()
        if 'ym:pv:link' in df_batch.columns:
            link_click_count += df_batch['ym:pv:link'].sum()
        if 'ym:pv:goalsID' in df_batch.columns:
            goals_str_series = df_batch['ym:pv:goalsID'].dropna().astype(str)
            for goals_str in goals_str_series:
                goals_list = goals_str.split(',')
                for g in goals_list:
                    g_clean = g.strip()
                    if g_clean:
                        total_goals_from_hits += 1
    error_rate = error_count / hits_count if hits_count > 0 else 0
    not_bounce_rate = not_bounce_count / hits_count if hits_count > 0 else 0
    link_click_rate = link_click_count / hits_count if hits_count > 0 else 0
    return {
        "hits_count": hits_count,
        "error_rate": error_rate,
        "not_bounce_rate": not_bounce_rate,
        "link_click_rate": link_click_rate,
    }


def extract_behavior_patterns_from_chunks(visits_df, hits_df):
    hits_agg = hits_df.groupby('ym:pv:clientID').agg(
        total_links=('ym:pv:link', 'sum'),
        total_goals_from_hits=('ym:pv:goalsID', lambda x: x.notna().sum()),
        unique_pages=('ym:pv:URL', 'nunique'),
        total_pages=('ym:pv:URL', 'count'),
        most_visited_page=('ym:pv:URL', lambda x: x.mode().iloc[0] if not x.mode().empty else None),
        page_counts=('ym:pv:URL', lambda x: x.value_counts().max())  # макс. кол-во посещений одной страницы
    ).reset_index()

    # Переименуем для совпадения с визитами
    hits_agg.rename(columns={'ym:pv:clientID': 'ym:s:clientID'}, inplace=True)

    # 2. Объединяем с визитами
    full_data = visits_df.merge(hits_agg, on='ym:s:clientID', how='left')

    # Заполняем пропуски
    full_data['total_links'] = full_data['total_links'].fillna(0)
    full_data['total_goals_from_hits'] = full_data['total_goals_from_hits'].fillna(0)
    full_data['unique_pages'] = full_data['unique_pages'].fillna(0)
    full_data['total_pages'] = full_data['total_pages'].fillna(0)
    full_data['most_visited_page'] = full_data['most_visited_page'].fillna('')
    full_data['page_counts'] = full_data['page_counts'].fillna(0)

    # Подсчитываем цели из визитов
    def count_goals_from_visit(goals_str):
        if pd.isna(goals_str):
            return 0
        goals_list = str(goals_str).split(',')
        return len([g for g in goals_list if g.strip()])

    full_data['total_goals_from_visits'] = full_data['ym:s:goalsID'].apply(count_goals_from_visit)
    full_data['total_goals'] = full_data['total_goals_from_hits'] + full_data['total_goals_from_visits']

    # 3. Определяем паттерны
    patterns = {
        'contacts_without_interaction': [],
        'short_stay_then_contacts': [],
        'no_goals_no_pages': [],
        'repeat_same_page_many_times': [],
        'high_bounce_on_key_pages': []
    }

    for idx, row in full_data.iterrows():
        end_url = row.get('ym:s:endURL', '')
        duration = row.get('ym:s:visitDuration', 0)
        total_links = row['total_links']
        total_goals = row['total_goals']
        unique_pages = row['unique_pages']
        total_pages = row['total_pages']
        most_visited_page = row['most_visited_page']
        page_count_max = row['page_counts']
        bounce = row.get('ym:s:bounce', 0)

        if end_url.startswith('/contacts') and total_links == 0:
            patterns['contacts_without_interaction'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'endURL': end_url,
                'total_links': total_links,
                'visitDuration': duration,
                'description': 'Пользователь ушёл в /contacts, не кликая по внутренним ссылкам'
            })

        if end_url.startswith('/contacts') and duration < 10:
            patterns['short_stay_then_contacts'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'endURL': end_url,
                'visitDuration': duration,
                'description': 'Пользователь ушёл в /contacts, проведя мало времени на сайте'
            })

        if total_goals == 0 and unique_pages < 2:
            patterns['no_goals_no_pages'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'unique_pages': unique_pages,
                'total_goals': total_goals,
                'visitDuration': duration,
                'description': 'Пользователь не достиг целей и посетил мало страниц'
            })

        if page_count_max >= 5:
            patterns['repeat_same_page_many_times'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'most_visited_page': most_visited_page,
                'visit_count': page_count_max,
                'description': f'Пользователь часто посещал одну страницу: {most_visited_page} ({page_count_max} раз)'
            })

        start_url = row.get('ym:s:startURL', '')
        if bounce == 1 and ('programs' in start_url or 'application' in start_url or 'min-point' in start_url):
            patterns['high_bounce_on_key_pages'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'startURL': start_url,
                'endURL': end_url,
                'description': f'Высокий bounce на ключевой странице: {start_url}'
            })

    return patterns