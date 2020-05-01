function compile(template) {
    return Handlebars.compile(template.trim(), {
        noEscape: true,
        assumeObjects: true,
    });
}

export const PYAGRAM_TEMPLATE = compile(`
<div class="overlap-wrapper">
  <table class="overlap border-collapse font-family-monospace" id="pyagram-state-table">
    <tr>
      <td class="align-top">
        {{decodeFrameSnapshot global_frame}}
      </td>
      <td class="align-top pl-5">
        {{#each memory_state}}
          {{decodeObjectSnapshot this}}
        {{/each}}
      </td>
    </tr>
  </table>
  <svg class="overlap" id="pyagram-svg-canvas" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <marker id="circle" markerWidth="6.5" markerHeight="6.5" refX="5" refY="5">
        <circle cx="5" cy="5" r="1.5" fill="black"/>
      </marker>
      <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="5" viewBox="0 0 10 10" orient="auto">
        <path d="M0,0 L10,5 0,10 Z"/>
      </marker>
    </defs>
    <g id="pointers" fill="none" stroke="black" stroke-width="1.5" marker-start="url(#circle)" marker-end="url(#arrowhead)"/>
  </svg>
</div>
`)

export const ELEMENT_TEMPLATE = compile(`
{{#each flags}}
  {{decodeFlagSnapshot this}}
{{/each}}
`)

export const FLAG_TEMPLATE = compile(`
<div class="pyagram-flag m-3">
  <div class="pyagram-banner {{#if is_curr_element}} curr-element {{/if}}">
    <table class="text-center">
      <tr>
        {{#each banner}}
          <td {{#unless (isEmpty bindings)}} colspan="{{sum (mul 2 bindings.length) -1}}" {{/unless}}>
            {{code}}
          </td>
        {{/each}}
      </tr>
      <tr>
        {{#each banner}}
          {{#if (isEmpty bindings)}}
            {{#if (isEqual @index 1)}}
              {{#if @last}}
                <td class="text-left">()</td>
              {{else}}
                <td class="text-left">(</td>
              {{/if}}
            {{else if @last}}
              <td class="text-right">)</td>
            {{else}}
              <td class="text-left">,</td>
            {{/if}}
          {{else}}
            {{#each bindings}}
              <td class="pyagram-value {{#if (isNull this)}} pyagram-placeholder {{/if}}">
                {{#if (isNull this)}}
                  -
                {{else}}
                  {{decodeReferenceSnapshot this}}
                {{/if}}
              </td>
              {{#unless @last}}
                <td>,</td>
              {{/unless}}
            {{/each}}
          {{/if}}
        {{/each}}
      </tr>
    </table>
  </div>
  {{decodeElementSnapshot this}}
  {{#if (isNull frame)}}
    <div class="pyagram-placeholder">
      -
    </div>
  {{else}}
    {{decodeFrameSnapshot frame}}
  {{/if}}
</div>
`)

// TODO: Display the parent(s) too. Put the logic in the if/elif/elif/else cases.
// TODO: Verify this works with classes, instances, and generators (with `yield` + `yield from`).
// TODO: Replace {{key}} with {{decodeBindingSnapshot key}}. In 99.99% of cases the key should be a string; a variable `'var'` should show up as `var`. If it ain't a string, handle it like a ref. (This will require slight modification to encode.py based on the is_bindings parameter.)
// TODO: After doing that, make sure `x = 'hi'` shows up properly: `x` unquoted, but `hi` quoted.
export const FRAME_TEMPLATE = compile(`
<div class="pyagram-frame {{#if (isEqual type 'function')}} mx-3 {{else}} mr-3 {{/if}} my-3 {{#if is_curr_element}} curr-element {{/if}}">
  <div class="pyagram-frame-name">
    {{#if (isEqual type 'function')}}
      <span class="font-family-sans-serif">{{name}}</span>
    {{else if (isEqual type 'generator')}}
      <span class="font-family-sans-serif">generator </span>{{name}}
    {{else if (isEqual type 'class')}}
      <span class="font-family-sans-serif">class </span>{{name}}
    {{else if (isEqual type 'instance')}}
      {{name}}<span class="font-family-sans-serif"> instance</span>
    {{/if}}
  </div>
  <table class="ml-auto mr-0">
    {{#each bindings}}
      <tr>
        <td class="text-right">
          {{key}}
        </td>
        <td class="text-left pyagram-value" {{#unless (isNull ../from)}} colspan="3" {{/unless}}>
          {{decodeReferenceSnapshot value}}
        </td>
      </tr>
    {{/each}}
    {{#unless (isNull return_value)}}
      <tr>
        <td class="text-right font-family-sans-serif">
          {{#if (isEqual type 'generator')}}
            Yield value
          {{else}}
            Return value
          {{/if}}
        </td>
        <td class="text-left pyagram-value">
          {{decodeReferenceSnapshot return_value}}
        </td>
        {{#unless (isNull from)}}
          <td class="text-left font-family-sans-serif">
            from
          </td>
          <td class="text-left pyagram-value">
            {{decodeReferenceSnapshot from}}
          </td>
        {{/unless}}
      </tr>
    {{/unless}}
  </table>
</div>
{{decodeElementSnapshot this}}
`)

export const UNKNOWN_VALUE_TEMPLATE = compile(`
<span class="pyagram-unknown">(?)</span>
`)

export const PRIMITIVE_TEMPLATE = compile(`
{{this}}
`)

export const REFERENT_TEMPLATE = compile(`
<span class="pyagram-placeholder pyagram-reference reference-{{this}}">-</span>
`)

export const OBJECT_TEMPLATE = compile(`
<div id="object-{{id}}" class="pyagram-object m-3">
  {{decodeEncodedObjectSnapshot object}}
</div>
`)

export const FUNCTION_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  {{#if is_gen_func}}
    generator function
  {{else}}
    function
  {{/if}}
</span>
{{#if (isNull lambda_id)}}
  {{~name~}}
{{else}}
  {{~#with lambda_id~}}
    &#955;<sub>{{lineno}}{{#unless single}}#{{number}}{{/unless}}</sub>
  {{~/with~}}
{{/if}}
(
{{~#each parameters~}}
  {{~name~}}
  {{~#unless (isNull default)~}}
    =<span class="pyagram-value">{{decodeReferenceSnapshot default}}</span>
  {{~/unless~}}
  {{~#unless @last}}, {{/unless~}}
{{~/each~}}
)
<div class="font-family-sans-serif">
  [parent: {{parent}}]
</div>
`)

export const BUILTIN_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  function
</span>
{{this}}(...)
`)

export const ORDERED_COLLECTION_TEMPLATE = compile(`
{{#if (isEmpty elements)}}
  <div class="font-family-sans-serif">
    empty {{type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{type}}
    </div>
    <table class="pyagram-ordered-collection border-collapse ml-1" rules="cols">
      <tr>
        {{#each elements}}
          <td class="pyagram-collection-element px-2">{{decodeReferenceSnapshot this}}</td>
        {{/each}}
      </tr>
    </table>
  </div>
{{/if}}
`)

export const UNORDERED_COLLECTION_TEMPLATE = compile(`
{{#if (isEmpty elements)}}
  <div class="font-family-sans-serif">
    empty {{type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{type}}
    </div>
    <table class="pyagram-unordered-collection ml-1">
      <tr>
        {{#each elements}}
          <td class="pyagram-collection-element px-2">{{decodeReferenceSnapshot this}}</td>
        {{/each}}
      </tr>
    </table>
  </div>
{{/if}}
`)

export const MAPPING_TEMPLATE = compile(`
{{#if (isEmpty items)}}
  <div class="font-family-sans-serif">
    empty {{type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{type}}
    </div>
    <table class="pyagram-mapping border-collapse ml-1" rules="cols">
      <tr>
        {{#each items}}
          <td class="pyagram-mapping-key px-2 text-center">{{decodeReferenceSnapshot key}}</td>
        {{/each}}
      </tr>
      <tr>
        {{#each items}}
          <td class="pyagram-mapping-value px-2 text-center">{{decodeReferenceSnapshot value}}</td>
        {{/each}}
      </tr>
    </table>
  </div>
{{/if}}
`)

export const ITERATOR_TEMPLATE = compile(`
{{#if (isNull object)}}
  <div class="font-family-sans-serif">
    empty iterator
  </div>
{{else}}
  <span class="font-family-sans-serif">
    iterator over
  </span>
  <span class="pyagram-value">
    {{~decodeReferenceSnapshot object~}}
  </span>
  {{~#unless (isNull annotation)~}}
    <span class="font-family-sans-serif">
      {{annotation}}
    </span>
  {{~/unless~}}
  <div class="font-family-sans-serif">
    [next index: {{index}}]
  </div>
{{/if}}
`)

// TODO: Reconsider how you display these.
export const OTHER_TEMPLATE = compile(`
{{this}}
`)

// PRINT_TEMPLATE = """
// {% for line in print_output %}
//   <div class="print-output {% if is_exception %} pyagram-exception {% endif %} font-family-monospace">
//     {{ line }}
//   </div>
// {% endfor %}
// """
