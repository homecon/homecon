import React, { useState, useRef, useEffect } from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';

import Dialog from '@material-ui/core/Dialog';
import Fab from '@material-ui/core/Fab';
import IconButton from '@material-ui/core/IconButton';
import AddIcon from '@material-ui/icons/Add';
import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';
import MoreIcon from '@material-ui/icons/MoreVert';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';

import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';


import {PageHeader, PageSection} from './PageLayout.js'


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    tableRow: {
      borderColor: '#ff0000',
    },
  })
)

function EditStateDialog(props){
  const state = props.state;
  const onCancel = props.onCancel;
  const onSave = props.onSave;

  const [name, setName] = useState('')
  const [type, setType] = useState('')
  const [quantity, setQuantity] = useState('')
  const [unit, setUnit] = useState('')
  const [label, setLabel] = useState('')
  const [description, setDescription] = useState('')
  const [config, setConfig] = useState('{}')
  const [value, setValue] = useState('')

  useEffect(() => {
    setName(state.name || '');
    setType(state.type || '');
    setQuantity(state.quantity || '');
    setUnit(state.unit || '');
    setLabel(state.label || '');
    setDescription(state.description || '');
    setConfig(state.config !== null ? JSON.stringify(state.config, undefined, 2) : '{}');
    setValue(state.value !== null ? JSON.stringify(state.value) : '');
  }, [state]);

  const handleSave = () => {
    let newValue = null;
    if(type === 'int'){
      newValue = parseInt(value);
      if(isNaN(newValue)){
        newValue = null;
      }
    }
    else if(type === 'float'){
      newValue = parseFloat(value);
      if(isNaN(newValue)){
        newValue = null;
      }
    }
    else if(type === 'bool'){
      newValue = parseInt(value);
      if(isNaN(newValue)){
        newValue = null;
      }
      else if(newValue > 1){
        newValue = 1;
      }
      else if(newValue < 0){
        newValue = 0;
      }
    }
    else if(type === 'str'){
      newValue = value;
    }

    else{
      try {
        newValue = JSON.parse(value);
      }
      catch{
        newValue = value;
      }
    }


    let newState = JSON.parse(JSON.stringify(state));

    newState.name = name;
    newState.type = type === '' ? null : type;
    newState.quantity = quantity;
    newState.label = label;
    newState.description = description;
    newState.config = JSON.parse(config);
    newState.value = newValue;

    onSave(newState);
  }

  return (
    <div>
      <form>
        <div style={{display: 'flex', flexDirection: 'column'}}>
          <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)}/>
          <TextField label="Type" value={type} onChange={(e) => setType(e.target.value)}/>
          <TextField label="Quantity" value={quantity} onChange={(e) => setQuantity(e.target.value)}/>
          <TextField label="Unit" value={unit} onChange={(e) => setUnit(e.target.value)}/>
          <TextField label="Label" value={label} onChange={(e) => setLabel(e.target.value)}/>
          <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)}/>
          <TextField label="Config" value={config} onChange={(e) => setConfig(e.target.value)} multiline/>
          <TextField label="Value" value={value} onChange={(e) => setValue(e.target.value)}/>
        </div>
        <div style={{marginTop: '10px'}}>
          <Button onClick={(e) => handleSave()}>Save</Button>
          <Button onClick={(e) => onCancel()}>Cancel</Button>
        </div>
      </form>
    </div>
  )

}


function StatesList(props) {

  const states = props.states;
  const updateState = props.updateState;

  const [editStateDialogOpen, setEditStateDialogOpen] = useState(false)
  const [selectedState, setSelectedState] = useState(null)
  const [menuAnchorEl, setMenuAnchorEl] = React.useState(null);

  const openMenu = (event, state) => {
    setSelectedState(state);
    setMenuAnchorEl(event.currentTarget);
  };
  const closeMenu = () => {
    setMenuAnchorEl(null);
  };
  const editState = () => {
    closeMenu();
    setEditStateDialogOpen(true);
  }
  const handleSave = (state) => {
    setEditStateDialogOpen(false)
    updateState(state)
  }

  const classes = useStyles();

  const makeStateList = (states) => {
    if (states === null ){
      return [];
    }
    else {
      const statesList = Object.values(states).map((value) => {
        return value;
      })
      return statesList;
    }
  }

  return (
    <div>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Path</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {makeStateList(states).map((state) => (
              <TableRow key={state.id}>
                <TableCell component="th" scope="row" classes={classes.tableCell}>
                  {state.path}
                </TableCell>
                <TableCell classes={classes.tableCell}>
                  {state.type}
                </TableCell>
                <TableCell align="right" classes={classes.tableCell}>
                  <IconButton aria-label="more" color="inherit" size="small" onClick={(e) => openMenu(e, state)}>
                    <MoreIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Menu anchorEl={menuAnchorEl} keepMounted open={Boolean(menuAnchorEl)} onClose={closeMenu}>
        <MenuItem onClick={editState}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <EditIcon/>
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={closeMenu}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <AddIcon/>
          </ListItemIcon>
          <ListItemText primary="Add Child" />
        </MenuItem>
        <MenuItem onClick={closeMenu}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <DeleteIcon/>
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Menu>

      <Dialog open={editStateDialogOpen} onClose={(e) => setEditStateDialogOpen(false)} fullWidth maxWidth="sm">
        <div style={{padding: '10px'}}>
          <EditStateDialog state={selectedState} onCancel={(e) => setEditStateDialogOpen(false)} onSave={handleSave}/>
        </div>
      </Dialog>

      <Fab color="primary" aria-label="add" style={{float: 'right', marginRight: '20px', marginTop: '-5px'}}>
        <AddIcon />
      </Fab>
    </div>
  );
}

function ViewStates(props) {
  const states = props.states;
  const ws = props.ws;

  const export_states = () =>{
    ws.listen_for_response(
      'export_states', {}, (message) => {
        const filename = 'states.json'
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(message.data.value));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);

      }
    )
  }

  const inputFile = useRef(null)

  const openFileInput = () => {
    inputFile.current.click();
  }

  const onFileChange = async (event) => {
    try {
      const file = event.target.files[0];
      console.log(file)
      var reader = new FileReader();
      reader.readAsText(file, "UTF-8");
      reader.onload = function (evt) {
        console.log(evt.target.result);
        ws.send({event: 'import_states', data: {value: evt.target.result}})
      }
      reader.onerror = function (evt) {
          console.error('error reading file')
      }

    } catch (err) {
      console.error(err);
    }
  };


  return (
    <div>
      <PageHeader icon="message_ok" title="States"/>

      <PageSection type="raised">
        <Button onClick={(e) => export_states()}>Export states</Button>
        <Button onClick={e => openFileInput()}>Import states</Button>
        <input type='file' id='file' ref={inputFile} accept="*.json" style={{display: 'none'}} onChange={onFileChange}/>
      </PageSection>

      <PageSection type="raised">
        <StatesList states={states} updateState={(state) => ws.send({event: 'state_update', data: state})}/>
      </PageSection>
    </div>
  );
}

export default ViewStates;