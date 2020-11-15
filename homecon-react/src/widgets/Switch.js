import React, { useState } from 'react';
import { useParams } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';
import Paper from '@material-ui/core/Paper';

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
  const label = config.label;
  const icon = config.icon || 'light_light';
  const colorOn = config.colorOn || 'f79a1f';
  const colorOff = config.colorOff || 'ffffff';
  const valueOn = config.valueOn || 1;
  const valueOff = config.valueOff || 0;

  const valueThreshold = 0.5*valueOn + 0.5*valueOff;
  const states = props.states;
  const ws = props.ws

  let state = {value: 0};
  if(states !== null){
    state = states[stateId];
  }

  const classes = useStyles();

  const handleClick = (event) => {
    ws.send({event: 'state_value', data: {id: state.id, value: state.value > valueThreshold ? valueOff : valueOn}})
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


export {HomeconSwitch};