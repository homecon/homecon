import React, { useState } from 'react';
import { useTheme } from '@material-ui/styles';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Slider from '@material-ui/core/Slider';
import Fab from '@material-ui/core/Fab';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Switch from '@material-ui/core/Switch';
import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';
import Dialog from '@material-ui/core/Dialog';
import Button from '@material-ui/core/Button';
import DateFnsUtils from '@date-io/date-fns';
import {MuiPickersUtilsProvider, KeyboardTimePicker} from '@material-ui/pickers';


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
  const scale = props.scale;
  const precision = props.precision;
  const prefix = props.prefix;
  const suffix = props.suffix;

  let displayValue = value

  if(typeof value == 'number'){
    let scaledValue = parseFloat(value) * parseFloat(scale)
    displayValue = scaledValue.toFixed(precision)
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
    <Slider value={valueToSliderValue(value)} min={0} max={100} step={1} onChange={(e, v) => onChange(e, sliderValueToValue(v)) }/>
  );
}


function BaseAction(props){
  const state = props.state

  const openEditDialog = (e) => {
    console.log(e)
  }

  const openDeleteDialog = (e) => {
    console.log(e)
  }

  return (
    <div>
      <div>{state.label}</div>
      <div class="controls">
        <Fab color="primary" aria-label="edit" onClick={openEditDialog}>
          <EditIcon />
        </Fab>
        <Fab color="primary" aria-label="delete" onClick={openDeleteDialog}>
          <DeleteIcon />
        </Fab>
      </div>
    </div>
  )
}


function BaseAlarm(props){
  const alarm = props.alarm;
  const actions = props.actions;
  const onChange = props.onChange;
  const onDelete = props.onDelete;

  const [timePickerOpen, setTimePickerOpen] = useState(false)
  const [timePickerDate, setTimePickerDate] = React.useState(new Date('1970-01-01T00:00:00'));

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  const [dayOfWeekTrigger, setDayOfWeekTrigger] = React.useState(JSON.parse(`[${alarm.value.trigger.day_of_week}]`));

  let action = {key: 'no_action', 'label': 'No action'};
  actions.forEach((a) => {
    if(alarm.value.action === a.key){
      action = a;
    }
  });

  const parseTime = (trigger) => {
    var hh = '00';
    var mm = '00';

    if(trigger !== undefined && trigger.hour !== null){
      hh = String(trigger.hour);
      if(trigger.hour < 10){
          hh = '0' + hh;
      }
    }
    if(trigger !== undefined && trigger.minute !== null){
      mm = String(trigger.minute);
      if(trigger.minute < 10){
          mm = '0' + mm;
      }
    }
    return hh+':'+mm;
  }

  const weekDays = [
    {index: 0, day: 'mon', label: 'Mon'},
    {index: 1, day: 'tue', label: 'Tue'},
    {index: 2, day: 'wed', label: 'Wed'},
    {index: 3, day: 'thu', label: 'Thu'},
    {index: 4, day: 'fri', label: 'Fri'},
  ]

  const weekendDays = [
    {index: 5, day: 'sat', label: 'Sat'},
    {index: 6, day: 'sun', label: 'Sun'},
  ]

  const time = parseTime(alarm.value.trigger)

  const openTimePicker = () => {
    const d = new Date(`1970-01-01T${time}:00`)
    setTimePickerDate(d)
    setTimePickerOpen(true)
  }

  const handleTimePickerChange = (date) => {
    setTimePickerDate(date)
  }

  const handleTimePickerClose = (e) => {
    setTimePickerOpen(false)
  }

  const handleTimeChange = (e) => {
    setTimePickerOpen(false)

    let newAlarm = JSON.parse(JSON.stringify(alarm));
    newAlarm.value.trigger.hour = timePickerDate.getHours();
    newAlarm.value.trigger.minute = timePickerDate.getMinutes();
    onChange(newAlarm)
  }

  const handleDayChange = (e, day) => {
    let newDayOfWeekTrigger = JSON.parse(JSON.stringify(dayOfWeekTrigger))
    const index = newDayOfWeekTrigger.indexOf(day.index);
    if(index > -1){
      newDayOfWeekTrigger.splice(index, 1);
    }
    else{
      newDayOfWeekTrigger.push(day.index)
      newDayOfWeekTrigger = newDayOfWeekTrigger.sort()
    }
    setDayOfWeekTrigger(newDayOfWeekTrigger)

    let newAlarm = JSON.parse(JSON.stringify(alarm));
    const newDayOfWeekTriggerStr = JSON.stringify(newDayOfWeekTrigger)
    newAlarm.value.trigger.day_of_week = newDayOfWeekTriggerStr.substring(1, newDayOfWeekTriggerStr.length - 1);
    onChange(newAlarm)
  }

  const handleActionChange = (e) => {
    let newAlarm = JSON.parse(JSON.stringify(alarm));
    newAlarm.value.action = e.target.value;
    onChange(newAlarm)
  }

  const handleDeleteDialogClose = () => {
    setDeleteDialogOpen(false)
  }

  const handleDeleteAlarm = () => {
    onDelete(alarm);
  }

  const dayJsx = (day) => {
    return (
      <div key={day.index} style={{display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
        <div>{day.label}</div>
        <Switch checked={dayOfWeekTrigger.indexOf(day.index) > -1} onChange={(e) => {return handleDayChange(e, day)}} />
      </div>
    )
  }

  const theme = useTheme()

  return (
    <div style={{border: 'solid 1px', borderColor: theme.palette.primary.light, borderRadius: '5px', padding: '10px', position: 'relative'}}>
      <div style={{display: 'flex', width: '100%'}}>

        <div style={{width: '100%'}}>
          <div style={{fontSize: '45px', marginRight: '20px', marginBottom: '5px', cursor: 'pointer'}} onClick={openTimePicker}>
            {time}
          </div>

          <Dialog onClose={handleTimePickerClose} open={timePickerOpen}>
            <MuiPickersUtilsProvider utils={DateFnsUtils}>
              <KeyboardTimePicker margin="normal" id="time-picker" label="Time" value={timePickerDate} onChange={handleTimePickerChange} ampm={false} variant="static"/>
            </MuiPickersUtilsProvider>
            <Button variant="contained" onClick={() => setTimePickerOpen(false)}>cancel</Button>
            <Button variant="contained" color="primary" onClick={handleTimeChange}>save</Button>
          </Dialog>

          <div style={{display: 'flex', flexFlow: 'row wrap', width: '100%'}}>
            <div style={{display: 'flex', flexFlow: 'row wrap'}}>
              {weekDays.map((day) => {
                return dayJsx(day)
              })}
            </div>
            <div style={{display: 'flex', flexFlow: 'row wrap'}}>
               {weekendDays.map((day) => {
                return dayJsx(day)
              })}
            </div>
          </div>
        </div>

        <Fab color="primary" aria-label="delete" onClick={(e) => setDeleteDialogOpen(true)}>
          <DeleteIcon />
        </Fab>
        <Dialog onClose={handleDeleteDialogClose} open={deleteDialogOpen}>
          <h3>Delete alarm?</h3>
          <Button variant="contained" onClick={() => setDeleteDialogOpen(false)}>cancel</Button>
          <Button variant="contained" color="primary" onClick={(e) => handleDeleteAlarm()}>Delete</Button>
        </Dialog>

      </div>

      <div style={{width: '100%', marginTop: '5px'}}>
        <InputLabel id="action-select-label">Action</InputLabel>
        <Select style={{width: '80%'}} labelId="action-select-label" id="demo-simple-select-helper" value={action.key} onChange={handleActionChange}>
          {actions.map((a) => {
            return <MenuItem key={a.key} value={a.key}>{a.label}</MenuItem>
          })}
        </Select>
      </div>

    </div>
  );
}

export {BaseStatusLight, BaseValueDisplay, BaseSlider, BaseAction, BaseAlarm};