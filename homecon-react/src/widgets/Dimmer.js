import React, { useState } from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';

import {BaseStatusLight, BaseSlider} from './Base.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
      justifyContent: 'flex-start',
      alignItems: 'center',
    },
    icon: {
      width: '60px',
      height: '60px',
      cursor: 'pointer'
    },
    rest: {
      display: 'flex',
      flexDirection: 'column',
      flexGrow: 1,
    },
    slider: {
      marginLeft: '15px',
      marginRight: '15px',
    },
    label: {
      fontSize: '16px',
      fontWeight: 700
    },
  })
);


function HomeconDimmer(props){
  const config = props.config;

  const stateId = config.state;
  const icon = config.icon || 'light_light';
  const colorOn = config.colorOn || 'f79a1f';
  const colorOff = config.colorOff || 'ffffff';
  const valueOn = config.valueOn || 1;
  const valueOff = config.valueOff || 0;

  const valueThreshold = 0.01*valueOn + 0.99*valueOff;
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

  const setValue = (value) => {
    ws.send({event: 'state_value', data: {id: state.id, value: value}});
  }

  const handleClick = (event) => {
    setValue(state.value > valueThreshold ? valueOff : valueOn);
  }

  const onChange = (event, newValue) => {
    setValue(newValue);
  }

  return (
    <div className={classes.root}>
      <div className={classes.icon} onClick={(e) => handleClick(e)}>
        <BaseStatusLight value={state.value} valueThreshold={valueThreshold} icon={icon} colorOn={colorOn} colorOff={colorOff} />
      </div>

      <div className={classes.rest}>
        <div className={classes.label}>{label}</div>
        <div className={classes.slider}>
          <BaseSlider value={state.value} valueMin={valueOff} valueMax={valueOn} onChange={onChange} />
        </div>
      </div>
    </div>
  );

}


export {HomeconDimmer};