
import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-input/paper-input.js';

import './shared-styles.js';
import './homecon-web-socket-object.js';
import './homecon-edit-dialog.js';
import './homecon-pages-menu-page.js';

class HomeconPagesMenuGroup extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: block;
          width: 100%;
          position: relative;
        }
        a.header{
          display: block;
          cursor: pointer;
          min-height: 16px;
          padding: 12px 12px 12px 40px;

          background-color: var(--header-background-color);
          border-top: solid 1px;
          border-color: var(--header-border-color);

          font-size: 16px;
          font-family: sans-serif;
          font-weight: 700;
          color: var(--header-text-color);
          text-shadow: 0 1px 0 var(--header-text-shadow-color);
          text-decoration: none;
        }
        a.header:hover{
          background-color: var(--header-background-color-hover);
        }
        .edit{
          position: absolute;
          top: 0px;
          right: 5px;
          color: var(--header-text-color);
        }
      </style>

      <homecon-web-socket-sender id="websocket">
      </homecon-web-socket-sender>

      <homecon-web-socket-object event="pages_group" key="{{key}}" data="{{group}}" auto>
      </homecon-web-socket-object>

      <a class="header" on-tap="changeState">
        {{group.config.title}}
      </a>

      <div class="edit" hidden="{{!edit}}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <iron-collapse opened="{{opened}}">
        <template is="dom-repeat" id="groups" items="{{group.pages}}" as="page_id">
          <homecon-pages-menu-page key="{{page_id}}" on-delete="deletePage">
          </homecon-pages-menu-page>
        </template>

        <div class$="vertical layout [[_hiddenclass(edit)]]">
          <paper-button raised noink="true" on-click="addPage">add page</paper-button>
        </div>
      </iron-collapse>

      <homecon-edit-dialog id="editDialog" on-save="save">
          <paper-input label="Title:" value="{{newTitle}}"></paper-input>
          <paper-button raised on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      key: {
        type: String,
      },
      opened: {
        type: Boolean,
      },
    };
  }

  ready() {
    super.ready();
    this.addEventListener('menu-change-state',  (e) => this._menuChangeState(e));
    this.edit = false
    this.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  addPage(e) {
    this.$.websocket.send({'event': 'pages_group_page'})
  }

  changeState(){
    this.opened = !this.opened;
    this.dispatchEvent(new CustomEvent('change-state', {'detail': {'element': this}}));
  }

  _menuChangeState(e){
    if(e.detail.element != this){
      this.opened = false;
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

window.customElements.define('homecon-pages-menu-group', HomeconPagesMenuGroup);
