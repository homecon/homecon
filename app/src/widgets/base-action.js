import {LitElement, html, css} from 'lit-element';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/paper-input/paper-input.js';
import '@lrnwebcomponents/json-editor/json-editor.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';

class BaseAction extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean,
      },
      state: {
        type: Object,
        hasChanged(newVal, oldVal) {
          if(newVal != oldVal && newVal != null){
            window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': newVal.id}})
          }
          return false
        }
      },
      value: {
        type: Object,
      }
    };
  }

  constructor() {
    super();

    var that = this
    window.addEventListener('homecon-web-socket-message', function(e, d){
      if(e.detail.event == 'state_value' && typeof that.state != 'undefined' && (e.detail.data.path == that.state.path || e.detail.data.id == that.state.id)){
        var oldVal = that.action
        that.value = e.detail.data.value
        that.requestUpdate('value', oldVal);
      }
    });
  }

  static get styles(){
    return css`
      :host{
        display: block;
      }
      div.action{
        font-weight: 500;
        margin-top: 10px;
      }
      div.action:hover .controls{
        display: inline;
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
        <span>${this.state.label}</span>
        <span class="controls">
          <paper-icon-button icon="editor:mode-edit" noink="true" @tap="${this.openEditDialog}"></paper-icon-button>
          <paper-icon-button icon="icons:delete" noink="true" @tap="${this.openDeleteDialog}"></paper-icon-button>
        </span>
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
