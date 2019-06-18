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
import '../homecon-page-section.js';


class HomeconKnxSettings extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">

      </style>

      <!--<homecon-web-socket-sender id="websocket"></homecon-web-socket-sender>
      <homecon-web-socket-object event="knx_settings" key="{{key}}" data="{{section}}" auto>
      </homecon-web-socket-object>-->

      <homecon-page-section type="raised" title="KNX settings">

      </homecon-page-section>
    `;
  }
}

window.customElements.define('HomeconKnxSettings', HomeconKnxSettings);
