/* eslint-disable @typescript-eslint/no-unused-vars */
interface MessageData {
	messageType: string
	message?: string
	triage?: string
	actionName?: string
	patientInjury?: string
	patientHistory?: string
	patientPersonalDetails?: string
	patientBiometrics?: string
	areaName?: string
	patientName?: string
	patientCode?: number
	patientId?: number
	personnelName?: string
	personnelId?: number
	materialName?: string
	exercise?: Exercise
	state?: State
	logEntries?: LogEntry[]
	availablePatients: AvailablePatients
	availableActions: AvailableActions
	availableMaterialList: AvailableMaterial
	actionDeclinationReason?: string
	ressourceAssignments: RessourceAssignments
}

interface Exercise {
	exerciseId: string
	areas: Area[]
}

interface Area {
	areaName: string
	patients: Patient[]
	personnel: Personnel[]
	material: Material[]
}

interface Patient {
	patientId: number
	patientName: string
	patientCode: number
	triage: string
}

interface Personnel {
	personnelId: number
	personnelName: string
}

interface Material {
	materialId: number
	materialName: string
	materialType: string
}

interface State {
	phaseNumber: number
	airway: string
	breathing: string
	circulation: string
	consciousness: string
	pupils: string
	psyche: string
	skin: string
}

interface Availables {
	actions: AvailableAction[],
	patients: AvailablePatient[],
	material: AvailableMaterial[],
}

interface AvailableActions {
	availableActions: AvailableAction[],
}

interface AvailableAction {
	actionName: string
	actionDescription: string
	actionType: string
}

interface AvailablePatients {
	availablePatients: AvailablePatient[],
}

interface AvailablePatient {
	patientCode: number
	triage: string
	patientInjury: string
	patientHistory: string
	patientPersonalDetails: string
	patientBiometrics: string
}

interface AvailableMaterialList {
	availableMaterialList: AvailableMaterial[],
}

interface AvailableMaterial {
	materialName: string
	materialType: string
}

interface RessourceAssignments {
	ressourceAssignments: RessourceAssignment[]
}

interface RessourceAssignment {
	areaName: string
	personnel: PersonnelAssignments[]
	material: MaterialAssignments[]
}

interface PersonnelAssignments {
	personnelId: number
	personnelName: string
	patientId: number
}

interface MaterialAssignments {
	materialId: number
	materialName: string
	patientId: number
}

interface Log {
	log: LogEntry[]
}

interface LogEntry {
	logId: number
	logMessage: string
	logTime: Date
	areaName: string
	patientId: number
	personnelId: number
}