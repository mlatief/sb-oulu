
http://stackoverflow.com/questions/7919516/using-textures-in-three-js
var texture = materials[i].map;
if(texture instanceof THREE.Texture){
  var image = texture.sourceFile;
}



for(i=0; i<4; i++){
  var light = new THREE.SpotLight( 0xffffff, 0.75 );
  light.castShadow = true;
  scene.add( light );
  lights.push( light );
}
lights[0].position.set(5,5,5);
lights[1].position.set(-5,5,5);
lights[2].position.set(-5,5,-5);
lights[3].position.set(5,5,-5);

//Point the lights toward dear Brad!
_.each(lights, function(t){
  this.target = brad;
  });
