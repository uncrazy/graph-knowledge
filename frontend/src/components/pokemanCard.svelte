<script>
    import { fade } from 'svelte/transition';
    import { inputChosens } from '../pokestore.js';
    import { outputChosens } from '../pokestore.js';
    export let nodeData;
    let addInputSrc = "images/icons8-input-24.png"

    const addInput = (data) => {
        inputChosens.update(arr => {
            return [...arr, data]
        });
    };

    const addOutput = (data) => {
        outputChosens.update(arr => {
            return [...arr, data]
        });
    };
</script>

<div class="list-none p-6 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-md flex flex-col items-center" transition:fade>
<!--    <img class="h-40 w-40 " src={nodeData.image} alt={nodeData.name}/>-->
<!--    <h2 class="uppercase text-2xl">{nodeData['Название']}</h2>-->
    <div class="flex">
        <p>{nodeData['Description']}</p>
        <div class="top-0 right-0 w-24">
            <img class="w-24 h-24" src="{addInputSrc}" alt="addInput" />
        </div>

    </div>

<!--    {#each Object.entries(nodeData) as [param, val]}-->
<!--        <p>{param}: {val}</p>-->
<!--    {/each}}-->
    <button on:click={addInput(nodeData)}>choose as input</button>
    <button on:click={addOutput(nodeData)}>choose as output</button>
</div>

<style>
    .p {
        text-align: left;
    }
</style>