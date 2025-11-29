def compare_versions_full(v1_data: dict, v2_data: dict) -> dict:
    comparison = {
        "metrics_comparison": compare_versions_metrics(v1_data["metrics"], v2_data["metrics"]),
        #"patterns_comparison": compare_patterns(v1_data["patterns"], v2_data["patterns"]),
        "device_comparison": compare_device_agg(v1_data["device_agg"], v2_data["device_agg"]),
        "funnels_comparison": compare_conversion_funnels(v1_data["funnels"], v2_data["funnels"]),
        "utm_source_comparison": compare_utm_source_impact(v1_data["metrics"], v2_data["metrics"]),
        "error_rates_comparison": compare_error_rates_by_page(v1_data["metrics"], v2_data["metrics"]),
        "time_on_page_comparison": compare_time_on_page(v1_data["metrics"], v2_data["metrics"]),
        "new_vs_returning_comparison": compare_new_vs_returning_users(v1_data["metrics"], v2_data["metrics"]),
        "goals_completion_comparison": compare_goals_completion(v1_data["metrics"], v2_data["metrics"]),
        "device_performance_comparison": compare_device_performance_by_metric(v1_data["metrics"], v2_data["metrics"]),
        "os_browser_performance_comparison": compare_os_browser_performance(v1_data["metrics"], v2_data["metrics"]),
        "session_depth_comparison": compare_session_depth_and_pages(v1_data["metrics"], v2_data["metrics"]),
        "form_interactions_comparison": compare_form_interactions(v1_data["metrics"], v2_data["metrics"]),
    }
    return comparison

def compare_versions_metrics(metrics_v1: dict, metrics_v2: dict) -> dict:
    comparison = {}
    for key in metrics_v1:
        if key in metrics_v2:
            val1 = metrics_v1[key]
            val2 = metrics_v2[key]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                delta = val2 - val1
                delta_pct = (delta / val1 * 100) if val1 != 0 else 0
                comparison[key] = {
                    "v1": val1,
                    "v2": val2,
                    "delta": delta,
                    "delta_pct": round(delta_pct, 2)
                }
            else:
                comparison[key] = {"v1": val1, "v2": val2, "delta": "N/A"}
    return comparison

def compare_device_agg(device_agg_v1: list, device_agg_v2: list) -> dict:
    def list_to_dict(agg_list):
        result = {}
        for item in agg_list:
            key = (item.get('ym:s:deviceCategory'), item.get('ym:s:operatingSystem'))
            result[key] = item
        return result

    dict_v1 = list_to_dict(device_agg_v1)
    dict_v2 = list_to_dict(device_agg_v2)

    comparison = {
        "common_segments": {},
        "only_in_v1": [],
        "only_in_v2": []
    }

    all_keys = set(dict_v1.keys()) | set(dict_v2.keys())

    for key in all_keys:
        v1_data = dict_v1.get(key)
        v2_data = dict_v2.get(key)

        if v1_data is not None and v2_data is not None:
            segment_comparison = {}
            for metric in ['visits', 'avg_duration', 'bounce_rate', 'form_view_rate', 'form_submit_rate']:
                v1_val = v1_data.get(metric, 0)
                v2_val = v2_data.get(metric, 0)
                if isinstance(v1_val, (int, float)) and isinstance(v2_val, (int, float)):
                    delta = v2_val - v1_val
                    delta_pct = (delta / v1_val * 100) if v1_val != 0 else 0
                    segment_comparison[metric] = {
                        "v1": v1_val,
                        "v2": v2_val,
                        "delta": delta,
                        "delta_pct": round(delta_pct, 2)
                    }
            comparison["common_segments"][str(key)] = segment_comparison
        elif v1_data is not None:
            comparison["only_in_v1"].append(key)
        elif v2_data is not None:
            comparison["only_in_v2"].append(key)

    return comparison

def compare_patterns(patterns_v1: dict, patterns_v2: dict) -> dict:
    comparison = {}
    all_pattern_types = set(patterns_v1.keys()) | set(patterns_v2.keys())

    for p_type in all_pattern_types:
        list_v1 = patterns_v1.get(p_type, [])
        list_v2 = patterns_v2.get(p_type, [])

        count_v1 = len(list_v1)
        count_v2 = len(list_v2)
        delta = count_v2 - count_v1
        delta_pct = (delta / count_v1 * 100) if count_v1 != 0 else 0

        comparison[p_type] = {
            "v1_count": count_v1,
            "v2_count": count_v2,
            "delta": delta,
            "delta_pct": round(delta_pct, 2)
        }

    return comparison

def compare_utm_source_impact(metrics_v1: dict, metrics_v2: dict) -> dict:
    utm1 = metrics_v1.get('utm_source_distribution', {})
    utm2 = metrics_v2.get('utm_source_distribution', {})
    comparison = {}
    all_sources = set(utm1.keys()) | set(utm2.keys())
    for src in all_sources:
        v1_val = utm1.get(src, 0)
        v2_val = utm2.get(src, 0)
        delta = v2_val - v1_val
        delta_pct = (delta / v1_val * 100) if v1_val != 0 else 0
        comparison[src] = {
            "v1": v1_val,
            "v2": v2_val,
            "delta": delta,
            "delta_pct": round(delta_pct, 2)
        }
    return comparison

def compare_error_rates_by_page(metrics_v1: dict, metrics_v2: dict) -> dict:
    errors_v1 = metrics_v1.get('page_error_rates', {})
    errors_v2 = metrics_v2.get('page_error_rates', {})
    comparison = {}
    all_pages = set(errors_v1.keys()) | set(errors_v2.keys())
    for page in all_pages:
        v1_rate = errors_v1.get(page, 0)
        v2_rate = errors_v2.get(page, 0)
        delta = v2_rate - v1_rate

        comparison[page] = {
            "v1_error_rate": v1_rate,
            "v2_error_rate": v2_rate,
            "delta": delta
        }
    return comparison

def compare_time_on_page(metrics_v1: dict, metrics_v2: dict) -> dict:
    time_v1 = metrics_v1.get('avg_time_per_page', {})
    time_v2 = metrics_v2.get('avg_time_per_page', {})
    comparison = {}
    all_pages = set(time_v1.keys()) | set(time_v2.keys())
    for page in all_pages:
        v1_time = time_v1.get(page, 0)
        v2_time = time_v2.get(page, 0)
        delta = v2_time - v1_time
        delta_pct = (delta / v1_time * 100) if v1_time != 0 else 0
        if abs(delta_pct)>99 or abs(delta_pct)<1:
            continue
        comparison[page] = {
            "v1_avg_time": v1_time,
            "v2_avg_time": v2_time,
            "delta": delta,
            "delta_pct": round(delta_pct, 2)
        }
    return comparison

def compare_new_vs_returning_users(metrics_v1: dict, metrics_v2: dict) -> dict:
    new_v1 = metrics_v1.get('new_user_metrics', {})
    new_v2 = metrics_v2.get('new_user_metrics', {})
    returning_v1 = metrics_v1.get('returning_user_metrics', {})
    returning_v2 = metrics_v2.get('returning_user_metrics', {})

    comparison = {
        'new_users': {
            'bounce_rate': {'v1': new_v1.get('bounce_rate', 0), 'v2': new_v2.get('bounce_rate', 0)},
            'avg_duration': {'v1': new_v1.get('avg_duration', 0), 'v2': new_v2.get('avg_duration', 0)},
            'conversion_rate': {'v1': new_v1.get('conversion_rate', 0), 'v2': new_v2.get('conversion_rate', 0)}
        },
        'returning_users': {
            'bounce_rate': {'v1': returning_v1.get('bounce_rate', 0), 'v2': returning_v2.get('bounce_rate', 0)},
            'avg_duration': {'v1': returning_v1.get('avg_duration', 0), 'v2': returning_v2.get('avg_duration', 0)},
            'conversion_rate': {'v1': returning_v1.get('conversion_rate', 0), 'v2': returning_v2.get('conversion_rate', 0)}
        }
    }
    return comparison

def compare_goals_completion(metrics_v1: dict, metrics_v2: dict) -> dict:
    goals_v1 = metrics_v1.get('goals', {})
    goals_v2 = metrics_v2.get('goals', {})
    comparison = {}
    all_goals = set(goals_v1.keys()) | set(goals_v2.keys())
    for goal in all_goals:
        v1_count = goals_v1.get(goal, 0)
        v2_count = goals_v2.get(goal, 0)
        delta = v2_count - v1_count
        comparison[goal] = {
            "v1_count": v1_count,
            "v2_count": v2_count,
            "delta": delta
        }
    return comparison

def compare_device_performance_by_metric(metrics_v1: dict, metrics_v2: dict) -> dict:
    dev_v1 = metrics_v1.get('device_metrics', {})
    dev_v2 = metrics_v2.get('device_metrics', {})
    comparison = {}
    all_devices = set(dev_v1.keys()) | set(dev_v2.keys())
    for device in all_devices:
        v1_bounce = dev_v1.get(device, {}).get('bounce_rate', 0)
        v2_bounce = dev_v2.get(device, {}).get('bounce_rate', 0)
        v1_duration = dev_v1.get(device, {}).get('avg_duration', 0)
        v2_duration = dev_v2.get(device, {}).get('avg_duration', 0)
        comparison[device] = {
            "bounce": {"v1": v1_bounce, "v2": v2_bounce, "delta": v2_bounce - v1_bounce},
            "duration": {"v1": v1_duration, "v2": v2_duration, "delta": v2_duration - v1_duration}
        }
    return comparison

def compare_os_browser_performance(metrics_v1: dict, metrics_v2: dict) -> dict:
    os_v1 = metrics_v1.get('os_metrics', {})
    os_v2 = metrics_v2.get('os_metrics', {})
    browser_v1 = metrics_v1.get('browser_metrics', {})
    browser_v2 = metrics_v2.get('browser_metrics', {})

    os_comparison = {}
    all_os = set(os_v1.keys()) | set(os_v2.keys())
    for os in all_os:
        v1_conv = os_v1.get(os, {}).get('conversion_rate', 0)
        v2_conv = os_v2.get(os, {}).get('conversion_rate', 0)
        if abs( (v1_conv - v2_conv) / v1_conv ) > 0.05:
            os_comparison[os] = {"v1_conv_rate": v1_conv, "v2_conv_rate": v2_conv}

    browser_comparison = {}
    all_browsers = set(browser_v1.keys()) | set(browser_v2.keys())
    for browser in all_browsers:
        v1_bounce = browser_v1.get(browser, {}).get('bounce_rate', 0)
        v2_bounce = browser_v2.get(browser, {}).get('bounce_rate', 0)
        if abs( (v2_bounce - v1_bounce) / v1_bounce ) > 0.05:
            browser_comparison[browser] = {"v1_bounce": v1_bounce, "v2_bounce": v2_bounce}

    return {"os": os_comparison, "browser": browser_comparison}

def compare_session_depth_and_pages(metrics_v1: dict, metrics_v2: dict) -> dict:
    depth_v1 = metrics_v1.get('avg_page_depth', 0)
    depth_v2 = metrics_v2.get('avg_page_depth', 0)
    pages_v1 = metrics_v1.get('avg_pages_per_session', 0)
    pages_v2 = metrics_v2.get('avg_pages_per_session', 0)

    comparison = {
        "avg_page_depth": {"v1": depth_v1, "v2": depth_v2, "delta": depth_v2 - depth_v1},
        "avg_pages_per_session": {"v1": pages_v1, "v2": pages_v2, "delta": pages_v2 - pages_v1}
    }
    return comparison

def compare_form_interactions(metrics_v1: dict, metrics_v2: dict) -> dict:
    form_v1 = metrics_v1.get('form_metrics', {})
    form_v2 = metrics_v2.get('form_metrics', {})

    comparison = {
        "form_view_rate": {"v1": form_v1.get('view_rate', 0), "v2": form_v2.get('view_rate', 0)},
        "form_submit_rate": {"v1": form_v1.get('submit_rate', 0), "v2": form_v2.get('submit_rate', 0)},
        "form_drop_off": {"v1": form_v1.get('drop_off_rate', 0), "v2": form_v2.get('drop_off_rate', 0)}
    }
    return comparison

def compare_conversion_funnels(funnels_v1: dict, funnels_v2: dict) -> dict:
    comparison = {}
    steps = set(funnels_v1.keys()) | set(funnels_v2.keys())
    for step in steps:
        v1_count = funnels_v1.get(step, 0)
        v2_count = funnels_v2.get(step, 0)
        conversion_v1 = funnels_v1.get('conversion_rate', 0)
        conversion_v2 = funnels_v2.get('conversion_rate', 0)
        comparison[step] = {
            "v1_count": v1_count,
            "v2_count": v2_count,
            "v1_conversion_rate": conversion_v1,
            "v2_conversion_rate": conversion_v2
        }
    return comparison