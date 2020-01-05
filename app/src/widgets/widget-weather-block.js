import {LitElement, html, css} from 'lit-element';

import '../shared-styles.js';

class WidgetWeatherBlock extends LitElement {

  static get properties() {
    return {
      edit: {
        type: Boolean,
      },
      state: {
        type: Number,
      },
      timeoffset: {
        type: Number,
      },
      forecast: {
        type: Object,
      },
      daily: {
        type: Boolean,
      },
      classes: {
        type: String,
      },
    };
  }

  constructor() {
    super();
    this.classes = 'quarterwidth'
    this.state = 'weather/forecast/0'
    window.addEventListener('homecon-web-socket-message', this._handleMessage);
    window.homecon.WebSocket.send({'event': 'state_value', 'data': {'path': this.state}})
  }

  static get styles(){
    return css`
      :host{
        display: block;
        position: relative;
        margin-top: 20px;
        text-align: center;
      }
      .icon{
        width: 100%;
      }
      .value{
        text-align: center;
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
      <div>
        <img class="icon" src="${this._icon(this.forecast)}">
        <div class="value time">${this._time(this.forecast)}</div>
        <div class="value">${this._temperature(this.forecast)}</div>
        <div class="value">${this._wind(this.forecast)}</div>
        <div class="value">Clouds: ${this._clouds(this.forecast)}</div>
      </div>

      <div class="edit" hidden="${!this.edit}">
        <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <paper-button on-tap="delete">Delete</paper-button>
      </homecon-edit-dialog>`;
  }

  _handleMessage(e, d){
    if(e.detail.event == 'state_value' && (e.detail.data.path == this.state || e.detail.data.id == this.state)){
      this.forecast = console.log(e.detail.data.value)
    }
  }

  _icon(forecast){
    var icons = {
      '01d': 'sun_1',
      '02d': 'sun_3',
      '03d': 'cloud_4',
      '04d': 'cloud_5',
      '09d': 'cloud_7',
      '10d': 'sun_7' ,
      '11d': 'cloud_10',
      '13d': 'cloud_13',
      '50d': 'sun_6',
      '01n': 'moon_1',
      '02n': 'moon_3',
      '03n': 'cloud_4',
      '04n': 'cloud_5',
      '09n': 'cloud_7',
      '10n': 'moon_7',
      '11n': 'cloud_10',
      '13n': 'cloud_13',
      '50n': 'moon_6',
      'clear-day': 'sun_1',
      'clear-night': 'moon_1',
      'rain': 'cloud_8',
      'snow': 'cloud_13',
      'sleet': 'cloud_15',
      'wind': 'wind',
      'fog': 'cloud_6' ,
      'cloudy': 'cloud_4',
      'partly-cloudy-day': 'sun_4',
      'partly-cloudy-night': 'moon_4' ,
      'hail': 'cloud_11',
      'thunderstorm': 'cloud_10'
    };

    if(forecast != null && forecast.icon in icons){
      return '/images/weather/' + icons[forecast.icon] + '.png';
    }
    else{
      return '/images/weather/blank.png';
    }
  }

  _time(forecast){
    if(forecast != null && typeof forecast != 'undefined'){
      var date = new Date(forecast.timestamp*1000);
      days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
      if(this.daily){
        dayofthemonth = date.getDate();
        if(dayofthemonth<10){
          dayofthemonth = '0' + dayofthemonth;
        }
        month = date.getMonth()+1
        if(month<10){
          month = '0' + month;
        }
        return days[date.getDay()] + ' ' + dayofthemonth + '-' + month;
      }
      else{
        return date.getHour();
      }
    }
  }

  _temperature(forecast){
    if(forecast != null && typeof forecast != 'undefined'){
      return forecast.temperature_day.toFixed(1) + '°C';
    }
  }

  _wind(forecast){
    var dirs = ['N','NE','E','SE','S','SW','W','NW','N'];
    if(forecast != null && typeof forecast != 'undefined'){
      var dir = dirs[Math.round(forecast.wind_direction/360*8)];
      return (forecast.wind_speed*3.6).toFixed(1) + ' km/h ' + dir;
    }
  }

  _clouds(forecast){
    if(forecast != null && typeof forecast != 'undefined'){
      return parseInt(forecast.cloudcover*100) + '%';
    }
  }
}

window.customElements.define('widget-weather-block', WidgetWeatherBlock);
