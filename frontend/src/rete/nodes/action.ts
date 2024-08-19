import { ClassicPreset as Classic } from "rete"
import { DataflowNode } from "rete-engine"
import { socket } from "../sockets"

interface DropdownOption {
  name: string;
  value: string;
}

export class DropdownControl extends Classic.Control {
  selection: DropdownOption
  optionsList: DropdownOption[]

  constructor(optionsList: DropdownOption[], change?: (option: DropdownOption) => void) {
    super()
    this.optionsList = optionsList || []
    this.selection = this.optionsList[0]
    this.onChange = change as any
  }

  setValue(option: DropdownOption): void {
    this.selection = option
    if (this.onChange) {
      this.onChange(option)
    }
  }

  onChange(option: DropdownOption): void {
    this.setValue(option)
  }
}

export class ActionNode
  extends Classic.Node<
    { input: Classic.Socket; true: Classic.Socket; false: Classic.Socket },
    { true: Classic.Socket; false: Classic.Socket },
    { selection: DropdownControl }
  >
  implements DataflowNode
{
  width = 180
  height = 190

  constructor(change?: (option: DropdownOption) => void) {
    super("Action")

    this.addInput("input", new Classic.Input(socket, "input"))
    this.addOutput("true", new Classic.Output(socket, "true"))
    this.addOutput("false", new Classic.Output(socket, "false"))
    this.addControl(
      "selection",
      new DropdownControl(
        [
          { name: "Option 1", value: "00001" },
          { name: "Option 2", value: "00002" },
          { name: "Option 3", value: "00003" },
        ],
        change,
      )
    )
  }

  selection() {
    return this.controls["selection"].selection.value
  }

  data() {
    const value = this.controls["selection"].selection

    return {
      value,
    }
  }
}