{#
    Appends a JSON comment to every statement dbt sends to Snowflake.

    Distinct from set_query_tag: the query tag is a single indexed session
    parameter that is cheap to GROUP BY in QUERY_HISTORY, whereas this comment
    is embedded in the SQL text itself and survives into anything that captures
    raw statements — third-party monitoring, Snowflake's query profile export,
    and a DBA staring at a slow query with no idea where it came from.

    Between them, "which model is burning credits" and "what is this query and
    who deployed it" both become answerable without asking the data team.
#}

{% macro query_comment(node) %}

    {%- set comment_dict = {
        'app':            'dbt',
        'dbt_version':    dbt_version,
        'project':        project_name,
        'target':         target.name,
        'profile':        target.profile_name,
        'invocation_id':  invocation_id,
        'run_started_at': run_started_at | string
    } -%}

    {%- if node is not none -%}
        {%- do comment_dict.update(
            node_id       = node.unique_id,
            node_name     = node.name,
            resource_type = node.resource_type,
            package       = node.package_name,
            relation      = {
                'database': node.database,
                'schema':   node.schema,
                'identifier': node.identifier
            }
        ) -%}
    {%- else -%}
        {%- do comment_dict.update(node_id = 'internal') -%}
    {%- endif -%}

    {{ return(tojson(comment_dict)) }}

{% endmacro %}
