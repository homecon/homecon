import React from 'react';


function HomeconWeatherBlock(props){
  const config = props.config;
  const states = props.states;

  let state = undefined;
  if(states!== null){
    let path = '';
    if(config.daily){
      path = `/weather/forecast/daily/${config.timeoffset}`;
    }
    else if(config.hourly){
      path = `/weather/forecast/hourly/${config.timeoffset}`;
    }

    for (const value of Object.values(states)) {
      if(value.path === path){
        state = value;
        break;
      }
    }
  }

  if(state === undefined){
    state = {value: {}};
  }

  const getIcon = (value) => {
    if(value.icon !== undefined && value.icon !== null){
      return `/weather/${value.icon}.png`;
    }
    else{
      return '/weather/blank.png';
    }
  }

  const getDate = (value) => {
    if(value.timestamp !== undefined && value.timestamp !== null){
      const date = new Date(value.timestamp * 1000);
      const locale = config.locale || 'nl-BE';
      const options = config.dateOptions || {weekday: 'long'};
      return date.toLocaleDateString(locale, options)
    }
    else {
      return '';
    }
  }

  const getTemperature = (value) => {
    if(value.temperature_max !== undefined && value.temperature_max !== null){
      return `${(value.temperature_max).toFixed(1)} °C`
    }
    else{
      return ''
    }
  }

  const getWindSpeed = (value) => {
    if(value.wind_speed !== undefined && value.wind_speed !== null){
      return `${(value.wind_speed*3.6).toFixed(1)} km/h`
    }
    else{
      return ''
    }
  }
  const getWindDirection = (value) => {
    const dirs = ['N','NE','E','SE','S','SW','W','NW','N'];
    if(value.wind_direction !== undefined && value.wind_direction !== null){
      return dirs[Math.round(value.wind_direction/360*8)];
    }
    else{
      return ''
    }
  }
  const getRain = (value) => {
    if(value.rain !== undefined && value.rain !== null){
      return `${(value.rain*100).toFixed(0)} %`
    }
    else{
      return ''
    }
  }

  return (
    <div style={{display: "inline-block", maxWidth: "180px"}}>
      <img src={getIcon(state.value)} style={{width: "100%"}} alt="weather forecast"/>
      <div style={{textAlign: "center"}}>{getDate(state.value)}</div>
      <div style={{textAlign: "center"}}>{getTemperature(state.value)}</div>
      <div style={{textAlign: "center"}}>{getWindSpeed(state.value)} {getWindDirection(state.value)}</div>
      <div style={{textAlign: "center"}}>Regen: {getRain(state.value)}</div>
    </div>
  )
}

export {HomeconWeatherBlock};