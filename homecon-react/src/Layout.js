import React, { useState, useEffect } from 'react';

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import SwipeableDrawer from '@material-ui/core/SwipeableDrawer';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import CssBaseline from '@material-ui/core/CssBaseline';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import Hidden from '@material-ui/core/Hidden';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import MenuIcon from '@material-ui/icons/Menu';
import MoreIcon from '@material-ui/icons/MoreVert';

import HomeconPagesMenu from './PagesMenu.js';

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
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar style={{display: "flex", paddingRight: "12px"}}>
          <Hidden mdUp>
            <IconButton edge="start" color="inherit" aria-label="open drawer" onClick={togglePagesMenu()}>
              <MenuIcon/>
            </IconButton>
          </Hidden>

          <img src="./logo512.png" style={{height: '50px', marginRight: '20px', marginLeft: '10px'}}/>

          <Typography variant="h6" style={{flexGrow: 1}} noWrap>
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
          <HomeconPagesMenu groups={props.pagesData.groups}/>
        </SwipeableDrawer>
      </Hidden>

      <Hidden smDown>
        <Drawer anchor="left" className={classes.drawer} classes={{paper: classes.drawerPaper}} variant="permanent">
          <Toolbar />
          <HomeconPagesMenu groups={props.pagesData.groups}/>
        </Drawer>
      </Hidden>

      <Menu anchorEl={settingsMenuAnchor} keepMounted open={Boolean(settingsMenuAnchor)} onClose={toggleSettingsMenu(false)}
       anchorReference="none" PaperProps={{style: {top: '70px', right: '12px'}}}>
        <MenuItem onClick={toggleSettingsMenu(false)}>Profile</MenuItem>
        <MenuItem onClick={toggleSettingsMenu(false)}>My account</MenuItem>
        <MenuItem onClick={toggleSettingsMenu(false)}>Logout</MenuItem>
      </Menu>

      <main className={classes.content}>
        <Toolbar />
        test 123
      </main>
    </div>
  );
}


export default HomeconLayout;