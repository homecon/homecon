import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-slider/paper-slider.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';

class BaseSlider extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: inline-block;
          position: relative;
        }
        paper-slider{
          width: 100%;
          --paper-slider-height: 5px;
          --paper-slider-active-color: #efad57;
          --paper-slider-knob-color: #f79a1f;
        }
        .icon{
          width: 100%;
          height: 100%;
        }
      </style>

      <template is="dom-if" if="{{_useKey(key)}}">
        <homecon-web-socket-object id="websocketObject" event="state_value" key="{{key}}" data="{{value}}" on-change="_valueChanged" send-on-authenticated></homecon-web-socket-object>
      </template>

      <paper-slider min="[[_valueToSliderValue(min, log)]]" max="[[_valueToSliderValue(max, log)]]" step="[[_sliderStep(min, max, log)]]" value="{{sliderValue}}" on-change="call"></paper-slider>
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
        notify: true,
      },
      valueMin: {
        type: Number,
        value: 0,
      },
      valueMax: {
        type: Number,
        value: 1,
      },
      log: {
        type: Boolean,
        value: false,
      },
    };
  }

  _keyChanged(key){
    if(this._useKey(key)){
//      this.$.websocketObject.send();
    }
  }

  send(value) {
    if(this._useKey(this.key)){
      this.$.websocketObject.send(value);
    }
  }

  call(){
    if(this._useKey(this.key)){
      var value = this._sliderValueToValue(this.sliderValue, this.log);
      window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.key, 'value': value}})
    }
    else{
      this.dispatchEvent(new CustomEvent('value-changed', {'detail': {'value': this._sliderValueToValue(this.sliderValue, this.log)}}));
    }
  }

  _useKey(key) {
    return key != '';
  }

  _valueToSliderValue(value, log){
    if(log){
      return Math.log10(value);
    }
    else{
      return value-0;
    }
  }

  _sliderValueToValue(value, log){
    if(log){
      return Math.pow(10,value);
    }
    else{
      return value-0;
    }
  }

  _valueChanged(event, data){
    this.sliderValue = this._valueToSliderValue(this.value,this.log);
  }

  _sliderStep(min, max, log){
      return Math.min(1,(this._valueToSliderValue(max, log)-this._valueToSliderValue(min, log))/100);
  }

}

window.customElements.define('base-slider', BaseSlider);
