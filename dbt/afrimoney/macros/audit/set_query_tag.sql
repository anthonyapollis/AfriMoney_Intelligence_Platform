{#
    Stamps every statement dbt issues with a JSON query tag.

    Snowflake's QUERY_HISTORY is the only place credit spend can be attributed
    after the fact. Without a tag, a $400 month is an undifferentiated blob; with
    one, spend can be grouped by model, materialization and target, which is how
    you find that a single full-refresh mart is eating 40% of the warehouse.

    dbt-snowflake calls set_query_tag / unset_query_tag around each node
    automatically — overriding them here changes what gets stamped.
#}

{% macro set_query_tag() -%}

    {%- set tag_payload = {
        "dbt_project":     project_name,
        "dbt_model":       model.name if model is defined else "unknown",
        "dbt_resource":    model.resource_type if model is defined else "unknown",
        "dbt_target":      target.name,
        "dbt_invocation":  invocation_id,
        "dbt_user":        target.user
    } -%}

    {%- set original_query_tag = get_current_query_tag() -%}
    {{ log("Setting query_tag: " ~ tojson(tag_payload), info=false) }}
    {% call statement('set_query_tag', fetch_result=false) %}
        alter session set query_tag = '{{ tojson(tag_payload) }}';
    {% endcall %}
    {{ return(original_query_tag) }}

{%- endmacro %}
