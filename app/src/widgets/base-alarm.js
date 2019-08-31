import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';

import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/paper-dropdown-menu/paper-dropdown-menu.js';
import '@polymer/paper-item/paper-item.js';
import '@polymer/paper-listbox/paper-listbox.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-toggle-button/paper-toggle-button.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import '../homecon-web-socket-object.js';


class BaseAlarm extends PolymerElement {
  static get template() {
    return html`
      <style include="iron-flex iron-flex-alignment">
        :host{
          display: block;
          position: relative;
        }
        .alarm{
          position: relative;
          border: solid 1px;
          border-radius: 5px;
          border-color:  #2f2f2f;
          padding: 10px;
          margin-bottom: 4px;
        }
        .time{
          font-size: 45px;
          cursor: pointer;
          margin-right: 40px;
        }
        .repeat{
          margin-right: 20px;
        }
        .repeat .day{
          margin: 5px;
        }
        paper-button{
          text-transform: none;
        }
        .delete{
          position: absolute;
          top: 10px;
          right: 20px;
          color: var(--button-text-color);
        }
        </style>

        <homecon-web-socket-object id="websocketObject" event="state_value" key="{{key}}" data="{{alarm}}" auto></homecon-web-socket-object>

        <div class="alarm vertical layout">
          <div class="horizontal layout wrap">
            <div class="time" on-tap="editTime">
              {{_parseTime(alarm)}}
            </div>
            <div class="repeat horizontal layout center wrap">
              <div class="horizontal layout center wrap">
                <template is="dom-repeat" items="{{_parseWeekDays(alarm)}}" as="day">
                  <div class="day vertical layout center-justify">
                    <div>{{day.label}}</div>
                    <paper-toggle-button checked="{{day.value}}" on-change="_dayChanged"></paper-toggle-button>
                  </div>
                </template>
              </div>
              <div class="horizontal layout center wrap">
                <template is="dom-repeat" items="{{_parseWeekendDays(alarm)}}" as="day">
                  <div class="day vertical layout center-justify">
                    <div>{{day.label}}</div>
                    <paper-toggle-button checked="{{day.value}}" on-change="_dayChanged"></paper-toggle-button>
                  </div>
                </template>
              </div>
            </div>
          </div>
          <paper-dropdown-menu label="Action">
            <paper-listbox slot="dropdown-content" selected="{{alarm.action}}" attr-for-selected="value" on-selected-changed="_actionChanged">
              <template is="dom-repeat" items="{{actions}}" as="action">
                <paper-item value="{{action.id}}">{{action.name}}</paper-item>
              </template>
            </paper-listbox>
          </paper-dropdown-menu>
          <div class="delete">
            <paper-icon-button icon="icons:delete" noink="true" on-tap="deleteAlarm"></paper-icon-button>
          </div>
        </div>

        <paper-dialog id="timepickerDialog">
          Pick time
          <paper-input label="Hour" value="{{newHour}}"></paper-input>
          <paper-input label="Minute" value="{{newMinute}}"></paper-input>
          <div class="horizontal layout">
            <paper-button raised on-tap="cancelTime">Cancel</paper-button>
            <paper-button raised on-tap="saveTime">Save</paper-button>
          </div>
        </paper-dialog>    `;
  }

  static get properties() {
    return {
      key: {
        type: 'String',
      },
      actions: {
        type: 'Array',
      },
    };
  }

  editTime(e){
    this.newHour = this.alarm.trigger['hour'];
    this.newMinute = this.alarm.trigger['minute'];
    this.$.timepickerDialog.open()
  }

  saveTime(e,d){
    this.$.timepickerDialog.close();
    var alarm = JSON.parse(JSON.stringify(this.alarm))
    alarm.trigger.hour = this.newHour
    alarm.trigger.minute = this.newMinute
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.key, 'value': alarm}})
  }

  cancelTime(){
    this.$.timepickerDialog.close();
  }

  _parseTime(alarm){
    var hh = '00';
    var mm = '00';

    if(typeof alarm.trigger != 'undefined' && alarm.trigger['hour'] != null){
      var hh = String(alarm.trigger['hour']);
      if(alarm.trigger['hour'] < 10){
          hh = '0' + hh;
      }
    }
    if(typeof alarm.trigger != 'undefined' && alarm.trigger['minute'] != null){
      var mm = String(alarm.trigger['minute']);
      if(alarm.trigger['minute'] < 10){
          mm = '0' + mm;
      }
    }
    return hh+':'+mm;
  }

  _parseDay(trigger, days){
    if(typeof trigger != 'undefined' && trigger['day_of_week'] != null){
      var trigger_day_of_week = JSON.parse('[' + trigger['day_of_week'] + ']')
      for(var i=0;i<days.length;i++){
        if(trigger_day_of_week.indexOf(days[i].index) > -1){
            days[i].value = true;
        }
        else{
            days[i].value = false;
        }
      }
    }
    return days;
  }

  _parseWeekDays(alarm){
    var days = [
      {'index': 0, 'day':'mon', 'label':'Mon'},
      {'index': 1, 'day':'tue', 'label':'Tue'},
      {'index': 2, 'day':'wed', 'label':'Wed'},
      {'index': 3, 'day':'thu', 'label':'Thu'},
      {'index': 4, 'day':'fri', 'label':'Fri'},
    ]
    return this._parseDay(alarm.trigger, days)
  }

  _parseWeekendDays(alarm){
    var days = [
      {'index': 5, 'day':'sat', 'label':'Sat'},
      {'index': 6, 'day':'sun', 'label':'Sun'},
    ]
    return this._parseDay(alarm.trigger, days)
  }

  _dayChanged(event){
    var day = event.model.__data.day;

    var alarm = JSON.parse(JSON.stringify(this.alarm))
    var trigger_day_of_week = JSON.parse('[' + alarm.trigger['day_of_week'] + ']')
    if(day.value && trigger_day_of_week.indexOf(day.index) == -1){
      trigger_day_of_week.push(day.index)
    }
    else if(!day.value){
      var index = trigger_day_of_week.indexOf(day.index);
      if(index > -1) {
         trigger_day_of_week.splice(index, 1);
      }
    }
    var str_trigger_day_of_week = JSON.stringify(trigger_day_of_week)
    alarm.trigger.day_of_week = str_trigger_day_of_week.substring(1, str_trigger_day_of_week.length - 1);
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.key, 'value': alarm}})
  }

  _actionChanged(event, data){
    var alarm = JSON.parse(JSON.stringify(this.alarm))
    alarm.action = data.value
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.key, 'value': alarm}})
  }

  deleteAlarm(event){
    window.homeconWebSocket.send({'event': 'delete_schedule', 'data': {'id': this.key}})
  }

}

window.customElements.define('base-alarm', BaseAlarm);
