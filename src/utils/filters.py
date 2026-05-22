from typing import Any

RESERVED_PARAMS = {"name", "category_id", "limit", "offset", "start_id"}


def parse_param_filters(query_params: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parses query parameters into a list of parameter filter dicts.

    Conventions:
      {short_name}_min=N   → {"short_name": ..., "min": N}
      {short_name}_max=N   → {"short_name": ..., "max": N}
      {short_name}_contains=S → {"short_name": ..., "contains": S}
      {short_name}=V       → {"short_name": ..., "eq": V}

    Reserved keys (name, category_id, limit, offset, start_id) are ignored.
    """
    filters = []

    for key, value in query_params.items():
        if key in RESERVED_PARAMS:
            continue

        if key.endswith("_min"):
            try:
                filters.append({"short_name": key[:-4], "min": float(value)})
            except ValueError:
                pass
        elif key.endswith("_max"):
            try:
                filters.append({"short_name": key[:-4], "max": float(value)})
            except ValueError:
                pass
        elif key.endswith("_contains"):
            filters.append({"short_name": key[:-9], "contains": value})
        else:
            filters.append({"short_name": key, "eq": value})

    return filters
