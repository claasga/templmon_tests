import { parentPort, workerData } from "worker_threads";
import now from "performance-now";
import {SocketTrainer} from "./sockets/SocketTrainer.js"
import {SocketPatient} from "./sockets/SocketPatient.js";
import {connectPatient, connectTrainer} from "./setupHelper.js";

const socketTrainer = new SocketTrainer('http://localhost/ws/trainer/?token=')
const socketPatient = new SocketPatient('http://localhost/ws/patient/?token=')
let exerciseId, areaId, patientId, materialId

const assignmentCycles = 50

async function simulate(userIndex) {
	const trainerName = `testuser${crypto.randomUUID()}`

	try {
		await connectTrainer(socketTrainer, trainerName)
		await prepareExercise()
		await connectPatient(socketPatient, exerciseId, patientId)

		let responseTime = 0

		for (let i = 0; i < assignmentCycles; i++) {
			let startTime = now();
			await new Promise(resolve => {
				socketPatient.assignMaterial(materialId, () => resolve())
			})
			let endTime = now();
			responseTime += (endTime - startTime)

			startTime = now();
			await new Promise(resolve => {
				socketPatient.releaseMaterial(materialId, () => resolve())
			})
			endTime = now();
			responseTime += (endTime - startTime)
		}

		socketPatient.close()
		socketTrainer.close()

		parentPort.postMessage({
			userIndex,
			responseTime: responseTime / (assignmentCycles*2),
			success: true
		});
		parentPort.close()
	} catch (error) {
		parentPort.postMessage({
			userIndex,
			responseTime: 0,
			success: false,
			error: error.message
		});
	}
	parentPort.close()
}

async function prepareExercise() {
	await new Promise(resolve => {
		socketTrainer.exerciseCreate(exercise => {
			exerciseId = exercise.exerciseId
			resolve()
		})
	})

	await new Promise(resolve => {
		socketTrainer.areaAdd(exercise => {
			areaId = exercise.areas[0].areaId
			resolve(true)
		})
	})

	await new Promise(resolve => {
		socketTrainer.patientAdd(areaId, "", 1001, exercise => {
			patientId = exercise.areas[0].patients[0].patientId
			resolve()
		})
	})

	await new Promise(resolve => {
		socketTrainer.materialAdd(areaId, "BZ-Messgerät", exercise => {
			materialId = exercise.areas[0].material[0].materialId
			resolve()
		})
	})

	await new Promise(resolve => {
		socketTrainer.exerciseStart(() => resolve())
	})
}

simulate(workerData.userIndex);