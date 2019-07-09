import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';

class BaseStatusLight extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: inline-block;
          position: relative;
        }
        .icon{
          width: 100%;
          height: 100%;
        }
      </style>

      <template is="dom-if" if="{{_useKey(key)}}">
        <homecon-web-socket-object id="websocketObject" event="state" key="{{key}}" data="{{value}}" send-on-authenticated></homecon-web-socket-object>
      </template>

      <img class="icon" src="[[_parseIcon(icon, value)]]">
    `;
  }

  static get properties() {
    return {
      key: {
        type: 'String',
        value: '',
        observer: '_keyChanged'
      },
      value: {
        type: 'Number',
        value: 0,
      },
      valueThreshold: {
        type: Number,
        value: 0.01,
      },
      icon: {
        type: 'String',
        value: 'light_light',
      },
      colorOn: {
        type: 'String',
        value: 'f79a1f',
      },
      colorOff: {
        type: 'String',
        value: 'ffffff',
      },
    };
  }

  ready() {
    super.ready()
    this.color = 'ffffff';
  }

  _keyChanged(key){
    if(this._useKey(key)){
      this.$.websocketObject.send();
    }
  }

  send(value) {
    if(this._usePath(this.path)){
      this.$.websocketObject.send(value);
    }
  }

  _useKey(key) {
    return key != '';
  }

  _parseIcon(icon, value){
    var color = this.colorOff;
    if(value >= this.valueThreshold){
      color = this.colorOn;
    }

    if(icon==''){
      return '/images/icon/'+color+'/blank.png';
    }
    else{
      return '/images/icon/'+color+'/'+ icon +'.png';
    }
  }
}

window.customElements.define('base-status-light', BaseStatusLight);
