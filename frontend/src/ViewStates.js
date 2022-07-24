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
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Checkbox from '@material-ui/core/Checkbox';

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
  const parentState = props.parentState || null;
  const states = props.states;

  const onCancel = props.onCancel;
  const onSave = props.onSave;

  const [name, setName] = useState('')
  const [parent, setParent] = useState(null)
  const [type, setType] = useState('')
  const [quantity, setQuantity] = useState('')
  const [unit, setUnit] = useState('')
  const [label, setLabel] = useState('')
  const [description, setDescription] = useState('')
  const [logKey, setLogKey] = useState('')
  const [config, setConfig] = useState('{}')
  const [value, setValue] = useState('')

  useEffect(() => {
    if(state !== null){
      setName(state.name || '');
      setParent(state.parent || null);
      setType(state.type || '');
      setQuantity(state.quantity || '');
      setUnit(state.unit || '');
      setLabel(state.label || '');
      setDescription(state.description || '');
      setLogKey(state.log_key || '');
      setConfig(state.config !== null ? JSON.stringify(state.config, undefined, 2) : '{}');
      setValue(state.value !== null ? JSON.stringify(state.value) : '');
    }
    else if(parentState !== null){
      setParent(parentState.key);
    }
  }, [state, parentState]);

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

    let newState = {}
    if(state !== null){
      newState.key = state.key;
    }
    newState.name = name;
    newState.parent = parent;
    newState.type = type === '' ? null : type;
    newState.quantity = quantity;
    newState.label = label;
    newState.description = description;
    newState.log_key = logKey;
    newState.config = JSON.parse(config);
    newState.value = newValue;

    onSave(newState);
  }

  const handleLogKeyCheckbox = (value) => {
    const UUIDGeneratorBrowser = () =>
      ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
      );

    if(value) {
      setLogKey(UUIDGeneratorBrowser())
    }
    else {
      setLogKey('')
    }

  }

  return (
    <div>
      <form>
        <div style={{display: 'flex', flexDirection: 'column'}}>
          <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)}/>
          <InputLabel id="Parent-select-label">Parent</InputLabel>
          <Select style={{width: '80%'}} labelId="action-select-label" id="demo-simple-select-helper" value={parent} onChange={(e) => setParent(e.target.value)} MenuProps={{style: {top: "100px", maxHeight: "500px"}}}>
            <MenuItem value={null}>/</MenuItem>
            {states.map((a) => {
              return <MenuItem key={a.key} value={a.key}>{a.path}</MenuItem>
            })}
          </Select>
          <TextField label="Type" value={type} onChange={(e) => setType(e.target.value)}/>
          <TextField label="Quantity" value={quantity} onChange={(e) => setQuantity(e.target.value)}/>
          <TextField label="Unit" value={unit} onChange={(e) => setUnit(e.target.value)}/>
          <TextField label="Label" value={label} onChange={(e) => setLabel(e.target.value)}/>
          <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)}/>
          <div style={{marginTop: '10px', width: '100%'}}>
            <InputLabel>Log Values</InputLabel>
            <div style={{display: 'flex', flexDirection: 'row'}}>
              <Checkbox style={{marginTop: '10px'}} checked={logKey !== ''} onChange={(e) => handleLogKeyCheckbox(e.target.checked)}/>
              <TextField label="Key" value={logKey} onChange={(e) => setLogKey(e.target.value)} style={{flexGrow: 1}}/>
            </div>
          </div>
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
  const addState = props.addState;
  const deleteState = props.deleteState;

  const [editStateDialogOpen, setEditStateDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  const [selectedState, setSelectedState] = useState(null)
  const [parentState, setParentState] = useState(null)
  const [menuAnchorEl, setMenuAnchorEl] = React.useState(null);
  const [filter, setFilter] = React.useState('');

  const openMenu = (event, state) => {
    setSelectedState(state);
    setMenuAnchorEl(event.currentTarget);
  };
  const closeMenu = () => {
    setMenuAnchorEl(null);
  };
  const editStateDialog = () => {
    closeMenu();
    setEditStateDialogOpen(true);
  }
  const addStateDialog = () => {
    setSelectedState(null);
    setEditStateDialogOpen(true);
  }
  const addChildStateDialog = () => {
    closeMenu();
    setParentState(selectedState)
    setSelectedState(null);
    setEditStateDialogOpen(true);
  }
  const deleteStateDialog = () => {
    closeMenu();
    setDeleteDialogOpen(true);
  }


  const handleSave = (state) => {
    setEditStateDialogOpen(false)
    if(state.key === undefined){
      addState(state)
    }
    else {
      updateState(state)
    }
  }
  const handleDeleteState = () => {
    setDeleteDialogOpen(false)
    if(selectedState.key !== undefined){
      deleteState(selectedState)
    }
  }

  const classes = useStyles();

  const makeStateList = (states, filter) => {
    if (states === null ){
      return [];
    }
    else {
      const statesList = Object.values(states).map((value) => {
        return value;
      }).filter(el => filter === '' || el.path.toLowerCase().indexOf(filter) > -1)
      statesList.sort((a, b) => {
        if(a.path > b.path) {
          return 1
        }
        else {
          return -1
        }
      })
      return statesList;
    }
  }

  return (
    <div>
      <TextField label="Filter" value={filter} onChange={(e) => setFilter(e.target.value.toLowerCase())} variant="outlined"/>
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
            {makeStateList(states, filter).map((state) => (
              <TableRow key={state.key}>
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
        <MenuItem onClick={editStateDialog}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <EditIcon/>
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={addChildStateDialog}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <AddIcon/>
          </ListItemIcon>
          <ListItemText primary="Add Child" />
        </MenuItem>
        <MenuItem onClick={deleteStateDialog}>
          <ListItemIcon style={{color: "#ffffff"}}>
            <DeleteIcon/>
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Menu>

      <Dialog open={editStateDialogOpen} onClose={(e) => setEditStateDialogOpen(false)} fullWidth maxWidth="sm">
        <div style={{padding: '10px'}}>
          <EditStateDialog state={selectedState} parentState={parentState} states={makeStateList(states, '')} onCancel={(e) => setEditStateDialogOpen(false)} onSave={handleSave}/>
        </div>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={(e) => setDeleteDialogOpen(false)}>
          <h3>Delete state?</h3>
          <Button variant="contained" onClick={() => setDeleteDialogOpen(false)}>cancel</Button>
          <Button variant="contained" color="primary" onClick={(e) => handleDeleteState()}>Delete</Button>
      </Dialog>

      <Fab color="primary" aria-label="add" style={{float: 'right', marginRight: '20px', marginTop: '-5px'}} onClick={addStateDialog}>
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
      'states_export', {}, (message) => {
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
      var reader = new FileReader();
      reader.readAsText(file, "UTF-8");
      reader.onload = function (evt) {
        ws.send({event: 'states_import', data: {value: evt.target.result}})
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
        <StatesList states={states}
         updateState={(state) => ws.send({event: 'state_update', data: state})}
         addState={(state) => ws.send({event: 'state_add', data: state})}
         deleteState={(state)=> ws.send({event: 'state_delete', data: state})} />
      </PageSection>
    </div>
  );
}

export default ViewStates;