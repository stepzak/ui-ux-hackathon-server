import pandas as pd
from collections import Counter
import pyarrow.parquet as pq
from collections import Counter as ColCounter


def extract_patterns_and_aggregates_from_full_data(hits_path: str, visits_path: str, chunk_size: int = 150_000):

    hits_table = pq.ParquetFile(hits_path)
    visits_table = pq.ParquetFile(visits_path)

    try:
        visits_agg_metrics = extract_metrics_from_visits_chunks(visits_table, chunk_size)

        device_agg = aggregate_by_device_and_os_from_chunks(visits_table, chunk_size)

        hits_agg_metrics = extract_metrics_from_hits_chunks(hits_table, chunk_size)

        funnels = extract_paths_and_funnels_from_chunks(hits_table, chunk_size)

        #patterns = extract_behavior_patterns_from_chunks(visits_table, hits_table, chunk_size)

        metrics = {**visits_agg_metrics, **hits_agg_metrics}
        return {
            #"patterns": patterns,
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
    utm_counts = Counter()
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
        if 'ym:s:lastsignUTMSource' in df_batch.columns:
            utm_series = df_batch['ym:s:lastsignUTMSource'].dropna().astype(str)
            utm_counts.update(utm_series)
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
            for idx, row in df_batch.iterrows():
                page = row['ym:s:endURL']
                duration = row['ym:s:visitDuration']
                if pd.notna(page) and pd.notna(duration):
                    time_per_page[page] += duration
                    page_views_count[page] += 1
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
    utm_source_distribution = dict(utm_counts)
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
        "utm_source_distribution": utm_source_distribution,
        "avg_time_per_page": avg_time_per_page,
        "page_error_rates": page_error_rates,
        "new_user_metrics": new_user_metrics,
        "returning_user_metrics": returning_user_metrics,
        "form_metrics": form_metrics,
        "avg_page_depth": avg_page_depth
    }


def aggregate_by_device_and_os_from_chunks(visits_table: pq.ParquetFile, chunk_size: int) -> list:
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
        return final_df.to_dict(orient='records')
    return []


def aggregate_by_browser_and_device_from_chunks(visits_table: pq.ParquetFile, chunk_size: int) -> list:
    agg_data = []
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        if 'ym:s:browser' in df_batch.columns and 'ym:s:deviceCategory' in df_batch.columns:
            group = df_batch.groupby(['ym:s:browser', 'ym:s:deviceCategory']).agg(
                visits=('ym:s:visitID', 'count'),
                avg_duration=('ym:s:visitDuration', 'mean'),
                bounce_rate=('ym:s:bounce', 'mean'),
            ).reset_index()
            agg_data.append(group)
    if agg_data:
        final_df = pd.concat(agg_data, ignore_index=True)
        final_df = final_df.groupby(['ym:s:browser', 'ym:s:deviceCategory']).agg(
            visits=('visits', 'sum'),
            avg_duration=('avg_duration', 'mean'),
            bounce_rate=('bounce_rate', 'mean'),
        ).reset_index()
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


def extract_behavior_patterns_from_chunks(visits_table: pq.ParquetFile, hits_table: pq.ParquetFile,
                                          chunk_size: int) -> dict:
    hits_full_df = pd.DataFrame()
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
        hits_full_df = pd.concat([hits_full_df, df_batch], ignore_index=True)
    visits_full_df = pd.DataFrame()
    for batch in visits_table.iter_batches(batch_size=chunk_size):
        df_batch = batch.to_pandas()
        visits_full_df = pd.concat([visits_full_df, df_batch], ignore_index=True)
    visits_with_context = visits_full_df.merge(
        hits_full_df.groupby('ym:pv:clientID').agg(
            total_links=('ym:pv:link', 'sum'),
            total_goals_from_hits=('ym:pv:goalsID', lambda x: x.notna().sum())
        ).reset_index(),
        left_on='ym:s:clientID',
        right_on='ym:pv:clientID',
        how='left'
    )
    visits_with_context['total_links'] = visits_with_context['total_links'].fillna(0)
    visits_with_context['total_goals_from_hits'] = visits_with_context['total_goals_from_hits'].fillna(0)

    def count_goals_from_visit(goals_str):
        if pd.isna(goals_str):
            return 0
        goals_list = str(goals_str).split(',')
        return len([g for g in goals_list if g.strip()])

    visits_with_context['total_goals_from_visits'] = visits_with_context['ym:s:goalsID'].apply(count_goals_from_visit)
    visits_with_context['total_goals'] = (
            visits_with_context['total_goals_from_hits'] + visits_with_context['total_goals_from_visits']
    )
    patterns = {
        'aimless_users': [],
        'readability_issues': [],
        'navigation_issues': [],
        'cycling_users': []
    }
    for idx, row in visits_with_context.iterrows():
        end_url = row.get('ym:s:endURL', '')
        duration = row.get('ym:s:visitDuration', 0)
        total_goals = row['total_goals']
        total_links = row['total_links']
        goes_to_contacts = end_url.startswith('/contacts')
        if total_goals == 0 and duration > 0:
            patterns['aimless_users'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'endURL': end_url,
                'visitDuration': duration
            })
        if goes_to_contacts and duration < 15:
            patterns['readability_issues'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'endURL': end_url,
                'visitDuration': duration,
                'description': 'Пользователь ушёл в /contacts, проведя мало времени на сайте'
            })
        if goes_to_contacts and total_links == 0:
            patterns['navigation_issues'].append({
                'visitID': row.get('ym:s:visitID', 'unknown'),
                'clientID': row['ym:s:clientID'],
                'endURL': end_url,
                'total_links': total_links,
                'description': 'Пользователь ушёл в /contacts, не кликая по внутренним ссылкам'
            })
    path_analysis = extract_cycling_patterns_from_hits(hits_full_df)
    patterns['cycling_users'] = path_analysis
    return patterns


def extract_cycling_patterns_from_hits(hits_df):
    df = hits_df.sort_values(['ym:pv:clientID', 'ym:pv:watchID'])
    paths = df.groupby('ym:pv:clientID')['clean_url'].apply(list).reset_index()
    cycling = []
    for idx, row in paths.iterrows():
        path = row['clean_url']
        unique_pages = set(path)
        if len(unique_pages) / len(path) < 0.7:
            cycling.append({
                'clientID': row['ym:pv:clientID'],
                'path_length': len(path),
                'unique_pages_count': len(unique_pages),
                'path_sample': path[:10],
                'description': 'Пользователь циклически ходит между страницами'
            })
    return cycling