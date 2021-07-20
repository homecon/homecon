import React, { useState } from 'react';
import { Link } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';

import HomeconIcon from './Icon.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    group: {
        display: 'block',
        cursor: 'pointer',
        minHeight: '16px',
        padding: '12px 12px 12px 40px',
        backgroundColor: theme.palette.secondary.main,
        borderTop: 'solid 1px ' + theme.palette.secondary.dark,
        fontSize: '16px',
        fontWeight: 700,
        textDecoration: 'none',
        color: theme.palette.secondary.contrastText,
        '&:hover': {
          backgroundColor: theme.palette.secondary.light,
      },
    },
    page: {
      display: 'flex',
      position: 'relative',
      cursor: 'pointer',
      height: '60px',
      borderBottom: 'solid 1px ' + theme.palette.primary.main,
      fontSize: '18px',
      fontWeight: 700,
      textDecoration: 'none',
      color: theme.palette.primary.contrastText,
      '&:hover': {
          backgroundColor: theme.palette.primary.light,
      },
      alignItems: 'center'
    },
    pageIcon: {
      width: '59px',
      height: '59px'
    },
    pageTitle: {
      marginLeft: '40px'
    }
  })
);


function HomeconPagesMenu(props){

  const [openGroupPath, setOpenGroupPath] = useState(null);
  const closeMenu = props.closeMenu;

  const toggleCollapse = (group) => (event) =>  {
    setOpenGroupPath(group.path)
  };

  if(props.groups !== undefined){
    const menuGroups = props.groups.filter((group) => group.path !== '/home')

    const menu = menuGroups.map((group) => <HomeconPagesMenuGroup key={group.path} title={group.config.title} path={group.path} pages={group.pages}
                                            handleClick={toggleCollapse(group)} collapsed={openGroupPath===group.path} closeMenu={closeMenu}/>);
    return menu;
  }
  else {
    return '';
  }
}


function HomeconPagesMenuGroup(props){
  const classes = useStyles();

  const menuPages = props.pages
  const closeMenu = props.closeMenu;

  const menu = menuPages.map((page) => <HomeconPagesMenuPage key={page.path} title={page.config.title} path={page.path} icon={page.config.icon} closeMenu={closeMenu}/>);
  return (
    <div>
      <span className={classes.group} onClick={props.handleClick}>{props.title}</span>
      <Collapse in={props.collapsed}>
        {menu}
      </Collapse>
    </div>
  );
}


function HomeconPagesMenuPage(props){
  const classes = useStyles();

  const link = `/pages${props.path}`
  const closeMenu = props.closeMenu;
  console.log(closeMenu)

  return (
    <div>
      <Link to={link} className={classes.page} onClick={(e) => closeMenu !== undefined ? closeMenu() : null}>
        <div className={classes.pageIcon}>
          <HomeconIcon name={props.icon} color="ffffff"/>
        </div>
        <div className={classes.pageTitle}>{props.title}</div>
      </Link>
    </div>
  );
}
//        <MyIcon stroke="#ffffff"/>


export default HomeconPagesMenu;