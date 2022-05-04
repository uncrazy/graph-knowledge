<Svelecte {options} {labelAsValue}
  bind:readSelection={selection}
  bind:value={value}
  multiple
  placeholder="Select country"
></Svelecte>

<div class="float-right">
  Pick
  <label><input type="radio" bind:group={labelAsValue} value={false}> value</label>
  <label><input type="radio" bind:group={labelAsValue} id="" value={true}> label</label>
</div>

<div>
  Current <code>readSelection</code> value: <b>{JSON.stringify(selection) }</b>
  <br>
  Current <code>value</code> value: <b>{value}</b>
</div>