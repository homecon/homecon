import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';

import './shared-styles.js';
import './homecon-edit-dialog.js';
import './homecon-web-socket.js';
import './homecon-web-socket-object.js';
import './homecon-page-section.js';
import './homecon-pages-widget.js';

class HomeconPagesSection extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        .fullwidth{
          width: 100%;
        }
        .halfwidth{
          width: 49%;
          min-width: 190px;
        }
        .quarterwidth{
          width: 24%;
        }
        .center{
          text-align: center;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--primary-text-color);
        }
        .edit .collapsible{
          color: var(--header-text-color);
        }
      </style>

      <homecon-web-socket-object event="pages_section" key="{{key}}" data="{{section}}" auto>
      </homecon-web-socket-object>

      <homecon-page-section type="{{section.config.type}}" title="{{section.config.title}}">

        <template is="dom-repeat" id="widgets" items="{{section.widgets}}" as="widgetId">
          <homecon-pages-widget key="{{widgetId}}"></homecon-pages-widget>
        </template>

        <div class$="vertical layout [[_hiddenClass(edit)]]">
          <paper-button raised noink="true" on-tap="addWidgetDialog">add widget</paper-button>
        </div>

        <div class="edit" hidden="{{!edit}}">
          <paper-icon-button class$="{{section.config.type}}" icon="editor:mode-edit" noink="true" on-click="openEditDialog"></paper-icon-button>
        </div>
      </homecon-page-section>


      <homecon-edit-dialog id="editDialog" on-save="save">
          <paper-dropdown-menu label="page section type">
              <paper-menu class="dropdown-content" attr-for-selected="value" selected="{{newType}}">
                  <paper-item value="collapsible">collapsible</paper-item>
                  <paper-item value="raised">raised</paper-item>
                  <paper-item value="transparent">transparent</paper-item>
                  <paper-item value="underlined">underlined</paper-item>
              </paper-menu>
          </paper-dropdown-menu>
          <paper-input label="Title:" value="{{newTitle}}"></paper-input>
          <paper-button raised on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>

      <homecon-edit-dialog id="addWidgetDialog" on-save="addWidget">
          <paper-dropdown-menu label="widget type">
              <paper-menu class="dropdown-content" attr-for-selected="value" selected="{{widgetType}}">
                  <template is="dom-repeat" items="{{widgets}}" as="widget">
                      <paper-item value="{{widget}}">{{widget}}</paper-item>
                  </template>
              </paper-menu>
          </paper-dropdown-menu>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      key: {
        type: Number,
      },
    };
  }

  ready() {
    super.ready();
    this.edit = window.homecon.app_edit || false
    window.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  changeState() {
    this.opened = !this.opened;
  }

  openEditDialog() {
    this.newType = this.section.config.type;
    this.newTitle = this.section.config.title;
    this.$.editDialog.open();
  }

  save() {
    /*
    this.set('type',this.newType);
    this.set('title',this.newTitle);
    */
    this.$.editDialog.close();
  }

  delete() {
    this.fire('delete')
  }

  _openedClass(opened){
    if(opened){
        return "opened"
    }
    else{
        return "";
    }
  }

  _hiddenClass(edit){
      if(edit){
          return ""
      }
      else{
          return "hidden";
      }
  }

  _collapsibleClass(type){
      if(type!='collapsible'){
          this.opened = true;
          return "hidden"
      }
      else{
          return "";
      }
  }

}

window.customElements.define('homecon-pages-section', HomeconPagesSection);
