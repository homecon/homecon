import React, { useState } from 'react';
import { useParams } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Collapse from '@material-ui/core/Collapse';
import Paper from '@material-ui/core/Paper';

import HomeconIcon from './Icon.js';
import {HomeconSwitch} from './widgets/Switch.js';
import {HomeconDimmer} from './widgets/Dimmer.js';
import {HomeconValue} from './widgets/Value.js';
import {HomeconShading} from './widgets/Shading.js';
import {HomeconAlarm} from './widgets/Alarm.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    pageHeader: {
      display: 'flex',
      marginBottom: '20px'
    },
    pageIcon: {
      height: '60px'
    },
    pageTitle: {
      flexGrow: 1,
      alignSelf: 'center',
      margin: '5px 5px 5px 20px',
      fontSize: '26px',
      fontWeight: 700,
    },
    pageHeaderWidget: {

    },
    pageSection: {
      width: '100%',
      marginBottom: '25px',
      padding: '10px',
      position: 'relative'
    },
    underlined: {
      borderBottom: '1px solid ' + theme.palette.primary.main
    }
  })
);

const getPage = (pagesData, groupName, pageName) => {
  let p = null

  if((groupName !== undefined) && (pageName !== undefined) && (pagesData.groups !== undefined)){
    pagesData.groups.some((group) => {
      if(group.name === groupName){
        group.pages.some((page) => {
          if(page.name === pageName){
            p = page
            return true;
          }
        });
        return true;
      }
    });
  }
  return p;
}


function HomeconPages(props){

  const pagesData = props.pagesData;
  const states = props.states;
  const ws = props.ws;

  const params = useParams()
  const groupName = params.group;
  const pageName = params.page;

  const page = getPage(pagesData, groupName, pageName)
  if(page !== null){
    return <HomeconPage page={page} states={states} ws={ws}/>;
  }
  return null;
}


function HomeconPage(props){
  const page = props.page;
  const states = props.states;
  const ws = props.ws;

  const classes = useStyles();

  let headerWidget = '';
  if(page !== null && page.config.widget !== undefined){
    headerWidget = <HomeconWidget key={page.config.widget.path} type={page.config.widget.type} config={page.config.widget.config}
                    states={states} ws={ws}/>
  }

  if(page !== null){
    return (
      <div>
        <HomeconPageHeader icon ={page.config.icon} title={page.config.title} widget={headerWidget}/>
        <div className={classes.pageContent}>

        {page.sections.map((section) => {
        return <HomeconPageSection key={section.path} title={section.config.title} type={section.config.type}>
          {section.widgets.map((widget) => {
            return <HomeconWidget key={widget.path} type={widget.type} config={widget.config} states={states} ws={ws}/>
          })}
        </HomeconPageSection>

        })}
        </div>
      </div>
    );
  }
  return '';
}


function HomeconPageHeader(props){
  const title = props.title;
  const icon = props.icon;
  const widget = props.widget;

  const classes = useStyles();

  return (
    <div className={classes.pageHeader}>
     <div className={classes.pageIcon}>
        <HomeconIcon name={icon} color="ffffff"/>
     </div>
     <div className={classes.pageTitle}>
      {title}
     </div>
     <div className={classes.pageWidget}>
       {widget}
     </div>
   </div>
  );
}

function HomeconPageSection(props){
  const title = props.title;
  const type = props.type;

  const children = props.children

  const classes = useStyles();

  if(type === 'raised') {
    return (
      <Paper className={classes.pageSection}>
        <div style={{position: 'absolute', top: '-12px', left: '5px'}}>{title}</div>
        <div>
          {children}
        </div>
      </Paper>
    );
  }
  else if(type === 'underlined') {
    return (
      <div className={`${classes.pageSection} ${classes.underlined}`}>
        {children}
      </div>
    );
  }
  else {
    return (
      <div className={classes.pageSection}>
        {children}
      </div>
    );
  }
}

function HomeconWidget(props){
  const type = props.type;
  const config = props.config;
  const states = props.states;
  const ws = props.ws;

  if(type === 'switch'){
    return <HomeconSwitch config={config} states={states} ws={ws}/>
  }
  else if(type === 'dimmer'){
    return <HomeconDimmer config={config} states={states} ws={ws}/>
  }
  else if(type === 'shading'){
    return <HomeconShading config={config} states={states} ws={ws}/>
  }
  else if(type === 'value-display'){
    return <HomeconValue config={config} states={states}/>
  }
  else if(type === 'alarm'){
    return <HomeconAlarm config={config} states={states} ws={ws}/>
  }
  return (
    <div>{type} {JSON.stringify(config)}</div>
  );
}


export {HomeconPage, HomeconPages, getPage};