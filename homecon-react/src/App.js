import React from 'react';
import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';

import HomeconLayout from './Layout.js';


const darkTheme = createMuiTheme({
  palette: {
    background: {
      default: "rgba(38, 38, 38, 1)",
      paper: "rgba(35, 35, 35, 1)"
    },
    primary: {
      main: "rgba(20, 20, 20, 1)",
      light: "rgba(25, 25, 25, 1)",
      dark: "rgba(10, 10, 10, 1)",
      contrastText: "rgba(240, 240, 240, 1)",
      on: "#f79a1f"
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
    }
  },
  overrides: {
    // Style sheet name ⚛️
    MuiSlider: {
      // Name of the rule
      colorPrimary: {
        // Some CSS
        color: "rgba(240, 240, 240, 1)",
      },
    },
  },
});


class HomeconWebsocket {

  constructor(app) {
    this.app = app
    this.ws = null
  }

  timeout = 250; // Initial timeout duration as a class variable

  connect() {
    var ws = new WebSocket("ws://localhost:9099");
    let that = this; // cache the this
    var connectInterval;

    // websocket onopen event listener
    ws.onopen = () => {
      console.log("connected to homecon");
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
        `Socket is closed. Reconnect will be attempted in ${Math.min(10000 / 1000, (that.timeout + that.timeout) / 1000)} second.`,
        e.reason
      );

      that.timeout = that.timeout + that.timeout; //increment retry interval
      connectInterval = setTimeout(this.check.bind(this), Math.min(10000, that.timeout)); //call check function after timeout
    };

    // websocket onerror event listener
    ws.onerror = err => {
      console.error(
        "Socket encountered error: ",
        err.message,
        "Closing socket"
      );
      ws.close();
    };

    ws.onmessage = evt => {
      // listen to data sent from the websocket server
      const message = JSON.parse(evt.data)
      console.log(`received ${evt.data}`)

      if(message.event === 'pages_timestamp'){
        if(this.app.state.pages === null || this.app.state.pages.timestamp < message.data.value){
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
        this.app.setState({
          stateList: message.data.value
        });

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
        states[message.data.id].value = message.data.value;

        this.app.setState({
          states: states
        });
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

  parse_pages_data(pages_data) {
    if(pages_data !== null){
      this.app.setState({
        pagesData: pages_data
      });

      const pages = {};
      pages_data.groups.forEach((group, index) => {
        group.pages.forEach((page, index) => {
          pages[page.path] = page;
        });
      });
      this.app.setState({
        pages: pages
      });

    }
  }

  /**
   * utilited by the @function connect to check if the connection is close, if so attempts to reconnect
   */
  check() {
    console.log(this)
    const  ws = this.ws;
    if (!ws || ws.readyState === WebSocket.CLOSED){
      this.connect(); //check if websocket instance is closed, if so call `connect` function.
    }
  };

}


class App extends React.Component {

  constructor(props) {
    super(props);

    this.homeconWebsocket= new HomeconWebsocket(this)

    this.state = {
      ws: null,
      states: null,
      stateList: [],
      pages: null,
      pagesData: [],
      pagesMenuOpen: false
    };
  }

  componentDidMount() {
    this.homeconWebsocket.connect();
  }

  render(){
    return (
      <ThemeProvider theme={darkTheme}>
        <HomeconLayout pagesData={this.state.pagesData} states={this.state.states} ws={this.state.ws}/>
      </ThemeProvider>
    );
  }
}

export default App;
