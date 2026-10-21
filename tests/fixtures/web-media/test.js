import expected from './expected.json' assert {type: 'json'};

console.warn('TEST_MEDIA_PAGE_LOADED');const got={};
function done(k,e){got[k]=e;document.querySelector('#result').textContent=JSON.stringify(got);}
wallpaperRegisterMediaStatusListener(e=>{if(!e.enabled)throw Error('Media status disabled');done('status',e);});
wallpaperRegisterMediaPropertiesListener(e=>{if(e.title!==expected.title||e.artist!==expected.artist)throw Error('Wrong media metadata '+JSON.stringify(e));done('properties',e);});
wallpaperRegisterMediaPlaybackListener(e=>{if(e.state!==wallpaperMediaIntegration.PLAYBACK_PLAYING)throw Error('Wrong playback state');done('playback',e);});
wallpaperRegisterMediaTimelineListener(e=>{if(e.duration!==120||e.position!==30)throw Error('Wrong timeline units '+JSON.stringify(e));done('timeline',e);});
wallpaperRegisterMediaThumbnailListener(e=>{if(!e.thumbnail.startsWith('data:image/png;base64,'))throw Error('Wrong album art');if(e.primaryColor!=='rgb(220,30,50)')throw Error('Wrong cover color '+e.primaryColor);done('thumbnail',e.thumbnail.slice(0,22));});
setTimeout(()=>{if(Object.keys(got).length!==5)throw Error('Missing media callbacks '+JSON.stringify(got));else console.warn('TEST_MEDIA_BRIDGE_PASS');},3000);
