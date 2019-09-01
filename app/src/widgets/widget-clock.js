import {LitElement, html, css} from 'lit-element';

import '../shared-styles.js';

class WidgetClock extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean,
      },
      hour: {
        type: String,
      },
      minute: {
        type: String,
      },
      srcHourBackground: {
        type: String,
      },
      srcHour0: {
        type: String,
      },
      srcHour1: {
        type: String,
      },
      srcMinuteBackground: {
        type: String,
      },
      srcMinute0: {
        type: String,
      },
      srcMinute1: {
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

    this.h0_current = -1;
    this.h1_current = -1;
    this.m0_current = -1;
    this.m1_current = -1;

    this.srcHourBackground = '/images/clock/clockbg.png';
    this.srcHour0 = '/images/clock/blank.png';
    this.srcHour1 = '/images/clock/blank.png';

    this.srcMinuteBackground = '/images/clock/clockbg.png';
    this.srcMinute0 = '/images/clock/blank.png';
    this.srcMinute1 = '/images/clock/blank.png';

    var that = this;
    this._setTime(false);
    setInterval(function(){that._setTime(true)}, 5000);
  }

  _setTime(animate) {
    var now = new Date();
    var h0 = Math.floor( now.getHours() / 10 );
    var h1 = now.getHours() % 10;

    this.hour = ''+ h0 + h1

    var m0 = Math.floor( now.getMinutes() / 10 );
    var m1 = now.getMinutes() % 10;

    this.minute = ''+ m0 + m1

    if(h1 != this.h1_current){
      this._flip('srcHour1',animate,h1);
      this.h1_current = h1;

      this._flip('srcHour0',animate,h0);
      this.h0_current = h0;

      this._flip('srcHourBackground', animate);
    }

    if( m1 != this.m1_current){
      this._flip('srcMinute1',animate,m1);
      this.m1_current = m1;

      this._flip('srcMinute0',animate,m0);
      this.m0_current = m0;

      this._flip('srcMinuteBackground',animate);
    }
  }

  _flip(prop, animate, num) {

    var that = this;

    if(prop == 'srcMinuteBackground' || prop == 'srcHourBackground'){
      var src1 = '/images/clock/clockbg-1.png';
      var src2 = '/images/clock/clockbg-2.png';
      var src3 = '/images/clock/clockbg-3.png';
      var src = '/images/clock/clockbg.png';
    }
    else{
      var src1 = '/images/clock/'+num+'-1.png';
      var src2 = '/images/clock/'+num+'-2.png';
      var src3 = '/images/clock/'+num+'-3.png';
      var src  = '/images/clock/'+num+'.png';
    }

    if(!animate){
      this[prop] = src
    }

    else{
      that[prop] = src1

      setTimeout(function(){
        that[prop] = src2
      },60);
      setTimeout(function(){
        that[prop] = src3
      },120);
      setTimeout(function(){
        that[prop] = src
      },180);
    }
  }

  static get styles(){
    return css`
      :host{
        display: block;
        position: relative;
        margin-top: 20px;
        text-align: center;
      }
      .background{
        width: 100%;
      }
      .hour, .minute{
        display: inline-block;
        position: relative;
        width: 20%;
        min-width: 100px;
        max-width: 150px;
      }
      .digit{
        width: 42%;
        position: absolute;
        top: 0px;
      }
      .digit.left{
        left: 10%;
      }
      .digit.right{
        right: 10%;
      }
      .edit{
        position: absolute;
        top: -10px;
        right: -10px;
        color: var(--button-text-color);
      }`
  }

  render() {
    return html`
      <div class="horizontal layout center-justified">
        <div class="hour">
          <img class="background" src="${this.srcHourBackground}">
          <img class="digit left" src="${this.srcHour0}"/>
          <img class="digit right" src="${this.srcHour1}"/>
        </div>
        <div class="minute">
          <img class="background" src="${this.srcMinuteBackground}">
          <img class="digit left" src="${this.srcMinute0}"/>
          <img class="digit right" src="${this.srcMinute1}"/>
        </div>
      </div>

      <div class="edit" hidden="${!this.edit}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-button on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>`;
  }

}

window.customElements.define('widget-clock', WidgetClock);
