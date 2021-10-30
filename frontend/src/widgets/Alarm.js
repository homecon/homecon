import React from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Fab from '@material-ui/core/Fab';
import AddIcon from '@material-ui/icons/Add';

import {BaseAlarm} from './Base.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      position: 'relative',
      marginTop: '10px',
      minHeight: '50px',
      paddingBottom: '30px'
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
  const states = props.states;
  const ws = props.ws

  if(states === null){
    return null
  }

  const state = states[stateId];
  if(state === undefined){
    return null
  }
  const label = config.label || state.label;

  let alarmStates = []
  let actionStates = []

  Object.values(states).forEach((s) => {
    if(s.parent === state.id){
      if(s.type === 'alarm'){
        alarmStates.push(s)
      }
      if(s.type === 'action'){
        actionStates.push(s)
      }
    }
  });

  const addAlarm = () => {
    ws.send({event: 'add_schedule', data: {id: state.id}})
  }

  const handleAlarmChange = (alarm) => {
    ws.send({event: 'state_value', data: {id: alarm.id, value: alarm.value}})
  }

  const handleAlarmDelete = (alarm) => {
    ws.send({event: 'delete_schedule', data: {id: alarm.id}})
  }

  return (
    <div className={classes.root}>
      <div>{label || state.label}</div>
      <div>
        {alarmStates.map((alarm) => {
          return (
            <div key={alarm.id} style={{marginBottom: '5px'}}>
              <BaseAlarm alarm={alarm} actions={actionStates} onChange={handleAlarmChange} onDelete={handleAlarmDelete}/>
            </div>
          );
        })}
      </div>
      <Fab style={{position: 'absolute', bottom: '-10px', right: '10px'}} color="primary" aria-label="delete" onClick={(e) => addAlarm()}>
        <AddIcon />
      </Fab>
    </div>
  )

}


export {HomeconAlarm};