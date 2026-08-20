{#
    Overrides dbt's default schema-naming behaviour.

    dbt's default prefixes the target schema onto the custom schema
    (e.g. target "dev_anthony" + custom "GOLD" -> "dev_anthony_GOLD"),
    which is right for dev but wrong for prod — in prod we want the bare
    schema name so Power BI and the Snowflake roles point at a stable
    AFRIMONEY_DB.GOLD regardless of who ran the build.

    Rules:
      prod target  -> use the custom schema verbatim  (GOLD, SILVER, BRONZE)
      any other    -> prefix with the developer's target schema so two
                      engineers never collide in the same database
#}

{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}

        {{ default_schema }}

    {%- elif target.name == 'prod' -%}

        {{ custom_schema_name | trim | upper }}

    {%- else -%}

        {{ default_schema | trim }}_{{ custom_schema_name | trim | upper }}

    {%- endif -%}

{%- endmacro %}
