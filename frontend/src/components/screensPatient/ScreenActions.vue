<script setup lang="ts">
	import PageActionOverview from './pagesAction/PageActionOverview.vue'
	import PageActionSelection from './pagesAction/PageActionSelection.vue'
	import PageActionCheck from './pagesAction/PageActionCheck.vue'
	import PagePersonnel from './pagesAction/PagePersonnel.vue'
	import PageMaterial from './pagesAction/PageMaterial.vue'
	import {computed, ref} from 'vue'

	const currentPage = ref(Pages.ACTION_OVERVIEW)
	const currentPageComponent = computed(() => getPageComponent(currentPage.value))

	const getPageComponent = (page: Pages) => {
		switch (page) {
			case Pages.ACTION_OVERVIEW:
				return PageActionOverview
			case Pages.ACTION_SELECTION:
				return PageActionSelection
			case Pages.ACTION_CHECK:
				return PageActionCheck
			case Pages.PERSONNEL:
				return PagePersonnel
			case Pages.MATERIAL:
				return PageMaterial
		}
	}

	const setPage = (newPage: Pages) => {
		currentPage.value = newPage
	}
</script>
<script lang="ts">
	export enum Pages {
		ACTION_OVERVIEW = "PageActionOverview",
		ACTION_SELECTION = "PageActionSelection",
		ACTION_CHECK = "PageActionCheck",
		PERSONNEL = "PagePersonnel",
		MATERIAL = "PageMaterial"
	}
</script>
<template>
	<div class="page">
		<component
			:is="currentPageComponent"
			@add-action="setPage(Pages.ACTION_SELECTION)"
			@close-action-selection="setPage(Pages.ACTION_OVERVIEW)"
			@set-page="(page) => setPage(page as Pages)"
			@close-action="setPage(Pages.ACTION_OVERVIEW)"
		/>
	</div>
	<nav>
		<button
			id="nav-left"
			:class="{ 'selected': currentPage === Pages.ACTION_OVERVIEW }"
			@click="setPage(Pages.ACTION_OVERVIEW)"
		>
			Übersicht
		</button>
		<button id="nav-center" :class="{ 'selected': currentPage === Pages.PERSONNEL }" @click="setPage(Pages.PERSONNEL)">
			Personal
		</button>
		<button id="nav-right" :class="{ 'selected': currentPage === Pages.MATERIAL }" @click="setPage(Pages.MATERIAL)">
			Material
		</button>
	</nav>
</template>
<style scoped>
	.page {
		height: calc(100% - 60px);
	}

	nav {
		width: 100%;
		height: 60px;
		bottom: 0;
		position: absolute;
		display: flex;
		float: left;
		border-top: 2px solid var(--border-color);
	}

	button {
		width: calc(100% / 3);
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 1.5em;
		background-color: white;
		border: none;
	}

	button.selected {
		filter: brightness(0.9);
		font-weight: bold;
	}
</style>