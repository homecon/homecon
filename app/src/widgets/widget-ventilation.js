import {LitElement, html, css} from 'lit-element';

import './base-status-light.js';

import { addStateListener, stateReadHasChanged } from '../homecon-web-socket.js';


class WidgetVentilationSpeed extends LitElement {

  static get properties() {
    return {
      label: {
        type: String,
      },
      state: {
        type: Number,
        hasChanged(newVal, oldVal) {
          return stateReadHasChanged(newVal, oldVal)
        }
      },
      value: {
        type: Number,
      },
      values: {
        type: Array,
      },
      edit: {
        type: Boolean,
        value: false
      },
      classes: {
        type: String,
      },
    };
  }

  constructor() {
    super();

    this.label = 'new ventilation speed'
    this.values = [0, 1, 2, 3]
    this.classes = 'fullwidth'

    addStateListener(this)
  }

  static get styles(){
    return css`
      :host{
        display: block;
        position: relative;
      }
      .label{
        font-size: 16px;
        font-weight: 700;
      }
      .icons{
        display: flex;
        justify-content: center;
      }
      .icon{
        width: 60px;
        cursor: pointer;
      }
      .edit{
        position: absolute;
        top: -10px;
        right: -10px;
        color: var(--button-text-color);
      }`
  }

  render() {
    return html`
      <div class="label">${this.label}</div>
      <div class="icons">
        ${this.values.map((v, i) => html`<base-status-light class="icon" icon="vent_ventilation_level_${4-this.values.length +i}" value="${this.value == v ? 1 : 0}" @tap="${this.getCallFunction(i)}"></base-status-light>`)}
      </div>

      <div class="edit" hidden="${!this.edit}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-button on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>`;
  }

  getCallFunction(ind) {
    var that = this
    return function(e){
      window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': that.values[ind]}})
    }
  }
}

window.customElements.define('widget-ventilation-speed', WidgetVentilationSpeed);
