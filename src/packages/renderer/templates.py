STATE_TEMPLATE = """
<table>
  <tr>
    <td valign="top">
      {{ get_frame_html(global_frame) }}
    </td>
    <td valign="top">
      {% for object in memory_state %}
        {{ get_object_html(object) }}
      {% endfor %}
    </td>
  </tr>
</table>
"""

ELEMENT_TEMPLATE = """
{% for flag in flags %}
  {{ get_flag_html(flag) }}
{% endfor %}
"""

FLAG_TEMPLATE = """
<div class="pyagram-flag">
  <div class="pyagram-banner {% if is_curr_element %} curr-element {% endif %}">
    <table class="banner-bindings-table mono">
      <tr>
        {% for label, bindings in banner %}
          <td class="binding-var" {% if bindings|length > 0 %} colspan="{{ bindings|length }}" {% endif %}>
            {{ label }} <!-- TODO: What if a parameter is bound to valid HTML? -->
          </td>
        {% endfor %}
      </tr>
      <tr>
        {% for label, bindings in banner %}
          {% if bindings|length == 0 %}
            <td></td>
          {% else %}
            {% for binding in bindings %}
              <td class="binding-val {% if binding is none %} invisble {% endif %}">
                {% if binding is none %}
                  -
                {% else %}
                  {{ get_reference_html(binding) }}
                {% endif %}
              </td>
            {% endfor %}
          {% endif %}
        {% endfor %}
      </tr>
    </table>
  </div>
  {{ get_element_html(this) }}
  {% if frame is none %}
    <p class="invisble mono">...</p>
  {% else %}
    {{ get_frame_html(frame) }}
  {% endif %}
</div>
"""

FRAME_TEMPLATE = """
<div class="pyagram-frame {% if is_curr_element %} curr-element {% endif %}">
  <p>
    {{ name }}
    {% if parent is not none %}
      {{ get_parent_frame_html(parent) }}
    {% endif %}
  </p>
  <table class="frame-bindings-table mono">
    {% for key, value in bindings.items() %}
      <tr>
        <td class="binding-var">{{ key }}</td>
        <td class="binding-val">{{ get_reference_html(value) }}</td>
      </tr>
    {% endfor %}
    {% if return_value is not none %}
      <tr>
        <td class="binding-ret">Return value</td>
        <td class="binding-val">{{ get_reference_html(return_value) }}</td>
      </tr>
    {% endif %}
  </table>
</div>
{{ get_element_html(this) }}
"""

LINK_TEMPLATE = """
<a href="{{ link }}">{{ text }}</a>
"""

FUNCTION_TEMPLATE = """
  <div>
    function
    <span class="mono">
      {{ name }}(
        {% for parameter in parameters %}
          {{ get_parameter_html(parameter) }}
        {% endfor %}
      )
    </span>
    {{ get_parent_frame_html(parent) }}
  </div>
"""

ORDERED_COLLECTION_TEMPLATE = """
  TODO
"""

UNORDERED_COLLECTION_TEMPLATE = """
  TODO
"""

MAPPING_TEMPLATE = """
  TODO
"""

ITERATOR_TEMPLATE = """
  TODO
"""

GENERATOR_TEMPLATE = """
  TODO
"""

OBJECT_FRAME_TEMPLATE = """
  TODO
"""

OBJECT_REPR_TEMPLATE = """
  TODO
"""

PARENT_FRAME_TEMPLATE = """
  [parent: {{ parent_frame_name }}]
"""

PARAMETER_TEMPLATE = """
  {{ name }} {% if default is not none %}={{ get_reference_html(default) }}{% endif %}
  <!-- TODO: The default value should appear in a black box, like a frame binding. -->
"""
