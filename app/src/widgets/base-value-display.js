import {LitElement, html} from 'lit-element';

import '../shared-styles.js';

class BaseValueDisplay extends LitElement {

  static get properties() {
    return {
      prefix: {
        type: 'String'
      },
      suffix: {
        type: 'String'
      },
      state: {
        type: 'String',
        hasChanged(newVal, oldVal){
          if(typeof newVal != 'undefined'){
            window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': newVal}});
          }
        }
      },
      precision: {
        type: 'Number'
      },
      value: {
        type: 'String'
      },
    };
  }

  constructor() {
    super();
    this.precision = 1
    window.addEventListener('homecon-web-socket-message', (e) => this._handleMessage(e))
  }

  _handleMessage(e){
    // check if the message matches the template
    if(e.detail['event']==='state_value' && e.detail['data']['id']===this.state){
      this.value = e.detail['data']['value'];
    }
  }

  parseValue(value, precision){
    if(typeof value == 'number'){
      value = parseFloat(value).toFixed(precision)
    }
    return value;
  }

  render() {
    return html`
      <style include="shared-styles">
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
      <div class="value horizontal layout" on-tap="editValueDialog">
        <span class="prefix">${this.prefix}</span>
        <span class="flex">${this.parseValue(this.value, this.precision)}</span>
        <span class="suffix">${this.suffix}</span>
      <div>`;
  }

}

window.customElements.define('base-value-display', BaseValueDisplay);
