import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-localstorage/iron-localstorage.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-button/paper-button.js';
import '@hunsalz/web-socket/web-socket.js';

class HomeconAuthentication extends PolymerElement {

  static get template() {
    return html`
    `;
  }

  static get properties() {
    return {
      authenticated: {
        type: Boolean,
        notify: true,
        //value: false,
      },
      token: {
        type: String,
        notify: true,
        observer: '_tokenChanged'
      },
      tokenPayload: {
        type: String,
        notify: true
      },
      tokenHeader: {
        type: String,
        notify: true
      },
      connected: {
        type: Boolean,
        observer: '_connectedChanged'
      }
    };
  }

  ready(){
    // attatch the component to the window
    window.homeconAuthentication = this;
    this.authenticated = true; // FIXME temporarily
    //this.listen(window.homeconWebSocket, 'homecon-web-socket-message', 'onMessage');
  }

  login(){
    // Send a message to HomeCon
    if(this.token != ''){
      console.log('login');
      window.homeconWebSocket.send({'event':'authenticate','token':this.token});
    }
  }

  logout(){
    console.log('logout');
    if(this.connected){
      window.homeconWebSocket.send({'event':'logout','token':this.token});

    }
    this.token = '';
  }

  _connectedChanged(connected){
    if(connected){
      this.login();
    }
  }

  _tokenChanged(token){
    try{
      var parts = token.split('.');
      this.tokenHeader = JSON.parse(atob(parts[0]));
      this.tokenPayload = JSON.parse(atob(parts[1]));
      if(this.connected){
          this.login();
      }
    }
    catch(e){
      this.tokenHeader = {};
      this.tokenPayload = {};
      this.authenticated = false;
    }
  }

  _authenticatedChanged(e, d){
    if(this.authenticated){
      console.log('user authenticated');
      this.fire('homecon-authenticated');
    }
  }

  _logoutChanged(data){
    this.token = '';
  }

  _initializeDefaultToken(){
    this.token = ''
  }

}


window.customElements.define('homecon-authentication', HomeconAuthentication);
