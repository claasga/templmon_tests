<script setup lang="ts">
	import {useAvailablesStore} from "@/stores/Availables"
	import PatientInfo from "./PatientInfo.vue"
	import {computed, ref} from "vue"
	import TriageForListItems from "./TriageForListItems.vue"
	import {useExerciseStore} from "@/stores/Exercise"
	import socketTrainer from "@/sockets/SocketTrainer"
	import PatientCodeList from "./PatientCodeList.vue"
	import CloseButton from "./CloseButton.vue"
	import {ListItem, ListItemName, ListItemLeft} from "@/components/widgets/List"

	const emit = defineEmits(['close-popup'])

	const props = defineProps({
		patientId: {
			type: String,
			default: ''
		}
	})

	function updatePatient(patientId: string, patientCode: number) {
		socketTrainer.patientUpdate(patientId, patientCode)
		emit('close-popup')
	}

	const exerciseStore = useExerciseStore()
	const currentPatientName = computed(() => exerciseStore.getPatient(props.patientId)?.patientName)
	const currentPatientCode = ref(exerciseStore.getPatient(props.patientId)?.code)

	const availablesStore = useAvailablesStore()

	const currentPatient = computed(() => {
		if (currentPatientCode.value !== undefined) {
			return availablesStore.getPatient(currentPatientCode.value)
		}
		return null
	})

	function changePatientCode(patientCode: number) {
		currentPatientCode.value = patientCode
	}

</script>

<template>
	<div class="popup-overlay" @click="emit('close-popup')">
		<div class="popup" @click.stop="">
			<CloseButton @close="emit('close-popup')" />
			<div id="left-side">
				<div class="flex-container">
					<PatientCodeList @change-patient="changePatientCode" />
				</div>
			</div>
			<div id="right-side">
				<div class="flex-container">
					<ListItem>
						<ListItemLeft>
							{{ props.patientId }}
						</ListItemLeft>
						<TriageForListItems :patient-code="currentPatient?.code" />
						<ListItemName :name="currentPatientName" />
					</ListItem>
					<div class="scroll">
						<PatientInfo
							:injury="currentPatient?.injury"
							:biometrics="currentPatient?.biometrics"
							:mobility="currentPatient?.mobility"
							:preexisting-illnesses="currentPatient?.preexistingIllnesses"
							:permanent-medication="currentPatient?.permanentMedication"
							:current-case-history="currentPatient?.currentCaseHistory"
							:pretreatment="currentPatient?.pretreatment"
						/>
					</div>
					<div id="button-row">
						<button
							id="save-button"
							@click="updatePatient(props.patientId, currentPatient?.code || Number.NEGATIVE_INFINITY)"
						>
							Änderung speichern
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.popup {
		width: 80vw;
		height: 50vh;
		display: flex;
	}

	#left-side {
		float: left;
		width: 50%;
		padding: 10px;
	}

	#right-side {
		width: 50%;
		padding: 10px;
	}

	#button-row {
		display: flex;
	}

	#delete-button, #save-button {
		position: relative;
		color: white;
		border: 1px solid rgb(209, 213, 219);
		border-radius: .5rem;
		width: 100%;
		font-size: 1.25rem;
		padding: .75rem 1rem;
		text-align: center;
		margin-top: 10px;
	}

	#delete-button {
		background-color: var(--red);
	}

	#save-button {
		background-color: var(--green);
		margin-left: 10px;
	}
</style>