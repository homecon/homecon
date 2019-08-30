import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-slider/paper-slider.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-alarm.js';

class WidgetAlarm extends PolymerElement {
  static get template() {
    return html`
      <style include="iron-flex iron-flex-alignment">
        :host{
          display: block;
          position: relative;
        }
        .alarm{
          position: relative;
        }
        .delete{
          position: absolute;
          top: 10px;
          right: 20px;
          color: var(--button-text-color);
        }
        paper-button{
          text-transform: none;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>

      <homecon-web-socket-object event="list_schedules" key="[[state]]" data="{{alarms}}" auto></homecon-web-socket-object>
      <homecon-web-socket-object event="list_actions" key="" data="{{actions}}" auto></homecon-web-socket-object>

      <template is="dom-repeat" items="{{alarms}}" as="key">
        <div class="alarm vertical layout">
          <base-alarm key="{{key}}" actions="{{actions}}"></base-alarm>
          <div class="delete">
            <paper-icon-button icon="icons:delete" noink="true" on-tap="deleteAlarm"></paper-icon-button>
          </div>
        </div>
      </template>

      <paper-button class="button" on-tap="addAlarm" raised="true"> Add Alarm</paper-button>

      <div class="edit" hidden="{{!edit}}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-input label="Label:" value="{{newLabel}}"></paper-input>
        <paper-input label="Filter:" value="{{newFilter}}"></paper-input>
        <paper-button on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      label: {
        type: String,
        value: 'new alarm',
      },
      state: {
        type: String,
        value: '',
      },
      edit: {
        type: 'Boolean',
        value: false
      },
      classes: {
        type: 'String',
        value: 'fullwidth',
      },
    };
  }

  openEditDialog(){
    this.set('newLabel',this.config.label);
    this.set('newFilter',this.config.filter);
    this.$.editDialog.open();
  }

  save(e){
    e.stopPropagation()
    this.$.editDialog.close();
    this.fire('edit-widget',{'label': this.newLabel, 'filter':this.newFilter});
  }

  delete(e){
    e.stopPropagation()
    this.fire('delete');
  }

  addAlarm(e){
    this.$.websocket.send({'event':'add_schedule', 'config': {'filter': this.config['filter']}, 'value': {'hour':0, 'minute':0}});
  }

  deleteAlarm(e){
    path = e.model.__data__.path;
    this.$.websocket.send({'event':'delete_schedule','path':path});
  }

}

window.customElements.define('widget-alarm', WidgetAlarm);
