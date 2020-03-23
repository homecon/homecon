import {LitElement, html, css} from 'lit-element';
import '@polymer/paper-input/paper-input.js';
import '@lrnwebcomponents/json-editor/json-editor.js';

import '../homecon-edit-dialog.js';
import { addStateListener, stateReadHasChanged } from '../homecon-web-socket.js';

class BaseAction extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean,
      },
      state: {
        type: Object,
        hasChanged(newVal, oldVal) {
          return stateReadHasChanged(newVal, oldVal)
        }
      },
      value: {
        type: Object,
      }
    };
  }

  constructor() {
    super();
    addStateListener(this, false)
  }

  static get styles(){
    return css`
      :host{
        display: block;
        width: 100%;
      }
      div.action{
        width: 100%;
        font-weight: 500;
        margin-top: 10px;
        display: flex;
        flex-direction: row;
      }
      div.action:hover .controls{
        display: inline;
      }
      .label{
        flex-grow: 1;
      }
      .controls {
        display: none;
        margin-left: 16px;
      }
      .controls paper-icon-button{
        padding: 0px;
        height: 22px;
        width: 22px;
        margin-left: 10px;
      }`
  }

  render() {
    return html`
      <div class="action">
        <div class="label">${this.state.label}</div>
        <div class="controls">
          <paper-icon-button icon="editor:mode-edit" noink="true" @tap="${this.openEditDialog}"></paper-icon-button>
          <paper-icon-button icon="icons:delete" noink="true" @tap="${this.openDeleteDialog}"></paper-icon-button>
        </div>
      </div>

      <homecon-edit-dialog id="editActionDialog" @save="${this._saveAction}">
        <paper-input id="actionLabel" label="Label" value="${this.state.label}"></paper-input>
        <json-editor id="actionValue" label="Config" value="${JSON.stringify(this.value)}"></json-editor>
      </homecon-edit-dialog>

      <homecon-dialog id="deleteStateDialog" on-save="_deleteAction">
        <div>Delete action ${this.state.name}</div>
        <div slot="buttons">
          <paper-button raised on-tap="_deleteAction">delete</paper-button>
          <paper-button raised on-tap="close">cancel</paper-button>
        </div>
      </homecon-dialog>`;
  }


  openEditDialog(e){
    this.shadowRoot.getElementById('editActionDialog').open()
  }

  openDeleteDialog(e){
    this.shadowRoot.getElementById('deleteActionDialog').open()
  }

  _saveAction(e){
    var label = this.shadowRoot.getElementById('actionLabel').value;
    var value = this.shadowRoot.getElementById('actionValue').currentData;
    window.homecon.WebSocket.send({'event': 'update_action', 'data': {'id': this.state.id, 'value': value, 'label': label}})
  }

  _deleteAction(e){
    window.homecon.WebSocket.send({'event': 'delete_action', 'data': {'id': this.state.id}})
  }

}

window.customElements.define('base-action', BaseAction);
