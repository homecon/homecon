import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-form/iron-form.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-dialog-scrollable/paper-dialog-scrollable.js';

import './shared-styles.js';
import './homecon-dialog.js';

class HomeconEditDialog extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
        }
      </style>

      <homecon-dialog id="dialog">
          <slot></slot>
          <div slot="buttons">
            <paper-button raised on-tap="save">save</paper-button>
            <paper-button raised on-tap="close">cancel</paper-button>
          </div>
      </homecon-dialog>
    `;
  }

  static get properties() {
    return {
    };
  }

  open() {
     this.$.dialog.open();
  }

  close() {
    this.$.dialog.close();
  }

  formSubmit() {
    this.$.form.submit();
  }

  save() {
    this.dispatchEvent(new CustomEvent('save', this.data));
    this.$.dialog.close();
  }

  center(){
    this.$.dialog.center();
  }

}

window.customElements.define('homecon-edit-dialog', HomeconEditDialog);
