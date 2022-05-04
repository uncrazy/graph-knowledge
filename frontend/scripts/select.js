<!-- <script> -->
import Svelecte from '../../src/Svelecte.svelte';
import { dataset } from './data.js';

/** plain text array */
let options = dataset.countries().map(opt => opt.text);

let labelAsValue = false;

let selection = [];
let value = ['Czechia', 'Germany'];
<!-- </script> -->

