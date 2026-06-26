def format_risk_label(risk_level):
    return risk_level.replace("_", " ").title()


def format_optional_days(days_until_critical):
    if days_until_critical != days_until_critical:
        return "No crossing"

    return f"{int(days_until_critical)} days"
