import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-slider/paper-slider.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-alarm.js';
import './base-action.js';


class WidgetAlarm extends PolymerElement {
  static get template() {
    return html`
      <style include="iron-flex iron-flex iron-flex-alignment">
        :host{
          display: block;
          position: relative;
          margin-top: 10px;
        }
        .alarm{
          position: relative;
        }
        .toggle{
          margin-top: -25px;
        }
        .details{
          margin-top: 5px;
          margin-bottom: 30px;
          margin-right: 30px;
          margin-left: 30px;
        }
        paper-button{
          text-transform: none;
        }
        h2 {
          font-size: 1.2em;
          margin: 0;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>

      <homecon-web-socket-object event="list_schedules" key="[[state]]" data="{{alarms}}" auto></homecon-web-socket-object>
      <homecon-web-socket-object event="list_actions" key="[[state]]" data="{{actions}}" auto></homecon-web-socket-object>

      <template is="dom-repeat" items="{{alarms}}" as="alarm">
        <div class="alarm vertical layout">
          <base-alarm state="{{alarm}}" actions="{{actions}}"></base-alarm>
        </div>
      </template>

      <paper-button class="button" on-tap="addAlarm" raised="true"> Add Alarm</paper-button>

      <div class="horizontal layout toggle">
        <div class="flex"></div>
        <iron-icon on-tap="_toggleCollapse" icon="{{_collapseIcon(detailsOpened)}}"></iron-icon>
      </div>

      <iron-collapse id="details" class="details" opened="{{detailsOpened}}">
        <h2>Actions</h2>
        <template is="dom-repeat" items="{{actions}}" as="action">
          <div class="action horizontal layout">
            <base-action state="{{action}}"></base-action>
          </div>
        </template>
        <paper-button class="button" on-tap="addActionDialog" raised="true"> Add Action</paper-button>
      </iron-collapse>

      <homecon-edit-dialog id="addActionDialog" on-save="addAction">
        <h3>Add action</h3>
        <paper-input id="actionLabel" label="Label" value="{{newActionLabel}}"></paper-input>
        <json-editor id="actionValue" label="Config" value="[]" current-data="{{newActionValue}}"></json-editor>
      </homecon-edit-dialog>

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
    window.homeconWebSocket.send({'event': 'add_schedule', 'data': {'id': this.state}})
  }

  deleteAlarm(e){
    path = e.model.__data__.path;
//    window.homeconWebSocket.send({'event': 'delete_schedule', 'data': {'id': this.config['filter']}})
//    this.$.websocket.send({'event':'delete_schedule','path':path});
  }
  addActionDialog(e){
    this.newActionLabel == 'New action'
    this.newActionValue == '[]'
    this.$.addActionDialog.open();
  }
  addAction(e){
    window.homeconWebSocket.send({'event': 'add_action', 'data': {'id': this.state, 'label': this.newActionLabel, 'value': this.newActionValue}})
  }

  deleteAction(e){
    path = e.model.__data__.path;
//    window.homeconWebSocket.send({'event': 'delete_schedule', 'data': {'id': this.config['filter']}})
//    this.$.websocket.send({'event':'delete_schedule','path':path});
  }

  _collapseIcon(detailsOpened){
    if(detailsOpened){
      return 'expand-less';
    }
    else{
      return 'expand-more';
    }
  }

  _toggleCollapse(){
    this.$.details.toggle()
  }
}

window.customElements.define('widget-alarm', WidgetAlarm);
