<script>
    import { writable } from 'svelte/store';
    import PokemanCard from "../components/pokemanCard.svelte";
    import {pokemon, fetchPokemon} from "../pokestore";
    import {inputChosens} from '../pokestore';
    import {outputChosens} from '../pokestore';
    import {config} from '../pokestore';
    import SplitPane from '../components/SplitPane.svelte'


    let searchTerm = "";
    let filteredPokemon = [];
    let inputChosen = [];
    let outputChosen = [];

    $: {
        if(searchTerm) {
            filteredPokemon = $pokemon.filter(
                // nodeData => nodeData.name.toLowerCase().includes(searchTerm.toLowerCase())
                el => {
                    let str = "";
                    Object.values(el).map(s => str += s ? s.toString() : "");
                    console.log(searchTerm.toLowerCase() + str);
                    // return str.indexOf(searchTerm.toString().toLowerCase()) != -1;
                    return str.includes(searchTerm.toLowerCase());
                });
        }
        else {
            filteredPokemon = [...$pokemon];
        }
    }

    let classPointerEventsNone;
    const onMouseDown = () => {
        classPointerEventsNone = 'pointer-events-none';
    }
    const onMouseUp = () => {
        classPointerEventsNone = '';
    }


    fetchPokemon();
</script>


<svelte:head>
	<title>Pokedex</title>
</svelte:head>


<SplitPane leftInitialSize="75%">

	<svelte:fragment slot="left">
        <iframe class="graph" src="{config['graphInstanceUrl']}">
        </iframe>

	</svelte:fragment>

	<svelte:fragment slot="right">
		<div class="logic">
			<h3 class="text-center">Исходные данные</h3>
            <div class="py-4 grid gap-4 grid-cols-1">
                {#each $inputChosens as nodeData}
                    <PokemanCard nodeData={nodeData}/>
                {/each}
            </div>

            <h3 class="text-center">Необходимый результат</h3>
            <div class="py-4 grid gap-4 grid-cols-1">
                {#each $outputChosens as nodeData}
                    <PokemanCard nodeData={nodeData}/>
                {/each}
            </div>

            <input class="w-full rounded-md text-sm p-4 border-2 border-gray-200" bind:value={searchTerm} placeholder="Поиск по ключевым словам">
            <div class="py-4 grid gap-4 grid-cols-1">
                {#each filteredPokemon as nodeData}
                        <PokemanCard nodeData={nodeData}/>
                {/each}
            </div>
		</div>
	</svelte:fragment>

</SplitPane>

<style>
	.graph,
	.logic {
		color: black;
		text-align: center;
        /*display: flex;*/
        /*background-color: white;*/
        /*flex-grow: 1;*/
        /*flex-shrink: 1;*/
        overflow: hidden;
	}

	.graph {
		height: 100vh;
        width: 70%;
        overflow: hidden;
        position: fixed;
	}

	.logic {
		height: 100%;
        overflow: auto;
	}
</style>


<!--LEFT SIDE-->
<!--<div class="wrapper">-->
<!--<HSplitPane updateCallback={() => {-->
<!--    console.log('HSplitPane Updated!');-->
<!--}}>-->
<!--    <left slot="left">-->
<!--        Left Pane-->
<!--    </left>-->
<!--    <right slot="right">-->
<!--        Right Pane-->
<!--    </right>-->
<!--</HSplitPane>-->
<!--</div>-->


<!--<h1>V Splite Pane Default</h1>-->
<!--<div class="wrapper">-->
<!--<VSplitPane updateCallback={() => {-->
<!--    console.log('VSplitPane Updated!');-->
<!--}}>-->
<!--    <top slot="top">-->
<!--        Top Pane-->
<!--    </top>-->
<!--    <down slot="down">-->
<!--        Down Pane-->
<!--    </down>-->
<!--</VSplitPane>-->
<!--</div>-->


<!--<h3 class="text-center my-8">Исходные данные</h3>-->
<!--<div class="py-4 grid gap-4 md:grid-cols-2 grid-cols-1">-->
<!--    {#each $inputChosens as nodeData}-->
<!--        <PokemanCard nodeData={nodeData}/>-->
<!--    {/each}-->
<!--</div>-->

<!--<h3 class="text-center my-8">Необходимый результат</h3>-->
<!--<div class="py-4 grid gap-4 md:grid-cols-2 grid-cols-1">-->
<!--    {#each $outputChosens as nodeData}-->
<!--        <PokemanCard nodeData={nodeData}/>-->
<!--    {/each}-->
<!--</div>-->

<!--<h1 class="text-4xl text-center my-8 uppercase">SvelteKit Pokedex</h1>-->
<!--<input class="w-full rounded-md text-lg p-4 border-2 border-gray-200" bind:value={searchTerm} placeholder="Search string">-->
<!--<div class="py-4 grid gap-4 md:grid-cols-2 grid-cols-1">-->
<!--    -->
<!--    {#each filteredPokemon as nodeData}-->
<!--            <PokemanCard nodeData={nodeData}/>-->
<!--    {/each}-->
<!--</div>-->
<!--    -->
