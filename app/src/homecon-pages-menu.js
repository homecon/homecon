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

      <homecon-web-socket-object id="pageGroups" event="pages_group_ids" key="" data="{{group_ids}}" auto>
      </homecon-web-socket-object>

      <template is="dom-repeat" id="groups" items="{{group_ids}}" as="group_id">
        <homecon-pages-menu-group key="{{group_id}}" on-delete="deleteGroup" on-change-state="changeState">
        </homecon-pages-menu-group>
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

  ready() {
    super.ready();
    this.edit = false
    this.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
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

}

window.customElements.define('homecon-pages-menu', HomeconPagesMenu);
