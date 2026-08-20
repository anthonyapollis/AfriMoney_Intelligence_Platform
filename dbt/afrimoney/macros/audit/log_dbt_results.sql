{#
    Run-level audit logging.

    Every dbt invocation appends one row per node to AFRIMONEY_DB.META.DBT_RUN_AUDIT.
    This is what makes "when did mart_remittance last actually succeed, and how
    long has it been getting slower?" answerable without digging through CI logs
    that expire after 30 days.

    Wired up via on-run-end in dbt_project.yml. `results` is injected by dbt.
#}

{% macro log_dbt_results(results) %}

    {#- Nothing to log on a parse-only or empty invocation -#}
    {% if results is none or results | length == 0 %}
        {{ return('select 1 where false') }}
    {% endif %}

    {#- Only emit DDL/DML during a real run, not during docs generate -#}
    {% if flags.WHICH not in ('run', 'build', 'test', 'snapshot', 'seed') %}
        {{ return('select 1 where false') }}
    {% endif %}

    create table if not exists {{ target.database }}.META.DBT_RUN_AUDIT (
        invocation_id   varchar,
        run_started_at  timestamp_ntz,
        node_id         varchar,
        node_name       varchar,
        resource_type   varchar,
        materialization varchar,
        schema_name     varchar,
        status          varchar,
        rows_affected   number,
        execution_time  float,
        target_name     varchar,
        dbt_version     varchar,
        logged_at       timestamp_ntz
    );

    insert into {{ target.database }}.META.DBT_RUN_AUDIT
    (
        invocation_id, run_started_at, node_id, node_name, resource_type,
        materialization, schema_name, status, rows_affected, execution_time,
        target_name, dbt_version, logged_at
    )
    values
    {%- for res in results %}
        {%- set node = res.node %}
        (
            '{{ invocation_id }}',
            '{{ run_started_at }}'::timestamp_ntz,
            '{{ node.unique_id }}',
            '{{ node.name }}',
            '{{ node.resource_type }}',
            '{{ node.config.materialized | default("n/a") }}',
            '{{ node.schema }}',
            '{{ res.status }}',
            {{ res.adapter_response.get("rows_affected", "null") if res.adapter_response else "null" }},
            {{ res.execution_time | round(4) }},
            '{{ target.name }}',
            '{{ dbt_version }}',
            current_timestamp()::timestamp_ntz
        ){{ "," if not loop.last }}
    {%- endfor %}
    ;

{% endmacro %}
