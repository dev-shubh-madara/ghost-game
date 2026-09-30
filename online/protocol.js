// Validate remote state before it reaches Three.js or changes the shared mission.
export function validPacket(p, host = false) {
  const vector=(v,limit)=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<=limit);
  if(!p||!Number.isInteger(p.round)||p.round<0||!vector(p.p,501)||p.p[1]<0||p.p[1]>7||!vector(p.dir,1.01)||Math.hypot(...p.dir)<.9||Math.hypot(...p.dir)>1.1||typeof p.torch!=='boolean'||typeof p.lit!=='boolean'||typeof p.dead!=='boolean'||typeof p.active!=='boolean')return false;
  if(host){const w=p.world;if(!w||!Number.isFinite(w.time)||w.time<0||w.time>86400000||!vector(w.ghost,530)||w.round!==p.round||typeof w.visible!=='boolean'||!Number.isInteger(w.mission)||w.mission<0||w.mission>=150||![0,1,2].includes(w.stage)||typeof w.paid!=='boolean'||typeof w.wood!=='boolean'||!Array.isArray(w.doors)||w.doors.length>100||w.doors.some(x=>typeof x!=='boolean'))return false;}
  return true;
}
