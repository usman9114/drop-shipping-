{# Small generic test so we need no package download (no dbt_utils download needed). #}
{% test in_range(model, column_name, min=none, max=none) %}
select * from {{ model }}
where {{ column_name }} is not null
  and ({% if min is not none %}{{ column_name }} < {{ min }}{% else %}false{% endif %}
       or {% if max is not none %}{{ column_name }} > {{ max }}{% else %}false{% endif %})
{% endtest %}
