STATE_TEMPLATE = """
{{ get_frame_html(global_frame) }}
<!-- TODO: Draw the memory_state too. -->
"""

ELEMENT_TEMPLATE = """
{% for flag in flags %}
  {{ get_flag_html(flag) }}
{% endfor %}
"""

FLAG_TEMPLATE = """
<div class="pyagram-flag">
  <div class="pyagram-banner {% if is_curr_element %} curr-element {% endif %}">
    <!-- TODO -->
    <p>TODO</p>
    <!-- TODO -->
  </div>
  {{ get_element_html(this) }}
  {% if frame is none %}
    <p>...</p>
  {% else %}
    {{ get_frame_html(frame) }}
  {% endif %}
</div>
"""

FRAME_TEMPLATE = """
<div class="pyagram-frame {% if is_curr_element %} curr-element {% endif %}">
  <p>
    {% if id == 0 %}
      Global Frame
    {% else %}
      Frame {{ id }} (parent: Frame {{ parent_id }})
    {% endif %}
  </p>
  <table class="frame-bindings-table mono">
    {% for key, value in bindings.items() %} <!-- TODO: Verify these show up in the right order! -->
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
