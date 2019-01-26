import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import './shared-styles.js';

import './homecon-page.js';
import './homecon-page-header.js';
import './homecon-web-socket-object.js';


class HomeconStatesList extends PolymerElement {
  static get template() {
    return html`
       <style>
          :host{
            display: block;
            padding: 20px;
          }
          @media only screen and (max-width: 768px) {
            :host{
                padding: 4px;
              }
          }
        </style>

      <homecon-web-socket-object event="state_children" key="{{key}}" data="{{states}}" auto>
      </homecon-web-socket-object>

      <template is="dom-repeat" id="sections" items="{{states}}" as="state">
        <div>{{state.path}}</div>
        <homecon-states-list key="{{state.id}}"></homecon-states-list>
      </template>
    `;
  }

  static get properties() {
    return {
      key: {
        type: Number,
      },
    };
  }
}

window.customElements.define('homecon-states-list', HomeconStatesList);


class ViewStates extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;
        }
      </style>


      <homecon-page>
        <homecon-page-header title="States" icon="edit_settings"></homecon-page-header>
        <div id="content" class="raised">
          <homecon-states-list key="0"></homecon-states-list>
        </div>
      </homecon-page>
    `;
  }
}

window.customElements.define('view-states', ViewStates);
