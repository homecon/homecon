import React from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';

import {BaseSlider} from './Base.js';
import HomeconIcon from '../Icon.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
      justifyContent: 'flex-start',
      alignItems: 'center',
    },
    iconLeft: {
      width: '60px',
      height: '60px',
      cursor: 'pointer',
      display: 'flex',
      justifyContent: 'flex-start',
      alignItems: 'center',
    },
    iconRight: {
      width: '60px',
      height: '60px',
      cursor: 'pointer',
      display: 'flex',
      justifyContent: 'flex-end',
      alignItems: 'center',
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


function HomeconShading(props){
  const config = props.config;

  const stateId = config.state;
  const iconOpen = config.iconOpen || 'fts_shutter_10';
  const iconClosed = config.iconClosed || 'fts_shutter_100';
  const positionOpen = config.positionOpen || 1;
  const positionClosed = config.positionClosed || 0;

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

  const openShading = (event) => {
    setValue(positionOpen);
  }
  const closeShading = (event) => {
    setValue(positionClosed);
  }

  const onChange = (event, newValue) => {
    setValue(newValue);
  }

  return (
    <div className={classes.root}>
      <div>
        <div className={classes.iconLeft} onClick={openShading}>
          <HomeconIcon color="ffffff" name={iconOpen}/>
        </div>
      </div>
      <div className={classes.rest}>
        <div className={classes.label}>{label}</div>
        <div className={classes.slider}>
          <BaseSlider value={state.value} valueMin={positionOpen} valueMax={positionClosed} onChange={onChange} />
        </div>
      </div>
      <div>
        <div className={classes.iconRight} onClick={closeShading}>
          <HomeconIcon color="ffffff" name={iconClosed}/>
        </div>
      </div>
    </div>
  );

}


export {HomeconShading};