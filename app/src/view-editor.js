import { LitElement, html } from 'lit-element';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-toggle-button/paper-toggle-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import './shared-styles.js';

import './homecon-page.js';
import './homecon-page-header.js';
import './homecon-page-section.js';


class ViewEditor extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean
      },
    };
  }

  constructor() {
    super();
    this.edit = false;
  }

  render() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;
        }
        #fileInput {
          display: none;
        }
      </style>

      <homecon-web-socket-object @change="${this._export_pages_changed}" id="pages_export" event="pages_export" key="pages_export">
      </homecon-web-socket-object>

      <homecon-page>
        <homecon-page-header title="Edtor" icon="pagebuilder_pagebuilder"></homecon-page-header>
        <homecon-page-section type="raised">
          <paper-toggle-button ?checked="${this.edit}" @checked-changed="${this._edit_changed}">Edit mode</paper-toggle-button>
        </homecon-page-section>

        <homecon-page-section type="raised">
          <paper-button @tap="${this._import_pages}">Import pages</paper-button>
          <paper-button @tap="${this._export_pages}">Export pages</paper-button>
        </homecon-page-section>

      </homecon-page>
      <input id="fileInput" type="file"></input>
    `;
  }

  _edit_changed(e, d){
    window.homecon.app_edit = e.detail.value
    window.dispatchEvent(new CustomEvent('app-edit', {bubbles: true, detail: {'edit': window.homecon.app_edit}}));
  }

  _export_pages(e, d){
    this.shadowRoot.getElementById('pages_export').send()
  }

  _export_pages_changed(e, d){
    var filename = 'homecon_pages_export.json'
    var text = JSON.stringify(e.detail.data, null, 4)
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  _import_pages(e, d){
    var element = this.shadowRoot.getElementById('fileInput')

    element.onchange = e => {
       var file = e.target.files[0];
       var reader = new FileReader();
       reader.readAsText(file,'UTF-8');
       reader.onload = readerEvent => {
          var value = JSON.parse(readerEvent.target.result);
          window.homecon.WebSocket.send({'event': 'pages_import', 'data': {'value': value}})
       }
    }
    element.click();
  }
}

window.customElements.define('view-editor', ViewEditor);
