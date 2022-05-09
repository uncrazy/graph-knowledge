import { writable } from 'svelte/store';

export const pokemon = writable([]);
export const inputChosens = writable([]);
export const outputChosens = writable([]);
export const config = {
	'graphDataUrl': 'http://localhost:8000/data',
	'graphInstanceUrl': 'http://localhost:8050'
}


const pokemonDetails = {};
let loaded = false;

export const fetchPokemon = async () => {
	if (loaded) return;
	// const url = `https://pokeapi.co/api/v2/pokemon?limit=10`;
	const res = await fetch(config['graphDataUrl']);
	const data = await res.json();
	// const loadedPokemon = data.results.map((data, index) => ({
	// 	name: data.name,
	// 	id: index + 1,
	// 	image: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${
	// 		index + 1
	// 	}.png`
	// }));
	pokemon.set(data);
	loaded = true;
};

export const getPokemonById = async (id) => {
	if (pokemonDetails[id]) return pokemonDetails[id];

	try {
		const url = `https://pokeapi.co/api/v2/pokemon/${id}`;
		const res = await fetch(url);
		const data = await res.json();
		pokemonDetails[id] = data;
		return data;
	} catch (err) {
		console.error(err);
		return null;
	}
};


// export const addInput = (data) => {
// 	inputChosens.update(inputChosens => ([...inputChosens, data]));
// };
//
//
// export const addOutput = (data) => {
// 	outputChosens.update($outputChosens => ([...$outputChosens, data]));
// };


// export const fetchPokemon = async () => {
// 	if (loaded) return;
// 	const url = 'http://localhost:8000/data';
// 	const res = await fetch(url);
// 	const data = await res.json();
// 	// const loadedPokemon = data.results.map((data, index) => ({
// 	// 	name: data.name,
// 	// 	id: index + 1,
// 	// 	image: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${
// 	// 		index + 1
// 	// 	}.png`
// 	// }));
// 	pokemon.set(data);
// 	loaded = true;
// };