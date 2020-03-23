import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-icon-button/paper-icon-button.js';

import './shared-styles.js';

import './homecon-page.js';
import './homecon-page-header.js';
import './homecon-page-section.js';
import './homecon-widget.js';
import './homecon-web-socket-object.js';
import './homecon-state-edit.js';
import './homecon-edit-dialog.js';


class ViewSettings extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;
        }
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
      </style>

      <homecon-web-socket-object event="plugins_settings" key-key="plugin" key="all" data="{{plugins_sections}}" auto>
      </homecon-web-socket-object>

      <homecon-page>
        <homecon-page-header title="Settings" icon="edit_settings"></homecon-page-header>

        <template is="dom-repeat" id="sections" items="{{plugins_sections}}" as="section">
          <homecon-page-section type="raised" title="{{section.config.title}}">

          <template is="dom-repeat" id="widgets" items="{{section.widgets}}" as="widget">
            <homecon-widget widget="{{widget}}"></homecon-widget>
          </template>

        </template>

      </homecon-page>
    `;
  }

}

window.customElements.define('view-settings', ViewSettings);
