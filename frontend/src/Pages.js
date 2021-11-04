import React from 'react';
import { useParams } from "react-router-dom";

import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';


import {PageHeader, PageSection} from './PageLayout.js'
import {HomeconSwitch} from './widgets/Switch.js';
import {HomeconDimmer} from './widgets/Dimmer.js';
import {HomeconValue} from './widgets/Value.js';
import {HomeconShading} from './widgets/Shading.js';
import {HomeconAlarm} from './widgets/Alarm.js';
import {HomeconClock} from './widgets/Clock.js';
import {HomeconWeatherBlock} from './widgets/Weather.js';


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
          return false;
        });
        return true;
      }
      return false;
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
  let showHeader = true;

  const classes = useStyles();

  let headerWidget = '';
  if(page !== null && page.config.widget !== undefined){
    headerWidget = <HomeconWidget key={page.config.widget.path} type={page.config.widget.type} config={page.config.widget.config}
                    states={states} ws={ws}/>
  }
  if(page !== null && page.config.show_header !== undefined){
    showHeader = page.config.show_header;
  }

  if(page !== null){
    return (
      <div>
        {showHeader && (<PageHeader icon={page.config.icon} title={page.config.title} widget={headerWidget}/>)}
        <div className={classes.pageContent}>

        {page.sections.map((section) => (
          <PageSection key={section.path} title={section.config.title} type={section.config.type}>
            {section.widgets.map((widget) => {
              return <HomeconWidget key={widget.path} type={widget.type} config={widget.config} states={states} ws={ws}/>
            })}
          </PageSection>
        ))}
        </div>
      </div>
    );
  }
  return '';
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
  else if(type === 'clock'){
    return <HomeconClock config={config}/>
  }
  else if(type === 'weather-block'){
    return <HomeconWeatherBlock config={config} states={states}/>
  }

  return (
    <div>{type} {JSON.stringify(config)}</div>
  );
}


export {HomeconPage, HomeconPages, getPage};