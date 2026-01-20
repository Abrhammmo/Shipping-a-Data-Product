def classify_image(detected_objects):
    labels = {label for label, _ in detected_objects}

    if "person" in labels and labels & {"bottle", "container"}:
        return "promotional"
    if labels & {"bottle", "container"}:
        return "product_display"
    if "person" in labels:
        return "lifestyle"
    return "other"
