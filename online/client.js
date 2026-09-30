import {validPacket} from './protocol.js';
export async function setupOnline(adapter){
  const $=s=>document.querySelector(s),status=t=>$('#onlineStatus').textContent=t;
  let db,user,room=null,outgoing,incoming,peerActive=false,peerSeen=0,connected=false,refreshing=false,disposed=false;
  const api={get room(){return room;},get isHost(){return room?.host===user?.id;},canPlay(){return connected&&room?.ready&&peerSeen>0&&(api.isHost||peerActive);},send(packet){if(connected)outgoing.send({type:'broadcast',event:'state',payload:packet}).catch(()=>status('Connection interrupted. Reconnecting…'));}};
  $('#onlineToggle').onclick=()=>$('#onlinePanel').classList.toggle('hidden');
  const config=await fetch('./online/config.json').then(r=>{if(!r.ok)throw Error('Configuration unavailable');return r.json();});
  if(!config.supabaseUrl||!config.supabasePublishableKey){status('Online play is not activated yet. Solo Torch Survival is ready.');$('#authForm').querySelectorAll('input,button').forEach(e=>e.disabled=true);return api;}
  const {createClient}=await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.57.4/+esm');
  db=createClient(config.supabaseUrl,config.supabasePublishableKey);
  async function rpc(action,target=null){const {data,error}=await db.rpc('wraith_action',{action,target});if(error)throw error;return data;}
  const run=fn=>async e=>{e?.preventDefault();try{await fn();}catch(error){status(error.message||'Online action failed');}};
  function button(text,fn){const b=document.createElement('button');b.className='secondary';b.textContent=text;b.onclick=run(fn);return b;}
  async function detach(){connected=false;peerSeen=0;peerActive=false;const channels=[outgoing,incoming].filter(Boolean);outgoing=incoming=null;room=null;await Promise.all(channels.map(c=>db.removeChannel(c)));$('#leaveRoom').classList.add('hidden');$('#lobbyStatus').textContent='';adapter.onDisconnect();}
  async function enter(r){
    if(room)await detach();room=r;disposed=false;adapter.onRoom();$('#leaveRoom').classList.remove('hidden');
    await db.realtime.setAuth((await db.auth.getSession()).data.session.access_token);
    const other=api.isHost?r.guest:r.host;
    outgoing=db.channel(`wraith:${r.id}:${user.id}`,{config:{private:true,broadcast:{ack:true}}});
    incoming=db.channel(`wraith:${r.id}:${other}`,{config:{private:true}}).on('broadcast',{event:'state'},({payload})=>{
      if(!validPacket(payload,!api.isHost))return;peerSeen=Date.now();peerActive=payload.active;adapter.onPeer(payload);
    });
    let ownReady=false,otherReady=false;
    const observe=own=>state=>{if(!room)return;if(own)ownReady=state==='SUBSCRIBED';else otherReady=state==='SUBSCRIBED';connected=ownReady&&otherReady;if(state==='CHANNEL_ERROR'||state==='TIMED_OUT'){status('Co-op connection lost. Leave and rejoin the room.');}updateLobby();};
    outgoing.subscribe(observe(true));incoming.subscribe(observe(false));updateLobby();
  }
  function updateLobby(){if(!room)return;$('#lobbyStatus').textContent=`Room ${room.id.slice(0,8)} · ${!room.ready?'Waiting for your friend to accept…':!connected||!peerSeen?'Connecting both players…':api.isHost?'Friend connected. Enter the house to start.':'Connected. The host starts the round; then choose Enter the house.'} The host carries clues; either torch protects the team. Esc opens the menu but does not pause co-op.`;}
  async function refresh(){
    if(!user||refreshing)return;refreshing=true;
    try{
      const [friends,rooms]=await Promise.all([db.from('wraith_friends').select('*'),db.from('wraith_rooms').select('*').eq('closed',false).gt('created_at',new Date(Date.now()-86400000).toISOString())]);
      if(friends.error)throw friends.error;if(rooms.error)throw rooms.error;
      $('#friends').replaceChildren();for(const f of friends.data){const other=f.sender===user.id?f.recipient:f.sender,li=document.createElement('li');li.textContent=`${other} · ${f.status} `;
        if(f.status==='pending'&&f.recipient===user.id){li.append(button('ACCEPT',async()=>{await rpc('accept',other);await refresh();}),button('DECLINE',async()=>{await rpc('decline',other);await refresh();}));}
        if(f.status==='accepted')li.append(button('INVITE TO CO-OP',async()=>{await enter(await rpc('create',other));}));$('#friends').append(li);}
      $('#roomInvites').replaceChildren();for(const r of rooms.data){if(r.id===room?.id)continue;const li=document.createElement('li');li.textContent=`${r.host===user.id?'Your lobby':'Invitation from '+r.host} `;li.append(button('JOIN',async()=>enter(r.host===user.id?r:await rpc('join',r.id))));$('#roomInvites').append(li);}
      if(room){const current=rooms.data.find(r=>r.id===room.id);if(!current){await detach();status('The room was closed.');}else{room=current;updateLobby();}}
    }finally{refreshing=false;}
  }
  async function sessionChanged(session){user=session?.user;$('#authForm').classList.toggle('hidden',!!user);$('#accountPanel').classList.toggle('hidden',!user);if(!user){if(room)await detach();status('Log in or create an account to play with a friend.');return;}await rpc('profile');$('#playerId').textContent='Your player ID: '+user.id;status('Signed in. Share your player ID with your friend.');await refresh();}
  $('#authForm').onsubmit=run(async()=>{const {error}=await db.auth.signInWithPassword({email:$('#email').value.trim(),password:$('#password').value});$('#password').value='';if(error)throw error;});
  $('#signup').onclick=run(async()=>{if(!$('#authForm').reportValidity())return;const {error}=await db.auth.signUp({email:$('#email').value.trim(),password:$('#password').value});$('#password').value='';if(error)throw error;status('Account created. Check your email to confirm it, then log in.');});
  $('#signout').onclick=run(async()=>{if(room){await rpc('leave',room.id);await detach();}const {error}=await db.auth.signOut();if(error)throw error;});
  $('#friendForm').onsubmit=run(async()=>{const id=$('#friendId').value.trim();if(!/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(id))throw Error('Paste the complete player ID.');await rpc('request',id);status('Friend request sent.');await refresh();});
  $('#refreshFriends').onclick=run(refresh);$('#leaveRoom').onclick=run(async()=>{await rpc('leave',room.id);await detach();await refresh();});
  // Defer async work outside the auth callback to avoid holding the SDK auth lock.
  db.auth.onAuthStateChange((_event,session)=>setTimeout(()=>sessionChanged(session).catch(e=>status(e.message)),0));
  await sessionChanged((await db.auth.getSession()).data.session);
  setInterval(()=>{if(!disposed)refresh().catch(e=>status(e.message));if(room&&peerSeen&&Date.now()-peerSeen>12000){disposed=true;detach().then(()=>status('Your friend disconnected. Return to the lobby to reconnect.'));}},3000);
  return api;
}
