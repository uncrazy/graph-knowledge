<script>
    import { fade } from 'svelte/transition';
    import { inputChosens, outputChosens, pokemon } from '../pokestore.js';
    export let nodeData;
    export let toDelete;
    export let arr;
    let addInputSrc = "images/icons8-input-24.png"
    let addOutputSrc = "images/icons8-output-24.png"
    let deleteSrc = "images/icons8-remove-24.png"

    const addInput = (data) => {
        inputChosens.update(arr_ => [...arr_, data]);
        pokemon.update(arr_ => arr_.filter(el => el != data))
    };

    const addOutput = (data) => {
        outputChosens.update(arr_ => [...arr_, data]);
        pokemon.update(arr_ => arr_.filter(el => el != data))
    };

    const remove = (data, arrName) => {
        if (arrName == "inputChosens")
            var arr_ = inputChosens;
        else if (arrName == "outputChosens")
            var arr_ = outputChosens;
        console.log(arr_)
        arr_ = arr_.update(array => array.filter(el => el != data));
        pokemon.update(array => [data, ...array]);
    };

    export const findPath = () => {
        var button = document.getElementById("button");
        button.click();
      // return n.setProps({
      //   n_clicks: n.n_clicks + 1,
      //   n_clicks_timestamp: Date.now()
      // })
    }
</script>

<div class="list-none p-4 bg-gray-100 text-gray-800 rounded-md shadow-sm hover:shadow-md flex flex-col" transition:fade>
<!--    <img class="h-40 w-40 " src={nodeData.image} alt={nodeData.name}/>-->
<!--    <h2 class="uppercase text-2xl">{nodeData['Название']}</h2>-->
    <div class="top-0 right-0">
        {#if toDelete}
            <button type="button" on:click={remove(nodeData, arr)} class="text-blue-700 border border-blue-700 hover:shadow-md focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm p-2.5 text-center inline-flex items-center mr-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:focus:ring-blue-800">
                <img class="" src="{deleteSrc}" alt="delete" />
            </button>
        {:else}
            <button type="button" on:click={addInput(nodeData)} class="text-blue-700 border border-blue-700 hover:shadow-md focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm p-2.5 text-center inline-flex items-center mr-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:focus:ring-blue-800">
                <img class="w-12" src="{addInputSrc}" alt="addInput" />
            </button>
            <button type="button" on:click={addOutput(nodeData)} class="text-blue-700 border border-blue-700 hover:shadow-md focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm p-2.5 text-center inline-flex items-center mr-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:focus:ring-blue-800">
                <img class="" src="{addOutputSrc}" alt="addOutput" />
            </button>
        {/if}

    </div>

    <div class="flex">
        <p>({nodeData['name']}) {nodeData['Description']}</p>
    </div>

<!--    {#each Object.entries(nodeData) as [param, val]}-->
<!--        <p>{param}: {val}</p>-->
<!--    {/each}}-->
</div>

<style>
    .p {
        text-align: left;
    }
</style>