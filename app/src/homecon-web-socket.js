import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-localstorage/iron-localstorage.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-button/paper-button.js';
import '@hunsalz/web-socket/web-socket.js';


const addStateListener = function(obj, id=true, valueKey='value', stateKey='state'){
  if(id){
    window.addEventListener('homecon-web-socket-message', function(e, d){
      if(e.detail.event == 'state_value' && typeof obj[stateKey] != 'undefined' && (e.detail.data.path == obj[stateKey] || e.detail.data.id == obj[stateKey])){
        var oldVal = obj[valueKey]
        obj[valueKey] = e.detail.data.value
        obj.requestUpdate(valueKey, oldVal);
      }
    });
  }
  else{
    window.addEventListener('homecon-web-socket-message', function(e, d){
      if(e.detail.event == 'state_value' && typeof obj[stateKey] != 'undefined' && (e.detail.data.path == obj[stateKey].path || e.detail.data.id == obj[stateKey].id)){
        var oldVal = obj[valueKey]
        obj[valueKey] = e.detail.data.value
        obj.requestUpdate(valueKey, oldVal);
      }
    });
  }
}

const stateReadHasChanged = function(newVal, oldVal) {
  if(newVal != oldVal && newVal != null){
    if(typeof newVal == 'number'){
      window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': newVal}})
    }
    else{
      window.homecon.WebSocket.send({'event': 'state_value', 'data': {'id': newVal.id}})
    }
  }
  return false
}


class HomeconWebSocket extends PolymerElement {

  static get template() {
    return html`
      <style>
        :host {
          display: block;
        }

        #noConnection{
          position: fixed;
          bottom: 16px;
          right: 16px;
          margin: 0px;
        }
        #noConnection p{
          margin: 6px;
        }
      </style>

      <iron-localstorage name="homecon-websocket-settings" value="{{settings}}" @iron-localstorage-load-empty="_initializeDefaultSettings"></iron-localstorage>

      <web-socket id="webSocket"
        auto
        url="{{settings.address}}"
        on-state-changed="_stateChanged"
        on-last-response-changed="_handleResponse"
        on-last-error-changed="_handleError">
      </web-socket>

      <paper-dialog id="settings" no-cancel-on-outside-click no-cancel-on-esc-key>
        <h1>Websocket settings</h1>

        <p>Could not connect to homecon. Please review the connection settings</p>
        <paper-input label="Address:" value="{{settings.address}}"></paper-input>

        <paper-button dialog-dismiss>Close</paper-button>
      </paper-dialog>

      <paper-dialog id="noConnection" verticalAlign="bottom" no-cancel-on-outside-click no-cancel-on-esc-key>
        <p>No connection with HomeCon, <a href="#" on-tap="openSettings">review settings</a> or <a href="#" on-tap="connect">reconnect</a></p>
      </paper-dialog>
    `;
  }

  static get properties() {
    return {
      settings: {
        type: Object,
        notify: true
      },
      connected: {
        type: Boolean,
        notify: true,
        value: false,
      },
      response: {
        type: Object,
        observer: '_handleResponse'
      },
      error: {
        type: Object,
        observer: '_handleError'
      },
    };
  }

  ready() {
    super.ready();
    if(!this.connected){
        this.$.settings.open();
    }
    // attach the component to the window
    window.homeconWebSocket = this;
    window.homecon.WebSocket = this;
  }

  send(data) {
    this.$.webSocket.send(JSON.stringify(data))
  }

  connect() {
    this.$.webSocket.open();
  }

  openSettings() {
    this.$.settings.open()
  }

  _stateChanged(e) {
    if(e.detail.value == 1){
      this.$.settings.close();
      this.$.noConnection.close();

      console.log('Connected to HomeCon');
      this.connected = true;

      this.dispatchEvent(new CustomEvent('homecon-web-socket-connected'));
      window.dispatchEvent(new CustomEvent('homecon-authenticated')); // FIXME
    }
    else{
      console.log('Connection Closed');
      this.connected = false;
      this.$.noConnection.open();
    }
  }

  _initializeDefaultSettings() {
    this.settings = {'address':'ws://xxx:9024'};
  }


  _handleResponse(e, d) {
    window.dispatchEvent(new CustomEvent('homecon-web-socket-message', {'detail': JSON.parse(d['value'])}));
  }

  _handleError(e) {
    console.log('Error in HomeCon connection: '+ e.detail);
  }

}

window.customElements.define('homecon-web-socket', HomeconWebSocket);

export {addStateListener, stateReadHasChanged}
