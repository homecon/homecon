import React, { useRef } from 'react';

import Button from '@material-ui/core/Button';


import {PageHeader, PageSection} from './PageLayout.js'


function ViewEditPages(props) {
  const ws = props.ws;

  const export_pages = () =>{
    ws.listen_for_response(
      'pages_export', {}, (message) => {
        const filename = 'pages.json'
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
        ws.send({event: 'pages_import', data: {value: evt.target.result}})
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
      <PageHeader icon="message_ok" title="Pages"/>

      <PageSection type="raised">
        <Button onClick={(e) => export_pages()}>Export pages</Button>
        <Button onClick={e => openFileInput()}>Import pages</Button>
        <input type='file' id='file' ref={inputFile} accept="*.json" style={{display: 'none'}} onChange={onFileChange}/>
      </PageSection>

    </div>
  );
}

export default ViewEditPages;