import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-status-light.js';

class WidgetSwitch extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
        }
        .button {
          text-transform: none;
          min-width: 250px;
          padding: 0px;
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
        <homecon-web-socket-object event="state_value" key="[[config.state]]" data="{{value}}" auto>
        </homecon-web-socket-object>

        <paper-button noink class="button horizontal layout start-justified" on-tap="call">
          <base-status-light class="icon" value="{{value}}" value-threshold="[[_valueThreshold(config.valueOn, config.valueOff)]]" icon="[[config.icon]]" color-on="[[config.colorOn]]" color-off="[[config.colorOff]]"></base-status-light>
          <div class="label">[[config.label]]</div>
        </paper-button>


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
      config: {
        type: 'Object',
        value: {'label': 'new switch', 'state': '', 'valueOn': 1, 'valueOff': 0, 'colorOn': 'f79a1f', 'colorOff': 'ffffff', 'icon': 'light_light'},
      },
      edit: {
        type: 'Boolean',
        value: false
      },
      classes: {
        type: 'String',
        value: 'halfwidth',
      },
    };
  }

  _valueThreshold(valueOn, valueOff){
    return 0.5*valueOn + 0.5*valueOff
  }

  call(){
    if(this.value < this._valueThreshold(this.config.valueOn, this.config.valueOff)) {
      window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.config.state, 'value': this.config.valueOn}})
    }
    else {
      window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.config.state, 'value': this.config.valueOff}})
    }
  }

}

window.customElements.define('widget-switch', WidgetSwitch);
