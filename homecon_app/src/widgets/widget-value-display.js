import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-value-display.js';

class WidgetValueDisplay extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>

        <base-value-display state="{{state}}" prefix="{{prefix}}" suffix="{{suffix}}"></base-value-display>

        <div class="edit" hidden="{{!edit}}">
          <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
        </div>

        <homecon-edit-dialog id="editDialog" on-save="save">
          <template is="dom-if" if="{{edit}}">
            <paper-input label="prefix:" value="{{newPrefix}}"></paper-input>
            <paper-input label="suffix:" value="{{newSuffix}}"></paper-input>
            <homecon-state-select value="{{newState}}"></homecon-state-select>
            <paper-button on-tap="delete">Delete</paper-button>
          </template>
        </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      prefix: {
        type: String,
        value: '',
      },
      suffix: {
        type: String,
        value: '',
      },
      state: {
        type: Number,
      },
      edit: {
        type: Boolean,
        value: false
      },
      classes: {
        type: String,
        value: 'halfwidth',
      },
    };
  }

  openEditDialog(e){
    this.newPrefix = this.prefix
    this.newSuffix = this.suffix
    this.newState = this.state
    this.$.openEditDialog.open()
  }

}

window.customElements.define('widget-value-display', WidgetValueDisplay);
