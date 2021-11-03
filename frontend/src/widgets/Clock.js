import React, { useEffect, useState } from 'react';


function HomeconClock(props){
  const config = props.config;
  const [date, setDate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(
      () => setDate(new Date()), 1000
    );
    return () => {
      clearInterval(interval);
    }
  }, []);

  const getTime = (date) => {
    let hour = date.getHours();
    if(hour < 10){
      hour = `0${hour}`;
    }
    else {
      hour = `${hour}`;
    }
    let minute = date.getMinutes();
    if(minute < 10){
      minute = `0${minute}`;
    }
    else {
      minute = `${minute}`;
    }
    return `${hour}:${minute}`
  }
  const getDate = (date) => {
    const locale = config.locale || 'nl-BE';
    const options = config.dateOptions || {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
    return date.toLocaleDateString(locale, options)
  }

  return (
    <div>
      <div style={{display: "flex", flexDirection: "row", justifyContent: "center", fontSize: "6em", fontWeight: 700}}>
        {getTime(date)}
      </div>
      <div style={{display: "flex", flexDirection: "row", justifyContent: "center", fontSize: "1.2em",}}>
        {getDate(date)}
      </div>
    </div>
  )
}


export {HomeconClock};