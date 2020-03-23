import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-form/iron-form.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-dialog-scrollable/paper-dialog-scrollable.js';

import './shared-styles.js';
import './homecon-web-socket-object.js';
import './homecon-pages-menu-group.js';

class HomeconDialog extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
        }
      </style>

      <paper-dialog id="dialog" dynamic-align>
        <paper-dialog-scrollable>
          <slot></slot>
          <div class="horizontal layout">
            <slot name="buttons"></slot>
          </div>
        </paper-dialog-scrollable>
      </paper-dialog>
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

  center(){
    this.$.dialog.center();
  }

}

window.customElements.define('homecon-dialog', HomeconDialog);
