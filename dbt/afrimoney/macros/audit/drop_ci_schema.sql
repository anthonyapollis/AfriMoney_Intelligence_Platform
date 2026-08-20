{#
    Tears down a CI schema after a pull-request build.

    Invoked from the workflow as:
        dbt run-operation drop_ci_schema --args "{schema_name: CI_PR_42}"

    Guarded deliberately hard. A run-operation that issues DROP SCHEMA CASCADE is
    exactly the sort of thing that, given a wrong argument, deletes GOLD. The
    guards below make that impossible rather than unlikely:

      1. The name must start with CI_ — no other schema can ever be targeted.
      2. Refuses to run against the prod target at all.
      3. Logs the fully-qualified name before dropping, so the destructive act is
         always visible in the CI transcript.
#}

{% macro drop_ci_schema(schema_name) %}

    {% if target.name == 'prod' %}
        {{ exceptions.raise_compiler_error(
            "drop_ci_schema refuses to run against the prod target."
        ) }}
    {% endif %}

    {% if not schema_name %}
        {{ exceptions.raise_compiler_error("drop_ci_schema requires schema_name.") }}
    {% endif %}

    {% set schema_upper = schema_name | upper | trim %}

    {% if not schema_upper.startswith('CI_') %}
        {{ exceptions.raise_compiler_error(
            "Refusing to drop '" ~ schema_upper ~ "' — only CI_-prefixed schemas may be dropped."
        ) }}
    {% endif %}

    {{ log("Dropping CI schema " ~ target.database ~ "." ~ schema_upper, info=true) }}

    {% call statement('drop_ci_schema', fetch_result=false) %}
        drop schema if exists {{ target.database }}.{{ schema_upper }} cascade;
    {% endcall %}

    {{ log("Dropped " ~ schema_upper ~ ".", info=true) }}

{% endmacro %}
