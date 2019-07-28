import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';

import './shared-styles.js';
import './homecon-edit-dialog.js';
import './homecon-web-socket-object.js';
import './homecon-widget.js';
import './widgets/widget-switch.js';
import './widgets/widget-shading.js';

class HomeconPagesWidget extends PolymerElement {
  static get template() {
    return html`
      <style>
        :host{
          display: inline-block;
          position: relative;
        }
      </style>

      <homecon-web-socket-object id="websocketWidget" event="pages_widget" key="{{key}}" data="{{widget}}" auto></homecon-web-socket-object>

      <homecon-widget widget="{{widget}}" edit="{{edit}}"></homecon-widget>
    `;
  }

  static get properties() {
    return {
      class: {
        reflectToAttribute: true,
      },
      key: {
        type: 'String',
      },
      widget: {
        type: 'Object',
      },
      edit: {
        type: 'Boolean',
        value: false,
      }
    };
  }

  ready() {
    super.ready();
    this.loaded = false;
    this.edit = window.homecon.app_edit || false
    window.addEventListener('app-edit',  (e) => {this.edit = e.detail.edit});
  }

  editWidget(e, d){
    e.stopPropagation()
    this.$.websocketWidget.send({'config': d});
  }

  deleteWidget(e){
    e.stopPropagation();
    this.$.websocketWidget.send(null);
  }

}

window.customElements.define('homecon-pages-widget', HomeconPagesWidget);
