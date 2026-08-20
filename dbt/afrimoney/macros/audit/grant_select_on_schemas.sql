{#
    Idempotent role grants applied at the end of every production run.

    New models otherwise land in GOLD invisible to the BI service account until
    someone remembers to grant on them. Running this on-run-end means a model
    added on Friday is queryable by Power BI on Friday, not the following
    Tuesday after a support ticket.

    Future grants cover objects that don't exist yet; the plain grant covers
    everything already there.
#}

{% macro grant_select_on_schemas() %}

    {% if target.name != 'prod' %}
        {{ log("Skipping grants — not a prod target.", info=true) }}
        {{ return('') }}
    {% endif %}

    {% set roles = ['AFRIMONEY_ANALYST', 'AFRIMONEY_BI_SERVICE'] %}
    {% set schemas = ['SILVER', 'GOLD'] %}

    {% for schema in schemas %}
        {% for role in roles %}
            {% call statement('grant_' ~ schema ~ '_' ~ role, fetch_result=false) %}
                grant usage on schema {{ target.database }}.{{ schema }} to role {{ role }};
                grant select on all tables    in schema {{ target.database }}.{{ schema }} to role {{ role }};
                grant select on all views     in schema {{ target.database }}.{{ schema }} to role {{ role }};
                grant select on future tables in schema {{ target.database }}.{{ schema }} to role {{ role }};
                grant select on future views  in schema {{ target.database }}.{{ schema }} to role {{ role }};
            {% endcall %}
        {% endfor %}
    {% endfor %}

    {{ log("Grants refreshed on SILVER and GOLD.", info=true) }}

{% endmacro %}
