import React from 'react';

import {BaseValueDisplay} from './Base.js';


function HomeconValue(props){
  const config = props.config;

  const stateId = config.state;
  const precision = config.precision || 0;
  const scale = config.scale || 1;
  const prefix = config.prefix || '';
  const suffix = config.suffix || '';

  const states = props.states;

  let state = undefined;
  if(states !== null){
    state = states[stateId];
  }
  if(state === undefined){
    state = {value: 0};
  }

  return (
    <BaseValueDisplay value={state.value} scale={scale} precision={precision} prefix={prefix} suffix={suffix} />
  )

}


export {HomeconValue};