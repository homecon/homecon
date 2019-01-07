
import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

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

class HomeconPagesMenuPage extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: block;
          position: relative;
          width: 100%;
          color: var(--primary-text-color);
        }
        a.item{
          display: block;
          position: relative;
          cursor: pointer;

          background-color: var(--menu-item-background-color);
          border-bottom: solid 1px;
          border-color: var(--menu-item-border-color);

          text-decoration: none;

          height: 60px;
        }
        a.item:hover{
          background-color: var(--menu-item-background-color-hover);
        }
        a.item .icon{
          height: 100%;
        }
        a.item .title{
          display: inline-block;
          font-size: 18px;
          font-family: sans-serif;
          font-weight: 700;
          color: var(--menu-item-text-color);
          text-shadow: 0 1px 0 var(--text-shadow-color);
          margin-left: 40px;
          overflow: hidden;
        }
        .edit{
          position: absolute;
          top: 0px;
          right: 5px;
          color: var(--menu-item-text-color);
        }
      </style>

      <homecon-web-socket-sender id="websocket">
      </homecon-web-socket-sender>

      <homecon-web-socket-object event="pages_page" key="{{key}}" data="{{page}}" auto>
      </homecon-web-socket-object>

      <a class="item horizontal layout center" href="/pages/[[page.path]]">
        <img class="icon" src="[[_parseIcon(page.config.icon)]]">
        <h1 class="title">{{page.config.title}}</h1>
      </a>

      <div class="edit" hidden="{{!edit}}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-click="openEditDialog"></paper-icon-button>
      </div>


      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-input label="Title:" value="{{newTitle}}"></paper-input>
        <homecon-icon-select icon="{{newIcon}}"></homecon-icon-select>
        <paper-button raised on-click="delete">Delete</paper-button>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      key: {
        type: String,
      },
    };
  }

  ready() {
    super.ready();
    this.edit = false
    this.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  openEditDialog(){
    this.set('newTitle',this.config.title);
    this.set('newIcon',this.config.icon);
    this.$.editDialog.open();
  }

  save(){
    this.$.editDialog.close();
    this.$.websocket.send({'event':'pages_page','path':this.path,'value':{'config':{'title':this.newTitle,'icon':this.newIcon}}})
  }

  delete(){
    this.$.websocket.send({'event':'pages_page','path':this.path,'value':null})
  }

  _parseIcon(icon){
    if(icon==''){
      return '/images/icon/ffffff/blank.png';
    }
    else{
      return '/images/icon/ffffff/'+ icon +'.png';
    }
  }

}

window.customElements.define('homecon-pages-menu-page', HomeconPagesMenuPage);
