import { LitElement, html, css } from 'lit-element';
import '@polymer/iron-localstorage/iron-localstorage.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-button/paper-button.js';
import '@hunsalz/web-socket/web-socket.js';


class HomeconWebSocketLit extends LitElement {

  static get properties() {
    return {
      settings: {
        type: Object,
      },
      connected: {
        type: Boolean,
      },
    };
  }

  constructor() {
    super();
    window.homecon.WebSocket = this
    this.connected = false;

    var settings = JSON.parse(localStorage.getItem('homecon-websocket-settings'))
    if(settings === null){
      this.settings = {'address': 'ws://xxx:9024'};
    }
    else{
      this.settings = settings
    }
    console.log(this.settings.address)
    var socket = new WebSocket(this.settings.address);

    socket.onOpen = function(e) {
      console.log('Connected to HomeCon');
      window.homecon.WebSocket.connected = true;

      window.homecon.WebSocket.$.noConnection.close();

      window.dispatchEvent(new CustomEvent('homecon-web-socket-connected'));
      window.dispatchEvent(new CustomEvent('homecon-authenticated')); // FIXME
    };

    socket.onclose = function(event) {
      window.homecon.WebSocket.connected = false;
      window.homecon.WebSocket.$.noConnection.open();
      if(event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
      } else {
        console.log('[close] Connection died');
      }
    };

    socket.onerror = function(error) {
      console.log(`Error in HomeCon connection: ${error.message}`);
    };

    socket.onmessage = function(event) {
      console.log(`Data received: ${event.data}`);
      window.dispatchEvent(new CustomEvent('homecon-web-socket-message', {'detail': JSON.parse(event.data)}));
    };

  }

  connect() {

  }

  _address_changed(e) {
    console.log(e.detail)
    this.settings.address = e.detail.value;
    localStorage.setItem('homecon-websocket-settings', this.settings)
  }

  static get styles() {
    return css `
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
    `;
  }

  render() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;
        }
      </style>

      <paper-dialog id="settings" no-cancel-on-outside-click no-cancel-on-esc-key>
        <h1>Websocket settings</h1>

        <p>Could not connect to homecon. Please review the connection settings</p>
        <paper-input label="Address:" value="${this.settings.address}" @changed="${this._address_changed}"></paper-input>

        <paper-button dialog-dismiss>Close</paper-button>
      </paper-dialog>

      <paper-dialog id="noConnection" verticalAlign="bottom" no-cancel-on-outside-click no-cancel-on-esc-key>
        <p>No connection with HomeCon, <a href="#" on-tap="openSettings">review settings</a> or <a href="#" on-tap="connect">reconnect</a></p>
      </paper-dialog>
    `;
  }



}

window.customElements.define('homecon-web-socket-lit', HomeconWebSocketLit);


class HomeconWebSocketObjectLit extends LitElement {

  static get properties() {
    return {
      event: {
        type: String,
      },
      key: {
        type: String,
      },
      keyKey: {
        type: String,
      },
      debounce: {
        type: Number,
      }
    };
  }
  constructor() {
    this.event = '';
    this.debounce = 10;

    window.addEventListener('homecon-authenticated',  (e) => {this.send()});
    window.addEventListener('homecon-web-socket-message', (e) => this._handleMessage(e))
  }

  send(data){
    var senddata = {'event': this.event, 'data': {}}
    if(typeof this.key != undefined && this.key !== ''){
      senddata['data'][this.keyKey] = this.key
    }
    if(typeof data != undefined){
      senddata['data'][this.dataKey] = data
    }
    window.homecon.WebSocket.send(senddata);
  }

}

window.customElements.define('homecon-web-socket-object-lit', HomeconWebSocketObjectLit);
