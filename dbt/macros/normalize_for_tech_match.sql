-- dbt/macros/normalize_for_tech_match.sql
{% macro normalize_for_tech_match(column_expr) %}
    ' ' || regexp_replace(
        replace(replace(lower({{ column_expr }}), 'c#', 'csharp'), 'c++', 'cplusplus'),
        '[^a-z0-9]+', ' ', 'g'
    ) || ' '
{% endmacro %}