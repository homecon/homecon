import React, { useState } from 'react';
import { useParams } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';
import Paper from '@material-ui/core/Paper';

import {BaseValueDisplay} from './Base.js';


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


function HomeconValue(props){
  const config = props.config;

  const stateId = config.state;
  const precision = config.precision || 0;
  const prefix = config.prefix || '';
  const suffix = config.suffix || '';

  const states = props.states;

  let state = {value: 0};
  if(states !== null){
    state = states[stateId];
  }
  return (
    <BaseValueDisplay value={state.value} precision={precision} prefix={prefix} suffix={suffix} />
  )

}


export {HomeconValue};