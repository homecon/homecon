import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import {microTask} from '@polymer/polymer/lib/utils/async.js';
import {Debouncer} from '@polymer/polymer/lib/utils/debounce.js';

class HomeconWebSocketObject extends PolymerElement {
  /*
  the json messages are structured like this

  {
    "event": "some-event",
    "data": {
      "id": "the_object_identifier",
      "value": 123,
    },
  }

  or

  {
    "event": "some-event",
    "data": [123, 456, 789],
  }

  */
  static get template() {
    return html`
    `;
  }

  static get properties() {
    return {
      auto: {
        type: Boolean,
        value: false
      },
      sendOnAuthenticated: {
        type: Boolean,
        value: false
      },
      event: {
        type: String,
        value: ''
      },
      key: {
        type: String,
        observer: '_keyChanged',
      },
      keyKey: {
        type: String,
        value: 'id'
      },
      data: {
        notify: true,
        observer: '_dataChanged'
      },
      dataKey: {
        type: String,
        value: 'value'
      },
      debounce: {
        type: Number,
        value: 10
      }
    };
  }

  ready(){
    this.observe = true;
    window.addEventListener('homecon-web-socket-message', (e) => this._handleMessage(e))
    if(this.auto || this.sendOnAuthenticated){
      window.addEventListener('homecon-authenticated',  (e) => this._handleAuthenticated(e));
      //window.addEventListener('homecon-connected',  (e) => this._handleAuthenticated(e));  fixme
      // send without value key to start monitoring
      if(window.homeconWebSocket.connected && window.homeconAuthentication.authenticated && typeof this.key != 'undefined'){
        this.send();
      }
    }
  }

  send(data){
    var senddata = {'event': this.event, 'data': {}}
    if(typeof this.key != undefined && this.key !== ''){
      senddata['data'][this.keyKey] = this.key
    }
    if(typeof data != undefined){
      senddata['data'][this.dataKey] = data
    }
    window.homeconWebSocket.send(senddata);
  }

  _handleMessage(e){
    // check if the message matches the template
    if(e.detail['event']===this.event && (typeof this.key==='undefined'  || this.key==='' || e.detail['data'][this.keyKey]===this.key)){
      // avoid looping forever
      this.observe = false;
      // extract data from the message
      this.data = e.detail['data'][this.dataKey];
      this.dispatchEvent(new CustomEvent('change', {'detail': {'data': this.data}}));
      // reobserve
      this.observe = true;
    }
  }

  _handleAuthenticated(e){
      if(this.auto || this.sendOnAuthenticated){
        this.send();
      }
    }

  _sendData(){
    this.send(this.data);
  }

  _dataChanged(data, olddata){
    if(this.auto && this.observe && window.homeconWebSocket.connected && window.homeconAuthentication.authenticated && typeof this.path != 'undefined' && typeof this.event != 'undefined' && !(data == '' && typeof olddata == 'undefined') ){
      this._debounceJob = Debouncer.debounce(this._debounceJob, microTask, () => this._sendData());
    }
  }

  _keyChanged(key, oldKey){
    if( (this.auto || this.sendOnAuthenticated) && this.observe && window.homeconWebSocket.connected && window.homeconAuthentication.authenticated && !(key == '')){
      this._debounceJob = Debouncer.debounce(this._debounceJob, microTask, () => this.send());
    }
  }

}


window.customElements.define('homecon-web-socket-object', HomeconWebSocketObject);
