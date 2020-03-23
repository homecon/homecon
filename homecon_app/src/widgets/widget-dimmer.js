import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-status-light.js';
import './base-slider.js';


class WidgetDimmer extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
          width: 100%;
        }
        .button {
          text-transform: none;
          //width: 60px;
          padding: 0px;
          margin: 0px;
          min-width: 0px;
        }
        .icon{
          width: 60px;
          height: 60px;
        }
        .label{
          font-size: 16px;
          font-weight: 700;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>

      <homecon-web-socket-object id="websocketObject" event="state_value" key="{{state}}" data="{{value}}" send-on-authenticated></homecon-web-socket-object>

      <div class="horizontal layout">
        <div class="clickable horizontal layout start-justified center" on-tap="call">
          <base-status-light class="icon" value="{{value}}"></base-status-light>
        </div>
        <div class="flex">
          <div class="vertical layout center-justified">
            <div class="label">{{label}}</div>
            <base-slider slider-value="{{value}}" min="{{valueOff}}" max="{{valueOn}}" on-value-changed="valueChanged"></base-slider>
          </div>
        </div>
      </div>

      <div class="edit" hidden="{{!edit}}">
          <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <template is="dom-if" if="{{edit}}">
          <paper-input label="Label:" value="{{newLabel}}"></paper-input>
          <select-component id="componentSelect" path="{{newPath}}"></select-component>
          <paper-input label="value on:" value="{{newValueOn}}"></paper-input>
          <paper-input label="value off:" value="{{newValueOff}}"></paper-input>
          <homecon-icon-select icon="{{newIcon}}"></homecon-icon-select>
          <paper-input label="color on:" value="{{newColorOn}}"></paper-input>
          <paper-input label="color off:" value="{{newColorOff}}"></paper-input>
          <paper-button on-tap="delete">Delete</paper-button>
        </template>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      label: {
        type: String,
        value: 'new dimmer'
      },
      state: {
        type: Number,
      },
      value: {
        type: Number,
      },
      valueOff: {
        type: Number,
        value: 0
      },
      valueOn: {
        type: Number,
        value: 1
      },
      edit: {
        type: Boolean,
        value: false
      },
      classes: {
        type: String,
        value: 'fullwidth',
      },
    };
  }

  valueChanged(e){
    window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': e.detail.value}})
  }

  call(){
    if(this.value < 0.5*this.valueOff + 0.5*this.valueOn){
      window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': this.valueOn}})
    }
    else{
      window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': this.valueOff}})
    }
  }

}

window.customElements.define('widget-dimmer', WidgetDimmer);
