from collections import Counter

import pandas as pd


def extract_metrics_from_csv(hits_path: str, visits_path: str):
    hits_df = pd.read_csv(hits_path)
    visits_df = pd.read_csv(visits_path)

    metrics = {
        "visits_count": len(visits_df),
        "hits_count": len(hits_df),
        "avg_visit_duration": visits_df['ym:s:visitDuration'].mean() if 'ym:s:visitDuration' in visits_df.columns else 0,
        "bounce_rate": visits_df['ym:s:bounce'].mean() if 'ym:s:bounce' in visits_df.columns else 0,
        "avg_page_views": visits_df['ym:s:pageViews'].mean() if 'ym:s:pageViews' in visits_df.columns else 0,
        "error_rate": (hits_df['ym:pv:httpError'] != 0).mean() if 'ym:pv:httpError' in hits_df.columns else 0,
        "not_bounce_rate": hits_df['ym:pv:notBounce'].mean() if 'ym:pv:notBounce' in hits_df.columns else 0,
        "link_click_rate": hits_df['ym:pv:link'].mean() if 'ym:pv:link' in hits_df.columns else 0,
    }

    if 'ym:s:goalsID' in visits_df.columns:
        goals_str = " ".join(visits_df['ym:s:goalsID'].dropna().astype(str))
        goals_list = goals_str.replace(',', ' ').split()
        goal_counts = Counter(goals_list)
        metrics['form_view_count'] = goal_counts.get('94939123', 0)
        metrics['form_submit_count'] = goal_counts.get('94939720', 0)
        metrics['vk_contact_clicks'] = goal_counts.get('225392702', 0)
        metrics['tg_contact_clicks'] = goal_counts.get('225392736', 0)

    if 'ym:s:deviceCategory' in visits_df.columns:
        device_counts = visits_df['ym:s:deviceCategory'].value_counts().to_dict()
        metrics['device_category_distribution'] = device_counts

    if 'ym:s:operatingSystem' in visits_df.columns:
        os_counts = visits_df['ym:s:operatingSystem'].value_counts().to_dict()
        metrics['os_distribution'] = os_counts

    return metrics