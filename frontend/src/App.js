import React, { useState, useEffect }  from 'react';
import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';

import HomeconLayout from './Layout.js';

import Dialog from '@material-ui/core/Dialog';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';



const darkTheme = createMuiTheme({
  palette: {
    background: {
      default: "rgba(38, 38, 38, 1)",
      paper: "rgba(30, 30, 30, 1)"
    },
    primary: {
      main: "rgba(20, 20, 20, 1)",
      light: "rgba(55, 55, 55, 1)",
      dark: "rgba(10, 10, 10, 1)",
      contrastText: "rgba(240, 240, 240, 1)",
    },
    secondary: {
      main: "rgba(229, 229, 229, 1)",
      light: "rgba(220, 220, 220, 1)",
      dark: "rgba(200, 200, 200, 1)",
      contrastText: "rgba(33, 33, 33, 1)",
    },
    text: {
      primary: "rgba(233, 233, 233, 0.87)",
      secondary: "rgba(190, 190, 190, 1)",
      disabled: "rgba(0, 0, 0, 1)",
      hint: "rgba(75, 75, 75, 1)",
    },
    widget: {
      on: "rgba(247, 154, 31, 1)",
      off: "rgba(240, 240, 240, 1)",
    }
  },

  overrides: {
    MuiSlider: {
      colorPrimary: {
        color: "rgba(240, 240, 240, 1)",
      },
    },
    MuiSwitch: {
      colorSecondary: {
        '&$checked': {
          color: "rgba(247, 154, 31, 1)",
        },
        '&$checked + $track': {
          backgroundColor: "rgba(247, 154, 31, 1)",
        },
      },
    }

  },
});


class HomeconWebsocket {

  constructor(app) {
    this.app = app
    this.ws = null
    this.event_listeners = {}
  }

  timeout = 250; // Initial timeout duration as a class variable

  connect(url) {
    console.log(`attempting to connect to homecon at ${this.app.state.wsUrl}`)

    const fullUrl = this.app.state.wsUrl + "/" + this.app.state.token;
    let ws
    try{
      ws = new WebSocket(fullUrl);
    }
    catch(error){
      console.error(error)
      ws = null
    }

    if (ws !== null) {
      let that = this; // cache the this
      let connectInterval;

      // websocket onopen event listener
      ws.onopen = () => {
        console.log(`Connected to HomeCon server at ${this.app.state.wsUrl}`);
        this.ws = ws

        // add the websocket to the state
        this.app.setState({
          ws: this
        });

        // send connection messages
        // user auth
        // pages
        const pages_data = JSON.parse(window.localStorage.getItem('pages_data'));
        this.parse_pages_data(pages_data)
        this.send({'event': 'pages_timestamp', data: {'id': null}})

        // states
        this.send({'event': 'state_list', data: {'id': null}})

        that.timeout = 250; // reset timer to 250 on open of websocket connection
        clearTimeout(connectInterval); // clear Interval on on open of websocket connection
      };

      // websocket onclose event listener
      ws.onclose = e => {
        console.log(
          `Socket is closed. Reconnect will be attempted in ${Math.min(10000 / 1000, (that.timeout + that.timeout) / 1000)} second.`
        );

        that.timeout = that.timeout + that.timeout; //increment retry interval
        this.app.setState({
          ws: null
        });
        connectInterval = setTimeout(this.check.bind(this), Math.min(10000, that.timeout)); //call check function after timeout
      };

      // websocket onerror event listener
      ws.onerror = err => {
        console.error(
          "Socket encountered error, Closing socket"
        );
        ws.close();
      };

      ws.onmessage = evt => {
        // listen to data sent from the websocket server
        const message = JSON.parse(evt.data)
        console.log(`received ${evt.data}`)

        if(message.event === 'pages_timestamp'){
          if(this.app.state.pagesData === null || this.app.state.pagesData.timestamp === undefined ||
             this.app.state.pagesData.timestamp < message.data.value){
            this.send({'event': 'pages_pages', data: {'id': null}})
          }
        }
        else if(message.event === 'pages_pages'){
          this.app.setState({
            pagesData: message.data.value
          });
          window.localStorage.setItem('pages_data', JSON.stringify(message.data.value));
          this.parse_pages_data(message.data.value)
        }

        else if(message.event === 'state_list'){
          const states = {};
          message.data.value.forEach((item, index) => {
             states[item.id] = item;
          });
          this.app.setState({
            states: states
          });

        }

        else if(message.event === 'state_value'){

          var states = {...this.app.state.states}
          if(states === undefined || states[message.data.id] === undefined){
            console.info(`no state with id ${message.data.id}`)
          }
          else{
            states[message.data.id].value = message.data.value;
          }

          this.app.setState({
            states: states
          });
        }

        else if(message.event === 'state_timeseries'){
          var states = {...this.app.state.states}
          if(states === undefined || states[message.data.id] === undefined){
            console.info(`no state with id ${message.data.id}`)
          }
          else{
            states[message.data.id].timeseries = message.data.timeseries;
          }
          this.app.setState({
            states: states
          });
        }

        else if(message.event === 'state_timeseries_update'){
          var states = {...this.app.state.states}
          if(states === undefined || states[message.data.id] === undefined){
            console.info(`no state with id ${message.data.id}`)
          }
          else{
            states[message.data.id].timeseries.push(...message.data.timeseries);
          }

          this.app.setState({
            states: states
          });

        }

        else if(this.event_listeners[message.event] !== undefined){
          this.event_listeners[message.event](message)
        }
      }
    }
  };

  send(data) {
    const str_data = JSON.stringify(data)
    console.log(`sending ${str_data}`)
    try {
      this.ws.send(str_data)
    } catch (error) {
      console.log(error)
    }
  };

  listen_for_response(event, data, callback) {
    this.event_listeners[event] = (message) => {
      callback(message);
      // remove the listener?
    }
    this.send({event: event, data: data})
  };

  parse_pages_data(pages_data) {
    if(pages_data !== null){
      this.app.setState({
        pagesData: pages_data
      });
    }
  }

  /**
   * utilited by the @function connect to check if the connection is close, if so attempts to reconnect
   */
  check() {
    const  ws = this.ws;
    if (!ws || ws.readyState === WebSocket.CLOSED){
      this.connect(); //check if websocket instance is closed, if so call `connect` function.
    }
  };

}


function ConnectionSettings(props){
  const wsUrl = props.wsUrl;
  const setWsUrl = props.setWsUrl;
  const token = props.token;
  const setToken = props.setToken;

  const connect = props.connect;
  const connected = props.connected;

  const [open, setOpen] = useState(false)

  useEffect(() => {
    setOpen(!connected)
  }, [connected])

  return (
    <div>
      <Dialog open={open}>

        <div style={{margin: '20px'}}>

          <Typography>Not connected to homecon</Typography>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Connection settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                <div style={{display: "flex", flexDirection: "column"}}>
                  <TextField label="HomeCon Web Socket url" value={wsUrl} onChange={(e) => setWsUrl(e.target.value)}/>
                  <TextField label="Token" type="password" value={token} onChange={(e) => setToken(e.target.value)}/>
                </div>
                <div style={{marginTop: '10px'}}>
                  <Button onClick={() => connect()}>re-connect</Button>
                </div>
              </Typography>
            </AccordionDetails>
          </Accordion>
        </div>
      </Dialog>
    </div>
  )
}

class App extends React.Component {

  constructor(props) {
    super(props);

    this.homeconWebsocket = new HomeconWebsocket(this)

    let wsUrl = window.localStorage.getItem('websocketUrl');
    if(wsUrl === null){
      wsUrl = 'ws://localhost:9099'
    }
    let token = window.localStorage.getItem('token');
    if(token === null){
      token = ''
    }

    this.state = {
      wsUrl: wsUrl,
      token: token,
      ws: null,
      states: null,
      pages: null,
      pagesData: {timestamp: 0, groups: []},
    };
  }

  componentDidMount() {
    this.homeconWebsocket.check();
  }

  setWsUrl(value) {
    this.setState({wsUrl: value});
    window.localStorage.setItem('websocketUrl', value);
  }
  setToken(value) {
    this.setState({token: value});
    window.localStorage.setItem('token', value);
  }

  render() {

    return (
      <ThemeProvider theme={darkTheme}>
        <HomeconLayout pagesData={this.state.pagesData} states={this.state.states} ws={this.state.ws}/>
        <ConnectionSettings wsUrl={this.state.wsUrl} setWsUrl={(val) => this.setWsUrl(val)} token={this.state.token} setToken={(val) => this.setToken(val)} connect={() => this.homeconWebsocket.check()} connected={this.state.ws !== null}/>
      </ThemeProvider>
    );
  }
}

export default App;
