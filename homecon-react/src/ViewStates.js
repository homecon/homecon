import React, { useState, useRef } from 'react';

import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Fab from '@material-ui/core/Fab';
import IconButton from '@material-ui/core/IconButton';
import AddIcon from '@material-ui/icons/Add';
import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';
import Button from '@material-ui/core/Button';

import {PageHeader, PageSection} from './PageLayout.js'

function EditStateDialog(props){
  return (
    <div>
      <form>

      </form>
    </div>
  )

}

function State(props) {
  const state = props.state;

  return (

    <Card style={{display: 'flex', flexDirection: 'row', width: '100%', marginBottom: '5px'}}>
      <CardContent style={{display: 'flex', flexGrow: 1, width: '10%'}}>
        {state.path}
      </CardContent>
      <CardActions>
        <IconButton aria-label="edit" style={{marginLeft: '10px'}} color="inherit" size="small">
          <EditIcon />
        </IconButton>
        <IconButton aria-label="add" style={{marginLeft: '10px'}} color="inherit" size="small">
          <AddIcon />
        </IconButton>
        <IconButton aria-label="delete" style={{marginLeft: '10px'}} color="inherit" size="small">
          <DeleteIcon />
        </IconButton>
      </CardActions>
    </Card>
  );
}

function StatesList(props) {

  const states = props.states;
  const [editStateDialogOpen, setEditStateDialogOpen] = useState(false)

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
      {makeStateList(states).map((state) => (
        <State key={state.id} state={state} />
      ))}
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
        <StatesList states={states} />
      </PageSection>
    </div>
  );
}

export default ViewStates;