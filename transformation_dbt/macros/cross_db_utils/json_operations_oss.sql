{#
    Adapter Macros for the following functions:
    - Postgres: json_extract_path_text(<from_json>, 'path' [, 'path' [, ...}}) -> https://www.postgresql.org/docs/12/functions-json.html
#}

{# json_extract_text_custom -------------------------------------------------     #}

{% macro json_extract_text_custom(jcolumn, json_path, dtype) -%}
    {%- if dtype %}
        json_extract_path_text({{ jcolumn }}::json, '{{ json_path|join("','") }}')::{{ dtype }}
    {%- else -%}
        json_extract_path_text({{ jcolumn }}::json,  '{{ json_path|join("','") }}')
    {%- endif -%}

{%- endmacro %}
