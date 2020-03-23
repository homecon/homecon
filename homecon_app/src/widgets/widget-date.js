import {LitElement, html, css} from 'lit-element';

import '../shared-styles.js';

class WidgetDate extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean,
      },
      date: {
        type: String,
      },
      classes: {
        type: String,
      },
    };
  }

  constructor() {
    super();
    this.classes = 'fullwidth'

    this.weekday= ['maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag','zondag'];
    this.weekday_short= ['maa','din','woe','don','vri','zat','zon'];
    this.month= ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
    this.month_short= ['jan','feb','maa','apr','mei','jun','jul','aug','sep','okt','nov','dec'];

    var that = this;
    that._setDate();
    setInterval(function(){that._setDate()}, 30000);
  }

  _setDate(){
    var now = new Date();
    var weekday = (now.getDay()+6)%7;
    var day = now.getDate();
    var month = now.getMonth();
    var year = now.getFullYear();

    this.date = this.capitalize(this.weekday[weekday])+' '+day+' '+this.capitalize(this.month[month])+' '+year;
  }

  capitalize(string){
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  static get styles(){
    return css`
      :host{
        display: block;
        position: relative;
        margin-top: 10px;
        text-align: center;
      }
      .date{
        width: 100%;
      }
      .edit{
        position: absolute;
        top: -10px;
        right: -10px;
        color: var(--button-text-color);
      }`;
  }

  render() {
    return html`
      <div class="horizontal layout center-justified">
        ${this.date}
      </div>

      <div class="edit" hidden="${!this.edit}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-button on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>`;
  }

}

window.customElements.define('widget-date', WidgetDate);
