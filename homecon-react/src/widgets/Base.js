import React, { useState } from 'react';
import { useParams } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';
import Paper from '@material-ui/core/Paper';

import HomeconIcon from '../Icon.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    pageHeader: {
    },
  })
);


function BaseStatusLight(props){

  const value = props.value;
  const valueThreshold = props.valueThreshold;
  const icon = props.icon;
  const colorOn = props.colorOn;
  const colorOff = props.colorOff;

  const color = value > valueThreshold ? colorOn : colorOff;
  return <HomeconIcon color={color} name={icon}/>;

}

function BaseValueDisplay(props){
  const value = props.value;
  const precision = props.precision;
  const prefix = props.prefix;
  const suffix = props.suffix;

  let displayValue = value

  if(typeof value == 'number'){
    displayValue = parseFloat(value).toFixed(precision)
  }

  return (
    <div style={{display: 'inline-block'}}>
      <span style={{marginRight: '5px'}}>{prefix}</span>
      <span style={{fontSize: '16px', fontWeight: 700}}>{displayValue}</span>
      <span style={{marginLeft: '5px'}}>{suffix}</span>
    </div>
  );
}


export {BaseStatusLight, BaseValueDisplay};