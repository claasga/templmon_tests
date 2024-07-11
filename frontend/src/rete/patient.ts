import { ClassicPreset as Classic, GetSchemes, NodeEditor } from 'rete'
import { Area2D, AreaExtensions, AreaPlugin } from 'rete-area-plugin'
import { ConnectionPlugin } from 'rete-connection-plugin'
import { VuePlugin, VueArea2D, Presets as VuePresets } from 'rete-vue-plugin'
import {
  AutoArrangePlugin,
  Presets as ArrangePresets,
} from 'rete-auto-arrange-plugin'
import {
  ContextMenuPlugin,
  ContextMenuExtra,
  Presets as ContextMenuPresets,
} from 'rete-context-menu-plugin'
import { ClassicFlow, getSourceTarget } from 'rete-connection-plugin'
import CircleNode from './customization/CircleNode.vue'
import SquareNode from './customization/SquareNode.vue'
import { loadPatientState } from '@/components/componentsPatientEditor/PatientStateForm.vue'
import { showPatientStateForm } from '@/components/ModulePatientEditor.vue'
import {
  AddNode,
  NumberNode,
  InputNode,
  OutputNode,
  ModuleNode
} from "./nodes"
import { DataflowEngine } from "rete-engine"
import { Modules } from "./modules"
import { clearEditor } from "./utils"
import { createNode, exportEditor, importEditor } from "./import"
import rootModule from "./modules/root.json"
import transitModule from "./modules/transit.json"
import doubleModule from "./modules/double.json"
import { createEngine } from "./processing"

const modulesData: { [key in string]: any } = {
  root: rootModule,
  transit: transitModule,
  double: doubleModule
}

type Node = StateNode | TransitionNode | AddNode | NumberNode | InputNode | OutputNode | ModuleNode;

type Conn =
  | Connection<StateNode, TransitionNode>
  | Connection<TransitionNode, StateNode>
  | Connection<NumberNode, AddNode>
  | Connection<AddNode, AddNode>
  | Connection<InputNode, OutputNode>

type Schemes = GetSchemes<Node, Conn>

export class Connection<A extends Node, B extends Node> extends Classic.Connection<A,B> {}

class StateNode extends Classic.Node {
  width = 100
  height = 100

  constructor() {
    super('State')

    this.label = 'State'

    this.addInput('in', new Classic.Input(socket, undefined, false))
    this.addOutput('out', new Classic.Output(socket, undefined, false))
  }
}

class TransitionNode extends Classic.Node {
  width = 150
  height = 100

  constructor() {
    super('Transition')

    this.label = 'Transition'

    this.addInput('in', new Classic.Input(socket, undefined, true))
    this.addOutput('out', new Classic.Output(socket, undefined, true))
  }
}

type AreaExtra =
  | Area2D<Schemes>
  | VueArea2D<Schemes>
  | ContextMenuExtra

export type Context = {
  process: () => void
  modules: Modules<Schemes>
  editor: NodeEditor<Schemes>
  area: AreaPlugin<Schemes, any>
  dataflow: DataflowEngine<Schemes>
}

const socket = new Classic.Socket('socket')

async function createNodesAndConnections(patientStateStore: PatientStateStore, transitionStore: TransitionStore, editor: NodeEditor<Schemes>) {
  console.log("Creating nodes and connections")
  // Create nodes from patient states and store them in an object
   for (const patientState of Object.values(patientStateStore.patientStates)) {
    const node = new StateNode()
    await editor.addNode(node)
    patientState.nodeId = node.id
  }
  
  // Create nodes from transitions and store them in an object
  for (const transition of Object.values(transitionStore.transitions)) {
    const node = new TransitionNode()
    await editor.addNode(node)
    transition.nodeId = node.id
  }
  
  // Create connections from patient states to transitions
  for (const patientState of patientStateStore.patientStates) {
    const node = editor.getNode(patientState.nodeId)
    if (patientState.nextTransition == null) continue
    const nextTransition = transitionStore.getTransitionById(patientState.nextTransition)
    const nextNode = editor.getNode(nextTransition.nodeId)
    await editor.addConnection(new Connection(node, 'out', nextNode, 'in'))
  }
  
  // Create connections from transitions to patient states
  for (const transition of transitionStore.transitions) {
    const node = editor.getNode(transition.nodeId)
    for(const nextStateId of transition.nextStates) {
      const nextState = patientStateStore.getPatientStateById(nextStateId)
      const nextNode = editor.getNode(nextState.nodeId)
      await editor.addConnection(new Connection(node, 'out', nextNode, 'in'))
    }
  }
}

export async function createEditor(
  container: HTMLElement,
  patientEditorStore: any,
  patientStateStore: any,
  transitionStore: any
) {
  const editor = new NodeEditor<Schemes>()
  const area = new AreaPlugin<Schemes, AreaExtra>(container)
  const connection = new ConnectionPlugin<Schemes, AreaExtra>()
  const vueRender = new VuePlugin<Schemes, AreaExtra>()
  const arrange = new AutoArrangePlugin<Schemes, AreaExtra>()
  
  vueRender.addPreset(
    VuePresets.classic.setup({
      customize: {
        node(context) {
          if (context.payload.label === 'State') {
            return CircleNode
            } else if (context.payload.label === 'Transition') {
            return SquareNode
            }
            return VuePresets.classic.Node
            },
      },
    })
  )

  const contextMenu = new ContextMenuPlugin<Schemes>({
    items: ContextMenuPresets.classic.setup([
      ['State', () => new StateNode()],
      ['Transition', () => new TransitionNode()],
      ["Number", () => createNode(context, "Number", { value: 0 })],
      ["Add", () => createNode(context, "Add", {})],
      ["Input", () => createNode(context, "Input", { key: "key" })],
      ["Output", () => createNode(context, "Output", { key: "key" })],
      ["Module", () => createNode(context, "Module", { name: "" })]
    ])
  })
  
  editor.use(area)
  area.use(vueRender)
  area.use(connection)
  area.use(contextMenu)

  area.area.setZoomHandler(null)

  area.addPipe(context => {
    if (context.type === 'nodepicked') {
      const node = editor.getNode(context.data.id)
      showPatientStateForm()
      loadPatientState(node.id)
    }
    return context
  })
  
  connection.addPreset(() => new ClassicFlow({
    makeConnection(from, to, context) {
      const [source, target] = getSourceTarget(from, to) || [null, null]
      const { editor } = context

      // no connections with nodes with the same label
      if (editor.getNode(source?.nodeId || '').label ===  editor.getNode(target?.nodeId || '').label) return false
  
      if (source && target) {
        editor.addConnection(
          new Connection(
            editor.getNode(source.nodeId),
            source.key,
            editor.getNode(target.nodeId),
            target.key
          )
        )
        return true
      }
    }
  }))

  vueRender.addPreset(VuePresets.classic.setup())
  vueRender.addPreset(VuePresets.contextMenu.setup())

  await createNodesAndConnections(patientStateStore, transitionStore, editor)
  
  arrange.addPreset(ArrangePresets.classic.setup())
  area.use(arrange)
  AreaExtensions.zoomAt(area, editor.getNodes())
  AreaExtensions.simpleNodesOrder(area)
  const selector = AreaExtensions.selector()
  const accumulating = AreaExtensions.accumulateOnCtrl()
  AreaExtensions.selectableNodes(area, selector, { accumulating })
  
  const { dataflow, process } = createEngine(editor, area)
  editor.use(dataflow)

  const modules = new Modules<Schemes>(
    (path) => modulesData[path],
    async (path, editor) => {
      const data = modulesData[path];

      if (!data) throw new Error("cannot find module");
      await importEditor(
        {
          ...context,
          editor
        },
        data
      );
    }
  );
  const context: Context = {
    editor,
    area,
    modules,
    dataflow,
    process
  }

  await process()

  let currentModulePath: null | string = null

  async function openModule(path: string) {
    currentModulePath = null

    await clearEditor(editor)

    const module = modules.findModule(path)

    if (module) {
      currentModulePath = path
      await module.apply(editor)
    }

    await arrange.layout()
    AreaExtensions.zoomAt(area, editor.getNodes())
  }
  (window as any).area = area

  await arrange.layout()

  return {
    getModules() {
      return Object.keys(modulesData)
    },
    saveModule: () => {
      if (currentModulePath) {
        const data = exportEditor(context)
        modulesData[currentModulePath] = data
      }
    },
    restoreModule: () => {
      if (currentModulePath) openModule(currentModulePath)
    },
    newModule: (path: string) => {
      modulesData[path] = { nodes: [], connections: [] }
    },
    openModule,
    layout: async () => {
      await arrange.layout()
      console.log("Layout arranged")
      AreaExtensions.zoomAt(area, editor.getNodes())
    },
    destroy: () => {
      console.log("area.destroy1", area.nodeViews.size)

      area.destroy()
    }
  }
}