import { LitElement, html } from 'lit-element';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-toggle-button/paper-toggle-button.js';

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
      </style>

      <homecon-page>
        <homecon-page-header title="Edtor" icon="pagebuilder_pagebuilder"></homecon-page-header>
        <homecon-page-section type="raised">
          <paper-toggle-button ?checked="${this.edit}" @checked-changed="${this._edit_changed}">Edit mode</paper-toggle-button>
        </homecon-page-section>
      </homecon-page>
    `;
  }

  _edit_changed(e, d){
    window.homecon.app_edit = e.detail.value
    window.dispatchEvent(new CustomEvent('app-edit', {bubbles: true, detail: {'edit': window.homecon.app_edit}}));
  }
}

window.customElements.define('view-editor', ViewEditor);
