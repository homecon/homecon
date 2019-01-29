import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/paper-dropdown-menu/paper-dropdown-menu.js';
import '@polymer/paper-item/paper-item.js';
import '@polymer/paper-listbox/paper-listbox.js';

import './homecon-web-socket-object.js';

class HomeconStateSelect extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: block;
        }
      </style>

      <homecon-web-socket-object event="state_list" key="" data="{{states}}" auto>
      </homecon-web-socket-object>

      <paper-dropdown-menu label="{{label}}" on-opened-changed="_getStates" no-animations>
        <paper-listbox slot="dropdown-content" selected="{{value}}">
        <paper-item key="0">/</paper-item>
          <template is="dom-repeat" items="{{states}}" as="state">
            <paper-item key="{{state.id}}">{{state.path}}</paper-item>
          </template>
        </paper-listbox>
      </paper-dropdown-menu>
    `;
  }

  static get properties() {
    return {
      label: {
        type: 'String',
        value: 'State',
      },
      value: {
        type: 'Number',
        notify: true
      },
    };
  }

}

window.customElements.define('homecon-state-select', HomeconStateSelect);
