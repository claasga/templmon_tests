<script setup lang="ts">
    const props = defineProps({
		text: {
			type: String,
			default: "Hinzufügen"
		}
	})
</script>

<template>
	<button class="list-item-add-button">
		{{ props.text }}
	</button>
</template>

<style>
    .list-item-add-button {
        text-align: center;
        position: relative;
        background-color: var(--green);
        color: white;
        border: 1px solid rgb(209, 213, 219);
        box-sizing: border-box;
        width: 100%;
        font-size: 1.25rem;
        line-height: 1.25rem;
        padding: .75rem 1rem;
        margin-top: -1px;
        min-height: 50px;
        border-radius: 10px 10px 0px 0px;
        box-shadow: 3px 3px 3px rgba(0, 0, 0, 0.1);
    }
</style>