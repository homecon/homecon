import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/paper-button/paper-button.js';

import './shared-styles.js';
import './homecon-web-socket-object.js';
import './homecon-pages-menu-group.js';

class HomeconPagesMenu extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
        }
        paper-button{
          width: 90%;
          margin: 8px;
        }
        .spacer{
          height: 70px;
        }
      </style>

      <homecon-web-socket-sender id="websocket">
      </homecon-web-socket-sender>

      <template is="dom-repeat" id="groups" items="{{groups}}" as="group">
        <template is="dom-if" if="{{_isNotHome(group)}}">
          <homecon-pages-menu-group group="{{group}}" on-delete="deleteGroup" on-change-state="changeState">
          </homecon-pages-menu-group>
        </template>
      </template>

      <div class$="vertical layout [[_hiddenclass(edit)]]">
          <paper-button raised noink="true" on-click="addGroup">add group</paper-button>
      </div>

      <!--a spacer to be able to scroll all the way down-->
      <div class="spacer">
          &nbsp;
      </div>
    `;
  }

  static get properties() {
    return {
      groups: Object,
    };
  }

  ready() {
    super.ready();
    this.edit = window.homecon.app_edit || false
    window.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  changeState(e) {
    var elements = this.shadowRoot.querySelectorAll('homecon-pages-menu-group');//this.getElementsByTagName("HOMECON-PAGES-MENU-GROUP")
    for(var i=0;i<elements.length;i++){
      elements[i].dispatchEvent(new CustomEvent('menu-change-state', {'detail': {'element': e.detail.element}}));
    }
  }

  addGroup(e) {
    this.$.websocket.send({'event': 'pages_group'})
  }

  deleteGroup(e) {
    console.log(e) // FIXME
    this.$.websocket.send({'event': 'pages_group'})
  }

  _hiddenclass(edit) {
    if(edit){
      return '';
    }
    else{
      return 'hidden';
    }
  }

  _isNotHome(group){
    return group.name != 'home';
  }

}

window.customElements.define('homecon-pages-menu', HomeconPagesMenu);
