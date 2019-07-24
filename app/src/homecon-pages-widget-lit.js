//<script src="node_modules/@webcomponents/webcomponentsjs/webcomponents-bundle.js"></script>
//<script type="module">
import {LitElement, html} from 'lit-element';

import './shared-styles.js';
import './homecon-web-socket-object.js';
import './homecon-edit-dialog.js';
import './widgets/widget-switch.js';
import './widgets/widget-shading.js';


class HomeconPagesWidget extends LitElement {

  static get properties() {
    return {
      key: {
        type: 'String'
      },
      edit: {
        type: 'Boolean',
        value: false,
        observer: 'editChanged'
      }
    };
  }

  constructor() {
    super();
  }

  async get_from_websocket(key) {
    console.log(this.key)
    let socket = new WebSocket('ws://localhost:9024');
    window.socket = socket

    var that = this
    window.socket.onmessage = function(event) {
      console.log(event)
      that.widget = {}
    };

    window.socket.onopen = function(e) {
      console.log("[open] Connection established, send -> server");
      window.socket.send({'event': 'pages_widget', 'data': {'id': this.key}})
    };

    return
  }

  render() {

    return html`
      <style>
        .mood {
          color: green;
        }
      </style>
      Web Components are <span class="mood">${this.get_from_websocket(this.key)}</span>!`;
  }

}

window.customElements.define('homecon-pages-widget', HomeconPagesWidget);
//</script>