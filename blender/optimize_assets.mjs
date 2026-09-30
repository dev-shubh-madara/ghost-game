import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {dedup,prune,weld,meshopt} from '@gltf-transform/functions';
import {MeshoptEncoder,MeshoptDecoder} from 'meshoptimizer';
import {fileURLToPath} from 'node:url';
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder});
for(const name of ['haunted-rooms','ghost','ethan','maya']){
 const file=fileURLToPath(new URL('../models/'+name+'.glb',import.meta.url));
 const doc=await io.read(file);
 await doc.transform(dedup(),weld(),prune(),meshopt({encoder:MeshoptEncoder,level:'high'}));
 await io.write(file,doc);console.log('Optimized',name);
}
