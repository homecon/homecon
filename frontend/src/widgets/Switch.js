import React from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';

import {BaseStatusLight} from './Base.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
      justifyContent: 'flex-start',
      alignItems: 'center',
      cursor: 'pointer'
    },
    label: {
      fontSize: '16px',
      fontWeight: 700
    },
    icon: {
      width: '60px',
      height: '60px',
    }
  })
);


function HomeconSwitch(props){
  const config = props.config;

  const stateId = config.state;
  const icon = config.icon || 'light_light';
  const colorOn = config.colorOn || 'f79a1f';
  const colorOff = config.colorOff || 'ffffff';
  const valueOn = config.valueOn || 1;
  const valueOff = config.valueOff || 0;

  const valueThreshold = 0.5*valueOn + 0.5*valueOff;
  const states = props.states;
  const ws = props.ws

  let state = undefined;
  if(states !== null){
    state = states[stateId];
  }
  if(state === undefined){
    state = {value: 0, label: ''};
  }
  const label = config.label || state.label;

  const classes = useStyles();

  const handleClick = (event) => {
    ws.send({event: 'state_value', data: {key: state.key, value: state.value > valueThreshold ? valueOff : valueOn}})
  }

  return (
    <div className={classes.root} onClick={handleClick}>
      <div className={classes.icon}>
        <BaseStatusLight value={state.value} valueThreshold={valueThreshold} icon={icon} colorOn={colorOn} colorOff={colorOff} />
      </div>
      <div className={classes.label}>{label}</div>
    </div>
  )
}


function HomeconMultiSwitch(props){
  const config = props.config;

  const stateKey = config.state;
  const levels = config.values || [
    {value: 0, icon: 'vent_ventilation_level_0'},
    {value: 1, icon: 'vent_ventilation_level_1'},
    {value: 2, icon: 'vent_ventilation_level_2'},
    {value: 3, icon: 'vent_ventilation_level_3'},
  ];
  const threshold = config.threshold || 0.1;
  const colorOn = config.colorOn || 'f79a1f';
  const colorOff = config.colorOff || 'ffffff';
  const states = props.states;
  const ws = props.ws

  let state = undefined;
  if(states !== null){
    state = states[stateKey];
  }
  if(state === undefined){
    state = {value: 0, label: ''};
  }
  const label = config.label || state.label;

  const handleClick = (value) => {
    const handle = (event) => {
      console.log({key: state.key, value: value})
      ws.send({event: 'state_value', data: {key: state.key, value: value}})
    };
    return handle;
  }

  const getStatusValue = (value, levelValue) => {
    if(Math.abs(value - levelValue) < threshold){
      return 1;
    }
    return 0;
  }

  const classes = useStyles();

  return (
    <div style={{display: "flex", flexDirection: "column"}}>

      <div className={classes.label}>{label}</div>
      <div style={{display: "flex", flexDirection: "row"}}>
        {levels.map((level, index) => (
          <div className={classes.icon} style={{cursor: 'pointer'}} key={index} onClick={handleClick(level.value)}>
            <BaseStatusLight value={getStatusValue(state.value, level.value)} valueThreshold={0.5} icon={level.icon}
             colorOn={colorOn} colorOff={colorOff}/>
          </div>
        ))}
      </div>

    </div>
  )
}


export {HomeconSwitch, HomeconMultiSwitch};