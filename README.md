
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


Q. How much fast is SmartBody simulation? and when do these calculations occur actually?


Python floating point hell!
http://stackoverflow.com/a/455634/1461232


looks like there is a bug in json.dumps which might be called from Python print to dictionaries
use https://github.com/esnme/ultrajson instead!


consider using gevent http://blog.pythonisito.com/2011/07/gevent-zeromq-websockets-and-flot-ftw.html

consider this article about thread safety http://stackoverflow.com/questions/5841896/0mq-how-to-use-zeromq-in-a-threadsafe-manner

DZone article about ZMQ http://java.dzone.com/articles/distributed-systems-zeromq

Getting rid of ZMQ context http://250bpm.com/blog:23

SOA and ZMQ architecture use case http://www.aosabook.org/en/zeromq.html#fig.zeromq.multiuse

CONSIDER to use Greenlets!!

CONSIDER again throwing this whole Python thing and use NodeJS
  http://socket.io/blog/introducing-socket-io-1-0/#binary
  https://nodejs.org/api/addons.html
