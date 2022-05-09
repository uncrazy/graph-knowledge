<script>
	export let leftInitialSize = '50%';

	let left;
	let isDragging = false;

	function dragstart() {
		isDragging = true;
	}

	function drag(e) {
		if (!isDragging) return;

		const elementLeft = left.getBoundingClientRect().left;
		left.style.flexBasis = e.clientX - elementLeft + 'px';
	}

	function dragend() {
		if (!isDragging) return;

		isDragging = false;
	}
</script>

<div class="split-pane" on:mousemove={drag} on:mouseup={dragend}>
	<div bind:this={left} class="left" style="flex-basis: {leftInitialSize}">
		<slot name="left" />
	</div>
	<div class="splitter drop-shadow-2xl md:filter-none" on:mousedown={dragstart} />
	<div class="right">
		<slot name="right" />
	</div>
</div>

<style>
	.splitter {
		flex-grow: 0;
		flex-shrink: 0;
		width: 3px;
		background-color: #7c7e80;
		cursor: col-resize;
	}

	.split-pane {
		display: flex;
		align-items: stretch;
		width: 100%;
		max-width: 100%;
	}

	.split-pane > div {
		display: block;
	}

	.left {
		/*flex-grow: 0;*/
		/*flex-shrink: 1;*/
        min-width: 70%;
	}

	.right {
		/*flex-grow: 1;*/
		/*flex-shrink: 0;*/
        min-width: 30%;
	}
</style>