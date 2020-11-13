import React, { useState, useEffect, useRef } from 'react';

//function HomeconIcon({ name, ...rest }) {
//  const ImportedIconRef = useRef(null);
//  const [loading, setLoading] = useState(false);
//
//  useEffect(() => {
//    setLoading(true);
//    const importIcon = async () => {
//      try {
//        ImportedIconRef.current = (await import(`./icons/${name}.svg`)).ReactComponent;
//      } catch (err) {
//        // Your own error handling logic, throwing error for the sake of
//        // simplicity
//        throw err;
//      } finally {
//        setLoading(false);
//      }
//    };
//    importIcon();
//  }, [name]);
//
//  return <MyIcon {...rest} />;
//
//  console.log(loading, ImportedIconRef)
//  if (!loading && ImportedIconRef.current) {
//    const { current: ImportedIcon } = ImportedIconRef;
//    return <ImportedIcon {...rest} />;
//  }
//
//  return null;
//};

function HomeconIcon(props) {
  const src = `./icons/${props.color}/${props.name}.png`;
  if(props.name !== undefined){
    return (
      <img src={src} style={{height: '100%'}}/>
    );
  }
  return null;
};


export default HomeconIcon;