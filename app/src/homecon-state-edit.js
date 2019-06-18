import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';

import '@lrnwebcomponents/json-editor/json-editor.js';

import './shared-styles.js';
import './homecon-state-select.js';


class HomeconStateEdit extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: block;
          padding-left: 10px;
        }
      </style>

      <homecon-state-select id="stateSelect" label="Parent" value="{{newParent}}"></homecon-state-select>
      <paper-input label="Name" value="{{newName}}"></paper-input>
      <paper-input label="Type" value="{{newType}}"></paper-input>
      <paper-input label="Quantity" value="{{newQuantity}}"></paper-input>
      <paper-input label="Unit" value="{{newUnit}}"></paper-input>
      <paper-input label="Label" value="{{newLabel}}"></paper-input>
      <paper-input label="Description" value="{{newDescription}}"></paper-input>
      <json-editor label="Config" value="{{newConfig}}"></json-editor>
    `;
  }

  static get properties() {
    return {
      oldState: {
        type: Object,
        observer: '_oldStateChanged'
      }
    };
  }

  save() {
    var parent = this.newParent
    if(parent==0){
      parent = null
    }

    var state = {
      'name': this.newName,
      'parent': parent,
      'type': this.newType,
      'quantity': this.newQuantity,
      'unit': this.newUnit,
      'label': this.newLabel,
      'description': this.newDescription,
      'config': JSON.parse(this.newConfig),
    };
    if(typeof this.oldState == 'undefined' || this.oldState == null){
      window.homeconWebSocket.send({'event': 'state_add', 'data': state})
    }
    else{
      state.id = this.oldState.id;
      window.homeconWebSocket.send({'event': 'state_update', 'data': state})
    }
  }

  _oldStateChanged(e) {
    if(typeof this.oldState == 'undefined' || this.oldState == null){
      this.newName = 'my_new_state';
      this.newParent = 0;
      this.newType = '';
      this.newQuantity = '';
      this.newUnit = '';
      this.newLabel = '';
      this.newDescription = '';
      this.newConfig = '{}';
    }
    else{
      console.log(this.oldState);
      this.newName = this.oldState.name;
      if(this.oldState.parent == null) {
        this.newParent = 0;
      }
      else{
        this.newParent = this.oldState.parent;
      }
      this.newType = this.oldState.type;
      this.newQuantity = this.oldState.quantity;
      this.newUnit = this.oldState.unit;
      this.newLabel = this.oldState.label;
      this.newDescription = this.oldState.description;
      this.newConfig = JSON.stringify(this.oldState.config);
    }
  }

}

window.customElements.define('homecon-state-edit', HomeconStateEdit);
