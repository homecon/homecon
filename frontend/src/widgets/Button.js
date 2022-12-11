import React from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

import {BaseStatusLight} from './Base.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
      justifyContent: 'flex-start',
      alignItems: 'center',
      cursor: 'pointer'
    },
    icon: {
      width: '40px',
      height: '40px',
    }
  })
);


function HomeconButton(props){
  const config = props.config;

  const clickEvent = config.event;
  const clickData = config.data;
  const label = config.label;

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

  const handleClick = (event) => {
    ws.send({event: clickEvent, data: clickData})
  }

  const classes = useStyles();

  return (
    <Button className={classes.root} onClick={() => handleClick()}>
      {state !== undefined && (
        <div className={classes.icon}>
          <BaseStatusLight value={state.value} valueThreshold={valueThreshold} icon={icon} colorOn={colorOn} colorOff={colorOff} />
        </div>)}
      {label}
    </Button>
  )
}

function HomeconStateValueButton(props){
  const config = props.config;

  const stateId = config.state;
  const value = config.value;

  return HomeconButton({
    config: {
      event: 'state_value',
      data: {key: stateId, value: value},
      label: config.label,
      state: config.statusState,
      icon: config.icon,
      colorOn: config.colorOn,
      colorOff: config.colorOff,
      valueOn: config.valueOn,
      valueOff: config.valueOff
    },
    states: props.states,
    ws: props.ws
  })
}



export {HomeconButton, HomeconStateValueButton};