import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/paper-button/paper-button.js';

import './shared-styles.js';
import './homecon-page.js';
import './homecon-web-socket-object.js';
import './homecon-pages-menu-group.js';
import './homecon-page-header.js';
import './homecon-pages-section.js';

class HomeconPagesPage extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: block;
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

      <homecon-page>
        <template is="dom-if" if="[[_filterHome(page)]]">
          <homecon-page-header title="[[page.config.title]]" icon="[[page.config.icon]]" widget="[[page.config.widget]]"></homecon-page-header>
        </template>

        <template is="dom-repeat" id="sections" items="{{page.sections}}" as="section">
          <homecon-pages-section section="{{section}}" on-delete="deletePageSection"></homecon-pages-section>
        </template>


        <div class$="vertical layout [[_hiddenclass(edit)]]">
          <paper-button raised noink="true" on-tap="addSection">add section</paper-button>
        </div>
      </homecon-page>

      <homecon-edit-dialog id="addSectionDialog" on-save="addSection">
        Add section
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      page: Object,
    };
  }

  ready() {
    super.ready();
    this.loaded = false;
    this.edit = window.homecon.app_edit || false
    window.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  load(){
      if( !this.loaded ){
          this.$.websocketPage.send();
          this.loaded = true;
      }
  }

  addSection(){
      this.$.websocket.send({'event':'pages_section', 'page':this.path})
  }

  _filterHome(item){
    if(typeof item != 'undefined'){
      return item.path != '/home/home';
    }
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

window.customElements.define('homecon-pages-page', HomeconPagesPage);
