import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';

import HomeconIcon from './Icon.js';


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


export function PageHeader(props){
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


export function PageSection(props){
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
