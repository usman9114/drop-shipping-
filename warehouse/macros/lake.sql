{# Read one lake dataset (scout.store runs) with an explicit column contract.
   Only the latest run is kept unless all_runs=true. #}
{% macro lake(dataset, columns, all_runs=false) %}
  {%- set root = env_var('SCOUT_LAKE', '../data/private/lake') -%}
  {%- set cols = [] -%}
  {%- for name, type in columns.items() -%}{%- do cols.append("'" ~ name ~ "': '" ~ type ~ "'") -%}{%- endfor -%}
  (
    select *
    from read_json('{{ root }}/{{ dataset }}/*/*.jsonl.gz',
                   format = 'newline_delimited',
                   columns = { {{ cols | join(', ') }}, 'run_id': 'VARCHAR' })
    {% if not all_runs %}
    qualify run_id = max(run_id) over ()
    {% endif %}
  )
{% endmacro %}

{# Schema names without the target prefix: stg, enrich, core, mart, rules. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ custom_schema_name | trim if custom_schema_name else target.schema }}
{%- endmacro %}
