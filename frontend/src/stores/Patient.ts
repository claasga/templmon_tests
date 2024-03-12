import {defineStore} from "pinia"

export const usePatientStore = defineStore('patient', {
	state: () => ({
		token: '',
		patientID: Number.NEGATIVE_INFINITY,
		patientName: '',
		triage: '-',
		areaName: '',
		patientInjury: '',
		patientHistory: '',
		patientPersonalDetails: '',
		patientBiometrics: '',
		airway: '',
		breathing: '',
		circulation: '',
		consciousness: '',
		phaseNumber: 0,
		psyche: '',
		pupils: '',
		skin: ''
	}),
	actions: {
		loadStatusFromJSON(state: State) {
			this.phaseNumber = state.phaseNumber
			this.airway = state.airway
			this.breathing = state.breathing
			this.circulation = state.circulation
			this.consciousness = state.consciousness
			this.psyche = state.psyche
			this.pupils = state.pupils
			this.skin = state.skin
		}
	}
})