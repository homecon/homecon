import React, { useEffect } from 'react';
import { useTheme } from '@material-ui/core/styles';


import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Label } from 'recharts';
import moment from 'moment'

const colors = [
  '#9A641E',
  '#54991E',
  '#1E5499',
  '#641E99',
  '#991E2B',
]


function HomeconChart(props){
  const config = props.config;
  const states = props.states;
  const ws = props.ws;

  const now = parseInt((new Date()).getTime()/1000)
  const days = config.days  || 1;

  const from = now - days * 24 * 3600;
  const to = now;

  const stateIds = config.states || [];

  const allStates = stateIds.map(stateId => {
    let state = undefined;
    if(states !== null){
      state = states[stateId];
    }
    if(state === undefined){
      state = {};
    }
    return state;
  })

  const title = config.title;

  useEffect(() => {
    allStates.forEach(state => {
      if(state !== null && state.key !== undefined && state.timeseries === undefined) {
        const now = parseInt((new Date()).getTime()/1000)
        const from = now - days * 24 * 3600;
        let event = {'event': 'state_timeseries', 'data': {'id': state.id, 'since': from}};
        console.log(event)
        ws.send(event)
      }
    })
  }, [ws, allStates, config]);

  const makeData = (timeseries) => {
    let data = timeseries.map(value => {return {timestamp: value[0], value: value[1]}})
    return data;
  }

  const allSeries = allStates.map((state, index) => {
    return {
      quantity: state.quantity || '',
      unit: state.unit || '',
      label: state.label || '',
      data: makeData(state.timeseries || []),
      color: colors[index]
    }
  });

  let unit = null
  let quantity = null
  allSeries.forEach(series =>{
    if (series.quantity !== ''){
      quantity = series.quantity;
      return false;
    }
  })
  allSeries.forEach(series =>{
    if (series.unit !== ''){
      unit = series.unit;
      return false;
    }
  })

  let ylabel = '';
  if( quantity !== null ) {
    ylabel = ylabel + quantity;
  }
  if( unit !== null ) {
    ylabel = ylabel + ` (${unit})`;
  }

  const theme = useTheme();

  const CustomizedAxisTick = (props) => {
    const x = props.x;
    const y = props.y;
    const payload = props.payload;

    return (
      <g transform={`translate(${x},${y})`}>
        <text x={0} y={0} dy={16} fill="#666">
          <tspan textAnchor="middle" x="0">{moment(payload.value*1000).format('HH:mm:ss')}</tspan>
          <tspan textAnchor="middle" x="0" dy="20">{moment(payload.value*1000).format('DD-MM')}</tspan>
        </text>
      </g>
    )
  }

  return (
    <div>
      <div>{title}</div>
      <ResponsiveContainer width = '95%' height = {500} >
        <LineChart>
          {allSeries.map((series, index) => (
              <Line key={index} isAnimationActive={false} data={series.data} dataKey='value' type='stepAfter' stroke={series.color} name={series.label} />
          ))}

          <XAxis dataKey='timestamp' domain={[from, to]} type='number' tick={<CustomizedAxisTick/>} height={50} allowDuplicatedCategory={false}/>
          <YAxis>
            <Label value={ylabel} angle={-90} position='insideLeft' style={{fill: theme.palette.secondary.dark}}/>
          </YAxis>

          <CartesianGrid stroke="#444" strokeDasharray="5 5"/>
          <Tooltip labelFormatter={(ts) => moment(ts*1000).format('DD-MM-YYYY HH:mm:ss')} contentStyle={{backgroundColor: theme.palette.background.default, borderColor: theme.palette.primary.light}}/>

          <Legend verticalAlign="bottom" height={25}/>
        </LineChart>
      </ResponsiveContainer>

    </div>
  )
}

export {HomeconChart};