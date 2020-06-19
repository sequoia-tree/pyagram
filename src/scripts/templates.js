function compile(template) {
    return Handlebars.compile(
        template.split('\n').map(function(line) {
            line = line.replace(/^\s+/, '');
            line = line.replace(/\s+$/, '');
            return line;
        }).join(''),
        {
            noEscape: true,
            assumeObjects: true,
        },
    );
}

export const ESCAPE = Handlebars.compile(`{{this}}`);

export const STACK_TEMPLATE = compile(`
<div class="font-family-monospace">
  {{decodeFrameSnapshot this}}
</div>
`);

export const ELEMENT_TEMPLATE = compile(`
{{#each flags}}
  {{decodeFlagSnapshot this}}
{{/each}}
`);

export const FLAG_TEMPLATE = compile(`
<div class="pyagram-flag m-3">
  <div class="pyagram-banner mr-3 {{#if is_curr_element}} curr-element {{/if}}">
    <table class="text-center">
      {{#if (isEqual type 'call')}}
        <tr>
          {{#each banner}}
            <td colspan="{{n_cols}}">
              {{escape code}}
            </td>
            {{#if @first}}
              {{#if @last}}
                <td>()</td>
              {{else}}
                <td>(</td>
              {{/if}}
            {{else}}
              {{#if @last}}
                <td>)</td>
              {{else}}
                <td>,</td>
              {{/if}}
            {{/if}}
          {{/each}}
        </tr>
        <tr>
          {{#each banner}}
            {{#if (isNull bindings)}}
              <td class="pyagram-value pyagram-placeholder">
                -
              </td>
            {{else if (isEmpty bindings)}}
              <td></td>
            {{else}}
              {{#each bindings}}
                {{#unless (isNull key)}}
                  <td class="banner-text">{{decodeReferenceSnapshot key}}=</td>
                {{/unless}}
                <td class="pyagram-value">
                  {{decodeReferenceSnapshot value}}
                </td>
                {{#unless @last}}
                  <td class="banner-text">,</td>
                {{/unless}}
              {{/each}}
            {{/if}}
            {{#if @first}}
              {{#if @last}}
                <td>()</td>
              {{else}}
                <td>(</td>
              {{/if}}
            {{else}}
              {{#if @last}}
                <td>)</td>
              {{else}}
                {{#if (isNull bindings)}}
                  <td>,</td>
                {{else if (isEmpty bindings)}}
                  <td></td>
                {{else}}
                  <td>,</td>
                {{/if}}
              {{/if}}
            {{/if}}
          {{/each}}
        </tr>
      {{else if (isEqual type 'comp')}}
        <tr>
          {{#each banner}}
            <td>
              {{escape code}}
            </td>
          {{/each}}
        </tr>
      {{/if}}
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
`);

export const FRAME_TEMPLATE = compile(`
<div class="pyagram-frame {{#if (isEqual type 'function')}} m-3 {{/if}} {{#if is_curr_element}} curr-element {{/if}}">
  <div class="pyagram-frame-name">
    {{#if (isEqual type 'function')}}
      <span class="font-family-sans-serif">
        {{escape name}}{{#unless (isNull parent)}} [parent: {{escape parent}}]{{/unless}}
      </span>
    {{else if (isEqual type 'generator')}}
      <span class="font-family-sans-serif">
        {{escape name}} [parent: {{escape parent}}]
      </span>
    {{else if (isEqual type 'class')}}
      <span class="font-family-sans-serif">
        class
        {{space 1}}
      </span>
      {{escape name}}
      {{#if (isNull parents)}}
        <span class="font-family-sans-serif">
          {{space 1}}
          [parent: <span class="font-family-monospace">{{decodeUnknownSnapshot this}}</span>]
        </span>
      {{else if (isEmpty parents)}}
      {{else}}
        <span class="font-family-sans-serif">
          {{space 1}}
          [parent{{#unless (isEqual parents.length 1)}}s{{/unless}}:
          {{space 1}}
          {{#each parents}}
            class <span class="font-family-monospace">{{escape this}}</span>
            {{#unless @last}}, {{/unless}}
          {{/each}}
          ]
        </span>
      {{/if}}
    {{else if (isEqual type 'instance')}}
      {{escape name}}
      <span class="font-family-sans-serif">
        {{space 1}}
        instance [parent: class <span class="font-family-monospace">{{escape parent}}</span>]
      </span>
    {{/if}}
  </div>
  <table class="ml-auto mr-0">
    {{#each bindings}}
      <tr>
        <td class="text-right">
          {{decodeReferenceSnapshot key}}
        </td>
        <td class="text-left pyagram-value pyagram-frame-value" {{#if (isEqual ../type 'generator')}}{{#unless (isNull ../from)}} colspan="3" {{/unless}}{{/if}}>
          {{decodeReferenceSnapshot value}}
        </td>
      </tr>
    {{/each}}
    {{#unless (isNull return_value)}}
      <tr>
        <td class="text-right font-family-sans-serif">
          {{#if (isEqual type 'generator')}}
            Yield:
          {{else}}
            Return:
          {{/if}}
        </td>
        <td class="text-left pyagram-value pyagram-frame-value">
          {{decodeReferenceSnapshot return_value}}
        </td>
        {{#if (isEqual type 'generator')}}
          {{#unless (isNull from)}}
            <td class="text-left font-family-sans-serif">
              from
            </td>
            <td class="text-left pyagram-value">
              {{decodeReferenceSnapshot from}}
            </td>
          {{/unless}}
        {{/if}}
      </tr>
    {{/unless}}
  </table>
  {{#if (isEqual type 'class')}}
    {{#if bltn}}
      <div class="text-center">
        ...
      </div>
    {{/if}}
  {{/if}}
</div>
{{#if (isEqual type 'function')}}
  {{decodeElementSnapshot this}}
{{/if}}
`);

export const HEAP_TEMPLATE_TEXTPOINTERS_T = compile(`
<table class="border-collapse my-2 font-family-monospace">
  {{#each this}}
    <tr>
      <td class="px-2 py-0 font-family-sans-serif">
        @{{decodeObjectIdSnapshot id}})
      </td>
      <td class="p-0">
        <div class="pyagram-object my-2 mr-3">
          {{decodeEncodedObjectSnapshot object}}
        </div>
      </td>
    </tr>
  {{/each}}
</table>
`);

export const HEAP_TEMPLATE_TEXTPOINTERS_F = compile(`
<table class="border-collapse my-2 font-family-monospace">
  {{#each this}}
    <tr>
      <td class="p-0">
        <div class="pyagram-object my-2 mr-3" id="object-{{decodeObjectIdSnapshot id}}">
          {{decodeEncodedObjectSnapshot object}}
        </div>
      </td>
    </tr>
  {{/each}}
</table>
`);

export const OMITTED_TEMPLATE = compile(`
<span title="This value cannot be displayed without compromising the pyagram's accuracy.">...</span>
`)

export const UNKNOWN_TEMPLATE = compile(`
<span class="pyagram-unknown">(?)</span>
`);

export const PRIMITIVE_TEMPLATE = compile(`
{{escape this}}
`);

export const REFERENT_TEMPLATE_TEXTPOINTERS_T = compile(`
<span class="font-family-sans-serif">@{{decodeObjectIdSnapshot this}}</span>
`);

export const REFERENT_TEMPLATE_TEXTPOINTERS_F = compile(`
<span class="pyagram-placeholder pyagram-pointer reference-{{decodeObjectIdSnapshot this}}">-</span>
`);

export const OBJECT_ID_TEMPLATE = compile(`
{{this}}
`);

export const FUNCTION_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  {{#if is_gen_func}}
    generator function
  {{else}}
    function
  {{/if}}
  {{space 1}}
</span>
{{#if (isNull lambda_id)}}
  {{escape name}}
{{else}}
  {{#with lambda_id}}
    &#955;<sub>{{lineno}}{{#unless single}}#{{number}}{{/unless}}</sub>
  {{/with}}
{{/if}}
(
{{#each parameters}}
  {{escape name}}
  {{#unless (isNull default)}}
    =<span class="pyagram-value">{{decodeReferenceSnapshot default}}</span>
  {{/unless}}
  {{#unless @last}}, {{/unless}}
{{/each}}
)
<div class="font-family-sans-serif">
  [parent: {{escape parent}}]
</div>
`);

export const METHOD_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  method
  {{space 1}}
</span>
<span class="pyagram-value">
  {{decodeReferenceSnapshot function}}
</span>
<span class="font-family-sans-serif">
  {{space 1}}
  bound to
  {{space 1}}
</span>
<span class="pyagram-value">
  {{decodeReferenceSnapshot instance}}
</span>
`);

export const BUILTIN_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  {{#if (isNull instance)}}
    function
  {{else}}
    method
  {{/if}}
  {{space 1}}
</span>
{{escape name}}(...)
{{#unless (isNull instance)}}
  <span class="font-family-sans-serif">
    {{space 1}}
    bound to
    {{space 1}}
  </span>
  <span class="pyagram-value">
    {{decodeReferenceSnapshot instance}}
  </span>
{{/unless}}
`);

export const ORDERED_COLLECTION_TEMPLATE = compile(`
{{#if (isEmpty elements)}}
  <div class="font-family-sans-serif">
    empty {{escape type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{escape type}}
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
`);

export const UNORDERED_COLLECTION_TEMPLATE = compile(`
{{#if (isEmpty elements)}}
  <div class="font-family-sans-serif">
    empty {{escape type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{escape type}}
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
`);

export const MAPPING_TEMPLATE = compile(`
{{#if (isEmpty items)}}
  <div class="font-family-sans-serif">
    empty {{escape type}}
  </div>
{{else}}
  <div class="d-flex flex-row align-items-center">
    <div class="font-family-sans-serif">
      {{escape type}}
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
`);

export const ITERATOR_TEMPLATE = compile(`
{{#if (isNull this)}}
  <div class="font-family-sans-serif">
    empty iterator
  </div>
{{else}}
  <span class="font-family-sans-serif">
    iterator over
    {{space 1}}
  </span>
  <span class="pyagram-value">
    {{decodeReferenceSnapshot object}}
  </span>
  {{#unless (isNull annotation)}}
    <span class="font-family-sans-serif">
      {{space 1}}
      {{escape annotation}}
    </span>
  {{/unless}}
  <div class="font-family-sans-serif">
    [next index: {{index}}]
  </div>
{{/if}}
`);

export const GENERATOR_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  generator
  {{space 1}}
</span>
{{escape name}}
{{decodeFrameSnapshot frame}}
`);

export const RANGE_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  range
  {{space 1}}
</span>
[{{decodeReferenceSnapshot start}}, {{decodeReferenceSnapshot stop}})
<span class="font-family-sans-serif">
  {{space 1}}
  with step size
  {{space 1}}
</span>
{{decodeReferenceSnapshot step}}
`)

export const SLICE_TEMPLATE = compile(`
<span class="font-family-sans-serif">
  slice
  {{space 1}}
</span>
[
{{#unless (isNull start)}}{{decodeReferenceSnapshot start}}{{/unless}}
:
{{#unless (isNull stop)}}{{decodeReferenceSnapshot stop}}{{/unless}}
:
{{#unless (isNull stop)}}{{decodeReferenceSnapshot step}}{{/unless}}
]
`)

export const OTHER_TEMPLATE = compile(`
{{escape this}}
`);

export const EXCEPTION_TEMPLATE = compile(`
{{#unless (isNull this)}}
  <div class="px-3 py-2 pyagram-readout font-family-monospace">
    {{escape this}}
  </div>
{{/unless}}
`);

export const PRINT_OUTPUT_TEMPLATE = compile(`
<div class="pyagram-readout font-family-monospace">
  {{escape this}}
</div>
`);

export const ERROR_TEMPLATE = compile(`
<div class="p-3 pyagram-readout font-family-monospace">
  <div>
    {{escape type}}{{#unless (isNull lineno)}} (line {{lineno}}){{/unless}}:
  </div>
  {{#if (isEqual encoding 'pyagram')}}
    {{decodePyagramError data}}
  {{else if (isEqual encoding 'syntax')}}
    {{decodeSyntaxError data}}
  {{/if}}
</div>
`);

export const PYAGRAM_ERROR_TEMPLATE = compile(`
{{message}}
`)

export const SYNTAX_ERROR_TEMPLATE = compile(`
<div>
  {{escape code}}
</div>
<div>
  {{space offset}}^
</div>
`)
