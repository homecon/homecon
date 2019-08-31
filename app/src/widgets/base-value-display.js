import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';

import '../shared-styles.js';

class BaseValueDisplay extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
        }
        .value{
          font-size: 16px;
          font-weight: 700;
        }
        .prefix{
          margin-right: 5px;
        }
        .suffix{
          margin-left: 5px;
        }
      </style>
        <homecon-web-socket-object event="state_value" key="[[state]]" data="{{value}}" auto>
        </homecon-web-socket-object>

        <div class="value horizontal layout" on-tap="editValueDialog">
          <div class="prefix">{{prefix}}</div>
          <div class="flex">{{parseValue(value)}}</div>
          <div class="suffix">{{suffix}}</div>
        <div>
    `;
  }

  static get properties() {
    return {
      prefix: {
        type: String,
        value: '',
      },
      suffix: {
        type: String,
        value: '',
      },
      state: {
        type: Number,
      },
      precision: {
        type: Number,
        value: 1
      },
    };
  }

  parseValue(value){
    if(typeof value == 'number'){
      value = parseFloat(value).toFixed(this.precision)
    }

    return value;
  }

}

window.customElements.define('base-value-display', BaseValueDisplay);
