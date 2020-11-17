import React from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Slider from '@material-ui/core/Slider';

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

function BaseSlider(props){
  const value = props.value;
  const valueMin = props.valueMin;
  const valueMax = props.valueMax;
  const onChange = props.onChange;

  const valueToSliderValue = (value) =>{
    return (value-valueMin)/(valueMax-valueMin) * 100
  }
  const sliderValueToValue = (value) =>{
    return valueMin + value * (valueMax-valueMin) / 100
  }

  return (
    <Slider value={valueToSliderValue(value)} min={0} max={100} step={1} onChange={(e, v) => onChange(e, sliderValueToValue(v)) } colorPrimary='#fff'/>
  );
}


export {BaseStatusLight, BaseValueDisplay, BaseSlider};