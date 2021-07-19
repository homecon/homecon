import React, { useState } from 'react';
import { BrowserRouter, Switch, Route, Link } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import SwipeableDrawer from '@material-ui/core/SwipeableDrawer';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import CssBaseline from '@material-ui/core/CssBaseline';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Hidden from '@material-ui/core/Hidden';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import MenuIcon from '@material-ui/icons/Menu';
import MoreIcon from '@material-ui/icons/MoreVert';

import HomeconPagesMenu from './PagesMenu.js';
import {HomeconPage, HomeconPages, getPage} from './Pages.js';
import ViewStates from './ViewStates.js';
import ViewEditPages from './ViewEditPages.js';


const drawerWidth = 460;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
    },
    appBar: {
      zIndex: 1302
    },
    drawer: {
      width: drawerWidth,
      flexShrink: 0,
    },
    drawerPaper: {
      width: drawerWidth,
    },
    content: {
      flexGrow: 1,
      padding: theme.spacing(3),
    },
  }),
);


function HomeconLayout(props){

  const states = props.states;
  const ws = props.ws;
  console.log(states)
  const classes = useStyles();
  const [pagesMenuOpen, setPagesMenuOpen] = useState(false);
  const [settingsMenuAnchor, setSettingsMenuAnchor] = useState(null);

  const togglePagesMenu = (open) => (event) => {
    if(open === undefined){
      setPagesMenuOpen(!pagesMenuOpen);
    }
    else{
      setPagesMenuOpen(open);
    }
  }

  const toggleSettingsMenu = (open) => (event) => {
    if(open){
      setSettingsMenuAnchor(event.currentTarget);
    }
    else{
      setSettingsMenuAnchor(null);
    }
  };

  return (
    <BrowserRouter>
      <div className={classes.root}>
        <CssBaseline />
        <AppBar position="fixed" className={classes.appBar}>
          <Toolbar style={{display: "flex", paddingRight: "12px"}}>
            <Hidden mdUp>
              <IconButton edge="start" color="inherit" aria-label="open drawer" onClick={togglePagesMenu()}>
                <MenuIcon/>
              </IconButton>
            </Hidden>
            <Link to="/">
              <img src="/logo512.png" alt="Homecon logo" style={{height: '50px', marginRight: '20px', marginLeft: '10px'}}/>
            </Link>
            <Typography variant="h6" style={{flexGrow: 1}}  noWrap>
                HomeCon
            </Typography>

            <IconButton color="inherit" aria-label="open menu" onClick={toggleSettingsMenu(true)}>
              <MoreIcon/>
            </IconButton>

          </Toolbar>
        </AppBar>

        <Hidden mdUp>
          <SwipeableDrawer anchor="left" className={classes.drawer} classes={{paper: classes.drawerPaper}}
           open={pagesMenuOpen} onClose={togglePagesMenu(false)} onOpen={togglePagesMenu(true)}>
            <Toolbar />
            <HomeconPagesMenu groups={props.pagesData.groups} />
          </SwipeableDrawer>
        </Hidden>

        <Hidden smDown>
          <Drawer anchor="left" className={classes.drawer} classes={{paper: classes.drawerPaper}} variant="permanent">
            <Toolbar />
            <HomeconPagesMenu groups={props.pagesData.groups} />
          </Drawer>
        </Hidden>

        <Menu anchorEl={settingsMenuAnchor} keepMounted open={Boolean(settingsMenuAnchor)} onClose={toggleSettingsMenu(false)}
         anchorReference="none" PaperProps={{style: {top: '70px', right: '12px'}}}>
          <Link to="/profile"><MenuItem onClick={toggleSettingsMenu(false)}>Profile</MenuItem></Link>
          <Link to="/states"><MenuItem onClick={toggleSettingsMenu(false)}>States</MenuItem></Link>
          <Link to="/edit-pages"><MenuItem onClick={toggleSettingsMenu(false)}>Pages</MenuItem></Link>
          <Link to="/plugins"><MenuItem onClick={toggleSettingsMenu(false)}>Plugins</MenuItem></Link>
          <MenuItem onClick={toggleSettingsMenu(false)}>Logout</MenuItem>
        </Menu>

        <main className={classes.content}>
          <Toolbar />
          <Switch>
            <Route path="/pages/:group/:page" children={<HomeconPages pagesData={props.pagesData} states={states} ws={ws}/>} >
            </Route>
            <Route path="/login">
              Login
            </Route>
            <Route path="/profile">
              Profile
            </Route>
            <Route path="/states">
              <ViewStates states={states} ws={ws}/>
            </Route>
            <Route path="/edit-pages">
              <ViewEditPages ws={ws}/>
            </Route>
            <Route path="/plugins">
              Plugins
            </Route>
            <Route path="/">
              <HomeconPage page={getPage(props.pagesData, 'home', 'home')}/>
            </Route>
          </Switch>
        </main>

      </div>
    </BrowserRouter>
  );
}



export default HomeconLayout;