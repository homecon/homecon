import React, { useState } from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';
import Paper from '@material-ui/core/Paper';

import {BaseAlarm} from './Base.js';


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


function HomeconAlarm(props){
  const classes = useStyles();

  const config = props.config;

  const stateId = config.state;
  const label = config.label;
  const states = props.states;
  const ws = props.ws

  if(states === null){
    return null
  }

  const state = states[stateId];

  let alarmStates = []
  let actionStates = []

  Object.values(states).forEach((s) => {
    if(s.parent === state.id){
      if(s.type == 'alarm'){
        alarmStates.push(s)
      }
      if(s.type === 'action'){
        actionStates.push(s)
      }
    }
  });

  const handleAlarmChange = (alarm) => {
    ws.send({event: 'state_value', data: {id: alarm.id, value: alarm.value}})
  }

  return (
    <div style={{marginTop: '10px'}}>
      <div>{state.label}</div>
      <div>
        {alarmStates.map((alarm) => {
          return (
            <BaseAlarm key={alarm.id} alarm={alarm} actions={actionStates} onChange={handleAlarmChange}/>
          );
        })}
      </div>
    </div>
  )

}


export {HomeconAlarm};