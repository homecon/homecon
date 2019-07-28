import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-status-light.js';

class WidgetValueInput extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
        }
        .label{
          font-size: 16px;
          font-weight: 700;
          margin-right: 10px;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>
        <homecon-web-socket-object event="state_value" key="[[state]]" data="{{value}}" auto>
        </homecon-web-socket-object>


        <div class="horizontal layout" on-tap="editValueDialog">
          <div class="label">{{label}}:</div>
          <div class="value flex">{{value}}</div>
        <div>

        <homecon-edit-dialog id="editValueDialog" on-save="call">
          <paper-input label={{label}} value="{{newValue}}"></paper-input>
        </homecon-edit-dialog>

        <div class="edit" hidden="{{!edit}}">
          <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
        </div>

        <homecon-edit-dialog id="editDialog" on-save="save">
          <template is="dom-if" if="{{edit}}">
            <paper-input label="Label:" value="{{newLabel}}"></paper-input>
            <homecon-state-select></homecon-state-select>
            <paper-button on-tap="delete">Delete</paper-button>
          </template>
        </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      label: {
        type: String,
        value: 'new switch',
      },
      state: {
        type: Number,
      },
      edit: {
        type: Boolean,
        value: false
      },
      classes: {
        type: String,
        value: 'halfwidth',
      },
    };
  }

  editValueDialog(valueOn, valueOff){
    this.newValue = this.value
    this.$.editValueDialog.open()
  }

  call(){
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': this.newValue}})
  }

}

window.customElements.define('widget-value-input', WidgetValueInput);
