# Utility functions

def build_options(subject, df):
    series = df[subject]
    option_list = [{'label': i.replace("_", " ").title(), 'value': i} for i in series.unique()]
    # Uncomment if you need to remove specific POI types from the dropdown menus
    # banned_metrics = ['Strategic Centre', 'Job Centre']
    # option_list = [e for e in option_list if e['value'] not in banned_metrics]
    return option_list


def build_options_from_list(list):
    option_list = [{'label': i, 'value': i} for i in list]
    return option_list


